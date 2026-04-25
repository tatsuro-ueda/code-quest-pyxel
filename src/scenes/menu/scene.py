from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.menu.model import MenuModel
from src.scenes.menu.presenter import MenuPresenter
from src.scenes.menu.view import MenuView


@dataclass
class MenuScene:
    """menu シーン（P1-G7 で Game から 3 メソッドを取り込み）。"""

    name: str = "menu"
    model: MenuModel = field(default_factory=MenuModel)
    view: MenuView = field(default_factory=MenuView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = MenuPresenter(self.model)

    def _labels(self) -> list[str]:
        """既存テスト互換：Presenter.labels に委譲。"""
        return self.presenter.labels(self.game)

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。"""
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def draw(self) -> None:
        """メニュー画面を描画する。描画本体は View に委譲（M1-1 準拠）。"""
        game = self.game
        if game is None:
            return self.view.render()
        vm = self.presenter.build_view_model(self.presenter.labels(game), game)
        self.view.draw(vm, game.messages)
