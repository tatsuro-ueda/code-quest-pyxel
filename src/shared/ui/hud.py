from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HudLayout:
    """HUD（ステータス表示）の余白設定を表す不変レコード。"""

    top_margin: int = 0
    left_margin: int = 0

    def origin(self) -> tuple[int, int]:
        """HUD の描画原点 (x, y) を返す。"""
        return (self.left_margin, self.top_margin)
