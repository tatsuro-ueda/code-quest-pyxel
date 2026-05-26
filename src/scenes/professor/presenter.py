"""professor scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - professor の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.professor.model import ProfessorModel
from src.scenes.professor.view_model import (
    ProfessorChoiceRow,
    ProfessorViewModel,
)
from src.shared.services.page_dialog_flow import (
    advance_page_on_confirm,
    build_page_prompt_xy,
    current_page_lines_for_dialog,
)
from src.shared.services.input_bindings import (
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)


@dataclass
class ProfessorPresenter:
    """professor シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    # === Public API ===

    model: ProfessorModel

    def update_intro(self, game: Any, scene: Any) -> None:
        """intro のページ送りと選択肢。決定で受諾エンド or バトル開始。

        ``scene`` は受諾エンドへ遷移する際 ``scene.enter_ending_accepted()``
        を呼び戻すために必要（Phase 1 transitional pattern）。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update_intro(game, scene)

    def update_ending_main(self, game: Any) -> None:
        """Professor ending main のページ送り。完了で map に戻る。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update_ending_main(game)

    def update_ending_accepted(self, game: Any) -> None:
        """Professor 受諾エンドのページ送り。完了で title に戻る。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update_ending_accepted(game)

    def build_intro_view_model(self, game: Any) -> ProfessorViewModel:
        """intro phase の VM を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_build_intro_view_model(game)

    def build_ending_main_view_model(self, game: Any) -> ProfessorViewModel:
        """ending_main phase の VM を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        page_lines = self._page_lines(
            game, model.ending_lines, model.ending_idx
        )
        is_prompt_eligible = (
            bool(model.ending_lines)
            and model.ending_idx < len(model.ending_lines)
        )
        return ProfessorViewModel(
            page_lines=page_lines,
            text_y=80,
            text_color=10,
            prompt_xy=(228, 200) if is_prompt_eligible else None,
        )

    def build_ending_accepted_view_model(
        self, game: Any
    ) -> ProfessorViewModel:
        """ending_accepted phase の VM を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        page_lines = self._page_lines(
            game, model.ending_lines, model.ending_idx
        )
        is_prompt_eligible = (
            bool(model.ending_lines)
            and model.ending_idx < len(model.ending_lines)
        )
        return ProfessorViewModel(
            page_lines=page_lines,
            text_y=90,
            text_color=6,
            prompt_xy=(228, 210) if is_prompt_eligible else None,
        )

    # === Internal helpers (private) ===

    def _run_update_intro(self, game: Any, scene: Any) -> None:
        """_run_update_intro() の実装本体。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if not model.is_choice_active:
            self._advance_intro_page(game)
            return
        self._handle_intro_choice(game, scene)

    def _advance_intro_page(self, game: Any) -> None:
        """intro のページ送り入力を処理する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        model.intro_idx, done, did_advance = advance_page_on_confirm(
            game,
            model.intro_idx,
            model.intro_lines,
        )
        if did_advance and done:
            model.is_choice_active = True

    def _handle_intro_choice(self, game: Any, scene: Any) -> None:
        """intro の選択肢入力を処理する。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        model = self.model
        is_axis_pressed = (
            game.input_state.btnp(UP_BUTTONS)
            or game.input_state.btnp(DOWN_BUTTONS)
        )
        if is_axis_pressed:
            model.choice_cursor = 1 - model.choice_cursor
            game.sfx.play("cursor")
            return
        if not game.input_state.btnp(CONFIRM_BUTTONS):
            return
        game.sfx.play("select")
        if model.choice_cursor == 0:
            scene.enter_ending_accepted()
            return
        game.battle_scene.start(M.PROFESSOR_DATA, is_professor=True)

    def _run_update_ending_main(self, game: Any) -> None:
        """_run_update_ending_main() の実装本体。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        model.ending_idx, done, did_advance = advance_page_on_confirm(
            game,
            model.ending_idx,
            model.ending_lines,
        )
        if did_advance and done:
            game.explore_scene.model.start_a_cooldown()
            game.state = "map"

    def _run_update_ending_accepted(self, game: Any) -> None:
        """_run_update_ending_accepted() の実装本体。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        model.ending_idx, done, did_advance = advance_page_on_confirm(
            game,
            model.ending_idx,
            model.ending_lines,
        )
        if did_advance and done:
            game.state = "title"
            game.explore_scene.model.start_a_cooldown()

    def _run_build_intro_view_model(self, game: Any) -> ProfessorViewModel:
        """_run_build_intro_view_model() の実装本体。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        page_lines = current_page_lines_for_dialog(
            game,
            model.intro_lines,
            model.intro_idx,
        )
        choices = self._build_intro_choices(game)
        prompt_xy = None
        is_prompt_eligible = not model.is_choice_active
        if is_prompt_eligible:
            prompt_xy = build_page_prompt_xy(
                model.intro_lines,
                model.intro_idx,
            )
        return ProfessorViewModel(
            page_lines=page_lines,
            text_y=60,
            text_color=7,
            prompt_xy=prompt_xy,
            choices=choices,
        )

    def _build_intro_choices(self, game: Any) -> list[ProfessorChoiceRow]:
        """choice mode 時の選択肢行を組み立てる。

        Args:
            game: game の値。
        Returns:
            ProfessorChoiceRow のリスト（非 choice mode は空）。
        Policy:
            - JP / EN ラベルは game.has_jp_font で切り替える。
        """
        model = self.model
        if not model.is_choice_active:
            return []
        labels = (
            ["うけいれる", "ことわる"]
            if game.has_jp_font
            else ["ACCEPT", "REFUSE"]
        )
        choices: list[ProfessorChoiceRow] = []
        for i, label in enumerate(labels):
            color = 10 if i == model.choice_cursor else 7
            marker = ">" if i == model.choice_cursor else " "
            choices.append(
                ProfessorChoiceRow(label=f"{marker} {label}", color=color)
            )
        return choices

    @staticmethod
    def _page_lines(game: Any, lines: list[str], idx: int) -> list[str]:
        """idx ページの折返し済み行を返す。範囲外なら空リスト。

        Args:
            game: game の値。
            lines: lines の値。
            idx: idx の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return current_page_lines_for_dialog(
            game,
            lines,
            idx,
        )
