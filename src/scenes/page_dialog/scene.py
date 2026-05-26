"""page_dialog scene 本体（Model / View / Presenter の配線）。

Problems:
    - 魔王戦前の全画面会話を explore や runtime に直書きすると、scene 境界が
      崩れて Game が again 太くなる。
    - professor と別口の full-screen 会話を増やすとき、毎回 page index と
      callback の配線を作り直す必要がある。

Solutions:
    - page_dialog の Scene は enter / update / draw の薄い配線だけを持ち、
      汎用の full-screen 会話を 1 state に集約する。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.page_dialog.model import PageDialogModel
from src.scenes.page_dialog.presenter import PageDialogPresenter
from src.scenes.page_dialog.view import PageDialogView


@dataclass
class PageDialogScene:
    """full-screen page dialog scene。"""

    # === Public API ===

    name: str = "page_dialog"
    model: PageDialogModel = field(default_factory=PageDialogModel)
    view: PageDialogView = field(default_factory=PageDialogView)
    game: Any = None

    def __post_init__(self) -> None:
        self.presenter = PageDialogPresenter(self.model)

    def enter_scene(
        self,
        scene_name: str,
        *,
        callback=None,
        return_state: str = "map",
        text_y: int = 60,
        text_color: int = 7,
    ) -> None:
        """dialog scene 名から full-screen 会話へ入る。"""
        game = self.game
        if game is None:
            return
        self.presenter.enter_scene(
            game,
            scene_name,
            callback=callback,
            return_state=return_state,
            text_y=text_y,
            text_color=text_color,
        )

    def enter_lines(
        self,
        lines: list[str],
        *,
        callback=None,
        return_state: str = "map",
        text_y: int = 60,
        text_color: int = 7,
    ) -> None:
        """既存 lines から full-screen 会話へ入る。"""
        game = self.game
        if game is None:
            return
        self.presenter.enter_lines(
            game,
            lines,
            callback=callback,
            return_state=return_state,
            text_y=text_y,
            text_color=text_color,
        )

    def update(self) -> None:
        """配線：入力解釈は Presenter に委譲する。"""
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def draw(self) -> None:
        """配線：描画は View に委譲する。"""
        game = self.game
        if game is None:
            return
        vm = self.presenter.build_view_model(game)
        self.view.draw(vm, game.messages)
