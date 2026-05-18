"""メッセージウィンドウの寸法と純粋描画関数。

このファイルに含まれる関数・クラス：

- MessageWindowLayout: 短いメッセージ表示向けのウィンドウ寸法を保持する不変レコード
  - rect: 描画用に (x, y, width, height) のタプルを返す
- draw_message_window: メッセージウィンドウ枠と本文を描画する public エントリ
- draw_say_overlay: say_buffer のデバッグ行を画面左上に重ね描きする public エントリ
- _draw_message_window_impl: draw_message_window() の実装本体（背景・枠・本文・点滅カーソル）
- _draw_message_body: 折返し済み行と点滅カーソルを描画する内部 helper
- _draw_blinking_cursor: frame_count に応じて v カーソルを描く内部 helper
- _draw_say_overlay_impl: draw_say_overlay() の実装本体（空ガードと行ループ）
- _draw_say_line: 1 行分の背景塗りと文字描画を行う内部 helper

Problems:
    - service 側の MessageDisplay に pyxel.rect / rectb / frame_count を
      直接書くと、描画レイヤと state 管理（lines / index / say_buffer）が
      同じ場所に混ざってテストでモックしづらくなる。
    - dialog_window より短いメッセージ枠の magic number を各 scene に
      ばらまくと、レイアウト変更が複数箇所に波及してしまう。

Solutions:
    - メッセージ枠の寸法は MessageWindowLayout の frozen dataclass に
      集約し、scene / service 側は (x, y, w, h) を受け取って描画位置を
      決めるだけにする。
    - public 描画関数は private helper への単純委譲に留め、条件分岐や
      ループといった制御フローは private 側に隔離する。
"""
from __future__ import annotations

from dataclasses import dataclass

import pyxel

from src.shared.ui.text_renderer import draw_text


@dataclass(frozen=True)
class MessageWindowLayout:
    """短いメッセージ表示向けのウィンドウ寸法と行折返し幅。"""

    # === Public API ===

    x: int = 8
    y: int = 208
    width: int = 240
    height: int = 44
    wrap_width: int = 28

    def rect(self) -> tuple[int, int, int, int]:  # noqa: CR100
        """描画用に (x, y, width, height) のタプルを返す。

        Returns:
            (x, y, width, height) 形式の矩形寸法。
        Policy:
            - フィールドの単純な並び替えに留め、座標変換や副作用は行わない。
            - メソッド名 rect は他の UI レイアウト（DialogWindow）と統一されているため固定。
        """
        return (self.x, self.y, self.width, self.height)


# === Public API ===


def draw_message_window(
    lines: list[str],
    *,
    layout: MessageWindowLayout | None = None,
    draw_text_fn=None,
) -> None:
    """メッセージウィンドウ枠と本文 (折返し済み行) を描画する。

    Args:
        lines: 折返し済みの本文行（描画はそのまま行ごとに配置される）。
        layout: 描画位置・サイズを指定するレイアウト。None なら既定値を使う。
        draw_text_fn: 文字描画関数の差し替え用（test 用フック）。None なら text_renderer.draw_text。
    Policy:
        - public 関数は private helper への委譲のみとし、制御フローは内部に隔離する。
        - 関数名 draw_message_window は他モジュールから import されているため固定。
    """
    _draw_message_window_impl(lines, layout=layout, draw_text_fn=draw_text_fn)


def draw_say_overlay(say_buffer: list[str], *, draw_text_fn=None) -> None:
    """`MessageDisplay.say()` で蓄えたデバッグ行を画面左上に重ね描きする。

    Args:
        say_buffer: 重ね描きする文字列のリスト。空ならば no-op。
        draw_text_fn: 文字描画関数の差し替え用（test 用フック）。None なら text_renderer.draw_text。
    Policy:
        - public 関数は private helper への委譲のみとし、空ガードとループは内部に隔離する。
        - 関数名 draw_say_overlay は他モジュールから import されているため固定。
    """
    _draw_say_overlay_impl(say_buffer, draw_text_fn=draw_text_fn)


