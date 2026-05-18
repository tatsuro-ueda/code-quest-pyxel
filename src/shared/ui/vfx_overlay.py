"""画面全体を覆う VFX フラッシュの純粋描画関数。

このファイルに含まれる関数・クラス：

- 画面全体を指定色で塗り潰す VFX オーバーレイ描画関数

Problems:
    - VFX フラッシュの `pyxel.rect` 呼び出しが service に混ざると、
      service が判定ロジックと描画責務を両方持ち、テストしづらくなる。
    - 描画 API を直接触る箇所が散らばると、レイヤ境界が崩れる。

Solutions:
    - 画面塗り潰しを純粋関数として shared/ui に切り出し、
      service は判定（timer / VFX_FLASH cfg）だけを担当する。
    - 2026-05-07 改訂（CJ44 確定版）：vfx_enabled の概念は撤去済。
      VFX は常に ON。
"""
from __future__ import annotations

import pyxel


# === Public API ===

def draw_vfx_overlay(color: int) -> None:
    """画面全体 (256x256) を `color` で塗り潰す。

    Args:
        color: Pyxel パレット色番号。
    Policy:
        - 判定はせず、与えられた色で全画面 rect を描くだけの純粋描画関数。
    """
    pyxel.rect(0, 0, 256, 256, color)


# === Internal helpers (private) ===
