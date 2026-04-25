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

    model: ExploreModel

    def change_mode(self, mode: str) -> None:
        """探索モードを指定値（map / menu など）に差し替える。"""
        self.model.mode = mode

    def update(self, game: Any) -> None:
        """プレイヤー移動とタイルイベント・ランドマーク判定。"""
        import src.runtime.main_runtime as M

        if self.model.move_cooldown > 0:
            self.model.move_cooldown -= 1
            return

        # A-button cooldown: 「でる」直後やロード直後の1フレーム目に
        # 残っている A 押下を1回だけ捨てて、町メニューが暴発しないようにする。
        if self.model.a_cooldown:
            if game.input_state.btnp(CONFIRM_BUTTONS):
                self.model.a_cooldown = False
                return
            self.model.a_cooldown = False

        # Open menu
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.state = "menu"
            game.menu_cursor = 0
            game.menu_sub = None
            return

        p = game.player_model
        dx, dy = 0, 0
        if game.input_state.btn(UP_BUTTONS): dy = -1
        elif game.input_state.btn(DOWN_BUTTONS): dy = 1
        elif game.input_state.btn(LEFT_BUTTONS): dx = -1
        elif game.input_state.btn(RIGHT_BUTTONS): dx = 1

        if dx != 0 or dy != 0:
            nx, ny = p.x + dx, p.y + dy
            current_map = game.dungeon_map if p.in_dungeon else game.world_map
            mw = len(current_map[0]); mh = len(current_map)

            if 0 <= nx < mw and 0 <= ny < mh:
                tile = current_map[ny][nx]
                if tile not in M.IMPASSABLE:
                    old_zone = M.get_zone(p.y, p.in_dungeon)
                    p.x = nx; p.y = ny
                    game.sfx.play("step")
                    self.model.move_cooldown = 4
                    self.model.walk_timer += 1
                    new_zone = M.get_zone(p.y, p.in_dungeon)
                    p.max_zone_reached = max(p.max_zone_reached, new_zone)
                    if new_zone != old_zone:
                        game.sfx.play("zone_change")
                    if self.model.walk_timer >= 2:
                        self.model.walk_frame = 1 - self.model.walk_frame
                        self.model.walk_timer = 0

                    # Poison tick
                    if p.poisoned:
                        game._poison_step_counter = getattr(game, "_poison_step_counter", 0) + 1
                        if game._poison_step_counter >= 4:
                            game._poison_step_counter = 0
                            p.hp = max(1, p.hp - 2)
                            game.sfx.play("poison_tick")

                    # Check events after move
                    if self._check_landmark_events(game):
                        return
                    self._check_tile_events(game, tile, nx, ny)
            elif p.in_dungeon:
                # Exit dungeon at edges
                p.in_dungeon = False
                p.x = game.world_return_x
                p.y = game.world_return_y
                game.dungeon_map = None
                game.messages.enter(
                    game.messages.dialog_lines("dungeon.glitch.exit"),
                    callback=self._dungeon_exit_callback(game),
                )
                return

    def _check_tile_events(self, game: Any, tile, nx, ny) -> None:
        """タイル上のイベント（ダンジョン階段・町・城・洞窟・エンカウント）を処理する。"""
        import src.runtime.main_runtime as M
        p = game.player_model

        if p.in_dungeon and tile == M.T_STAIR_UP:
            p.in_dungeon = False
            p.x = game.world_return_x
            p.y = game.world_return_y
            game.dungeon_map = None
            game.messages.enter(
                game.messages.dialog_lines("dungeon.glitch.exit"),
                callback=self._dungeon_exit_callback(game),
            )
            return

        if p.in_dungeon and tile == M.T_GLITCH_LORD_TRIGGER:
            if not p.glitch_lord_defeated:
                game.battle_scene.start(M.GLITCH_LORD_DATA, is_glitch_lord=True)
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
            if game.player_model.glitch_lord_defeated and (nx, ny) == (25, 6):
                game.professor_scene.enter_intro()
                return
            scene_name = M.TOWN_DIALOG_SCENES.get((nx, ny))
            if scene_name is None:
                lines = ["..."]
            else:
                lines = game.messages.dialog_lines(scene_name, ProfessorPhase=game.professor_scene.phase())
            game.messages.show(lines)
            game.state = "town"
            return

        if tile == M.T_CAVE and not p.in_dungeon:
            if not p.towerNoiseCleared:
                game.messages.enter(game.messages.dialog_lines("cave.blocked"))
                return
            if not getattr(game, "_cave_unblock_shown", False):
                game._cave_unblock_shown = True
                game.messages.enter(game.messages.dialog_lines("cave.unblocked"))
                return
            game.sfx.play("dungeon_in")
            game.world_return_x = nx
            game.world_return_y = ny
            game.dungeon_map = [row[:] for row in game.dungeon_template]
            game.dungeon_rooms = game.dungeon_template_rooms
            p.in_dungeon = True
            sx, sy = game.dungeon_spawn
            p.x = sx
            p.y = sy
            game.messages.enter(game.messages.dialog_lines("dungeon.glitch.enter"))
            return

        # Random encounter
        if not game.debug_mode:
            if p.in_dungeon and p.glitch_lord_defeated:
                return
            rate = M.ENCOUNTER_RATES.get(tile, 0)
            if rate > 0 and random.random() < rate:
                zone = M.get_zone(p.y, p.in_dungeon)
                enemies = M.ZONE_ENEMIES.get(zone, M.ZONE_ENEMIES[0])
                enemy_template = random.choice(enemies)
                game.battle_scene.start(enemy_template, is_glitch_lord=False)

    def _check_landmark_events(self, game: Any) -> bool:
        """ランドマークイベントを判定し、発生したら True を返す。"""
        if game.player_model.in_dungeon:
            return False

        landmark = find_landmark_at(game.player_model.x, game.player_model.y)
        if landmark is None:
            return False

        p = game.player_model
        scene_name = self._resolve_landmark_scene(game, landmark)
        if scene_name is None:
            return False

        if landmark.flag_name == "landmarkTreeSeen":
            if not p.landmarkTreeSeen:
                p.landmarkTreeSeen = True
                p.treeAsked = True
        elif landmark.flag_name == "landmarkTowerSeen":
            if not p.landmarkTowerSeen:
                p.landmarkTowerSeen = True

        if scene_name == "landmark.tower.quest":
            game.messages.enter(
                game.messages.dialog_lines(scene_name),
                callback=game.battle_scene.start_noise_guardian,
            )
            return True

        if landmark.epilogue_flag and scene_name == landmark.epilogue_scene:
            setattr(p, landmark.epilogue_flag, True)

        game.messages.enter(game.messages.dialog_lines(scene_name))
        return True

    def _resolve_landmark_scene(self, game: Any, landmark):
        """洞窟ミッションのフラグに応じてランドマークのシーンを決定する。"""
        p = game.player_model
        cleared = p.towerNoiseCleared
        tree_asked = p.treeAsked

        if landmark.flag_name == "landmarkTreeSeen":
            if not p.landmarkTreeSeen:
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
            if not p.landmarkTowerSeen:
                return "landmark.tower.first"
            if cleared:
                if (
                    p.glitch_lord_defeated
                    and landmark.epilogue_scene
                    and not getattr(p, landmark.epilogue_flag, False)
                ):
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

    def _dungeon_exit_callback(self, game: Any):
        """ダンジョン脱出時のコールバック（ボス撃破済みならエンディングへ）。"""
        if game.player_model.glitch_lord_defeated:
            return game.ending_scene.enter
        return None

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
