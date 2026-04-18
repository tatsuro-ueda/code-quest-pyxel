from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_preview_module():
    source = (ROOT / "main_preview.py").read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType("main_preview_for_glitch_lord_trigger_test")
    module.__file__ = str((ROOT / "main_preview.py").resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


class PreviewGlitchLordTriggerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preview = load_preview_module()

    def make_stair_exit_game(self, *, glitch_lord_defeated=True):
        game = self.preview.Game.__new__(self.preview.Game)
        game.player = {
            "in_dungeon": True,
            "glitch_lord_defeated": glitch_lord_defeated,
            "x": 3,
            "y": 4,
        }
        game.world_return_x = 40
        game.world_return_y = 32
        game.dungeon_map = [[self.preview.T_FLOOR]]
        game._dialog_lines = MagicMock(return_value=["dungeon.glitch.exit"])
        game._enter_message = MagicMock()
        game._enter_ending = MagicMock()
        return game

    def make_edge_exit_game(self, *, glitch_lord_defeated=True):
        game = self.preview.Game.__new__(self.preview.Game)
        game.player = {
            "in_dungeon": True,
            "glitch_lord_defeated": glitch_lord_defeated,
            "x": 0,
            "y": 0,
            "max_zone_reached": 0,
        }
        game.dungeon_map = [[self.preview.T_FLOOR]]
        game.world_map = [[self.preview.T_GRASS]]
        game.world_return_x = 40
        game.world_return_y = 32
        game.move_cooldown = 0
        game._a_cooldown = False
        game.walk_timer = 0
        game.walk_frame = 0
        game.sfx = MagicMock()
        game._check_landmark_events = MagicMock(return_value=False)
        game._dialog_lines = MagicMock(return_value=["dungeon.glitch.exit"])
        game._enter_message = MagicMock()
        game._enter_ending = MagicMock()
        game._btnp = MagicMock(return_value=False)
        game._btn = MagicMock(
            side_effect=lambda buttons: buttons == self.preview.LEFT_BUTTONS
        )
        return game

    def test_check_tile_events_enters_glitch_lord_intro_on_trigger(self):
        game = self.preview.Game.__new__(self.preview.Game)
        game.player = {"in_dungeon": True, "glitch_lord_defeated": False}
        game._enter_glitch_lord_intro = MagicMock()
        game._start_battle = MagicMock()

        self.preview.Game._check_tile_events(
            game,
            self.preview.T_GLITCH_LORD_TRIGGER,
            7,
            8,
        )

        game._enter_glitch_lord_intro.assert_called_once_with()
        game._start_battle.assert_not_called()

    def test_enter_glitch_lord_intro_uses_fullscreen_dialog_with_battle_callback(self):
        game = self.preview.Game.__new__(self.preview.Game)
        game._dialog_lines = MagicMock(return_value=["line1", "line2"])
        game._enter_fullscreen_dialog = MagicMock()
        game._start_glitch_lord_battle = MagicMock()

        self.preview.Game._enter_glitch_lord_intro(game)

        game._dialog_lines.assert_called_once_with("boss.glitch.prebattle_01")
        game._enter_fullscreen_dialog.assert_called_once()
        args, kwargs = game._enter_fullscreen_dialog.call_args
        self.assertEqual(args[0], ["line1", "line2"])
        self.assertEqual(kwargs["on_complete"], game._start_glitch_lord_battle)

    def test_update_fullscreen_dialog_runs_completion_callback_after_last_page(self):
        game = self.preview.Game.__new__(self.preview.Game)
        on_complete = MagicMock()
        game.fullscreen_dialog_lines = ["line1"]
        game.fullscreen_dialog_idx = 0
        game.fullscreen_dialog_on_complete = on_complete
        game._btnp = MagicMock(
            side_effect=lambda buttons: buttons == self.preview.CONFIRM_BUTTONS
        )

        self.preview.Game.update_fullscreen_dialog(game)

        on_complete.assert_called_once_with()

    def test_stair_exit_after_glitch_lord_defeat_routes_message_to_ending(self):
        game = self.make_stair_exit_game()

        self.preview.Game._check_tile_events(game, self.preview.T_STAIR_UP, 7, 8)

        game._enter_message.assert_called_once_with(
            ["dungeon.glitch.exit"],
            callback=game._enter_ending,
        )

    def test_edge_exit_after_glitch_lord_defeat_routes_message_to_ending(self):
        game = self.make_edge_exit_game()

        self.preview.Game.update_map(game)

        game._enter_message.assert_called_once_with(
            ["dungeon.glitch.exit"],
            callback=game._enter_ending,
        )

    def test_stair_exit_before_glitch_lord_defeat_returns_without_ending(self):
        game = self.make_stair_exit_game(glitch_lord_defeated=False)

        self.preview.Game._check_tile_events(game, self.preview.T_STAIR_UP, 7, 8)

        game._enter_message.assert_called_once_with(
            ["dungeon.glitch.exit"],
            callback=None,
        )

    def test_edge_exit_before_glitch_lord_defeat_returns_without_ending(self):
        game = self.make_edge_exit_game(glitch_lord_defeated=False)

        self.preview.Game.update_map(game)

        game._enter_message.assert_called_once_with(
            ["dungeon.glitch.exit"],
            callback=None,
        )
