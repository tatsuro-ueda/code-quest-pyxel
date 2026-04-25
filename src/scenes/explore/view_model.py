from __future__ import annotations

"""explore シーンの ViewModel（M2-2：解釈済みの描画用データ）。

カメラ計算（game.cam_x/y への代入）は presenter 側に移し、view は VM に
入った座標とアセット参照だけで描画する。タイル境界判定や地形 variant
の解決はランタイム計算量が大きいので view 内のループに残す。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExploreLandmark:
    """ランドマーク強調 1 個（表示は view が pulse 計算）。"""

    tx: int
    ty: int
    color: int


@dataclass(frozen=True)
class ExploreViewModel:
    """explore シーン全体の解釈済みデータ。"""

    current_map: list[list[int]]
    in_dungeon: bool
    cam_x: int
    cam_y: int
    tx_start: int
    ty_start: int
    tx_end: int
    ty_end: int
    hero_screen_xy: tuple[int, int]
    hero_sprite_key: str  # "hero_walk" or "hero_down"
    landmarks: list[ExploreLandmark] = field(default_factory=list)
    boss_marker_active: bool = False  # ダンジョンかつ未撃破
    image_banks: Any = None  # 描画専用アセット参照（M2-1 例外）
