from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MenuModel:
    """menu シーンの状態（P1-G7 で Game.menu_* を取り込み）。"""

    cursor: int = 0
    sub: str | None = None
    item_cursor: int = 0
    message: str = ""
