"""固定幅テキストの折返し行解決 helper。

このファイルに含まれる関数：

- resolve_wrapped_lines: ``text_writer.wrap_text()`` を使って折返し済み行を返す public helper
- _resolve_wrapped_lines_impl: fallback と最大行数カットを行う内部 helper

Problems:
    - battle や shop のような独自 message 枠で折返しロジックを scene ごとに
      持つと、同じ overflow 修正を何度も書くことになる。
    - service 層の ``MessageDisplay.wrap_text()`` を各 View がばらばらに呼ぶと、
      fallback 条件も scene ごとにぶれて回帰しやすい。

Solutions:
    - View 層専用の ``resolve_wrapped_lines()`` を追加し、固定幅 text の
      折返し取得と最大行数制御を共通化する。
    - ``text_writer.wrap_text()`` が無い test double では 1 行 fallback を返し、
      View 側の責務に閉じた互換性を保つ。
"""
from __future__ import annotations

from typing import Any


# === Public API ===


def resolve_wrapped_lines(
    text: str,
    text_writer: Any,
    *,
    max_chars: int,
    max_rows: int,
) -> list[str]:
    """固定幅枠に表示する折返し済み行を返す。

    Args:
        text: 折返し前の文字列。
        text_writer: ``wrap_text()`` を持つ描画補助オブジェクト。
        max_chars: 1 行あたりの最大文字数。
        max_rows: 表示する最大行数。
    Returns:
        表示用に切り詰めた行リスト。
    Policy:
        - public helper は内部実装への単純委譲だけに留める。
    """
    return _resolve_wrapped_lines_impl(
        text,
        text_writer,
        max_chars=max_chars,
        max_rows=max_rows,
    )


# === Internal helpers (private) ===


def _resolve_wrapped_lines_impl(
    text: str,
    text_writer: Any,
    *,
    max_chars: int,
    max_rows: int,
) -> list[str]:
    """折返し関数の存在判定と最大行数カットを行う。

    Args:
        text: 折返し前の文字列。
        text_writer: ``wrap_text()`` を持つ描画補助オブジェクト。
        max_chars: 1 行あたりの最大文字数。
        max_rows: 表示する最大行数。
    Returns:
        折返し済みの行リスト。``wrap_text()`` が無いときは 1 行のまま返す。
    Policy:
        - wrap helper が無い test double でも描画が落ちないよう fallback を維持する。
    """
    wrap_text = getattr(text_writer, "wrap_text", None)
    if not callable(wrap_text):
        return [text]
    return wrap_text(text, max_chars=max_chars)[:max_rows]
