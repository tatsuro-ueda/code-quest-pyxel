from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProfessorModel:
    """professor シーンの状態（P1-G10 で Game.professor_* を取り込み）。"""

    choice_active: bool = False
    choice_cursor: int = 1  # 0=うけいれる / 1=ことわる
    intro_idx: int = 0
    intro_lines: list[str] = field(default_factory=list)
    ending_idx: int = 0
    ending_lines: list[str] = field(default_factory=list)
