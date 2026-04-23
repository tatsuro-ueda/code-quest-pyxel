from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.menu.model import MenuModel
from src.scenes.menu.presenter import MenuPresenter
from src.scenes.menu.view import MenuView


@dataclass
class MenuScene:
    """menu シーンの束ね役（Phase 1 スケルトン、update/draw は空）。"""

    name: str = "menu"
    model: MenuModel = field(default_factory=MenuModel)
    view: MenuView = field(default_factory=MenuView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = MenuPresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。Phase 1 スケルトンでは何もしない。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model から描画辞書を返す。"""
        return self.view.render()
