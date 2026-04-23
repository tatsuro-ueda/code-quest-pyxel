from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock
from src.scenes.explore.scene import ExploreScene
from src.scenes.ending.scene import EndingScene
from src.scenes.battle.scene import BattleScene
from src.shared.services.message_display import MessageDisplay


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_main_module():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType("main_for_dungeon_glitch_lord_trigger_test")
    module.__file__ = str((ROOT / "main.py").resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


class DungeonGlitchLordTriggerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def make_game(self):
        game = self.main.Game.__new__(self.main.Game)
        game.explore_scene = ExploreScene(game=game)
        game.ending_scene = EndingScene(game=game)
        game.battle_scene = BattleScene(game=game)
        game.battle_scene.start = MagicMock()
        game.player = {"in_dungeon": True, "glitch_lord_defeated": False}
        return game

    def make_draw_game(self):
        game = self.main.Game.__new__(self.main.Game)
        game.explore_scene = ExploreScene(game=game)
        game.ending_scene = EndingScene(game=game)
        game.player = {
            "in_dungeon": True,
            "glitch_lord_defeated": False,
            "x": 0,
            "y": 0,
        }
        game.dungeon_map = [
            [self.main.T_FLOOR, self.main.T_FLOOR, self.main.T_FLOOR],
            [self.main.T_FLOOR, self.main.T_GLITCH_LORD_TRIGGER, self.main.T_FLOOR],
            [self.main.T_FLOOR, self.main.T_FLOOR, self.main.T_FLOOR],
        ]
        game.world_map = [[self.main.T_GRASS]]
        game.path_variant_bank = {}
        game.shore_variant_bank = {}
        game.tile_bank_water2 = None
        game.tile_bank = {
            self.main.T_FLOOR: (0, 0),
            self.main.T_GLITCH_LORD_TRIGGER: (16, 0),
            self.main.T_GRASS: (32, 0),
            self.main.T_WATER: (48, 0),
            self.main.T_PATH: (64, 0),
        }
        game.sprite_bank = {
            "hero_down": (0, 0),
            "hero_walk": (16, 0),
        }
        game.explore_scene.model.walk_frame = 0
        game.explore_scene._draw_landmark_highlights = MagicMock()
        return game

    def make_stair_exit_game(self, *, glitch_lord_defeated=True):
        game = self.main.Game.__new__(self.main.Game)
        game.messages = MessageDisplay(game=game)
        game.messages.dialog_lines = MagicMock(return_value=["dungeon.glitch.exit"])
        game.messages.enter = MagicMock()
        game.explore_scene = ExploreScene(game=game)
        game.ending_scene = EndingScene(game=game)
        game.player = {
            "in_dungeon": True,
            "glitch_lord_defeated": glitch_lord_defeated,
            "x": 3,
            "y": 4,
        }
        game.world_return_x = 40
        game.world_return_y = 32
        game.dungeon_map = [[self.main.T_FLOOR]]
        game.ending_scene.enter = MagicMock()
        return game

    def make_edge_exit_game(self, *, glitch_lord_defeated=True):
        game = self.main.Game.__new__(self.main.Game)
        game.messages = MessageDisplay(game=game)
        game.messages.dialog_lines = MagicMock(return_value=["dungeon.glitch.exit"])
        game.messages.enter = MagicMock()
        game.explore_scene = ExploreScene(game=game)
        game.ending_scene = EndingScene(game=game)
        game.player = {
            "in_dungeon": True,
            "glitch_lord_defeated": glitch_lord_defeated,
            "x": 0,
            "y": 0,
            "max_zone_reached": 0,
        }
        game.dungeon_map = [[self.main.T_FLOOR]]
        game.world_map = [[self.main.T_GRASS]]
        game.world_return_x = 40
        game.world_return_y = 32
        game.explore_scene.model.move_cooldown = 0
        game.explore_scene.model.a_cooldown = False
        game.explore_scene.model.walk_timer = 0
        game.explore_scene.model.walk_frame = 0
        game.sfx = MagicMock()
        game.explore_scene._check_landmark_events = MagicMock(return_value=False)
        game.ending_scene.enter = MagicMock()
        game._btnp = MagicMock(return_value=False)
        game._btn = MagicMock(
            side_effect=lambda buttons: buttons == self.main.LEFT_BUTTONS
        )
        return game

    def test_generate_dungeon_places_single_glitch_lord_trigger_in_last_room(self):
        grid, rooms = self.main.generate_dungeon(seed=99)

        trigger_tiles = [
            (x, y)
            for y, row in enumerate(grid)
            for x, tile in enumerate(row)
            if tile == self.main.T_GLITCH_LORD_TRIGGER
        ]

        self.assertEqual(len(trigger_tiles), 1)
        bx, by = trigger_tiles[0]
        rx, ry, rw, rh = rooms[-1]
        self.assertTrue(rx <= bx < rx + rw)
        self.assertTrue(ry <= by < ry + rh)

        sx = rooms[0][0] + 1
        sy = rooms[0][1] + 1
        self.assertNotEqual((bx, by), (sx, sy))

    def test_check_tile_events_starts_glitch_lord_battle_on_trigger(self):
        game = self.make_game()

        game.explore_scene._check_tile_events(self.main.T_GLITCH_LORD_TRIGGER, 7, 8)

        game.battle_scene.start.assert_called_once_with(
            self.main.GLITCH_LORD_DATA,
            is_glitch_lord=True,
        )

    def test_check_tile_events_ignores_trigger_after_glitch_lord_defeat(self):
        game = self.make_game()
        game.player["glitch_lord_defeated"] = True

        game.explore_scene._check_tile_events(self.main.T_GLITCH_LORD_TRIGGER, 7, 8)

        game.battle_scene.start.assert_not_called()

    def test_stair_exit_after_glitch_lord_defeat_routes_message_to_ending(self):
        game = self.make_stair_exit_game()

        game.explore_scene._check_tile_events(self.main.T_STAIR_UP, 7, 8)

        game.messages.enter.assert_called_once_with(
            ["dungeon.glitch.exit"],
            callback=game.ending_scene.enter,
        )
        self.assertFalse(game.player["in_dungeon"])
        self.assertEqual((game.player["x"], game.player["y"]), (40, 32))

    def test_edge_exit_after_glitch_lord_defeat_routes_message_to_ending(self):
        game = self.make_edge_exit_game()

        game.explore_scene.update()

        game.messages.enter.assert_called_once_with(
            ["dungeon.glitch.exit"],
            callback=game.ending_scene.enter,
        )
        self.assertFalse(game.player["in_dungeon"])
        self.assertEqual((game.player["x"], game.player["y"]), (40, 32))

    def test_stair_exit_before_glitch_lord_defeat_returns_without_ending(self):
        game = self.make_stair_exit_game(glitch_lord_defeated=False)

        game.explore_scene._check_tile_events(self.main.T_STAIR_UP, 7, 8)

        game.messages.enter.assert_called_once_with(
            ["dungeon.glitch.exit"],
            callback=None,
        )

    def test_edge_exit_before_glitch_lord_defeat_returns_without_ending(self):
        game = self.make_edge_exit_game(glitch_lord_defeated=False)

        game.explore_scene.update()

        game.messages.enter.assert_called_once_with(
            ["dungeon.glitch.exit"],
            callback=None,
        )

    def test_draw_map_draws_glitch_lord_marker_before_defeat(self):
        game = self.make_draw_game()
        blt_calls = []
        self.main.pyxel.frame_count = 0
        self.main.pyxel.blt = lambda *args: blt_calls.append(args)

        game.explore_scene.draw()

        sprite_draws = [call for call in blt_calls if call[2] == 1]
        self.assertEqual(len(sprite_draws), 2)

    def test_draw_map_hides_glitch_lord_marker_after_defeat(self):
        game = self.make_draw_game()
        game.player["glitch_lord_defeated"] = True
        blt_calls = []
        self.main.pyxel.frame_count = 0
        self.main.pyxel.blt = lambda *args: blt_calls.append(args)

        game.explore_scene.draw()

        sprite_draws = [call for call in blt_calls if call[2] == 1]
        self.assertEqual(len(sprite_draws), 1)


if __name__ == "__main__":
    unittest.main()
