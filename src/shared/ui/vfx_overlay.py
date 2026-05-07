from __future__ import annotations

"""画面全体を覆う VFX フラッシュの純粋描画関数。

`VfxSystem.draw_overlay()` の `pyxel.rect` 呼び出しをここに移し、service は
判定ロジック（timer / VFX_FLASH cfg）のみを持つ。

2026-05-07 改訂（CJ44 確定版）：vfx_enabled の概念は撤去済。VFX は常に ON。
"""

import pyxel


def draw_vfx_overlay(color: int) -> None:
    """画面全体 (256x256) を `color` で塗り潰す。"""
    pyxel.rect(0, 0, 256, 256, color)
