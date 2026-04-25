from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.ai_help.model import AiHelpModel


@dataclass
class AiHelpView:
    """ai_help シーンの描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self, model: AiHelpModel, game: Any) -> None:
        """AI ヘルプ画面の枠と説明文を描画する。"""
        x, y, w, h = 12, 36, 232, 196
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        game.messages.text(x + 8, y + 8, "AIで このゲームを しゅうせい", 10)
        lines = [
            "",
            "１ Code Maker の Save をおして",
            "  main.py をダウンロード",
            "",
            "２ ブラウザで claude.ai か",
            "  chatgpt.com をひらく",
            "",
            "３ main.py をはりつけて",
            "  「ここを こう なおして」と たのむ",
            "",
            "４ かえってきた コードを",
            "  Code Maker に はりつける",
            "",
            f"  -> {model.status}",
        ]
        for i, line in enumerate(lines):
            game.messages.text(x + 8, y + 24 + i * 9, line, 7)
