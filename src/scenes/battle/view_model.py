from __future__ import annotations

"""battle シーンの ViewModel（M2-2：解釈済みの描画用データ）。

3 つの sub-panel (menu / spell_select / item_select) を BattleSubPanel に
統一し、view 側を単一描画ループに縮退する。enemy sprite は 3x 拡大 blit
が必要なので image_banks 参照を VM 経由で渡す（M2-1 描画専用アセット例外）。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BattleRow:
    """sub-panel の 1 行（marker 込み完成形）。"""

    text: str
    color: int


@dataclass(frozen=True)
class BattleSubPanel:
    """バトル画面下部 sub-panel。phase に応じて中身を差し替える。"""

    is_grid: bool = False  # True: 2x2 grid (menu), False: 縦 list
    rows: list[BattleRow] = field(default_factory=list)
    empty_message: str | None = None
    info_message: str | None = None  # phase 共通の m.text 別経路ではなく item_select 専用


@dataclass(frozen=True)
class BattleViewModel:
    """battle 画面 1 フレームの解釈済みデータ。"""

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
