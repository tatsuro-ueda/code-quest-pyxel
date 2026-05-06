from __future__ import annotations

"""メッセージウィンドウの寸法と純粋描画関数。

dialog_window.py より短いメッセージ向け。`MessageDisplay.draw_window` /
`draw_say_overlay` の `pyxel.rect / rectb / frame_count` 呼び出しはここに
集約し、service 側は state 管理（lines / index / say_buffer）のみを持つ。
"""

from dataclasses import dataclass

import pyxel

from src.shared.ui.text_renderer import draw_text


@dataclass(frozen=True)
class MessageWindowLayout:
    """短いメッセージ表示向けのウィンドウ寸法と行折返し幅。"""

    x: int = 8
    y: int = 208
    width: int = 240
    height: int = 44
    wrap_width: int = 28

    def rect(self) -> tuple[int, int, int, int]:
        """描画用に (x, y, width, height) のタプルを返す。"""
        return (self.x, self.y, self.width, self.height)


def draw_message_window(
    lines: list[str],
    *,
    layout: MessageWindowLayout | None = None,
    draw_text_fn=None,
) -> None:
    """メッセージウィンドウ枠と本文 (折返し済み行) を描画する。

    末尾には `(frame_count // 15) % 2` で点滅する `v` カーソルを描く。
    `draw_text_fn` を渡すと文字描画をその関数に委譲する (test での差し替え用)。
    """
    layout = layout or MessageWindowLayout()
    text_fn = draw_text_fn or draw_text
    x, y, w, h = layout.rect()
    pyxel.rect(x, y, w, h, 0)
    pyxel.rectb(x, y, w, h, 7)
    for i, line in enumerate(lines):
        text_fn(x + 8, y + 6 + i * 12, line, 7)
    if (pyxel.frame_count // 15) % 2:
        text_fn(x + w - 12, y + h - 12, "v", 7)


def draw_say_overlay(say_buffer: list[str], *, draw_text_fn=None) -> None:
    """`MessageDisplay.say()` で蓄えたデバッグ行を画面左上に重ね描きする。"""
    if not say_buffer:
        return
    text_fn = draw_text_fn or draw_text
    for i, line in enumerate(say_buffer):
        y = 4 + i * 12
        pyxel.rect(2, y - 1, 252, 12, 0)
        text_fn(4, y, line, 10)
