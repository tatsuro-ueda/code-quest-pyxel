from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SettingsModel:
    """settings シーンの状態（P1-G8 で Game.settings_{cursor, origin} を取り込み）。"""

    cursor: int = 0
    origin: str = "title"
