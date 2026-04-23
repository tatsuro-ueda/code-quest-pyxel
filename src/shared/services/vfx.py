from __future__ import annotations

"""画面エフェクト（Phase 1 スケルトン、P1-G14 で 2 メソッドを取り込む）。

P1-G14 で Game クラスから _start_vfx / _draw_vfx_overlay を取り込む。
"""

from dataclasses import dataclass


@dataclass
class VfxSystem:
    """画面エフェクトの状態（P1-G14 で中身を埋める）。"""

    vfx_timer: int = 0
    vfx_type: str | None = None
