"""menu scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を MenuRow に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MenuRow:
    """メニュー 1 行（main / sub 共通）。`text` は marker 込み完成形。"""

    # === Public API ===

    text: str
    color: int


@dataclass(frozen=True)
class MenuSubPanel:
    """サブパネル（status / items / equip）の解釈済みデータ。"""

    # === Public API ===

    height: int
    rows: list[MenuRow] = field(default_factory=list)
    empty_message: str | None = None  # rows が空のとき表示する代替（items 専用）
    info_message: str | None = None  # 一時 message（items 専用）


@dataclass(frozen=True)
class MenuViewModel:
    """menu シーン全体の解釈済みデータ。"""

    # === Public API ===

    main_rows: list[MenuRow] = field(default_factory=list)
    sub_panel: MenuSubPanel | None = None  # None なら main メニューのみ
