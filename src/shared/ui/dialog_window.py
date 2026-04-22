from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DialogWindow:
    """会話ウィンドウの配置寸法（画面下部の台詞枠）を表す不変レコード。"""

    x: int = 8
    y: int = 208
    width: int = 240
    height: int = 44

    def rect(self) -> tuple[int, int, int, int]:
        """描画用に (x, y, width, height) のタプルを返す。"""
        return (self.x, self.y, self.width, self.height)
