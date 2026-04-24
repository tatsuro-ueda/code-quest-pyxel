from __future__ import annotations

"""短いメッセージウィンドウ制御（P1-G12 で Game から 12 メソッドを取り込み）。

overlay 的に複数 scene から呼ばれる utility（Q1A）。structured dialog は
dialog_runner.py が担当、本 service は「1〜数行のメッセージ表示」に限る。
"""

from dataclasses import dataclass, field
from typing import Any

import pyxel

from src.shared.assets.jp_font_data import (
    JP_FONT_GLYPH_H,
    JP_FONT_GLYPH_W,
    JP_FONT_IMAGE_BANK,
    JP_FONT_LAYOUT,
)
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    UP_BUTTONS,
)


@dataclass
class MessageDisplay:
    """メッセージウィンドウの表示状態（P1-G12 で Game から取り込み）。"""

    game: Any = None
    lines: list[str] = field(default_factory=list)
    index: int = 0
    callback: Any = None
    say_buffer: list[str] = field(default_factory=list)

    def show(self, lines, callback=None):
        """メッセージ行を差し替えて index をリセットする。"""
        self.lines = lines
        self.index = 0
        self.callback = callback

    def enter(self, lines, callback=None):
        """map に戻る前提で message state に入る。"""
        self.show(lines, callback=callback)
        game = self.game
        game.prev_state = "map"
        game.state = "message"

    def dialog_text(self, scene_name, **extra_context):
        """dialog runner から scene の最初の 1 text を取得する。"""
        game = self.game
        return game.dialog.start(
            scene_name,
            state=game.player_model.dialog_flags,
            extra_context=extra_context,
        ).text

    def dialog_lines(self, scene_name, **extra_context):
        """dialog runner から scene の全行を取得する。"""
        game = self.game
        return game.dialog.load_all_lines(
            scene_name,
            state=game.player_model.dialog_flags,
            extra_context=extra_context,
        )

    def any_advance_btnp(self) -> bool:
        """メッセージを進める入力。決定/キャンセル/方向のどれでもOK。"""
        btnp = self.game.input_state.btnp
        return (
            btnp(CONFIRM_BUTTONS)
            or btnp(CANCEL_BUTTONS)
            or btnp(UP_BUTTONS)
            or btnp(DOWN_BUTTONS)
            or btnp(LEFT_BUTTONS)
            or btnp(RIGHT_BUTTONS)
        )

    def advance_page(self, index, lines):
        """次のページ index と終端判定を返す。"""
        next_index = index + 1
        return next_index, next_index >= len(lines)

    def current_page_lines(self, lines, index, *, max_chars=28, max_rows=3):
        """現在ページの折返し済み行を返す。"""
        if not lines or index < 0 or index >= len(lines):
            return []
        return self.wrap_text(lines[index], max_chars=max_chars)[:max_rows]

    def update(self):
        """message state のページ送りとコールバック呼出し。"""
        game = self.game
        if self.any_advance_btnp():
            self.index, done = self.advance_page(self.index, self.lines)
            if done:
                game.state = game.prev_state
                if self.callback:
                    self.callback()

    def wrap_text(self, text: str, max_chars: int = 28) -> list[str]:
        """簡易な折返し（CJK文字幅考慮なし、おおよその目安）。"""
        out: list[str] = []
        for raw_line in text.split("\n"):
            cur = ""
            for ch in raw_line:
                cur += ch
                if len(cur) >= max_chars:
                    out.append(cur)
                    cur = ""
            if cur:
                out.append(cur)
        return out or [""]

    def say(self, *args) -> None:
        """デバッグ用: 任意の値を画面左上にオーバーレイ表示する。"""
        msg = " ".join(str(a) for a in args)
        self.say_buffer.append(msg)
        if len(self.say_buffer) > 12:
            self.say_buffer = self.say_buffer[-12:]

    def text(self, x: int, y: int, s: str, col: int) -> None:
        """文字列を misaki_gothic 8x8 で描画する。"""
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

    def draw_say_overlay(self):
        """say() で蓄えたメッセージを画面左上に重ね描きする。"""
        if not self.say_buffer:
            return
        for i, line in enumerate(self.say_buffer):
            y = 4 + i * 12
            pyxel.rect(2, y - 1, 252, 12, 0)
            self.text(4, y, line, 10)

    def draw_window(self):
        """メッセージウィンドウを描画する（座標は MessageWindowLayout 参照）。"""
        from src.shared.ui.message_window import MessageWindowLayout
        layout = MessageWindowLayout()
        x, y, w, h = layout.rect()
        pyxel.rect(x, y, w, h, 0)
        pyxel.rectb(x, y, w, h, 7)
        for i, line in enumerate(
            self.current_page_lines(
                self.lines,
                self.index,
                max_chars=layout.wrap_width,
                max_rows=3,
            )
        ):
            self.text(x + 8, y + 6 + i * 12, line, 7)
        if (pyxel.frame_count // 15) % 2:
            self.text(x + w - 12, y + h - 12, "v", 7)