# === Internal helpers (private) ===


def _draw_message_window_impl(
    lines: list[str],
    *,
    layout: MessageWindowLayout | None,
    draw_text_fn,
) -> None:
    """draw_message_window() の実装本体（枠塗り→枠線→本文→点滅カーソル）。

    Args:
        lines: 折返し済みの本文行。
        layout: 描画位置・サイズを指定するレイアウト。None なら既定値を使う。
        draw_text_fn: 文字描画関数の差し替え。None なら text_renderer.draw_text。
    Policy:
        - layout / draw_text_fn の既定値補完を先頭で行い、以降は確定値で描く。
        - 枠と本文と点滅カーソルの責務を helper に分けて見通しを保つ。
    """
    resolved_layout = layout if layout is not None else MessageWindowLayout()
    resolved_text_fn = draw_text_fn if draw_text_fn is not None else draw_text
    x, y, w, h = resolved_layout.rect()
    pyxel.rect(x, y, w, h, 0)
    pyxel.rectb(x, y, w, h, 7)
    _draw_message_body(x, y, w, h, lines, resolved_text_fn)


def _draw_message_body(
    x: int,
    y: int,
    w: int,
    h: int,
    lines: list[str],
    text_fn,
) -> None:
    """折返し済み行を等間隔で描画し、最後に点滅カーソルを描く。

    Args:
        x: ウィンドウ左上 X 座標。
        y: ウィンドウ左上 Y 座標。
        w: ウィンドウ幅。
        h: ウィンドウ高さ。
        lines: 折返し済みの本文行。
        text_fn: 文字描画関数。
    Policy:
        - 行間 12px は MessageWindowLayout と整合する固定値。
        - 点滅判定は _draw_blinking_cursor 側に隔離する。
    """
    for i, line in enumerate(lines):
        text_fn(x + 8, y + 6 + i * 12, line, 7)
    _draw_blinking_cursor(x, y, w, h, text_fn)


def _draw_blinking_cursor(x: int, y: int, w: int, h: int, text_fn) -> None:
    """`(frame_count // 15) % 2` のタイミングで v カーソルを描く。

    Args:
        x: ウィンドウ左上 X 座標。
        y: ウィンドウ左上 Y 座標。
        w: ウィンドウ幅。
        h: ウィンドウ高さ。
        text_fn: 文字描画関数。
    Policy:
        - pyxel.frame_count を直接見るのはこの helper に閉じる。
        - 描かないフレームでは no-op で副作用を持たない。
    """
    if (pyxel.frame_count // 15) % 2:
        text_fn(x + w - 12, y + h - 12, "v", 7)


def _draw_say_overlay_impl(say_buffer: list[str], *, draw_text_fn) -> None:
    """draw_say_overlay() の実装本体（空ガードと行ループ）。

    Args:
        say_buffer: 重ね描きする文字列のリスト。
        draw_text_fn: 文字描画関数の差し替え。None なら text_renderer.draw_text。
    Policy:
        - say_buffer が空なら no-op を最初に確定させる。
        - draw_text_fn の既定値補完を行い、行描画は _draw_say_line に委譲する。
    """
    if not say_buffer:
        return
    resolved_text_fn = draw_text_fn if draw_text_fn is not None else draw_text
    for i, line in enumerate(say_buffer):
        y = 4 + i * 12
        _draw_say_line(y, line, resolved_text_fn)


def _draw_say_line(y: int, line: str, text_fn) -> None:
    """say_buffer の 1 行分の背景塗りと文字描画を行う。

    Args:
        y: 描画 Y 座標。
        line: 描画する 1 行分の文字列。
        text_fn: 文字描画関数。
    Policy:
        - 背景塗りは画面左上の固定矩形（x=2, w=252）に揃える。
        - 文字色 10 は debug 表示として固定値で扱う。
    """
    pyxel.rect(2, y - 1, 252, 12, 0)
    text_fn(4, y, line, 10)
