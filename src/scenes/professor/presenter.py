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
        import src.runtime.main_runtime as M
        model = self.model
        if not model.is_choice_active:
            if game.input_state.btnp(CONFIRM_BUTTONS):
                model.intro_idx, done = game.messages.advance_page(
                    model.intro_idx, model.intro_lines
                )
                if done:
                    model.is_choice_active = True
            return
        # choice mode
        if (
            game.input_state.btnp(UP_BUTTONS)
            or game.input_state.btnp(DOWN_BUTTONS)
        ):
            model.choice_cursor = 1 - model.choice_cursor
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            if model.choice_cursor == 0:
                scene.enter_ending_accepted()
            else:
                game.battle_scene.start(
                    M.PROFESSOR_DATA, is_professor=True
                )

    def update_ending_main(self, game: Any) -> None:
        """Professor ending main のページ送り。完了で map に戻る。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if game.input_state.btnp(CONFIRM_BUTTONS):
            model.ending_idx, done = game.messages.advance_page(
                model.ending_idx, model.ending_lines
            )
            if done:
                game.explore_scene.model.start_a_cooldown()
                game.state = "map"

    def update_ending_accepted(self, game: Any) -> None:
        """Professor 受諾エンドのページ送り。完了で title に戻る。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if game.input_state.btnp(CONFIRM_BUTTONS):
            model.ending_idx, done = game.messages.advance_page(
                model.ending_idx, model.ending_lines
            )
            if done:
                game.state = "title"
                game.explore_scene.model.start_a_cooldown()

    def build_intro_view_model(self, game: Any) -> ProfessorViewModel:
        """intro phase の VM を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        page_lines = self._page_lines(game, model.intro_lines, model.intro_idx)
        choices: list[ProfessorChoiceRow] = []
        if model.is_choice_active:
            labels = (
                ["うけいれる", "ことわる"]
                if game.has_jp_font
                else ["ACCEPT", "REFUSE"]
            )
            for i, label in enumerate(labels):
                color = 10 if i == model.choice_cursor else 7
                marker = ">" if i == model.choice_cursor else " "
                choices.append(
                    ProfessorChoiceRow(
                        label=f"{marker} {label}", color=color
                    )
                )
        # intro: prompt は is_choice_active でない時かつ page 範囲内のみ表示候補
        is_prompt_eligible = (
            (not model.is_choice_active)
            and bool(model.intro_lines)
            and model.intro_idx < len(model.intro_lines)
        )
        return ProfessorViewModel(
            page_lines=page_lines,
            text_y=60,
            text_color=7,
            prompt_xy=(228, 200) if is_prompt_eligible else None,
            choices=choices,
        )

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
        page_lines = self._page_lines(game, model.ending_lines, model.ending_idx)
        is_prompt_eligible = (
            bool(model.ending_lines) and model.ending_idx < len(model.ending_lines)
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
        page_lines = self._page_lines(game, model.ending_lines, model.ending_idx)
        is_prompt_eligible = (
            bool(model.ending_lines) and model.ending_idx < len(model.ending_lines)
        )
        return ProfessorViewModel(
            page_lines=page_lines,
            text_y=90,
            text_color=6,
            prompt_xy=(228, 210) if is_prompt_eligible else None,
        )

    # === Internal helpers (private) ===

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
        if not lines or idx < 0 or idx >= len(lines):
            return []
        return list(
            game.messages.current_page_lines(
                lines, idx, max_chars=28, max_rows=6
            )
        )
