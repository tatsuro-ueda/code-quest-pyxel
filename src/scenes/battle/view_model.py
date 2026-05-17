"""battle scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を BattleRow に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BattleRow:
    """sub-panel の 1 行（marker 込み完成形）。"""

    # === Public API ===

    text: str
    color: int


@dataclass(frozen=True)
class BattleSubPanel:
    """バトル画面下部 sub-panel。phase に応じて中身を差し替える。"""

    # === Public API ===

    is_grid: bool = False  # True: 2x2 grid (menu), False: 縦 list
    rows: list[BattleRow] = field(default_factory=list)
    empty_message: str | None = None
    info_message: str | None = None  # phase 共通の m.text 別経路ではなく item_select 専用


@dataclass(frozen=True)
class BattleViewModel:
    """battle 画面 1 フレームの解釈済みデータ。"""

    # === Public API ===

    enemy_sprite_key: str | None  # None なら enemy なし→ render skip
    enemy_name_text: str
    enemy_hp_label: str
    enemy_hp_ratio: float
    player_status_line1: str  # "プログラマー  レベルN"
    player_status_line2: str  # "HP a/b  MP c/d"
    player_hp_ratio: float
    player_hp_color: int  # 11 (健康) or 8 (危険)
    main_text: str | None  # m.text の上部表示。None なら非表示
    sub_panel: BattleSubPanel | None
    image_banks: Any = None  # 描画専用アセット参照（M2-1 例外）
