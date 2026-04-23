from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.ai_help.model import AiHelpModel
from src.scenes.ai_help.presenter import AiHelpPresenter
from src.scenes.ai_help.view import AiHelpView


@dataclass
class AiHelpScene:
    """ai_help シーンの束ね役（Phase 1 スケルトン、update/draw は空）。"""

    name: str = "ai_help"
    model: AiHelpModel = field(default_factory=AiHelpModel)
    view: AiHelpView = field(default_factory=AiHelpView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = AiHelpPresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。Phase 1 スケルトンでは何もしない。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model から描画辞書を返す。"""
        return self.view.render()
