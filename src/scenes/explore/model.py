from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.shared.constants.tile_data import IMPASSABLE, T_GRASS


@dataclass
class ExploreModel:
    """フィールド探索シーンの Model（M4-1 改訂版）。

    State：探索モード・移動演出。
    DB 読み取り責務：pyxel.tilemaps[0] と ImageBanks.tile_id_by_pixel から
    タイル ID を直読する（imagebank=DB 方針）。描画系 Pyxel API は呼ばない。
    """

    mode: str = "map"
    walk_frame: int = 0
    walk_timer: int = 0
    move_cooldown: int = 0
    a_cooldown: bool = False
    image_banks: Any = None
    # framework-rule.md M4-3: カメラ位置は Explore 専用なので Game ではなく
    # ExploreModel に持つ。presenter が build_view_model のたびに更新する。
    cam_x: int = 0
    cam_y: int = 0

    def start_a_cooldown(self) -> None:
        """次フレームの A 押下を 1 回吸収するクールダウンを立てる。"""
        self.a_cooldown = True

    def current_tilemap_id(self, in_dungeon: bool) -> int:
        """bltm 用 tilemap 番号。world / dungeon ともに tilemap[0] を使う
        （dungeon は Y オフセット領域）。"""
        return 0

    def get_tile(self, x: int, y: int, *, in_dungeon: bool) -> int:
        """マス (x, y) のタイル ID を pyxel.tilemaps から直読する（DB 読み取り）。

        - 1 ゲームタイル = 16x16 ピクセル = 2x2 cells（tilemap は 8x8 cell 単位）
        - dungeon は Y オフセット領域（DUNGEON_TM_OFFSET_Y は image_banks 側に定義）
        """
        from src.shared.services.image_banks import DUNGEON_TM_OFFSET_Y
        oy = DUNGEON_TM_OFFSET_Y if in_dungeon else 0
        tu, tv = pyxel.tilemaps[0].pget(2 * x, oy + 2 * y)
        key = (tu * 8, tv * 8)
        if self.image_banks is None:
            return T_GRASS
        return self.image_banks.tile_id_by_pixel.get(key, T_GRASS)

    def is_walkable(self, x: int, y: int, *, in_dungeon: bool) -> bool:
        """マス (x, y) が通行可能か。IMPASSABLE 集合に含まれなければ True。"""
        return self.get_tile(x, y, in_dungeon=in_dungeon) not in IMPASSABLE
