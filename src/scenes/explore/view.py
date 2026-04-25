from __future__ import annotations

from typing import Any

import pyxel

from src.scenes.explore.view_model import ExploreViewModel


class ExploreView:
    """探索シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self, *, mode: str) -> dict[str, str]:
        """現在の探索モードを描画に必要な辞書として返す（snapshot 用）。"""
        return {"mode": mode}

    def draw(self, vm: ExploreViewModel, text_writer: Any = None) -> None:
        """ExploreViewModel を画面に描く。"""
        import src.runtime.main_runtime as M
        cm = vm.current_map
        ib = vm.image_banks
        cam_x, cam_y = vm.cam_x, vm.cam_y
        water_frame2 = (pyxel.frame_count // 30) % 2 == 1

        for ty in range(vm.ty_start, vm.ty_end):
            for tx in range(vm.tx_start, vm.tx_end):
                tile = cm[ty][tx]
                sx = tx * 16 - cam_x
                sy = ty * 16 - cam_y + 24

                if tile == M.T_PATH and not vm.in_dungeon:
                    variant = M.get_path_variant(cm, tx, ty)
                    bank_pos = ib.path_variant_bank.get(id(variant))
                    if bank_pos:
                        pyxel.blt(sx, sy, 0, bank_pos[0], bank_pos[1], 16, 16, 0)
                    else:
                        bp = ib.tile_bank[M.T_PATH]
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                elif tile == M.T_WATER:
                    shore = None
                    if not vm.in_dungeon:
                        shore = M.get_shore_variant(cm, tx, ty)
                    if shore:
                        bank_pos = ib.shore_variant_bank.get(id(shore))
                        if bank_pos:
                            pyxel.blt(sx, sy, 0, bank_pos[0], bank_pos[1], 16, 16)
                        else:
                            bp = ib.tile_bank[M.T_WATER]
                            pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                    else:
                        if water_frame2 and ib.tile_bank_water2:
                            bp = ib.tile_bank_water2
                        else:
                            bp = ib.tile_bank[M.T_WATER]
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                else:
                    bp = ib.tile_bank.get(tile)
                    if bp:
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)

        # ランドマーク強調（pulse は frame_count から view 側で）
        if vm.landmarks:
            pulse = (pyxel.frame_count // 8) % 4
            for lm in vm.landmarks:
                sx = lm.tx * 16 - cam_x
                sy = lm.ty * 16 - cam_y + 24
                if sx < -16 or sx > 256 or sy < 8 or sy > 256:
                    continue
                pyxel.rectb(sx - 1 - pulse, sy - 1 - pulse,
                            18 + pulse * 2, 18 + pulse * 2, lm.color)

        # ボス目印（ダンジョン内かつ未撃破）
        if vm.boss_marker_active:
            bp = ib.sprite_bank.get("hero_down")
            if bp is not None:
                for ty, row in enumerate(cm):
                    for tx, tile in enumerate(row):
                        if tile != M.T_GLITCH_LORD_TRIGGER:
                            continue
                        sx = tx * 16 - cam_x
                        sy = ty * 16 - cam_y + 24
                        if sx < -16 or sx > 256 or sy < 8 or sy > 256:
                            break
                        pyxel.blt(sx, sy, 1, bp[0], bp[1], 16, 16, 0)
                        break

        # ヒーロー
        bp = ib.sprite_bank.get(vm.hero_sprite_key)
        if bp:
            hero_sx, hero_sy = vm.hero_screen_xy
            pyxel.blt(hero_sx, hero_sy, 1, bp[0], bp[1], 16, 16, 0)
