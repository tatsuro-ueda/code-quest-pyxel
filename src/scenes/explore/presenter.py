"""explore scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - explore の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from src.scenes.explore.model import ExploreModel
from src.scenes.explore.view_model import ExploreLandmark, ExploreViewModel
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    UP_BUTTONS,
)
from src.shared.services.landmark_events import find_landmark_at


@dataclass
class ExplorePresenter:
    """探索シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    # === Public API ===

    model: ExploreModel

    def change_mode(self, mode: str) -> None:
        """探索モードを指定値（map / menu など）に差し替える。

        Args:
            mode: mode の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.model.mode = mode

    def update(self, game: Any) -> None:
        """プレイヤー移動とタイルイベント・ランドマーク判定。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update(game)

    def build_view_model(self, game: Any) -> ExploreViewModel:
        """カメラ計算 + bltm 引数組み立て + landmark / boss marker 解決を行い VM を返す。

        副作用として self.model.cam_x / self.model.cam_y を更新する
        （M4-3: カメラは Explore 専用なので ExploreModel に持つ）。

        2026-05-05 改訂：world_map / dungeon_map のリスト走査をやめ、必要な
        マップ寸法・タイル ID 探索は ExploreModel.get_tile（pyxel.tilemaps
        直読）に問い合わせる。bltm 1 回呼びの引数を ViewModel に詰める。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_build_view_model(game)

    # === Internal helpers (private) ===

    @staticmethod
    def _read_move_input(game: Any) -> tuple[int, int]:
        """方向キー入力から (dx, dy) を返す。

        Args:
            game: game の値。
        Returns:
            (dx, dy) の組。何も押されていなければ (0, 0)。
        Policy:
            - 入力検出は上下左右のいずれか 1 軸のみ。
        """
        if game.input_state.btn(UP_BUTTONS):
            return 0, -1
        if game.input_state.btn(DOWN_BUTTONS):
            return 0, 1
        if game.input_state.btn(LEFT_BUTTONS):
            return -1, 0
        if game.input_state.btn(RIGHT_BUTTONS):
            return 1, 0
        return 0, 0

    def _run_update(self, game: Any) -> None:
        """_run_update() の実装本体。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M

        if self.model.move_cooldown > 0:
            self.model.move_cooldown -= 1
            return

        # A-button cooldown: 「でる」直後やロード直後の1フレーム目に
        # 残っている A 押下を1回だけ捨てて、町メニューが暴発しないようにする。
        if self.model.has_a_cooldown:
            if game.input_state.btnp(CONFIRM_BUTTONS):
                self.model.has_a_cooldown = False
                return
            self.model.has_a_cooldown = False

        # Open menu
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.state = "menu"
            game.menu_cursor = 0
            game.menu_sub = None
            return

        player = game.player_model
        dx, dy = self._read_move_input(game)

        is_predicate_19 = dx != 0 or dy != 0
        if is_predicate_19:
            nx, ny = player.x + dx, player.y + dy
            if player.in_dungeon:
                mw, mh = M.DUNGEON_W, M.DUNGEON_H
            else:
                mw, mh = M.MAP_W, M.MAP_H

            is_predicate_17 = 0 <= nx < mw and 0 <= ny < mh
            if is_predicate_17:
                tile = self.model.get_tile(
                    nx, ny, in_dungeon=player.in_dungeon
                )
                if tile not in M.IMPASSABLE:
                    old_zone = M.get_zone(player.y, player.in_dungeon)
                    player.x = nx
                    player.y = ny
                    game.sfx.play("step")
                    self.model.move_cooldown = 4
                    self.model.walk_timer += 1
                    new_zone = M.get_zone(player.y, player.in_dungeon)
                    player.max_zone_reached = max(
                        player.max_zone_reached, new_zone
                    )
                    if new_zone != old_zone:
                        game.sfx.play("zone_change")
                    if self.model.walk_timer >= 2:
                        self.model.walk_frame = 1 - self.model.walk_frame
                        self.model.walk_timer = 0

                    # Poison tick
                    if player.poisoned:
                        game._poison_step_counter = (
                            getattr(game, "_poison_step_counter", 0) + 1
                        )
                        if game._poison_step_counter >= 4:
                            game._poison_step_counter = 0
                            player.hp = max(1, player.hp - 2)
                            game.sfx.play("poison_tick")

                    # Check events after move
                    if self._check_landmark_events(game):
                        return
                    self._check_tile_events(game, tile, nx, ny)
            elif player.in_dungeon:
                # Exit dungeon at edges
                player.in_dungeon = False
                player.x = game.world_return_x
                player.y = game.world_return_y
                game.messages.enter(
                    game.messages.dialog_lines("dungeon.glitch.exit"),
                    callback=self._build_dungeon_exit_callback(game),
                )
                return

    def _run_build_view_model(self, game: Any) -> ExploreViewModel:
        """ExploreViewModel を組み立てる。

        Args:
            game: ゲーム本体。
        Returns:
            ExploreViewModel: view 用の純粋データ。
        Postconditions:
            - self.model.cam_x / cam_y はマップ境界内にクランプされる。
        """
        player = game.player_model
        mw, mh, view_w, view_h = self._compute_dimensions(player)
        self._compute_camera(player, mw, mh, view_w, view_h)
        return self._assemble_view_model(game, player, mw, mh, view_w, view_h)

    def _compute_dimensions(self, player) -> tuple[int, int, int, int]:
        """マップ寸法とビュー寸法を返す。

        Args:
            player: プレイヤーモデル。
        Returns:
            (mw, mh, view_w, view_h): タイル数とピクセル寸法。
        Postconditions:
            - view 寸法は 256x232 固定。
        """
        import src.runtime.main_runtime as M
        if player.in_dungeon:
            return M.DUNGEON_W, M.DUNGEON_H, 256, 232
        return M.MAP_W, M.MAP_H, 256, 232

    def _assemble_view_model(
        self, game, player, mw: int, mh: int, view_w: int, view_h: int
    ) -> ExploreViewModel:
        """副作用なしの計算 helper を呼び ExploreViewModel に詰める。

        Args:
            game, player, mw, mh, view_w, view_h: 呼び出し側で確定済み。
        Returns:
            ExploreViewModel: view 用の純粋データ。
        Postconditions:
            - 副作用は内部 helper（_compute_camera 等）に閉じる。
        """
        u, v, w, h, x, y = self._compute_bltm(player, view_w, view_h)
        hxy, key = self._compute_hero_sprite(player)
        boss = self._locate_boss_marker(player, mw, mh, view_w, view_h)
        is_active = player.in_dungeon and not player.glitch_lord_defeated
        return ExploreViewModel(
            is_in_dungeon=player.in_dungeon,
            cam_x=self.model.cam_x, cam_y=self.model.cam_y,
            tm=self.model.get_current_tilemap_id(in_dungeon=player.in_dungeon),
            bltm_u=u, bltm_v=v, bltm_w=w, bltm_h=h, bltm_x=x, bltm_y=y,
            boss_marker_screen_xy=boss,
            hero_screen_xy=hxy, hero_sprite_key=key,
            landmarks=self._collect_landmarks(player),
            is_boss_marker_active=is_active,
            image_banks=game.image_banks,
        )

    def _compute_camera(
        self, player, mw: int, mh: int, view_w: int, view_h: int
    ) -> None:
        """カメラ位置 (self.model.cam_x/cam_y) を player に追従させる。

        Args:
            player: プレイヤーモデル。
            mw, mh: マップ寸法（タイル数）。
            view_w, view_h: ビュー寸法（ピクセル）。
        Postconditions:
            - self.model.cam_x / cam_y がマップ境界内にクランプされる。
        """
        self.model.cam_x = player.x * 16 - view_w // 2 + 8
        self.model.cam_y = player.y * 16 - view_h // 2 + 8
        self.model.cam_x = max(0, min(mw * 16 - view_w, self.model.cam_x))
        self.model.cam_y = max(0, min(mh * 16 - view_h, self.model.cam_y))

    def _compute_bltm(
        self, player, view_w: int, view_h: int
    ) -> tuple[int, int, int, int, int, int]:
        """bltm 引数 6 値 (u, v, w, h, x, y) を返す。

        1 ゲームタイル (16x16 px) = 2x2 cells (8x8 px)。cam_x / cam_y は
        ピクセル単位のままで bltm_u / bltm_v に渡せる。dungeon 領域は
        cell 単位で DUNGEON_TM_OFFSET_Y、ピクセルに直すと *8。

        Args:
            player: プレイヤーモデル。
            view_w, view_h: ビュー寸法。
        Returns:
            (u, v, w, h, x, y): bltm 用の整数 6 値。
        Postconditions:
            - 純粋関数（副作用なし）。
        """
        from src.shared.services.image_banks import DUNGEON_TM_OFFSET_Y
        oy_px = DUNGEON_TM_OFFSET_Y * 8 if player.in_dungeon else 0
        return self.model.cam_x, oy_px + self.model.cam_y, view_w, view_h, 0, 24

    def _compute_hero_sprite(self, player) -> tuple[tuple[int, int], str]:
        """ヒーローの画面座標とスプライトキーを返す。

        Args:
            player: プレイヤーモデル。
        Returns:
            ((sx, sy), sprite_key): 画面座標と sprite 名。
        Postconditions:
            - 純粋関数（副作用なし）。
        """
        hero_sx = player.x * 16 - self.model.cam_x
        hero_sy = player.y * 16 - self.model.cam_y + 24
        key = "hero_walk" if self.model.walk_frame == 1 else "hero_down"
        return (hero_sx, hero_sy), key

    def _collect_landmarks(self, player) -> list[ExploreLandmark]:
        """ワールドマップ上のランドマーク列を返す（dungeon 内は空）。

        Args:
            player: プレイヤーモデル。
        Returns:
            list[ExploreLandmark]: 表示すべきランドマーク列。
        Postconditions:
            - 純粋関数（副作用なし）。
        """
        if player.in_dungeon:
            return []
        landmarks: list[ExploreLandmark] = []
        for tx, ty, color, enabled in (
            (32, 9, 11, True),
            (40, 32, 2, True),
            (25, 6, 10, player.glitch_lord_defeated),
        ):
            if enabled:
                landmarks.append(ExploreLandmark(tx=tx, ty=ty, color=color))
        return landmarks

    def _locate_boss_marker(
        self, player, mw: int, mh: int, view_w: int, view_h: int
    ) -> tuple[int, int] | None:
        """dungeon 内・未撃破時のみ画面内 T_GLITCH_LORD_TRIGGER 座標を返す。

        Args:
            player: プレイヤーモデル。
            mw, mh: マップ寸法。
            view_w, view_h: ビュー寸法。
        Returns:
            (sx, sy) or None: 画面内座標、無ければ None。
        Postconditions:
            - self.model は不変（読み取りのみ）。
        """
        if not (player.in_dungeon and not player.glitch_lord_defeated):
            return None
        return self._scan_boss_trigger(mw, mh, view_w, view_h)

    def _scan_boss_trigger(
        self, mw: int, mh: int, view_w: int, view_h: int
    ) -> tuple[int, int] | None:
        """カメラ範囲を走査して T_GLITCH_LORD_TRIGGER 座標を返す。

        Args:
            mw, mh: マップ寸法。
            view_w, view_h: ビュー寸法。
        Returns:
            (sx, sy) or None: 画面内座標、無ければ None。
        Postconditions:
            - self.model は不変。最初に見つかった行で内側ループも止める。
        """
        from src.shared.constants.tile_data import T_GLITCH_LORD_TRIGGER
        tx_start = max(0, self.model.cam_x // 16)
        ty_start = max(0, self.model.cam_y // 16)
        tx_end = min(mw, (self.model.cam_x + view_w) // 16 + 2)
        ty_end = min(mh, (self.model.cam_y + view_h) // 16 + 2)
        for ty in range(ty_start, ty_end):
            for tx in range(tx_start, tx_end):
                tile = self.model.get_tile(tx, ty, in_dungeon=True)
                if tile != T_GLITCH_LORD_TRIGGER:
                    continue
                sx = tx * 16 - self.model.cam_x
                sy = ty * 16 - self.model.cam_y + 24
                if -16 < sx < 256 and 8 < sy < 256:
                    return (sx, sy)
                break
        return None

    def _check_tile_events(self, game: Any, tile, nx, ny) -> None:
        """タイル上のイベント（ダンジョン階段・町・城・洞窟・エンカウント）を処理する。

        Args:
            game: game の値。
            tile: tile の値。
            nx: nx の値。
            ny: ny の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        player = game.player_model

        is_predicate_13 = player.in_dungeon and tile == M.T_STAIR_UP
        if is_predicate_13:
            player.in_dungeon = False
            player.x = game.world_return_x
            player.y = game.world_return_y
            game.messages.enter(
                game.messages.dialog_lines("dungeon.glitch.exit"),
                callback=self._build_dungeon_exit_callback(game),
            )
            return

        is_predicate_11 = player.in_dungeon and tile == M.T_GLITCH_LORD_TRIGGER
        if is_predicate_11:
            if not player.glitch_lord_defeated:
                game.battle_scene.start(
                    M.GLITCH_LORD_DATA, is_glitch_lord=True
                )
            return

        if tile == M.T_TOWN:
            from src.shared.services.game_state import TownContext
            pos = (nx, ny)
            game.town_model.menu_pos = pos
            game.town_model.menu_cursor = 0
            game.current_town = TownContext(
                index=M.TOWN_INDEX_BY_POS.get(pos, 0),
                pos=pos,
            )
            game.state = "town_menu"
            return

        if tile == M.T_CASTLE:
            is_predicate_9 = (
                game.player_model.glitch_lord_defeated
                and (nx, ny) == (25, 6)
            )
            if is_predicate_9:
                game.professor_scene.enter_intro()
                return
            scene_name = M.TOWN_DIALOG_SCENES.get((nx, ny))
            if scene_name is None:
                lines = ["..."]
            else:
                lines = game.messages.dialog_lines(
                    scene_name,
                    ProfessorPhase=game.professor_scene.phase(),
                )
            game.messages.show(lines)
            game.state = "town"
            return

        is_predicate_7 = tile == M.T_CAVE and (not player.in_dungeon)
        if is_predicate_7:
            if not player.towerNoiseCleared:
                game.messages.enter(
                    game.messages.dialog_lines("cave.blocked")
                )
                return
            if not getattr(game, "_cave_unblock_shown", False):
                game._cave_unblock_shown = True
                game.messages.enter(
                    game.messages.dialog_lines("cave.unblocked")
                )
                return
            game.sfx.play("dungeon_in")
            game.world_return_x = nx
            game.world_return_y = ny
            player.in_dungeon = True
            sx, sy = game.dungeon_spawn
            player.x = sx
            player.y = sy
            game.messages.enter(
                game.messages.dialog_lines("dungeon.glitch.enter")
            )
            return

        # Random encounter
        if not game.debug_mode:
            is_predicate_5 = player.in_dungeon and player.glitch_lord_defeated
            if is_predicate_5:
                return
            rate = M.ENCOUNTER_RATES.get(tile, 0)
            is_predicate_3 = rate > 0 and random.random() < rate
            if is_predicate_3:
                zone = M.get_zone(player.y, player.in_dungeon)
                enemies = M.ZONE_ENEMIES.get(zone, M.ZONE_ENEMIES[0])
                enemy_template = random.choice(enemies)
                game.battle_scene.start(enemy_template, is_glitch_lord=False)

    def _check_landmark_events(self, game: Any) -> bool:
        """ランドマークイベントを判定し、発生したら True を返す。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.player_model.in_dungeon:
            return False

        landmark = find_landmark_at(game.player_model.x, game.player_model.y)
        if landmark is None:
            return False

        player = game.player_model
        scene_name = self._resolve_landmark_scene(game, landmark)
        if scene_name is None:
            return False

        if landmark.flag_name == "landmarkTreeSeen":
            if not player.landmarkTreeSeen:
                player.landmarkTreeSeen = True
                player.treeAsked = True
        elif landmark.flag_name == "landmarkTowerSeen":
            if not player.landmarkTowerSeen:
                player.landmarkTowerSeen = True

        if scene_name == "landmark.tower.quest":
            game.messages.enter(
                game.messages.dialog_lines(scene_name),
                callback=game.battle_scene.start_noise_guardian,
            )
            return True

        is_predicate_1 = (
            landmark.epilogue_flag
            and scene_name == landmark.epilogue_scene
        )
        if is_predicate_1:
            setattr(player, landmark.epilogue_flag, True)

        game.messages.enter(game.messages.dialog_lines(scene_name))
        return True

    def _resolve_landmark_scene(self, game: Any, landmark):
        """洞窟ミッションのフラグに応じてランドマークのシーンを決定する。

        Args:
            game: game の値。
            landmark: landmark の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        player = game.player_model
        cleared = player.towerNoiseCleared
        tree_asked = player.treeAsked

        if landmark.flag_name == "landmarkTreeSeen":
            if not player.landmarkTreeSeen:
                return "landmark.tree.first"
            if cleared:
                if not getattr(game, "_tree_cleared_shown", False):
                    game._tree_cleared_shown = True
                    return "landmark.tree.cleared"
                return random.choice([
                    "landmark.tree.repeat",
                    "landmark.tree.repeat_02",
                    "landmark.tree.repeat_03",
                ])
            return "landmark.tree.waiting"

        if landmark.flag_name == "landmarkTowerSeen":
            if not player.landmarkTowerSeen:
                return "landmark.tower.first"
            if cleared:
                is_epilogue_ready = (
                    player.glitch_lord_defeated
                    and landmark.epilogue_scene
                    and not getattr(player, landmark.epilogue_flag, False)
                )
                if is_epilogue_ready:
                    return landmark.epilogue_scene
                return random.choice([
                    "landmark.tower.repeat",
                    "landmark.tower.repeat_02",
                    "landmark.tower.repeat_03",
                ])
            if tree_asked:
                return "landmark.tower.quest"
            return "landmark.tower.repeat"

        return None

    def _build_dungeon_exit_callback(self, game: Any):
        """ダンジョン脱出時のコールバック（ボス撃破済みならエンディングへ）。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.player_model.glitch_lord_defeated:
            return game.ending_scene.enter
        return None
