"""ai_help scene の local state。

Problems:
    - シーンの局所状態を Game に直書きすると、画面追加で状態が
      散らばってどこを直すか分かりにくくなる。
    - state 値や cursor 位置を View / Presenter から直接書き換えると
      不正な遷移を作りやすい。

Solutions:
    - ai_help シーンの局所状態を AiHelpModel に集約し、Presenter から
      渡された変更だけを受ける。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AiHelpModel:
    """ai_help シーンの状態（P1-G9 で Game._ai_help_status を取り込み）。"""

    # === Public API ===

    status: str = ""
