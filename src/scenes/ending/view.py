from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.ending.model import EndingModel


@dataclass
class EndingView:
    """ending シーンの描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self, model: EndingModel, game: Any) -> None:
        """エンディング画面を描画する。"""
        pyxel.cls(1)
        if model.lines:
            game.messages.text(60, 60, model.lines[0], 10)
        for index, line in enumerate(model.lines[1:]):
            game.messages.text(20, 90 + index * 15, line, 7)
        game.messages.text(40, 180, "PRESS Z TO TITLE", 6)
        p = game.player_model
        game.messages.text(30, 200, f"レベル{p.lv} Time:{pyxel.frame_count//30//60}m", 6)
