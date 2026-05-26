"""page_dialog scene の入力解釈・ViewModel 組立て。

Problems:
    - full-screen 会話の enter / update / callback が runtime に散ると、
      scene 追加のたびに state 遷移が重複する。
    - 魔王戦前会話と professor の非分岐ページ送りが別々に page 処理を持つと、
      UX と回帰が揃わない。

Solutions:
    - page_dialog の Presenter に full-screen 会話の進行制御を集約し、
      共通 page helper を使って update / draw をそろえる。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.page_dialog.model import PageDialogModel
from src.scenes.page_dialog.view_model import PageDialogViewModel
from src.shared.services.page_dialog_flow import (
    advance_page_on_confirm,
    build_page_prompt_xy,
    current_page_lines_for_dialog,
)


@dataclass
class PageDialogPresenter:
    """full-screen page dialog の入力解釈と VM 組立て。"""

    # === Public API ===

    model: PageDialogModel

    def enter_scene(
        self,
        game: Any,
        scene_name: str,
        *,
        callback=None,
        return_state: str = "map",
        text_y: int = 60,
        text_color: int = 7,
    ) -> None:
        """dialog runner から scene を読み、page_dialog state に入る。"""
        lines = game.messages.dialog_lines(scene_name)
        self.enter_lines(
            game,
            lines,
            callback=callback,
            return_state=return_state,
            text_y=text_y,
            text_color=text_color,
        )

    def enter_lines(
        self,
        game: Any,
        lines: list[str],
        *,
        callback=None,
        return_state: str = "map",
        text_y: int = 60,
        text_color: int = 7,
    ) -> None:
        """既存 lines を使って page_dialog state に入る。"""
        self._run_enter_lines(
            game,
            lines,
            callback=callback,
            return_state=return_state,
            text_y=text_y,
            text_color=text_color,
        )

    def update(self, game: Any) -> None:
        """決定入力でページ送りし、終端なら callback を呼ぶ。"""
        self._run_update(game)

    def build_view_model(self, game: Any) -> PageDialogViewModel:
        """描画用 ViewModel を返す。"""
        return self._run_build_view_model(game)

    # === Internal helpers (private) ===

    def _run_enter_lines(
        self,
        game: Any,
        lines: list[str],
        *,
        callback=None,
        return_state: str = "map",
        text_y: int = 60,
        text_color: int = 7,
    ) -> None:
        model = self.model
        model.lines = list(lines)
        model.index = 0
        model.callback = callback
        model.return_state = return_state
        model.text_y = text_y
        model.text_color = text_color
        game.state = "page_dialog"

    def _run_update(self, game: Any) -> None:
        model = self.model
        model.index, done, did_advance = advance_page_on_confirm(
            game,
            model.index,
            model.lines,
        )
        if not did_advance or not done:
            return
        self._finish_dialog(game)

    def _run_build_view_model(self, game: Any) -> PageDialogViewModel:
        model = self.model
        return PageDialogViewModel(
            page_lines=current_page_lines_for_dialog(
                game,
                model.lines,
                model.index,
            ),
            text_y=model.text_y,
            text_color=model.text_color,
            prompt_xy=build_page_prompt_xy(
                model.lines,
                model.index,
            ),
        )

    def _finish_dialog(self, game: Any) -> None:
        model = self.model
        callback = model.callback
        return_state = model.return_state
        model.lines = []
        model.index = 0
        model.callback = None
        game.state = return_state
        if callback is not None:
            callback()
