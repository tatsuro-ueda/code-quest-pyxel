from __future__ import annotations

from typing import Any

import pyxel

from src.scenes.explore.view_model import ExploreViewModel
from src.shared.services.audio_system import play_bgm_track


# pyxres 内 musics スロット番号（旧 TRACK_ORDER と整合）。
# town: 1 / overworld: 2 / dungeon: 3
TOWN_BGM_INDEX = 1
OVERWORLD_BGM_INDEX = 2
DUNGEON_BGM_INDEX = 3


def _select_explore_bgm(game) -> int:
    """game 状態から探索 BGM の musics index を決める純粋関数。"""
    if game is None:
        return TOWN_BGM_INDEX
    # 町メニュー (state == "town") を開いている間は town BGM を維持する。
    if getattr(game, "state", None) == "town":
        return TOWN_BGM_INDEX
    pm = getattr(game, "player_model", None)
    if pm is not None and getattr(pm, "in_dungeon", False):
        return DUNGEON_BGM_INDEX
    # zone 判定（旧 sync_audio と同じく runtime の get_zone を使う）。
    try:
        import src.runtime.main_runtime as M
        zone = M.get_zone(pm.y, pm.in_dungeon) if pm is not None else 0
    except Exception:
        zone = 0
    if zone >= 1:
        return OVERWORLD_BGM_INDEX
    return TOWN_BGM_INDEX


def play_bgm(game) -> None:
    """探索シーンの BGM を冪等に発火する（town/overworld/dungeon を分岐選択）。

    CJ44 確定版（追加整理）：冪等性は ``audio_system.play_bgm_track`` に集約。
    """
    if game is None:
        return
    play_bgm_track(_select_explore_bgm(game))


class ExploreView:
    """探索シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。

    2026-05-05 改訂（A 案）：タイル本体は `pyxel.bltm` 1 回呼びで描画する。
    landmark / boss marker / hero は引き続き個別 `pyxel.blt` で重ね描き。
    water animation・path_variant・shore_variant の動的計算は撤去（pyxres
    に刻まれたタイルがそのまま見える）。
    """

    def render(self, *, mode: str) -> dict[str, str]:
        """現在の探索モードを描画に必要な辞書として返す（snapshot 用）。"""
        return {"mode": mode}

    def draw(self, vm: ExploreViewModel, text_writer: Any = None) -> None:
        """ExploreViewModel を画面に描く。"""
        ib = vm.image_banks
        cam_x, cam_y = vm.cam_x, vm.cam_y

        # タイル本体：bltm 1 回。tilemap[0] からカメラ位置に対応するピクセル
        # 領域を切り出してそのまま画面に貼る（A 案：動的 variant 計算なし）。
        pyxel.bltm(
            vm.bltm_x, vm.bltm_y, vm.tm,
            vm.bltm_u, vm.bltm_v, vm.bltm_w, vm.bltm_h,
        )

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

        # ボス目印（ダンジョン内かつ未撃破。Presenter が画面内座標を解決済み）
        if vm.boss_marker_active and vm.boss_marker_screen_xy is not None:
            bp = ib.sprite_bank.get("hero_down") if ib else None
            if bp is not None:
                sx, sy = vm.boss_marker_screen_xy
                pyxel.blt(sx, sy, 1, bp[0], bp[1], 16, 16, 0)

        # ヒーロー
        bp = ib.sprite_bank.get(vm.hero_sprite_key) if ib else None
        if bp:
            hero_sx, hero_sy = vm.hero_screen_xy
            pyxel.blt(hero_sx, hero_sy, 1, bp[0], bp[1], 16, 16, 0)
