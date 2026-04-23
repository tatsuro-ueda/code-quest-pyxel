from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EndingModel:
    """ending シーンの状態（P1-G11 で Game.ending_lines を取り込み）。"""

    lines: list[str] = field(default_factory=list)
