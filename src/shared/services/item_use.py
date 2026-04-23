from __future__ import annotations

"""アイテム使用の効果適用（Phase 1 スケルトン、P1-G14 で 1 関数を取り込む）。

P1-G14 で Game._use_item をここに移動する。scenes/menu か scenes/battle
から呼ばれる。
"""

from typing import Any


def use_item(player: dict[str, Any], item_index: int) -> dict[str, Any]:
    """アイテムを使って効果を適用する（P1-G14 で中身を埋める）。

    Phase 1 スケルトンでは何もせず結果 dict を返すだけ。
    """
    return {"used": False, "reason": "not implemented yet"}
