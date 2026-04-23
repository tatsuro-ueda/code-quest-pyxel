from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pyxel

from src.scenes.splash.model import SplashModel
from src.scenes.splash.presenter import SplashPresenter
from src.scenes.splash.view import SplashView
from src.shared.services.input_bindings import CONFIRM_BUTTONS, CANCEL_BUTTONS


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
        """フレームを進めて自動遷移するか、任意キーでスキップする。"""
        game = self.game
        if game is None:
            return
        self.model.frame += 1
        if self.model.frame >= 90 or game._btnp(CONFIRM_BUTTONS) or game._btnp(CANCEL_BUTTONS):
            game.state = "title"

    def draw(self) -> None:
        """スプラッシュ画面を描画する。"""
        game = self.game
        if game is None:
            return
        pyxel.cls(0)
        f = self.model.frame
        col = 1 if f < 15 else (5 if f < 30 else 12)
        for i in range(8):
            x = 16 + i * 28
            pyxel.rect(x, 100, 12, 12, col)
        title_color = 7 if f >= 20 else 5
        game.messages.text(80, 80, "BLOCK QUEST", title_color)
        if f >= 40:
            game.messages.text(50, 130, game._t("コードのたびは、ここから", "Coding journey starts here"), 10)
        if f >= 60:
            game.messages.text(70, 160, game._t("presented by うえだたつろう", "by Tatsuro Ueda"), 6)
        if f >= 75 and (pyxel.frame_count // 8) % 2:
            game.messages.text(60, 220, "PRESS ANY KEY", 7)
