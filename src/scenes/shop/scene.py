from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.shop.model import ShopModel
from src.scenes.shop.presenter import ShopPresenter
from src.scenes.shop.view import ShopView


@dataclass
class ShopScene:
    """shop シーンの束ね役（Phase 1 スケルトン、update/draw は空）。"""

    name: str = "shop"
    model: ShopModel = field(default_factory=ShopModel)
    view: ShopView = field(default_factory=ShopView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = ShopPresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。Phase 1 スケルトンでは何もしない。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model から描画辞書を返す。"""
        return self.view.render()
