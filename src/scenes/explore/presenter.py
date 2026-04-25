from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.explore.model import ExploreModel
from src.scenes.explore.view_model import ExploreLandmark, ExploreViewModel


@dataclass
class ExplorePresenter:
    """探索シーンのモード切替と ViewModel 組立て（M3-1 / M2-2）。"""

    model: ExploreModel

    def change_mode(self, mode: str) -> None:
        """探索モードを指定値（map / menu など）に差し替える。"""
        self.model.mode = mode

    def build_view_model(self, game: Any) -> ExploreViewModel:
        """カメラ計算 + 表示範囲決定 + landmark 集約を行い VM を返す。

        副作用として game.cam_x / game.cam_y を更新する（M3-1: presenter は
        GameState を更新してよい）。
        """
        p = game.player_model
        current_map = game.dungeon_map if p.in_dungeon else game.world_map
        mw = len(current_map[0]); mh = len(current_map)
        view_w = 256; view_h = 232
        game.cam_x = p.x * 16 - view_w // 2 + 8
        game.cam_y = p.y * 16 - view_h // 2 + 8
        game.cam_x = max(0, min(mw * 16 - view_w, game.cam_x))
        game.cam_y = max(0, min(mh * 16 - view_h, game.cam_y))

        tx_start = max(0, game.cam_x // 16)
        ty_start = max(0, game.cam_y // 16)
        tx_end = min(mw, (game.cam_x + view_w) // 16 + 2)
        ty_end = min(mh, (game.cam_y + view_h) // 16 + 2)

        hero_sx = p.x * 16 - game.cam_x
        hero_sy = p.y * 16 - game.cam_y + 24
        sprite_key = "hero_walk" if self.model.walk_frame == 1 else "hero_down"

        landmarks: list[ExploreLandmark] = []
        if not p.in_dungeon:
            for tx, ty, color, enabled in (
                (32, 9, 11, True),
                (40, 32, 2, True),
                (25, 6, 10, p.glitch_lord_defeated),
            ):
                if enabled:
                    landmarks.append(ExploreLandmark(tx=tx, ty=ty, color=color))

        return ExploreViewModel(
            current_map=current_map,
            in_dungeon=p.in_dungeon,
            cam_x=game.cam_x,
            cam_y=game.cam_y,
            tx_start=tx_start,
            ty_start=ty_start,
            tx_end=tx_end,
            ty_end=ty_end,
            hero_screen_xy=(hero_sx, hero_sy),
            hero_sprite_key=sprite_key,
            landmarks=landmarks,
            boss_marker_active=(p.in_dungeon and not p.glitch_lord_defeated),
            image_banks=game.image_banks,
        )
