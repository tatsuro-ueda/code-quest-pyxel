"""Structured YAML-backed dialogue runtime for Block Quest."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.platform == "emscripten":
    _yaml = None
else:
    try:
        import yaml as _yaml
    except ModuleNotFoundError:
        _yaml = None

from src.simple_yaml import safe_load as simple_yaml_safe_load


class DialogValidationError(ValueError):
    """Dialogue data does not match the supported schema."""


@dataclass(frozen=True)
class DialogChoice:
    text: str
    next_scene: str | None = None


@dataclass(frozen=True)
class DialogStep:
    scene_name: str
    speaker: str | None
    text: str
    choices: list[DialogChoice] = field(default_factory=list)
    next_scene: str | None = None


class StructuredDialogRunner:
    """Load, validate, and execute the project's structured dialogue YAML."""

    _SCENE_KEYS = {"speaker", "text", "set", "choices", "next", "variants"}
    _VARIANT_KEYS = {"when", "speaker", "text", "set", "choices", "next"}

    def __init__(self, source_path: str | Path):
        self.source_path = Path(source_path)
        raw = self._safe_load(self.source_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise DialogValidationError("dialogue root must be a mapping")

        self.variables = self._validate_variables(raw.get("variables"))
        self.scenes = self._validate_scenes(raw.get("scenes"))

        self._mutable_state: dict[str, Any] = {}
        self._extra_context: dict[str, Any] = {}
        self._current_step: DialogStep | None = None

    def _safe_load(self, text: str) -> Any:
        if _yaml is not None:
            return _yaml.safe_load(text)
        return simple_yaml_safe_load(text)

    def start(
        self,
        scene_name: str,
        state: dict[str, Any] | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> DialogStep:
        self._mutable_state = state if state is not None else {}
        self._extra_context = dict(extra_context or {})
        self._current_step = self._resolve_scene(scene_name)
        return self._current_step

    def choose(self, index: int) -> DialogStep | None:
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
        try:
            scene = self.scenes[scene_name]
        except KeyError as exc:
            raise KeyError(f"unknown scene: {scene_name}") from exc

        body = self._select_body(scene_name, scene)
        self._apply_set(body.get("set"))
        choices = [
            DialogChoice(
                text=self._format_text(choice["text"]),
                next_scene=choice.get("next"),
            )
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
        if not values:
            return
        for name, value in values.items():
            self._mutable_state[name] = value

    def _format_text(self, text: str) -> str:
        values = {**self._mutable_state, **self._extra_context}
        try:
            return text.format(**values)
        except KeyError as exc:
            missing = exc.args[0]
            raise DialogValidationError(
                f"missing format value '{missing}' in scene text '{text}'"
            ) from exc

    def _validate_variables(self, raw_variables: Any) -> set[str]:
        if not isinstance(raw_variables, list) or not all(
            isinstance(item, str) for item in raw_variables
        ):
            raise DialogValidationError("variables must be a list of strings")
        return set(raw_variables)

    def _validate_scenes(self, raw_scenes: Any) -> dict[str, dict[str, Any]]:
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
        unknown_keys = set(scene) - self._SCENE_KEYS
        if unknown_keys:
            names = ", ".join(sorted(unknown_keys))
            raise DialogValidationError(f"scene '{scene_name}' has unknown keys: {names}")

        refs: list[tuple[str, str]] = []
        variants = scene.get("variants")
        if variants is not None:
            direct_keys = set(scene) & {"speaker", "text", "set", "choices", "next"}
            if direct_keys:
                names = ", ".join(sorted(direct_keys))
                raise DialogValidationError(
                    f"scene '{scene_name}' cannot mix variants with direct keys: {names}"
                )
            if not isinstance(variants, list) or not variants:
                raise DialogValidationError(
                    f"scene '{scene_name}' variants must be a non-empty list"
                )
            for index, variant in enumerate(variants):
                refs.extend(self._validate_variant(scene_name, index, variant))
            return refs

        refs.extend(self._validate_entry(scene_name, scene, allow_when=False))
        return refs

    def _validate_variant(
        self,
        scene_name: str,
        index: int,
        variant: Any,
    ) -> list[tuple[str, str]]:
        if not isinstance(variant, dict):
            raise DialogValidationError(
                f"scene '{scene_name}' variant {index} must be a mapping"
            )
        unknown_keys = set(variant) - self._VARIANT_KEYS
        if unknown_keys:
            names = ", ".join(sorted(unknown_keys))
            raise DialogValidationError(
                f"scene '{scene_name}' variant {index} has unknown keys: {names}"
            )
        refs = self._validate_entry(f"{scene_name}[{index}]", variant, allow_when=True)
        return refs

    def _validate_entry(
        self,
        owner: str,
        entry: dict[str, Any],
        *,
        allow_when: bool,
    ) -> list[tuple[str, str]]:
        refs: list[tuple[str, str]] = []
        when = entry.get("when")
        if when is not None:
            if not allow_when:
                raise DialogValidationError(f"scene '{owner}' cannot define when directly")
            self._validate_mapping_variables(owner, when, field_name="when")

        text = entry.get("text")
        if not isinstance(text, str) or not text:
            raise DialogValidationError(f"scene '{owner}' must define non-empty text")

        speaker = entry.get("speaker")
        if speaker is not None and not isinstance(speaker, str):
            raise DialogValidationError(f"scene '{owner}' speaker must be a string")

        if "set" in entry:
            self._validate_mapping_variables(owner, entry.get("set"), field_name="set")

        next_scene = entry.get("next")
        if next_scene is not None:
            if not isinstance(next_scene, str):
                raise DialogValidationError(f"scene '{owner}' next must be a string")
            refs.append((owner, next_scene))

        choices = entry.get("choices", [])
        if choices != [] and not isinstance(choices, list):
            raise DialogValidationError(f"scene '{owner}' choices must be a list")
        for choice_index, choice in enumerate(choices):
            refs.extend(self._validate_choice(owner, choice_index, choice))

        return refs

    def _validate_choice(
        self,
        owner: str,
        index: int,
        choice: Any,
    ) -> list[tuple[str, str]]:
        if not isinstance(choice, dict):
            raise DialogValidationError(
                f"scene '{owner}' choice {index} must be a mapping"
            )
        if not isinstance(choice.get("text"), str) or not choice["text"]:
            raise DialogValidationError(
                f"scene '{owner}' choice {index} must define non-empty text"
            )
        refs: list[tuple[str, str]] = []
        next_scene = choice.get("next")
        if next_scene is not None:
            if not isinstance(next_scene, str):
                raise DialogValidationError(
                    f"scene '{owner}' choice {index} next must be a string"
                )
            refs.append((f"{owner}.choice[{index}]", next_scene))
        return refs

    def _validate_mapping_variables(
        self,
        owner: str,
        values: Any,
        *,
        field_name: str,
    ) -> None:
        if not isinstance(values, dict):
            raise DialogValidationError(
                f"scene '{owner}' {field_name} must be a mapping"
            )
        unknown_names = set(values) - self.variables
        if unknown_names:
            names = ", ".join(sorted(unknown_names))
            raise DialogValidationError(
                f"scene '{owner}' {field_name} uses undeclared variables: {names}"
            )
