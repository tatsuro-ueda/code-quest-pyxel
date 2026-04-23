from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TownModel:
    """town シーンの状態（P1-G4 で Game.town_menu_* を取り込み）。"""

    menu_cursor: int = 0
    menu_pos: tuple[int, int] | None = None
