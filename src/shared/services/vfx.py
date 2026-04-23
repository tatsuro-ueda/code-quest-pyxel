from __future__ import annotations

"""画面エフェクト（P1-G14 で Game から 2 メソッドを取り込み）。"""

from dataclasses import dataclass
from typing import Any

import pyxel


@dataclass
class VfxSystem:
    """画面エフェクトの状態と描画。"""

    game: Any = None
    timer: int = 0
    type: str = ""

    def start(self, vfx_type):
        """指定タイプの VFX を発動する（プレイヤー設定で無効なら何もしない）。"""
        game = self.game
        if not game.player.get("vfx_enabled", True):
            return
        import src.runtime.main_runtime as M
        cfg = M.VFX_FLASH.get(vfx_type)
        if cfg:
            self.type = vfx_type
            self.timer = cfg["duration"]

    def draw_overlay(self):
        """アクティブな VFX の点滅オーバーレイを描画する。"""
        game = self.game
        if not game.player.get("vfx_enabled", True):
            return
        if self.timer <= 0:
            return
        import src.runtime.main_runtime as M
        cfg = M.VFX_FLASH.get(self.type)
        if not cfg:
            return
        if self.timer % 2 == 0:
            pyxel.rect(0, 0, 256, 256, cfg["color"])
