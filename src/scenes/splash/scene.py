from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.splash.model import SplashModel
from src.scenes.splash.presenter import SplashPresenter
from src.scenes.splash.view import SplashView


@dataclass
class SplashScene:
    """起動直後のスプラッシュ画面（P1-G2 で update_splash / draw_splash を取り込み）。"""

    name: str = "splash"
    model: SplashModel = field(default_factory=SplashModel)
    view: SplashView = field(default_factory=SplashView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = SplashPresenter(self.model)

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。"""
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def draw(self) -> None:
        """スプラッシュ画面を描画する。Presenter が ViewModel を組み立て、View に委譲（M1-1 / M2-2 準拠）。"""
        game = self.game
        if game is None:
            return
        vm = self.presenter.build_view_model(game)
        self.view.render(vm, game.messages)
