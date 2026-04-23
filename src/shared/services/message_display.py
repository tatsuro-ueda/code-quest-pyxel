from __future__ import annotations

"""短いメッセージウィンドウ制御（Phase 1 スケルトン、P1-G12 で 12 メソッドを取り込む）。

overlay 的に複数 scene から呼ばれる utility（Q1A）。structured dialog は
dialog_runner.py が担当、本 service は「1〜数行のメッセージ表示」に限る。

P1-G12 で Game クラスから以下を移す：
- _enter_message / show_message / update_message / draw_message_window
- _wrap_text / _dialog_lines / _dialog_text / _current_dialog_page_lines
- _advance_dialog_page / _draw_say_overlay / say / text
"""

from dataclasses import dataclass, field


@dataclass
class MessageDisplay:
    """メッセージウィンドウの表示状態（P1-G12 で中身を埋める）。"""

    msg_callback: object | None = None
    msg_index: int = 0
    msg_lines: list[str] = field(default_factory=list)
    say_buffer: list[str] = field(default_factory=list)
