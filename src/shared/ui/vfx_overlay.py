from __future__ import annotations

"""画面全体を覆う VFX フラッシュの純粋描画関数。

`VfxSystem.draw_overlay()` の `pyxel.rect` 呼び出しをここに移し、service は
判定ロジック（player_model.vfx_enabled / timer / VFX_FLASH cfg）のみを持つ。
"""

import pyxel


def draw_vfx_overlay(color: int) -> None:
    """画面全体 (256x256) を `color` で塗り潰す。"""
    pyxel.rect(0, 0, 256, 256, color)
