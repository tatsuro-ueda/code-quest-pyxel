"""misaki_gothic 8x8 グリフを image bank から blt する純粋描画関数。

このファイルに含まれる関数・クラス：

- draw_text: 文字列を misaki_gothic 8x8 で描画する public エントリ
- _draw_text_impl: draw_text() の実装本体（空文字列ガードと色置換）
- _draw_glyph_run: 文字列を 1 文字ずつ blt して描画する内部 helper
- _draw_one_glyph: 1 文字分のグリフを image bank から blt する内部 helper

Problems:
    - service 層に pyxel.pal / pyxel.blt が散ると、描画レイヤの境界が
      崩れて test でモックしづらく、M1-1 のガード違反になる。
    - 文字単位の blt ループを service に置くと、見た目を変えるだけの
      つもりが状態判定と絡みやすくなる。

Solutions:
    - misaki_gothic への blt をこのモジュールに集約し、service からは
      薄い委譲だけで呼べる純粋描画関数として公開する。
    - public 関数は private helper への単純委譲に留め、ガード判定や
      ループ等の制御フローは private 側に隔離する。
"""
from __future__ import annotations

import pyxel

from src.shared.assets.jp_font_data import (
    JP_FONT_GLYPH_H,
    JP_FONT_GLYPH_W,
    JP_FONT_IMAGE_BANK,
    JP_FONT_LAYOUT,
)


# === Public API ===


def draw_text(x: int, y: int, s: str, col: int) -> None:
    """文字列を misaki_gothic 8x8 で描画する。

    Args:
        x: 描画開始 X 座標。
        y: 描画開始 Y 座標。
        s: 描画する文字列。空文字列なら何もしない。
        col: パレット 0 番に割り当てる置換色。
    Policy:
        - public 関数は private helper への委譲のみとする。
        - 空文字列判定とループは private 側に隔離する。
        - 関数名 draw_text は他モジュールから import されているため固定。
    """
    _draw_text_impl(x, y, s, col)


# === Internal helpers (private) ===


def _draw_text_impl(x: int, y: int, s: str, col: int) -> None:
    """draw_text() の実装本体。

    Args:
        x: 描画開始 X 座標。
        y: 描画開始 Y 座標。
        s: 描画する文字列。空文字列なら no-op。
        col: パレット 0 番に割り当てる置換色。
    Policy:
        - 空文字列ガードを最初に置き、色置換 → 文字列描画 → 色復元の順で進める。
    """
    if not s:
        return
    pyxel.pal(7, col)
    _draw_glyph_run(x, y, s)
    pyxel.pal()


def _draw_glyph_run(x: int, y: int, s: str) -> None:
    """misaki_gothic グリフを 1 文字ずつ blt して文字列を描画する。

    Args:
        x: 描画開始 X 座標。
        y: 描画開始 Y 座標。
        s: 描画する文字列（空でない前提）。
    Policy:
        - JP_FONT_LAYOUT に無い文字はスキップし、字送りだけ進める。
        - 色置換 (pyxel.pal) は呼び出し側の前後処理に任せる。
    """
    cx = x
    for ch in s:
        _draw_one_glyph(cx, y, ch)
        cx += JP_FONT_GLYPH_W


def _draw_one_glyph(cx: int, y: int, ch: str) -> None:
    """1 文字分のグリフを image bank から blt する。

    Args:
        cx: 描画 X 座標。
        y: 描画 Y 座標。
        ch: 描画する 1 文字（JP_FONT_LAYOUT に無ければ no-op）。
    Policy:
        - レイアウト辞書に無い文字は no-op として呼び出し元の字送りに任せる。
    """
    pos = JP_FONT_LAYOUT.get(ch)
    if pos is None:
        return
    bcol, brow = pos
    pyxel.blt(
        cx, y,
        JP_FONT_IMAGE_BANK,
        bcol * JP_FONT_GLYPH_W,
        brow * JP_FONT_GLYPH_H,
        JP_FONT_GLYPH_W, JP_FONT_GLYPH_H,
        0,
    )
