"""shop scene の local state。

Problems:
    - シーンの局所状態を Game に直書きすると、画面追加で状態が
      散らばってどこを直すか分かりにくくなる。
    - state 値や cursor 位置を View / Presenter から直接書き換えると
      不正な遷移を作りやすい。

Solutions:
    - shop シーンの局所状態を ShopModel に集約し、Presenter から
      渡された変更だけを受ける。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ShopModel:
    """shop シーンの状態（P1-G5 で Game から shop_* を取り込み）。"""

    # === Public API ===

    kind: str = ""
    inventory: list[int] = field(default_factory=list)
    cursor: int = 0
    message: str = ""
    message_ttl: int = 0  # 下部メッセージの残り表示フレーム数（0 でカーソル装備判定にフォールバック）
