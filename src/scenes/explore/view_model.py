from __future__ import annotations

"""explore シーンの ViewModel（M2-2：解釈済みの描画用データ）。

カメラ計算（game.cam_x/y への代入）は presenter 側に移し、view は VM に
入った座標とアセット参照だけで描画する。
2026-05-05 (A 案) 以降、タイル合成は ``pyxel.bltm`` 1 回呼びで完結し、
view 内のタイル境界判定 / 地形 variant 解決ループは撤去済み。pyxres の
``tilemaps[0]`` が SSoT として描画されるため、VM は bltm に渡す矩形
（``bltm_x/y/w/h``、``bltm_u/v``、``tm``）と sprite 情報のみを保持する。
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
    """explore シーン全体の解釈済みデータ。

    2026-05-05 改訂：bltm 1 回呼び用の引数 (tm, bltm_u, bltm_v, bltm_w,
    bltm_h, bltm_x, bltm_y) を追加。View はこれをそのまま pyxel.bltm に
    渡すだけ。タイル本体描画はこれで完了し、landmark / boss / hero は
    引き続き個別 blt で重ね描きする。
    """

    in_dungeon: bool
    cam_x: int
    cam_y: int
    # bltm 引数（pyxel.bltm(bltm_x, bltm_y, tm, bltm_u, bltm_v, bltm_w, bltm_h, [colkey])）
    tm: int
    bltm_u: int
    bltm_v: int
    bltm_w: int
    bltm_h: int
    bltm_x: int
    bltm_y: int
    # ボスマーカー描画用：dungeon 内の T_GLITCH_LORD_TRIGGER の screen 座標
    boss_marker_screen_xy: tuple[int, int] | None
    hero_screen_xy: tuple[int, int]
    hero_sprite_key: str  # "hero_walk" or "hero_down"
    landmarks: list[ExploreLandmark] = field(default_factory=list)
    boss_marker_active: bool = False  # ダンジョンかつ未撃破
    image_banks: Any = None  # 描画専用アセット参照（M2-1 例外）
