from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel


@dataclass
class SplashView:
    """splash シーンの描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self, *, frame: int, game: Any) -> None:
        """フレーム数に応じてスプラッシュを描画する。"""
        pyxel.cls(0)
        col = 1 if frame < 15 else (5 if frame < 30 else 12)
        for i in range(8):
            x = 16 + i * 28
            pyxel.rect(x, 100, 12, 12, col)
        title_color = 7 if frame >= 20 else 5
        game.messages.text(80, 80, "BLOCK QUEST", title_color)
        if frame >= 40:
            game.messages.text(50, 130, game.text_fmt.t("コードのたびは、ここから", "Coding journey starts here"), 10)
        if frame >= 60:
            game.messages.text(70, 160, game.text_fmt.t("presented by うえだたつろう", "by Tatsuro Ueda"), 6)
        if frame >= 75 and (pyxel.frame_count // 8) % 2:
            game.messages.text(60, 220, "PRESS ANY KEY", 7)
