from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.explore.model import ExploreModel
from src.scenes.explore.presenter import ExplorePresenter
from src.scenes.explore.view import ExploreView


@dataclass
class ExploreScene:
    """探索シーンの model/view/presenter を束ねる Scene 実装。"""

    name: str = "explore"
    model: ExploreModel = field(default_factory=ExploreModel)
    view: ExploreView = field(default_factory=ExploreView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = ExplorePresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。現状は状態更新なし。"""
        return None

    def draw(self) -> dict[str, str]:
        """現在の探索モードから描画辞書を返す。"""
        return self.view.render(mode=self.model.mode)
