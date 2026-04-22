from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class DialogValidationError(ValueError):
    """Dialogue data does not match the supported schema."""


@dataclass(frozen=True)
class DialogChoice:
    """プレイヤー選択肢1件（表示文と遷移先シーン名）。"""

    text: str
    next_scene: str | None = None


@dataclass(frozen=True)
class DialogStep:
    """1シーン分の台詞（話者・本文・選択肢・次シーン）を束ねた不変レコード。"""

    scene_name: str
    speaker: str | None
    text: str
    choices: list[DialogChoice] = field(default_factory=list)
    next_scene: str | None = None


class StructuredDialogRunner:
    """構造化された会話データを再生するランナー。検証・分岐・変数展開を担う。"""

    _SCENE_KEYS = {"speaker", "text", "set", "choices", "next", "variants"}
    _VARIANT_KEYS = {"when", "speaker", "text", "set", "choices", "next"}

    def __init__(self, source: "dict[str, Any]"):
        """dict形式の会話データを受け取り、シーンと変数を検証した上で保持する。"""
        if not isinstance(source, dict):
            raise DialogValidationError(
                "StructuredDialogRunner now requires a dict (no YAML loader); "
                f"got {type(source).__name__}"
            )
        self.source_path = None
        self.variables = self._validate_variables(source.get("variables"))
        self.scenes = self._validate_scenes(source.get("scenes"))
        self._mutable_state: dict[str, Any] = {}
        self._extra_context: dict[str, Any] = {}
        self._current_step: DialogStep | None = None

    def start(
        self,
        scene_name: str,
        state: dict[str, Any] | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> DialogStep:
        """会話を指定シーンから開始し、可変状態と文脈を初期化して最初のステップを返す。"""
        self._mutable_state = state if state is not None else {}
        self._extra_context = dict(extra_context or {})
        self._current_step = self._resolve_scene(scene_name)
        return self._current_step

    def choose(self, index: int) -> DialogStep | None:
        """選択肢を選び、対応する次シーンのステップを返す（終端なら None）。"""
        if self._current_step is None:
            raise RuntimeError("choose() called before start()")
        if not self._current_step.choices:
            raise RuntimeError("choose() called without pending choices")
        if not (0 <= index < len(self._current_step.choices)):
            raise IndexError(f"choice index {index} out of range")
        choice = self._current_step.choices[index]
        if choice.next_scene is None:
            self._current_step = None
            return None
        self._current_step = self._resolve_scene(choice.next_scene)
        return self._current_step

    def continue_dialog(self) -> DialogStep | None:
        """選択肢なしシーンから next で繋がる次ステップへ進む（終端なら None）。"""
        if self._current_step is None:
            return None
        if self._current_step.choices or self._current_step.next_scene is None:
            self._current_step = None
            return None
        self._current_step = self._resolve_scene(self._current_step.next_scene)
        return self._current_step

    def load_all_lines(
        self,
        scene_name: str,
        state: dict[str, Any] | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> list[str]:
        """選択肢が出るまで（または終端まで）一気に読んで台詞一覧を返す。"""
        step = self.start(scene_name, state=state, extra_context=extra_context)
        lines = [step.text]
        while True:
            if step.choices:
                return lines
            step = self.continue_dialog()
            if step is None:
                return lines
            lines.append(step.text)

    def _resolve_scene(self, scene_name: str) -> DialogStep:
        """シーン名から適切な variant を選び、set 適用・変数展開して DialogStep を組み立てる。"""
        try:
            scene = self.scenes[scene_name]
        except KeyError as exc:
            raise KeyError(f"unknown scene: {scene_name}") from exc
        body = self._select_body(scene_name, scene)
        self._apply_set(body.get("set"))
        choices = [
            DialogChoice(text=self._format_text(choice["text"]), next_scene=choice.get("next"))
            for choice in body.get("choices", [])
        ]
        return DialogStep(
            scene_name=scene_name,
            speaker=body.get("speaker"),
            text=self._format_text(body["text"]),
            choices=choices,
            next_scene=body.get("next"),
        )

    def _select_body(self, scene_name: str, scene: dict[str, Any]) -> dict[str, Any]:
        """variants から現在の状態に一致するものを選ぶ（なければシーン自体をそのまま返す）。"""
        variants = scene.get("variants")
        if variants is None:
            return scene
        current_state = {**self._mutable_state, **self._extra_context}
        for variant in variants:
            when = variant.get("when")
            if when is None:
                return variant
            if all(current_state.get(name) == expected for name, expected in when.items()):
                return variant
        raise DialogValidationError(f"no matching variant for scene '{scene_name}'")

    def _apply_set(self, values: dict[str, Any] | None) -> None:
        """シーンの set 句を可変状態に反映する。"""
        if not values:
            return
        for name, value in values.items():
            self._mutable_state[name] = value

    def _format_text(self, text: str) -> str:
        """台詞テンプレートに状態・文脈の変数を差し込む。未定義変数は検証エラー。"""
        values = {**self._mutable_state, **self._extra_context}
        try:
            return text.format(**values)
        except KeyError as exc:
            raise DialogValidationError(
                f"missing format value '{exc.args[0]}' in scene text '{text}'"
            ) from exc

    def _validate_variables(self, raw_variables: Any) -> set[str]:
        """variables 宣言（文字列リスト）を検証して集合化する。"""
        if not isinstance(raw_variables, list) or not all(isinstance(item, str) for item in raw_variables):
            raise DialogValidationError("variables must be a list of strings")
        return set(raw_variables)

    def _validate_scenes(self, raw_scenes: Any) -> dict[str, dict[str, Any]]:
        """全シーンの構造と next 参照の整合性を検証する。"""
        if not isinstance(raw_scenes, dict) or not raw_scenes:
            raise DialogValidationError("scenes must be a non-empty mapping")
        scenes: dict[str, dict[str, Any]] = {}
        refs: list[tuple[str, str]] = []
        for scene_name, raw_scene in raw_scenes.items():
            if not isinstance(scene_name, str):
                raise DialogValidationError("scene names must be strings")
            if not isinstance(raw_scene, dict):
                raise DialogValidationError(f"scene '{scene_name}' must be a mapping")
            scenes[scene_name] = raw_scene
            refs.extend(self._validate_scene(scene_name, raw_scene))
        for source, target in refs:
            if target not in raw_scenes:
                raise DialogValidationError(
                    f"scene '{source}' references unknown next scene '{target}'"
                )
        return scenes

    def _validate_scene(self, scene_name: str, scene: dict[str, Any]) -> list[tuple[str, str]]:
        """1シーン分のキー妥当性と variants / 直接キーの排他を検証する。"""
        unknown_keys = set(scene) - self._SCENE_KEYS
        if unknown_keys:
            raise DialogValidationError(
                f"scene '{scene_name}' has unknown keys: {', '.join(sorted(unknown_keys))}"
            )
        refs: list[tuple[str, str]] = []
        variants = scene.get("variants")
        if variants is not None:
            direct_keys = set(scene) & {"speaker", "text", "set", "choices", "next"}
            if direct_keys:
                raise DialogValidationError(
                    f"scene '{scene_name}' cannot mix variants with direct keys: {', '.join(sorted(direct_keys))}"
                )
            if not isinstance(variants, list) or not variants:
                raise DialogValidationError(f"scene '{scene_name}' variants must be a non-empty list")
            for index, variant in enumerate(variants):
                refs.extend(self._validate_variant(scene_name, index, variant))
            return refs
        refs.extend(self._validate_entry(scene_name, scene, allow_when=False))
        return refs

    def _validate_variant(self, scene_name: str, index: int, variant: Any) -> list[tuple[str, str]]:
        """variant 単位でキー妥当性を検証する。"""
        if not isinstance(variant, dict):
            raise DialogValidationError(f"scene '{scene_name}' variant {index} must be a mapping")
        unknown_keys = set(variant) - self._VARIANT_KEYS
        if unknown_keys:
            raise DialogValidationError(
                f"scene '{scene_name}' variant {index} has unknown keys: {', '.join(sorted(unknown_keys))}"
            )
        return self._validate_entry(f"{scene_name}[{index}]", variant, allow_when=True)

    def _validate_entry(self, owner: str, entry: dict[str, Any], *, allow_when: bool) -> list[tuple[str, str]]:
        """シーン／variant 共通の本文部分（speaker/text/set/next/choices）を検証する。"""
        refs: list[tuple[str, str]] = []
        if allow_when and "when" in entry and not isinstance(entry["when"], dict):
            raise DialogValidationError(f"scene '{owner}' when must be a mapping")
        speaker = entry.get("speaker")
        if speaker is not None and not isinstance(speaker, str):
            raise DialogValidationError(f"scene '{owner}' speaker must be a string")
        text = entry.get("text")
        if not isinstance(text, str) or not text:
            raise DialogValidationError(f"scene '{owner}' text must be a non-empty string")
        set_values = entry.get("set")
        if set_values is not None:
            if not isinstance(set_values, dict):
                raise DialogValidationError(f"scene '{owner}' set must be a mapping")
            for name in set_values:
                if name not in self.variables:
                    raise DialogValidationError(f"scene '{owner}' sets unknown variable '{name}'")
        next_scene = entry.get("next")
        if next_scene is not None:
            if not isinstance(next_scene, str):
                raise DialogValidationError(f"scene '{owner}' next must be a string")
            refs.append((owner, next_scene))
        choices = entry.get("choices")
        if choices is not None:
            if next_scene is not None:
                raise DialogValidationError(f"scene '{owner}' cannot have both next and choices")
            if not isinstance(choices, list) or not choices:
                raise DialogValidationError(f"scene '{owner}' choices must be a non-empty list")
            for choice_index, choice in enumerate(choices):
                refs.extend(self._validate_choice(owner, choice_index, choice))
        return refs

    def _validate_choice(self, owner: str, choice_index: int, choice: Any) -> list[tuple[str, str]]:
        """選択肢1件の text と next を検証する。"""
        if not isinstance(choice, dict):
            raise DialogValidationError(f"scene '{owner}' choice {choice_index} must be a mapping")
        text = choice.get("text")
        if not isinstance(text, str) or not text:
            raise DialogValidationError(f"scene '{owner}' choice {choice_index} text must be a non-empty string")
        next_scene = choice.get("next")
        if next_scene is None:
            return []
        if not isinstance(next_scene, str):
            raise DialogValidationError(f"scene '{owner}' choice {choice_index} next must be a string")
        return [(owner, next_scene)]
