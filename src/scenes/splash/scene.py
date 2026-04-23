from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.splash.model import SplashModel
from src.scenes.splash.presenter import SplashPresenter
from src.scenes.splash.view import SplashView


@dataclass
class SplashScene:
    """splash シーンの束ね役（Phase 1 スケルトン、update/draw は空）。"""

    name: str = "splash"
    model: SplashModel = field(default_factory=SplashModel)
    view: SplashView = field(default_factory=SplashView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = SplashPresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。Phase 1 スケルトンでは何もしない。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model から描画辞書を返す。"""
        return self.view.render()
