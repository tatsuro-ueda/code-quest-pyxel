from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AiHelpModel:
    """ai_help シーンの状態（P1-G9 で Game._ai_help_status を取り込み）。"""

    status: str = ""
