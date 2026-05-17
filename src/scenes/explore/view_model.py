"""explore scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を ExploreLandmark に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExploreLandmark:
    """ランドマーク強調 1 個（表示は view が pulse 計算）。"""

    # === Public API ===

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

    # === Public API ===

    is_in_dungeon: bool
    cam_x: int
    cam_y: int
    # bltm 引数
    # pyxel.bltm(bltm_x, bltm_y, tm, bltm_u, bltm_v,
    #            bltm_w, bltm_h, [colkey])
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
    is_boss_marker_active: bool = False  # ダンジョンかつ未撃破
    image_banks: Any = None  # 描画専用アセット参照（M2-1 例外）
