from __future__ import annotations

"""ステータスバーの配置寸法（Phase 1 スケルトン）。

P1-G15 で Game.draw_status_bar がここの座標を参照するようになる。
現状の仮値は Phase 1 時点の暫定で、P1-G15 で確定する。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StatusBarLayout:
    """画面上部のステータスバー（HP / MP / LV / 所持金など）の寸法。"""

    x: int = 0
    y: int = 0
    width: int = 256
    height: int = 16

    def rect(self) -> tuple[int, int, int, int]:
        """描画用に (x, y, width, height) のタプルを返す。"""
        return (self.x, self.y, self.width, self.height)
