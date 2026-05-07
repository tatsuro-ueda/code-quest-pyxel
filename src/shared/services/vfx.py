from __future__ import annotations

"""画面エフェクト（P1-G14 で Game から 2 メソッドを取り込み）。"""

from dataclasses import dataclass
from typing import Any

from src.shared.ui.vfx_overlay import draw_vfx_overlay


@dataclass
class VfxSystem:
    """画面エフェクトの状態と描画。"""

    game: Any = None
    timer: int = 0
    type: str = ""

    def start(self, vfx_type):
        """指定タイプの VFX を発動する。

        2026-05-07 改訂（CJ44 確定版）：vfx_enabled の判定は撤去済。VFX は常に ON。
        """
        import src.runtime.main_runtime as M
        cfg = M.VFX_FLASH.get(vfx_type)
        if cfg:
            self.type = vfx_type
            self.timer = cfg["duration"]

    def draw_overlay(self):
        """アクティブな VFX の点滅オーバーレイを描画する（VFX は常に ON）。"""
        if self.timer <= 0:
            return
        import src.runtime.main_runtime as M
        cfg = M.VFX_FLASH.get(self.type)
        if not cfg:
            return
        if self.timer % 2 == 0:
            draw_vfx_overlay(cfg["color"])
