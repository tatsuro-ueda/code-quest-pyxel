"""shop scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を ShopRow に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ShopRow:
    """商品 1 行の解釈済みデータ。"""

    # === Public API ===

    label: str  # marker + 名前 + 効果値 + 価格（[もっています] は下部 message に分離）
    color: int


@dataclass(frozen=True)
class ShopViewModel:
    """shop シーン全体の解釈済みデータ。"""

    # === Public API ===

    title: str
    gold_label: str
    rows: list[ShopRow] = field(default_factory=list)
    empty_message: str | None = None  # 在庫なし時。None なら rows を表示
    message: str | None = None  # 一時 message。None なら非表示
