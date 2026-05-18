"""explore scene の描画。

Problems:
    - 描画コードに状態判定が混ざると、見た目を変えるだけのつもりが
      Model 整合性まで考えることになる。
    - Pyxel API が Presenter / Model 側に染み出すとレイヤ境界が崩れ、
      テストでモックしづらくなる。

Solutions:
    - explore の View は ViewModel と Pyxel API だけを扱い、
      判断は Presenter 側に閉じ込める。
"""
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


def _is_offscreen(sx: int, sy: int) -> bool:
    """画面外スクリーン座標かを判定する。

    Args:
        sx: スクリーン x 座標。
        sy: スクリーン y 座標。
    Returns:
        x が [-16, 256] / y が [8, 256] の範囲外なら True。
    Policy:
        - ランドマーク強調枠を画面外で描かないためのガード。
    """
    if not -16 <= sx <= 256:
        return True
    return not 8 <= sy <= 256


def _select_explore_bgm(game) -> int:
    """game 状態から探索 BGM の musics index を決める純粋関数。

    Args:
        game: game の値。
    Returns:
        関数の戻り値。
    Postconditions:
        - 副作用とモデル更新は実装どおり。
    """
    if game is None:
        return TOWN_BGM_INDEX
    # 町メニュー (state == "town") を開いている間は town BGM を維持する。
    if getattr(game, "state", None) == "town":
        return TOWN_BGM_INDEX
    pm = getattr(game, "player_model", None)
    is_predicate_3 = pm is not None and getattr(pm, 'in_dungeon', False)
    if is_predicate_3:
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

    Args:
        game: game の値。
    Postconditions:
        - 副作用とモデル更新は実装どおり。
    """
    _run_play_bgm(game)


def _run_play_bgm(game) -> None:
    """_run_play_bgm() の実装本体。

    Args:
        game: game の値。
    Postconditions:
        - 副作用とモデル更新は実装どおり。
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

    # === Public API ===

    def render(self, *, mode: str) -> dict[str, str]:
        """現在の探索モードを描画に必要な辞書として返す（snapshot 用）。

        Args:
            mode: mode の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return {"mode": mode}

    def draw(self, vm: ExploreViewModel, text_writer: Any = None) -> None:
        """ExploreViewModel を画面に描く。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_draw(vm, text_writer)

    # === Internal helpers (private) ===

    def _run_draw(self, vm: ExploreViewModel, text_writer: Any = None) -> None:
        """_run_draw() の実装本体。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._draw_tilemap(vm)
        self._draw_landmarks(vm)
        self._draw_boss_marker(vm)
        self._draw_hero(vm)

    @staticmethod
    def _draw_tilemap(vm: ExploreViewModel) -> None:
        """tilemap[0] からカメラ位置に対応するピクセル領域を貼る。

        Args:
            vm: vm の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        Policy:
            - A 案: 動的 variant 計算なし。
        """
        pyxel.bltm(
            vm.bltm_x, vm.bltm_y, vm.tm,
            vm.bltm_u, vm.bltm_v, vm.bltm_w, vm.bltm_h,
        )

    @staticmethod
    def _draw_landmarks(vm: ExploreViewModel) -> None:
        """ランドマーク強調枠（pulse 付き）を描画する。

        Args:
            vm: vm の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if not vm.landmarks:
            return
        cam_x, cam_y = vm.cam_x, vm.cam_y
        pulse = (pyxel.frame_count // 8) % 4
        for lm in vm.landmarks:
            sx = lm.tx * 16 - cam_x
            sy = lm.ty * 16 - cam_y + 24
            if _is_offscreen(sx, sy):
                continue
            pyxel.rectb(sx - 1 - pulse, sy - 1 - pulse,
                        18 + pulse * 2, 18 + pulse * 2, lm.color)

    @staticmethod
    def _draw_boss_marker(vm: ExploreViewModel) -> None:
        """ダンジョン内未撃破時のボス目印を描画する。

        Args:
            vm: vm の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if not vm.is_boss_marker_active:
            return
        if vm.boss_marker_screen_xy is None:
            return
        ib = vm.image_banks
        bp = ib.sprite_bank.get("hero_down") if ib else None
        if bp is None:
            return
        sx, sy = vm.boss_marker_screen_xy
        pyxel.blt(sx, sy, 1, bp[0], bp[1], 16, 16, 0)

    @staticmethod
    def _draw_hero(vm: ExploreViewModel) -> None:
        """ヒーロースプライトを描画する。

        Args:
            vm: vm の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        ib = vm.image_banks
        bp = ib.sprite_bank.get(vm.hero_sprite_key) if ib else None
        if bp is None:
            return
        hero_sx, hero_sy = vm.hero_screen_xy
        pyxel.blt(hero_sx, hero_sy, 1, bp[0], bp[1], 16, 16, 0)
