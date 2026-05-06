from __future__ import annotations

"""misaki_gothic 8x8 グリフを image bank から blt する純粋描画関数。

`MessageDisplay.text()` の旧実装をここに移し、service は薄い委譲にする
(M1-1 ガード：services から `pyxel.pal / blt` を排除)。
"""

import pyxel

from src.shared.assets.jp_font_data import (
    JP_FONT_GLYPH_H,
    JP_FONT_GLYPH_W,
    JP_FONT_IMAGE_BANK,
    JP_FONT_LAYOUT,
)


def draw_text(x: int, y: int, s: str, col: int) -> None:
    """文字列を misaki_gothic 8x8 で描画する。`col` はパレット 0 番置換色。"""
    if not s:
        return
    pyxel.pal(7, col)
    cx = x
    for ch in s:
        pos = JP_FONT_LAYOUT.get(ch)
        if pos is not None:
            bcol, brow = pos
            pyxel.blt(
                cx, y,
                JP_FONT_IMAGE_BANK,
                bcol * JP_FONT_GLYPH_W,
                brow * JP_FONT_GLYPH_H,
                JP_FONT_GLYPH_W, JP_FONT_GLYPH_H,
                0,
            )
        cx += JP_FONT_GLYPH_W
    pyxel.pal()
