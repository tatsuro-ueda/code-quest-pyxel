from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MenuWindow:
    """メニューウィンドウの配置寸法を表す不変レコード。"""

    x: int = 20
    y: int = 40
    width: int = 216
    height: int = 170

    def rect(self) -> tuple[int, int, int, int]:
        """描画用に (x, y, width, height) のタプルを返す。"""
        return (self.x, self.y, self.width, self.height)
