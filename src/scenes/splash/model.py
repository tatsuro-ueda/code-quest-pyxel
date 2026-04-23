from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SplashModel:
    """splash シーンの状態（P1-G2 で Game.splash_frame を取り込み）。"""

    frame: int = 0
