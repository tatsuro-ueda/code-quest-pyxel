from __future__ import annotations

from typing import Any

import pyxel


class ExploreView:
    """探索シーンの描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self, *, mode: str) -> dict[str, str]:
        """現在の探索モードを描画に必要な辞書として返す（snapshot 用）。"""
        return {"mode": mode}

    def draw(self, model: Any, game: Any) -> None:
        """フィールド地図とヒーローを Pyxel に描画する。"""
        import src.runtime.main_runtime as M
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

        water_frame2 = (pyxel.frame_count // 30) % 2 == 1

        for ty in range(ty_start, ty_end):
            for tx in range(tx_start, tx_end):
                tile = current_map[ty][tx]
                sx = tx * 16 - game.cam_x
                sy = ty * 16 - game.cam_y + 24

                if tile == M.T_PATH and not p.in_dungeon:
                    variant = M.get_path_variant(current_map, tx, ty)
                    bank_pos = game.image_banks.path_variant_bank.get(id(variant))
                    if bank_pos:
                        pyxel.blt(sx, sy, 0, bank_pos[0], bank_pos[1], 16, 16, 0)
                    else:
                        bp = game.image_banks.tile_bank[M.T_PATH]
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                elif tile == M.T_WATER:
                    shore = None
                    if not p.in_dungeon:
                        shore = M.get_shore_variant(current_map, tx, ty)
                    if shore:
                        bank_pos = game.image_banks.shore_variant_bank.get(id(shore))
                        if bank_pos:
                            pyxel.blt(sx, sy, 0, bank_pos[0], bank_pos[1], 16, 16)
                        else:
                            bp = game.image_banks.tile_bank[M.T_WATER]
                            pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                    else:
                        if water_frame2 and game.image_banks.tile_bank_water2:
                            bp = game.image_banks.tile_bank_water2
                        else:
                            bp = game.image_banks.tile_bank[M.T_WATER]
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                else:
                    bp = game.image_banks.tile_bank.get(tile)
                    if bp:
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)

        if not p.in_dungeon:
            self._draw_landmark_highlights(game)
        else:
            self._draw_dungeon_glitch_lord_marker(current_map, game)

        # Draw hero
        hero_sx = p.x * 16 - game.cam_x
        hero_sy = p.y * 16 - game.cam_y + 24
        sprite_key = "hero_walk" if model.walk_frame == 1 else "hero_down"
        bp = game.image_banks.sprite_bank.get(sprite_key)
        if bp:
            pyxel.blt(hero_sx, hero_sy, 1, bp[0], bp[1], 16, 16, 0)

    def _draw_dungeon_glitch_lord_marker(self, current_map: Any, game: Any) -> None:
        """ダンジョン最奥のボス位置に目印キャラを描く。"""
        import src.runtime.main_runtime as M
        p = game.player_model
        if p.glitch_lord_defeated:
            return
        bp = game.image_banks.sprite_bank.get("hero_down")
        if bp is None:
            return

        for ty, row in enumerate(current_map):
            for tx, tile in enumerate(row):
                if tile != M.T_GLITCH_LORD_TRIGGER:
                    continue
                sx = tx * 16 - game.cam_x
                sy = ty * 16 - game.cam_y + 24
                if sx < -16 or sx > 256 or sy < 8 or sy > 256:
                    return
                pyxel.blt(sx, sy, 1, bp[0], bp[1], 16, 16, 0)
                return

    def _draw_landmark_highlights(self, game: Any) -> None:
        """ランドマーク強調描画。"""
        p = game.player_model
        marks = [
            (32, 9, 11, True),
            (40, 32, 2, True),
            (25, 6, 10, p.glitch_lord_defeated),
        ]
        pulse = (pyxel.frame_count // 8) % 4
        for tx, ty, color, enabled in marks:
            if not enabled:
                continue
            sx = tx * 16 - game.cam_x
            sy = ty * 16 - game.cam_y + 24
            if sx < -16 or sx > 256 or sy < 8 or sy > 256:
                continue
            pyxel.rectb(sx - 1 - pulse, sy - 1 - pulse,
                        18 + pulse * 2, 18 + pulse * 2, color)
