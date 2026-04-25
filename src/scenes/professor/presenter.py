from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.professor.model import ProfessorModel
from src.scenes.professor.view_model import ProfessorChoiceRow, ProfessorViewModel
from src.shared.services.input_bindings import (
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)


@dataclass
class ProfessorPresenter:
    """professor シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    model: ProfessorModel

    def update_intro(self, game: Any, scene: Any) -> None:
        """intro のページ送りと選択肢。決定で受諾エンド or バトル開始。

        ``scene`` は受諾エンドへ遷移する際 ``scene.enter_ending_accepted()``
        を呼び戻すために必要（Phase 1 transitional pattern）。
        """
        import src.runtime.main_runtime as M
        m = self.model
        if not m.choice_active:
            if game.input_state.btnp(CONFIRM_BUTTONS):
                m.intro_idx, done = game.messages.advance_page(m.intro_idx, m.intro_lines)
                if done:
                    m.choice_active = True
            return
        # choice mode
        if game.input_state.btnp(UP_BUTTONS) or game.input_state.btnp(DOWN_BUTTONS):
            m.choice_cursor = 1 - m.choice_cursor
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            if m.choice_cursor == 0:
                scene.enter_ending_accepted()
            else:
                game.battle_scene.start(M.PROFESSOR_DATA, is_professor=True)

    def update_ending_main(self, game: Any) -> None:
        """Professor ending main のページ送り。完了で map に戻る。"""
        m = self.model
        if game.input_state.btnp(CONFIRM_BUTTONS):
            m.ending_idx, done = game.messages.advance_page(m.ending_idx, m.ending_lines)
            if done:
                game.explore_scene.model.a_cooldown = True
                game.state = "map"

    def update_ending_accepted(self, game: Any) -> None:
        """Professor 受諾エンドのページ送り。完了で title に戻る。"""
        m = self.model
        if game.input_state.btnp(CONFIRM_BUTTONS):
            m.ending_idx, done = game.messages.advance_page(m.ending_idx, m.ending_lines)
            if done:
                game.state = "title"
                game.explore_scene.model.a_cooldown = True

    def build_intro_view_model(self, game: Any) -> ProfessorViewModel:
        """intro phase の VM を組み立てる。"""
        m = self.model
        page_lines = self._page_lines(game, m.intro_lines, m.intro_idx)
        choices: list[ProfessorChoiceRow] = []
        if m.choice_active:
            labels = (
                ["うけいれる", "ことわる"]
                if game.has_jp_font
                else ["ACCEPT", "REFUSE"]
            )
            for i, label in enumerate(labels):
                color = 10 if i == m.choice_cursor else 7
                marker = ">" if i == m.choice_cursor else " "
                choices.append(ProfessorChoiceRow(label=f"{marker} {label}", color=color))
        # intro: prompt は choice_active でない時かつ page 範囲内のみ表示候補
        prompt_eligible = (
            (not m.choice_active)
            and bool(m.intro_lines)
            and m.intro_idx < len(m.intro_lines)
        )
        return ProfessorViewModel(
            page_lines=page_lines,
            text_y=60,
            text_color=7,
            prompt_xy=(228, 200) if prompt_eligible else None,
            choices=choices,
        )

    def build_ending_main_view_model(self, game: Any) -> ProfessorViewModel:
        """ending_main phase の VM を組み立てる。"""
        m = self.model
        page_lines = self._page_lines(game, m.ending_lines, m.ending_idx)
        prompt_eligible = bool(m.ending_lines) and m.ending_idx < len(m.ending_lines)
        return ProfessorViewModel(
            page_lines=page_lines,
            text_y=80,
            text_color=10,
            prompt_xy=(228, 200) if prompt_eligible else None,
        )

    def build_ending_accepted_view_model(self, game: Any) -> ProfessorViewModel:
        """ending_accepted phase の VM を組み立てる。"""
        m = self.model
        page_lines = self._page_lines(game, m.ending_lines, m.ending_idx)
        prompt_eligible = bool(m.ending_lines) and m.ending_idx < len(m.ending_lines)
        return ProfessorViewModel(
            page_lines=page_lines,
            text_y=90,
            text_color=6,
            prompt_xy=(228, 210) if prompt_eligible else None,
        )

    @staticmethod
    def _page_lines(game: Any, lines: list[str], idx: int) -> list[str]:
        """idx ページの折返し済み行を返す。範囲外なら空リスト。"""
        if not lines or idx < 0 or idx >= len(lines):
            return []
        return list(game.messages.current_page_lines(lines, idx, max_chars=28, max_rows=6))

