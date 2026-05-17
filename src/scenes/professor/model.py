"""professor scene の local state。

Problems:
    - シーンの局所状態を Game に直書きすると、画面追加で状態が
      散らばってどこを直すか分かりにくくなる。
    - state 値や cursor 位置を View / Presenter から直接書き換えると
      不正な遷移を作りやすい。

Solutions:
    - professor シーンの局所状態を ProfessorModel に集約し、Presenter から
      渡された変更だけを受ける。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProfessorModel:
    """professor シーンの状態（P1-G10 で Game.professor_* を取り込み）。"""

    # === Public API ===

    is_choice_active: bool = False
    choice_cursor: int = 1  # 0=うけいれる / 1=ことわる
    intro_idx: int = 0
    intro_lines: list[str] = field(default_factory=list)
    ending_idx: int = 0
    ending_lines: list[str] = field(default_factory=list)
