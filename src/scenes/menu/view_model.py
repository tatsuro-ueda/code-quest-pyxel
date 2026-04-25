from __future__ import annotations

"""menu シーンの ViewModel（M2-2：解釈済みの描画用データ）。"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MenuRow:
    """メニュー 1 行（main / sub 共通）。`text` は marker 込み完成形。"""

    text: str
    color: int


@dataclass(frozen=True)
class MenuSubPanel:
    """サブパネル（status / items / equip）の解釈済みデータ。"""

    height: int
    rows: list[MenuRow] = field(default_factory=list)
    empty_message: str | None = None  # rows が空のとき表示する代替（items 専用）
    info_message: str | None = None  # 一時 message（items 専用）


@dataclass(frozen=True)
class MenuViewModel:
    """menu シーン全体の解釈済みデータ。"""

    main_rows: list[MenuRow] = field(default_factory=list)
    sub_panel: MenuSubPanel | None = None  # None なら main メニューのみ
