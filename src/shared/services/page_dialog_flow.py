"""全画面ページ送り会話の共通 helper。

このファイルに含まれる関数：

- current_page_lines_for_dialog: 現在ページの折返し済み行を返す関数
- build_page_prompt_xy: 現在ページが有効ならプロンプト座標を返す関数
- advance_page_on_confirm: 決定入力があるときだけ index を進める関数
- _is_inactive: lines/index が有効範囲外かを返す private helper

Problems:
    - professor 系と魔王戦前会話で「現在ページ」「次ページプロンプト」「confirm
      で advance」の処理が重複すると、片方だけ直ってもう片方が古いまま残る。
    - page dialog の update / draw 条件が scene ごとに分散すると、full-screen
      会話を追加するたびに off-by-one や prompt 表示漏れが混ざりやすい。

Solutions:
    - ページ送りの共通計算を page_dialog_flow.py に寄せ、scene ごとの違いは
      text 色や text_y、callback だけに絞る。
"""
from __future__ import annotations

from typing import Any

from src.shared.services.input_bindings import CONFIRM_BUTTONS


# === Public API ===

def current_page_lines_for_dialog(
    game: Any,
    lines: list[str],
    index: int,
    *,
    max_chars: int = 28,
    max_rows: int = 6,
) -> list[str]:
    """現在ページの折返し済み行を返す。

    Args:
        game: MessageDisplay を持つ game。
        lines: 会話のページ配列。
        index: 現在のページ index。
        max_chars: 1 行あたりの最大文字数。
        max_rows: 1 ページあたりの最大行数。
    Returns:
        現在ページの描画行。範囲外なら空配列。
    """
    if _is_inactive(lines, index):
        return []
    return list(
        game.messages.current_page_lines(
            lines,
            index,
            max_chars=max_chars,
            max_rows=max_rows,
        )
    )


def build_page_prompt_xy(
    lines: list[str],
    index: int,
    *,
    x: int = 228,
    y: int = 200,
) -> tuple[int, int] | None:
    """現在ページが有効なら次ページプロンプト座標を返す。"""
    if _is_inactive(lines, index):
        return None
    return (x, y)


def advance_page_on_confirm(
    game: Any,
    index: int,
    lines: list[str],
) -> tuple[int, bool, bool]:
    """決定入力があるときだけ page を進める。

    Returns:
        `(next_index, done, did_advance)`。
    """
    if _is_inactive(lines, index):
        return index, False, False
    if not game.input_state.btnp(CONFIRM_BUTTONS):
        return index, False, False
    next_index, done = game.messages.advance_page(index, lines)
    return next_index, done, True


# === Internal helpers (private) ===

def _is_inactive(lines: list[str], index: int) -> bool:
    return not lines or index < 0 or index >= len(lines)
