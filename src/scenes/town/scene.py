from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.town.model import TownModel
from src.scenes.town.presenter import TownPresenter
from src.scenes.town.view import TownView


@dataclass
class TownScene:
    """town シーンの束ね役（Phase 1 スケルトン、update/draw は空）。"""

    name: str = "town"
    model: TownModel = field(default_factory=TownModel)
    view: TownView = field(default_factory=TownView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = TownPresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。Phase 1 スケルトンでは何もしない。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model から描画辞書を返す。"""
        return self.view.render()
