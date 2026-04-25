from __future__ import annotations

"""shop シーンの ViewModel（M2-2：解釈済みの描画用データ）。"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ShopRow:
    """商品 1 行の解釈済みデータ。"""

    label: str  # marker + 名前 + 効果値 + 価格 + [もっています]
    color: int


@dataclass(frozen=True)
class ShopViewModel:
    """shop シーン全体の解釈済みデータ。"""

    title: str
    gold_label: str
    rows: list[ShopRow] = field(default_factory=list)
    empty_message: str | None = None  # 在庫なし時。None なら rows を表示
    message: str | None = None  # 一時 message。None なら非表示
