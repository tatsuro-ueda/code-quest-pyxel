from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BattleModel:
    """バトル画面のフェーズ（command / action / result 等）を保持する。"""

    phase: str = "command"
