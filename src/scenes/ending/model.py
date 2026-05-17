"""ending scene の local state。

Problems:
    - シーンの局所状態を Game に直書きすると、画面追加で状態が
      散らばってどこを直すか分かりにくくなる。
    - state 値や cursor 位置を View / Presenter から直接書き換えると
      不正な遷移を作りやすい。

Solutions:
    - ending シーンの局所状態を EndingModel に集約し、Presenter から
      渡された変更だけを受ける。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EndingModel:
    """ending シーンの状態（P1-G11 で Game.ending_lines を取り込み）。"""

    # === Public API ===

    lines: list[str] = field(default_factory=list)
