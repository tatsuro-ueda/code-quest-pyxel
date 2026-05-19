"""構造化会話ランナー（旧 src/scenes/dialog/model.py）。

このファイルに含まれる関数・クラス：

- DialogValidationError: 会話データの schema 不一致を示す例外
- DialogChoice: 選択肢 1 件（表示文と遷移先シーン名）の不変レコード
- DialogStep: 1 シーン分の台詞情報をまとめた不変レコード
- StructuredDialogRunner: 構造化された会話データの検証・分岐・変数展開を担うランナー
  - __init__: dict 形式の会話データを検証して保持する
  - start: 会話を指定シーンから開始して最初のステップを返す
  - choose: 選択肢を選び対応する次シーンのステップを返す
  - continue_dialog: 選択肢なしシーンから next で次ステップへ進む
  - load_all_lines: 選択肢が出るか終端まで台詞一覧をまとめて返す
  - _require_dict_source: source が dict でなければ例外を投げる
  - _require_choose_ready: choose() の前提条件を検証する
  - _advance_with_choice: choose() の本体（次シーン解決）
  - _run_continue_dialog: continue_dialog() の本体（終端判定 + 次解決）
  - _is_dialog_terminated: 続けられない状態かの述語
  - _collect_lines_until_break: 選択肢／終端まで台詞を集める
  - _has_pending_choices: ステップが選択肢待ちかの述語
  - _resolve_scene: シーン名から DialogStep を組み立てる
  - _build_step_from_body: body dict から DialogStep を返す
  - _select_body: variants 一致 / scene 直書きから本文を選ぶ
  - _check_when_matches: when 句が現在状態に一致するかの述語
  - _apply_set: シーンの set 句を可変状態へ反映する
  - _format_text: 台詞テンプレートに状態・文脈の変数を差し込む
  - _validate_variables: variables 宣言を検証して集合化する
  - _is_nonempty_str: 値が空でない str かの述語
  - _is_nonempty_list: 値が空でない list かの述語
  - _is_nonempty_dict: 値が空でない dict かの述語
  - _is_string_list: 値が文字列リストかの述語
  - _validate_scenes: 全シーン構造と next 参照を検証する
  - _verify_refs_resolve: 参照リストの target がすべて存在するか検証する
  - _validate_scene: 1 シーン分のキー妥当性を検証する
  - _require_known_scene_keys: 未知 scene キーを検出して例外を投げる
  - _validate_scene_with_variants: variants 付きシーンを検証する
  - _require_variants_only: variants と直接キーの混在を弾く
  - _validate_variant: variant 単位のキー妥当性を検証する
  - _validate_entry: シーン／variant 共通本文を検証する
  - _validate_when: when キーの型を検証する
  - _validate_speaker: speaker の型を検証する
  - _validate_text: text が非空文字列かを検証する
  - _validate_set: set 句の型と未宣言変数を検証する
  - _validate_next_and_choices: next と choices の排他および型を検証する
  - _validate_next_ref: next キーの型を検証し参照リストに追加する
  - _validate_choices_block: choices ブロックの型・排他を検証する
  - _validate_choice: 選択肢 1 件の text と next を検証する

Problems:
    - 会話データの schema 検証と再生を Scene 直書きすると、検証ロジックと
      表示制御が混ざって不正なデータを早期に検出できなくなる。
    - 分岐（choices / next / variants）と変数展開（set / format）を
      ばらまくと、テンプレートの未定義変数や未知シーン参照を見落としやすい。

Solutions:
    - Scene から独立した service として StructuredDialogRunner に集約し、
      schema 検証（_validate_*）と再生（_resolve_scene/_select_body 等）を
      private helper に切り出す。
    - データソースは `src/generated/dialogue.py` の DIALOGUE_JA / DIALOGUE_EN
      を想定し、辞書を渡された時点で全シーンを検証してから再生する。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class DialogValidationError(ValueError):
    """Dialogue data does not match the supported schema."""

    # === Public API ===

    pass


@dataclass(frozen=True)
class DialogChoice:
    """プレイヤー選択肢 1 件（表示文と遷移先シーン名）。"""

    # === Public API ===

    text: str
    next_scene: str | None = None


@dataclass(frozen=True)
class DialogStep:
    """1 シーン分の台詞（話者・本文・選択肢・次シーン）を束ねた不変レコード。"""

    # === Public API ===

    scene_name: str
    speaker: str | None
    text: str
    choices: list[DialogChoice] = field(default_factory=list)
    next_scene: str | None = None


class StructuredDialogRunner:
    """構造化された会話データを再生するランナー。検証・分岐・変数展開を担う。"""

    # === Public API ===

    _SCENE_KEYS = {"speaker", "text", "set", "choices", "next", "variants"}
    _VARIANT_KEYS = {"when", "speaker", "text", "set", "choices", "next"}

    def __init__(self, source: "dict[str, Any]"):
        """dict 形式の会話データを受け取り、検証してシーンと変数を保持する。

        Args:
            source: variables（文字列リスト）と scenes（dict）を持つ辞書。
        Raises:
            DialogValidationError: source が dict でない、または schema 違反のとき。
        Policy:
            - dict 以外を渡された時点で DialogValidationError にする
              （YAML ローダーは廃止済み）。
            - 受け取り時に全シーンの構造と next 参照の整合を検証する。
        """
        self._require_dict_source(source)
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
        """会話を指定シーンから開始し、可変状態と文脈を初期化して最初のステップを返す。

        Args:
            scene_name: 開始するシーン名。
            state: 会話中に書き換える可変状態 dict（省略時は空辞書）。
            extra_context: 読み取り専用の追加文脈（省略時は空辞書）。
        Returns:
            開始シーンに対応する DialogStep。
        Policy:
            - 渡された state はそのまま保持し、set 句で書き換える。
        """
        self._mutable_state = state if state is not None else {}
        self._extra_context = dict(extra_context or {})
        self._current_step = self._resolve_scene(scene_name)
        return self._current_step

    def choose(self, index: int) -> DialogStep | None:
        """選択肢を選び、対応する次シーンのステップを返す（終端なら None）。

        Args:
            index: 選んだ選択肢の 0 始まりインデックス。
        Returns:
            次のシーンに対応する DialogStep、終端なら None。
        Raises:
            RuntimeError: start() より前か、選択肢の無い状態で呼ばれたとき。
            IndexError: index が選択肢範囲外のとき。
        Policy:
            - 述語ガードを通った後で private 委譲し、結果をそのまま返す。
        """
        self._require_choose_ready(index)
        return self._advance_with_choice(index)

    def continue_dialog(self) -> DialogStep | None:
        """選択肢なしシーンから next で繋がる次ステップへ進む（終端なら None）。

        Returns:
            次のシーンに対応する DialogStep、終端なら None。
        Policy:
            - 制御フローを持たず _run_continue_dialog に委譲する。
        """
        return self._run_continue_dialog()

    def load_all_lines(
        self,
        scene_name: str,
        state: dict[str, Any] | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> list[str]:
        """選択肢が出るまで（または終端まで）一気に読んで台詞一覧を返す。

        Args:
            scene_name: 開始するシーン名。
            state: 会話中に書き換える可変状態 dict（省略時は空辞書）。
            extra_context: 読み取り専用の追加文脈（省略時は空辞書）。
        Returns:
            開始から最初の選択肢／終端までの台詞文字列リスト。
        Policy:
            - 開始は start() に委譲し、収集は private helper に委ねる。
        """
        step = self.start(scene_name, state=state, extra_context=extra_context)
        return self._collect_lines_until_break(step)

    # === Internal helpers (private) ===

    def _require_dict_source(self, source: Any) -> None:
        """source が dict でなければ DialogValidationError を投げる。

        Args:
            source: __init__ に渡されたデータ。
        Raises:
            DialogValidationError: source が dict でないとき。
        Policy:
            - YAML ローダー廃止後のため、明示的に dict を要求する。
        """
        if not isinstance(source, dict):
            raise DialogValidationError(
                "StructuredDialogRunner now requires a dict (no YAML loader); "
                f"got {type(source).__name__}"
            )

    def _require_choose_ready(self, index: int) -> None:
        """choose() の前提条件（開始済み・選択肢有り・index 範囲内）を検証する。

        Args:
            index: 選んだ選択肢の 0 始まりインデックス。
        Raises:
            RuntimeError: start() 未呼出または選択肢が無いとき。
            IndexError: index が選択肢範囲外のとき。
        Policy:
            - 公開関数 choose() から制御フローを引き取り、述語チェックに専念する。
        """
        if self._current_step is None:
            raise RuntimeError("choose() called before start()")
        if not self._current_step.choices:
            raise RuntimeError("choose() called without pending choices")
        if not (0 <= index < len(self._current_step.choices)):
            raise IndexError(f"choice index {index} out of range")

    def _advance_with_choice(self, index: int) -> DialogStep | None:
        """choose() の本体（選択肢から次シーン解決まで）を担う。

        Args:
            index: 選んだ選択肢の 0 始まりインデックス。
        Returns:
            次のシーンに対応する DialogStep、終端なら None。
        Policy:
            - 前提条件は呼び出し側で保証済みのため、ここでは分岐実行のみ。
        """
        assert self._current_step is not None
        choice = self._current_step.choices[index]
        if choice.next_scene is None:
            self._current_step = None
            return None
        self._current_step = self._resolve_scene(choice.next_scene)
        return self._current_step

    def _run_continue_dialog(self) -> DialogStep | None:
        """continue_dialog() の本体（終端判定 + next シーン解決）。

        Returns:
            次のシーンに対応する DialogStep、終端なら None。
        Policy:
            - 終端判定は _is_dialog_terminated に切り出し、続行可能なら
              _resolve_scene で次ステップを解決する。
        """
        if self._is_dialog_terminated():
            self._current_step = None
            return None
        assert self._current_step is not None
        assert self._current_step.next_scene is not None
        self._current_step = self._resolve_scene(self._current_step.next_scene)
        return self._current_step

    def _is_dialog_terminated(self) -> bool:
        """continue_dialog() で続けられない状態か（現在ステップが無い／選択肢有り／next 無し）。

        Returns:
            続行できないなら True。
        Policy:
            - 制御フローの述語化のため、複合条件を 1 つのメソッドに切り出す。
        """
        if self._current_step is None:
            return True
        if self._current_step.choices:
            return True
        return self._current_step.next_scene is None

    def _collect_lines_until_break(self, first_step: DialogStep) -> list[str]:
        """選択肢が出るか終端に達するまで continue_dialog で台詞を集める。

        Args:
            first_step: start() で得られた最初のステップ。
        Returns:
            台詞文字列リスト（first_step.text を含む）。
        Policy:
            - load_all_lines() からループ制御を引き取り、収集処理を独立させる。
        """
        lines = [first_step.text]
        step: DialogStep | None = first_step
        while True:
            if self._has_pending_choices(step):
                return lines
            step = self.continue_dialog()
            if step is None:
                return lines
            lines.append(step.text)

    @staticmethod
    def _has_pending_choices(step: DialogStep | None) -> bool:
        """ステップが選択肢待ちの状態か。

        Args:
            step: 判定対象のステップ（None もありうる）。
        Returns:
            step が非 None で choices を持つなら True。
        Policy:
            - None ガードと choices 判定を 1 つに束ね、複合条件を述語化する。
        """
        if step is None:
            return False
        return bool(step.choices)

    def _resolve_scene(self, scene_name: str) -> DialogStep:
        """シーン名から variant 選択・set 適用・変数展開して DialogStep を組み立てる。

        Args:
            scene_name: 解決対象のシーン名。
        Returns:
            組み立て済みの DialogStep。
        Raises:
            KeyError: scene_name が未登録のとき。
            DialogValidationError: variant がいずれも一致しないとき。
        Policy:
            - 本文選択は _select_body、set は _apply_set、本体組立は
              _build_step_from_body に切り出す。
        """
        try:
            scene = self.scenes[scene_name]
        except KeyError as exc:
            raise KeyError(f"unknown scene: {scene_name}") from exc
        body = self._select_body(scene_name, scene)
        self._apply_set(body.get("set"))
        return self._build_step_from_body(scene_name, body)

    def _build_step_from_body(
        self, scene_name: str, body: dict[str, Any]
    ) -> DialogStep:
        """body dict から choices を組み立てて DialogStep を返す。

        Args:
            scene_name: シーン名（DialogStep に詰める）。
            body: variant または scene 直書きの本文 dict。
        Returns:
            組み立て済みの DialogStep。
        Policy:
            - choices と text の format をまとめて適用し、副作用は持たない。
        """
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

    def _select_body(
        self, scene_name: str, scene: dict[str, Any]
    ) -> dict[str, Any]:
        """variants から現在の状態に一致するものを選ぶ（無ければ scene 自体）。

        Args:
            scene_name: シーン名（エラーメッセージ用）。
            scene: 解決対象のシーン dict。
        Returns:
            選択された本文 dict（variant または scene 自体）。
        Raises:
            DialogValidationError: variants がいずれも一致しないとき。
        Policy:
            - variants が無ければ scene 自体を返す。
            - when 句との一致判定は _matches_when に切り出す。
        """
        variants = scene.get("variants")
        if variants is None:
            return scene
        current_state = {**self._mutable_state, **self._extra_context}
        for variant in variants:
            if self._check_when_matches(variant.get("when"), current_state):
                return variant
        raise DialogValidationError(
            f"no matching variant for scene '{scene_name}'"
        )

    @staticmethod
    def _check_when_matches(
        when: dict[str, Any] | None, current_state: dict[str, Any]
    ) -> bool:
        """when 句が現在状態に一致するか（when=None は常に一致）。

        Args:
            when: 一致条件 dict、または None。
            current_state: mutable_state と extra_context を合わせた現在状態。
        Returns:
            一致すれば True。
        Policy:
            - when=None はワイルドカード扱い。
        """
        if when is None:
            return True
        return all(
            current_state.get(name) == expected
            for name, expected in when.items()
        )

    def _apply_set(self, values: dict[str, Any] | None) -> None:
        """シーンの set 句を可変状態に反映する。

        Args:
            values: set 句の dict（None や空は何もしない）。
        Policy:
            - values の各キーは _validate_entry で variables 集合との
              整合が事前確認されている。
        """
        if not values:
            return
        for name, value in values.items():
            self._mutable_state[name] = value

    def _format_text(self, text: str) -> str:
        """台詞テンプレートに状態・文脈の変数を差し込む。

        Args:
            text: format 対象のテンプレート文字列。
        Returns:
            変数を差し込んだ文字列。
        Raises:
            DialogValidationError: 未定義の変数がテンプレートに含まれるとき。
        Policy:
            - mutable_state と extra_context をマージして str.format に渡す。
        """
        values = {**self._mutable_state, **self._extra_context}
        try:
            return text.format(**values)
        except KeyError as exc:
            raise DialogValidationError(
                f"missing format value '{exc.args[0]}' in scene text '{text}'"
            ) from exc

    def _validate_variables(self, raw_variables: Any) -> set[str]:
        """variables 宣言（文字列リスト）を検証して集合化する。

        Args:
            raw_variables: source["variables"] の値。
        Returns:
            宣言された変数名の集合。
        Raises:
            DialogValidationError: list[str] でないとき。
        Policy:
            - 述語に切り出さず単純な型チェックで早期に弾く。
        """
        if not self._is_string_list(raw_variables):
            raise DialogValidationError("variables must be a list of strings")
        return set(raw_variables)

    @staticmethod
    def _is_nonempty_str(value: Any) -> bool:
        """value が空でない str か。

        Args:
            value: 判定対象。
        Returns:
            str かつ非空なら True。
        Policy:
            - 空文字列は schema 上不正なので False を返す。
        """
        if not isinstance(value, str):
            return False
        return bool(value)

    @staticmethod
    def _is_nonempty_list(value: Any) -> bool:
        """value が空でない list か。

        Args:
            value: 判定対象。
        Returns:
            list かつ非空なら True。
        Policy:
            - schema 上空リストは許可しないため、空判定も含める。
        """
        if not isinstance(value, list):
            return False
        return bool(value)

    @staticmethod
    def _is_nonempty_dict(value: Any) -> bool:
        """value が空でない dict か。

        Args:
            value: 判定対象。
        Returns:
            dict かつ非空なら True。
        Policy:
            - schema 上空辞書は許可しないため、空判定も含める。
        """
        if not isinstance(value, dict):
            return False
        return bool(value)

    @staticmethod
    def _is_string_list(value: Any) -> bool:
        """value が文字列リストか。

        Args:
            value: 判定対象。
        Returns:
            list[str] であれば True。
        Policy:
            - 空リストも True とする（変数宣言が無い会話を許容するため）。
        """
        if not isinstance(value, list):
            return False
        return all(isinstance(item, str) for item in value)

    def _validate_scenes(
        self, raw_scenes: Any
    ) -> dict[str, dict[str, Any]]:
        """全シーンの構造と next 参照の整合性を検証する。

        Args:
            raw_scenes: source["scenes"] の値。
        Returns:
            シーン名から dict への辞書。
        Raises:
            DialogValidationError: scenes が空、または schema 違反、未知 next 参照のとき。
        Policy:
            - 各シーンの検証は _validate_scene に委譲し、参照の解決を最後にまとめる。
        """
        if not self._is_nonempty_dict(raw_scenes):
            raise DialogValidationError("scenes must be a non-empty mapping")
        scenes: dict[str, dict[str, Any]] = {}
        refs: list[tuple[str, str]] = []
        for scene_name, raw_scene in raw_scenes.items():
            if not isinstance(scene_name, str):
                raise DialogValidationError("scene names must be strings")
            if not isinstance(raw_scene, dict):
                raise DialogValidationError(
                    f"scene '{scene_name}' must be a mapping")
            scenes[scene_name] = raw_scene
            refs.extend(self._validate_scene(scene_name, raw_scene))
        self._verify_refs_resolve(refs, raw_scenes)
        return scenes

    @staticmethod
    def _verify_refs_resolve(
        refs: list[tuple[str, str]],
        raw_scenes: dict[str, Any],
    ) -> None:
        """next 参照リストが全て raw_scenes 内に解決するか検証する。

        Args:
            refs: (source_scene, target_scene) のタプルリスト。
            raw_scenes: シーン名から dict への辞書。
        Raises:
            DialogValidationError: target が未登録のとき。
        Policy:
            - _validate_scenes から参照解決を切り出す。
        """
        for source, target in refs:
            if target not in raw_scenes:
                raise DialogValidationError(
                    f"scene '{source}' references "
                    f"unknown next scene '{target}'"
                )

    def _validate_scene(
        self, scene_name: str, scene: dict[str, Any]
    ) -> list[tuple[str, str]]:
        """1 シーン分のキー妥当性と variants / 直接キーの排他を検証する。

        Args:
            scene_name: シーン名。
            scene: シーン dict。
        Returns:
            このシーンが持つ (source, target) next 参照リスト。
        Raises:
            DialogValidationError: 未知キー、variants と直接キーの混在、
                variants が非リスト／空のとき。
        Policy:
            - variants が有るか無いかで _validate_scene_with_variants と
              _validate_entry に分岐させる。
        """
        self._require_known_scene_keys(scene_name, scene)
        if scene.get("variants") is not None:
            return self._validate_scene_with_variants(scene_name, scene)
        return self._validate_entry(scene_name, scene, allow_when=False)

    def _require_known_scene_keys(
        self, scene_name: str, scene: dict[str, Any]
    ) -> None:
        """scene の未知キーを検出して DialogValidationError を投げる。

        Args:
            scene_name: シーン名（エラーメッセージ用）。
            scene: シーン dict。
        Raises:
            DialogValidationError: _SCENE_KEYS にないキーが含まれるとき。
        Policy:
            - 検証ステップを述語に揃えるための薄いガード。
        """
        unknown_keys = set(scene) - self._SCENE_KEYS
        if unknown_keys:
            raise DialogValidationError(
                f"scene '{scene_name}' has unknown keys: "
                f"{', '.join(sorted(unknown_keys))}"
            )

    def _validate_scene_with_variants(
        self, scene_name: str, scene: dict[str, Any]
    ) -> list[tuple[str, str]]:
        """variants 付きシーンの検証（直接キーとの排他、各 variant の検証）。

        Args:
            scene_name: シーン名。
            scene: variants を持つシーン dict。
        Returns:
            このシーンが持つ next 参照リスト。
        Raises:
            DialogValidationError: variants と直接キーの混在、または variants が
                非リスト／空のとき。
        Policy:
            - variant 単位の検証は _validate_variant に委譲する。
        """
        self._require_variants_only(scene_name, scene)
        variants = scene["variants"]
        if not self._is_nonempty_list(variants):
            raise DialogValidationError(
                f"scene '{scene_name}' variants must be a non-empty list"
            )
        refs: list[tuple[str, str]] = []
        for index, variant in enumerate(variants):
            refs.extend(self._validate_variant(scene_name, index, variant))
        return refs

    @staticmethod
    def _require_variants_only(
        scene_name: str, scene: dict[str, Any]
    ) -> None:
        """variants と直接キー（speaker/text/...）の混在を弾く。

        Args:
            scene_name: シーン名（エラーメッセージ用）。
            scene: variants を持つシーン dict。
        Raises:
            DialogValidationError: 直接キーが同時に存在するとき。
        Policy:
            - schema 上 variants と直接キーは排他なので、検出時点で投げる。
        """
        direct_keys = set(scene) & {
            "speaker", "text", "set", "choices", "next"
        }
        if direct_keys:
            raise DialogValidationError(
                f"scene '{scene_name}' cannot mix variants "
                f"with direct keys: "
                f"{', '.join(sorted(direct_keys))}"
            )

    def _validate_variant(
        self, scene_name: str, index: int, variant: Any
    ) -> list[tuple[str, str]]:
        """variant 単位でキー妥当性を検証する。

        Args:
            scene_name: シーン名。
            index: variants 内のインデックス。
            variant: variant 要素（dict 期待）。
        Returns:
            この variant が持つ next 参照リスト。
        Raises:
            DialogValidationError: 非 dict や未知キーがあるとき。
        Policy:
            - 共通本文の検証は _validate_entry に委譲する。
        """
        if not isinstance(variant, dict):
            raise DialogValidationError(
                f"scene '{scene_name}' variant {index} must be a mapping")
        unknown_keys = set(variant) - self._VARIANT_KEYS
        if unknown_keys:
            raise DialogValidationError(
                f"scene '{scene_name}' variant {index} has unknown keys: "
                f"{', '.join(sorted(unknown_keys))}"
            )
        return self._validate_entry(
            f"{scene_name}[{index}]", variant, allow_when=True)

    def _validate_entry(
        self,
        owner: str,
        entry: dict[str, Any],
        *,
        allow_when: bool,
    ) -> list[tuple[str, str]]:
        """シーン／variant 共通の本文部分を検証する。

        Args:
            owner: エラーメッセージに使う識別子（scene 名 / scene[idx]）。
            entry: 検証対象の本文 dict。
            allow_when: when キーを許可するか（variant のみ True）。
        Returns:
            この entry が持つ next 参照リスト。
        Raises:
            DialogValidationError: when/speaker/text/set/next/choices のいずれかが
                schema 違反のとき。
        Policy:
            - 役割ごとに _validate_when / _validate_speaker / _validate_text /
              _validate_set / _validate_next_and_choices に分割して検証する。
        """
        self._validate_when(owner, entry, allow_when=allow_when)
        self._validate_speaker(owner, entry)
        self._validate_text(owner, entry)
        self._validate_set(owner, entry)
        return self._validate_next_and_choices(owner, entry)

    @staticmethod
    def _validate_when(
        owner: str,
        entry: dict[str, Any],
        *,
        allow_when: bool,
    ) -> None:
        """when キーが許可かつ存在する場合のみ dict であることを検証する。

        Args:
            owner: エラーメッセージに使う識別子。
            entry: 検証対象の本文 dict。
            allow_when: when キーを許可するか。
        Raises:
            DialogValidationError: when が dict でないとき。
        Policy:
            - allow_when=False のときは when の有無を問わずスルー
              （未知キーは _require_known_scene_keys で弾かれる）。
        """
        if not allow_when:
            return
        if "when" not in entry:
            return
        if not isinstance(entry["when"], dict):
            raise DialogValidationError(
                f"scene '{owner}' when must be a mapping")

    @staticmethod
    def _validate_speaker(owner: str, entry: dict[str, Any]) -> None:
        """speaker が指定されているなら str であることを検証する。

        Args:
            owner: エラーメッセージに使う識別子。
            entry: 検証対象の本文 dict。
        Raises:
            DialogValidationError: speaker が文字列以外で指定されたとき。
        Policy:
            - speaker は省略可（None 扱い）。
        """
        speaker = entry.get("speaker")
        if speaker is None:
            return
        if not isinstance(speaker, str):
            raise DialogValidationError(
                f"scene '{owner}' speaker must be a string")

    @staticmethod
    def _validate_text(owner: str, entry: dict[str, Any]) -> None:
        """text が非空文字列であることを検証する。

        Args:
            owner: エラーメッセージに使う識別子。
            entry: 検証対象の本文 dict。
        Raises:
            DialogValidationError: text が無い／空／非文字列のとき。
        Policy:
            - text は会話の必須要素のため必ず存在する。
        """
        text = entry.get("text")
        if not StructuredDialogRunner._is_nonempty_str(text):
            raise DialogValidationError(
                f"scene '{owner}' text must be a non-empty string")

    def _validate_set(self, owner: str, entry: dict[str, Any]) -> None:
        """set 句が dict であり、各キーが宣言済み variables に含まれることを検証する。

        Args:
            owner: エラーメッセージに使う識別子。
            entry: 検証対象の本文 dict。
        Raises:
            DialogValidationError: set が dict でない／未宣言変数を含むとき。
        Policy:
            - set は省略可。
        """
        set_values = entry.get("set")
        if set_values is None:
            return
        if not isinstance(set_values, dict):
            raise DialogValidationError(
                f"scene '{owner}' set must be a mapping")
        for name in set_values:
            if name not in self.variables:
                raise DialogValidationError(
                    f"scene '{owner}' sets unknown variable '{name}'")

    def _validate_next_and_choices(
        self, owner: str, entry: dict[str, Any]
    ) -> list[tuple[str, str]]:
        """next と choices の排他および型を検証し、next 参照リストを返す。

        Args:
            owner: エラーメッセージに使う識別子。
            entry: 検証対象の本文 dict。
        Returns:
            この entry が持つ next 参照リスト。
        Raises:
            DialogValidationError: next が非文字列、または next と choices の共存、
                choices が非空リスト以外のとき。
        Policy:
            - next と choices の検証を _validate_next_ref / _validate_choices_block
              に分け、参照リストを順に積む。
        """
        refs: list[tuple[str, str]] = []
        next_scene = self._validate_next_ref(owner, entry, refs)
        self._validate_choices_block(owner, entry, next_scene, refs)
        return refs

    @staticmethod
    def _validate_next_ref(
        owner: str,
        entry: dict[str, Any],
        refs: list[tuple[str, str]],
    ) -> str | None:
        """next キーの型を検証し、参照リストに追加して値を返す。

        Args:
            owner: エラーメッセージに使う識別子。
            entry: 検証対象の本文 dict。
            refs: 参照リスト（副作用で append する）。
        Returns:
            next の文字列、無ければ None。
        Raises:
            DialogValidationError: next が非文字列のとき。
        Policy:
            - 副作用は refs への append のみ。
        """
        next_scene = entry.get("next")
        if next_scene is None:
            return None
        if not isinstance(next_scene, str):
            raise DialogValidationError(
                f"scene '{owner}' next must be a string")
        refs.append((owner, next_scene))
        return next_scene

    def _validate_choices_block(
        self,
        owner: str,
        entry: dict[str, Any],
        next_scene: str | None,
        refs: list[tuple[str, str]],
    ) -> None:
        """choices ブロックの型・排他を検証して各選択肢を _validate_choice に委ねる。

        Args:
            owner: エラーメッセージに使う識別子。
            entry: 検証対象の本文 dict。
            next_scene: 同 entry の next 値（排他チェック用）。
            refs: 参照リスト（副作用で extend する）。
        Raises:
            DialogValidationError: next と choices の共存、または choices が
                非空リスト以外のとき。
        """
        choices = entry.get("choices")
        if choices is None:
            return
        if next_scene is not None:
            raise DialogValidationError(
                f"scene '{owner}' cannot have both next and choices")
        if not self._is_nonempty_list(choices):
            raise DialogValidationError(
                f"scene '{owner}' choices must be a non-empty list")
        for choice_index, choice in enumerate(choices):
            refs.extend(self._validate_choice(owner, choice_index, choice))

    @staticmethod
    def _validate_choice(
        owner: str, choice_index: int, choice: Any
    ) -> list[tuple[str, str]]:
        """選択肢 1 件の text と next を検証する。

        Args:
            owner: エラーメッセージに使う識別子。
            choice_index: choices 内のインデックス。
            choice: choices 要素（dict 期待）。
        Returns:
            この choice が持つ next 参照（無ければ空リスト）。
        Raises:
            DialogValidationError: 非 dict、text が非空文字列でない、
                next が非文字列のとき。
        Policy:
            - text の型と next の型を順に弾き、参照のみ返す。
        """
        if not isinstance(choice, dict):
            raise DialogValidationError(
                f"scene '{owner}' choice {choice_index} must be a mapping")
        text = choice.get("text")
        if not StructuredDialogRunner._is_nonempty_str(text):
            raise DialogValidationError(
                f"scene '{owner}' choice {choice_index} text "
                f"must be a non-empty string"
            )
        next_scene = choice.get("next")
        if next_scene is None:
            return []
        if not isinstance(next_scene, str):
            raise DialogValidationError(
                f"scene '{owner}' choice {choice_index} next must be a string")
        return [(owner, next_scene)]
