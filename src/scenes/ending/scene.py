from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.ending.model import EndingModel
from src.scenes.ending.presenter import EndingPresenter
from src.scenes.ending.view import EndingView


@dataclass
class EndingScene:
    """ending シーンの束ね役（Phase 1 スケルトン、update/draw は空）。"""

    name: str = "ending"
    model: EndingModel = field(default_factory=EndingModel)
    view: EndingView = field(default_factory=EndingView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = EndingPresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。Phase 1 スケルトンでは何もしない。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model から描画辞書を返す。"""
        return self.view.render()
