from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ShopModel:
    """shop シーンの状態（P1-G5 で Game から shop_* を取り込み）。"""

    kind: str = ""
    inventory: list[int] = field(default_factory=list)
    cursor: int = 0
    message: str = ""
    message_ttl: int = 0  # 下部メッセージの残り表示フレーム数（0 でカーソル装備判定にフォールバック）
