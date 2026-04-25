from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.ending.model import EndingModel
from src.scenes.ending.presenter import EndingPresenter
from src.scenes.ending.view import EndingView


@dataclass
class EndingScene:
    """エンディング画面（P1-G11 で Game から 3 メソッドを取り込み）。"""

    name: str = "ending"
    model: EndingModel = field(default_factory=EndingModel)
    view: EndingView = field(default_factory=EndingView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = EndingPresenter(self.model)

    def enter(self) -> None:
        """エンディングに入る。"""
        game = self.game
        self.model.lines = game.messages.dialog_lines("ending.main.line01")
        game.state = "ending"

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。"""
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def draw(self) -> None:
        """エンディング画面を描画する。Presenter が VM 組立て、View に委譲（M1-1 / M2-2 準拠）。"""
        game = self.game
        if game is None:
            return
        if not self.model.lines:
            self.model.lines = game.messages.dialog_lines("ending.main.line01")
        vm = self.presenter.build_view_model(game)
        self.view.render(vm, game.messages)
