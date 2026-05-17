"""explore scene の local state。

Problems:
    - シーンの局所状態を Game に直書きすると、画面追加で状態が
      散らばってどこを直すか分かりにくくなる。
    - state 値や cursor 位置を View / Presenter から直接書き換えると
      不正な遷移を作りやすい。

Solutions:
    - explore シーンの局所状態を ExploreModel に集約し、Presenter から
      渡された変更だけを受ける。
"""
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

    # === Public API ===

    mode: str = "map"
    walk_frame: int = 0
    walk_timer: int = 0
    move_cooldown: int = 0
    has_a_cooldown: bool = False
    image_banks: Any = None
    # framework-rule.md M4-3: カメラ位置は Explore 専用なので Game ではなく
    # ExploreModel に持つ。presenter が build_view_model のたびに更新する。
    cam_x: int = 0
    cam_y: int = 0

    def start_a_cooldown(self) -> None:
        """次フレームの A 押下を 1 回吸収するクールダウンを立てる。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.has_a_cooldown = True

    def get_current_tilemap_id(self, in_dungeon: bool) -> int:
        """bltm 用 tilemap 番号。world / dungeon ともに tilemap[0] を使う
        （dungeon は Y オフセット領域）。
        Args:
            in_dungeon: in_dungeon の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return 0

    def get_tile(self, x: int, y: int, *, in_dungeon: bool) -> int:
        """マス (x, y) のタイル ID を pyxel.tilemaps から直読する（DB 読み取り）。

        - 1 ゲームタイル = 16x16 ピクセル = 2x2 cells（tilemap は 8x8 cell 単位）
        - dungeon は Y オフセット領域（DUNGEON_TM_OFFSET_Y は image_banks 側に定義）

        Args:
            x: x の値。
            y: y の値。
            in_dungeon: in_dungeon の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        from src.shared.services.image_banks import DUNGEON_TM_OFFSET_Y
        oy = DUNGEON_TM_OFFSET_Y if in_dungeon else 0
        tu, tv = pyxel.tilemaps[0].pget(2 * x, oy + 2 * y)
        key = (tu * 8, tv * 8)
        if self.image_banks is None:
            return T_GRASS
        return self.image_banks.tile_id_by_pixel.get(key, T_GRASS)

    def is_walkable(self, x: int, y: int, *, in_dungeon: bool) -> bool:
        """マス (x, y) が通行可能か。IMPASSABLE 集合に含まれなければ True。

        Args:
            x: x の値。
            y: y の値。
            in_dungeon: in_dungeon の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self.get_tile(x, y, in_dungeon=in_dungeon) not in IMPASSABLE
