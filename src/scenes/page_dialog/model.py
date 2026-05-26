"""page_dialog scene の局所状態。

Problems:
    - 魔王戦前の全画面会話を Game に直書きすると、line / callback / return
      state が散って他の会話画面へ再利用しにくい。
    - 会話完了後の callback を scene 外に置きっぱなしにすると、二重呼びや
      state 戻し忘れが起きやすい。

Solutions:
    - page_dialog の局所状態を PageDialogModel に集約し、Scene / Presenter は
      この dataclass だけを読み書きする。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PageDialogModel:
    """full-screen page dialog の局所状態。"""

    # === Public API ===

    lines: list[str] = field(default_factory=list)
    index: int = 0
    callback: Any = None
    return_state: str = "map"
    text_y: int = 60
    text_color: int = 7
