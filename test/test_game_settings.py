from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _setup_pyxel_mock():
    if "pyxel" in sys.modules:
        return
    mock_pyxel = types.ModuleType("pyxel")
    mock_pyxel.init = MagicMock()
    mock_pyxel.run = MagicMock()
    mock_pyxel.load = MagicMock()
    mock_pyxel.quit = MagicMock()
    mock_pyxel.images = [MagicMock() for _ in range(4)]
    mock_tilemap = MagicMock()
    mock_tilemap.pget = MagicMock(return_value=(0, 0))
    mock_pyxel.tilemaps = [mock_tilemap for _ in range(8)]
    mock_pyxel.sounds = [MagicMock() for _ in range(64)]
    mock_pyxel.musics = [MagicMock() for _ in range(8)]
    mock_pyxel.Font = MagicMock()
    mock_pyxel.KEY_RETURN = 0
    mock_pyxel.KEY_SPACE = 0
    mock_pyxel.KEY_UP = 0
    mock_pyxel.KEY_DOWN = 0
    mock_pyxel.KEY_LEFT = 0
    mock_pyxel.KEY_RIGHT = 0
    mock_pyxel.KEY_ESCAPE = 0
    mock_pyxel.KEY_BACKSPACE = 0
    mock_pyxel.KEY_X = 0
    mock_pyxel.KEY_Z = 0
    mock_pyxel.KEY_S = 0
    mock_pyxel.KEY_D = 0
    mock_pyxel.KEY_W = 0
    mock_pyxel.KEY_A = 0
    mock_pyxel.KEY_M = 0
    mock_pyxel.KEY_Q = 0
    mock_pyxel.GAMEPAD1_BUTTON_A = 0
    mock_pyxel.GAMEPAD1_BUTTON_B = 0
    mock_pyxel.GAMEPAD1_BUTTON_X = 0
    mock_pyxel.GAMEPAD1_BUTTON_DPAD_UP = 0
    mock_pyxel.GAMEPAD1_BUTTON_DPAD_DOWN = 0
    mock_pyxel.GAMEPAD1_BUTTON_DPAD_LEFT = 0
    mock_pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT = 0
    mock_pyxel.GAMEPAD1_BUTTON_START = 0
    mock_pyxel.btn = MagicMock(return_value=False)
    mock_pyxel.btnp = MagicMock(return_value=False)
    mock_pyxel.mouse_x = 0
    mock_pyxel.mouse_y = 0
    mock_pyxel.frame_count = 0
    mock_pyxel.cls = MagicMock()
    mock_pyxel.rect = MagicMock()
    mock_pyxel.rectb = MagicMock()
    mock_pyxel.text = MagicMock()
    mock_pyxel.blt = MagicMock()
    mock_pyxel.line = MagicMock()
    mock_pyxel.pset = MagicMock()
    mock_pyxel.circ = MagicMock()
    mock_pyxel.play = MagicMock()
    mock_pyxel.stop = MagicMock()
    mock_pyxel.playm = MagicMock()
    mock_pyxel.pal = MagicMock()
    mock_pyxel.clip = MagicMock()
    mock_pyxel.FONT_SIZE = 8
    mock_pyxel.width = 256
    mock_pyxel.height = 256
    mock_channel = MagicMock()
    mock_pyxel.channels = [mock_channel for _ in range(8)]
    sys.modules["pyxel"] = mock_pyxel


_setup_pyxel_mock()

import main as M  # noqa: E402


class GameSettingsTest(unittest.TestCase):
    def _make_game(self):
        g = object.__new__(M.Game)
        g.player = M.create_initial_player()
        g.has_jp_font = True
        g.sfx = MagicMock()
        g.audio = MagicMock()
        g.state = "title"
        g.title_cursor = 0
        g.settings_cursor = 0
        g.settings_origin = "title"
        return g

    def test_title_settings_item_opens_settings(self):
        g = self._make_game()
        g.title_cursor = 2
        g._has_save = False
        g._btnp = MagicMock(
            side_effect=lambda buttons: buttons in (M.CONFIRM_BUTTONS, M.TITLE_START_BUTTONS)
        )

        g.update_title()

        self.assertEqual(g.state, "settings")
        self.assertEqual(g.settings_origin, "title")

    def test_settings_toggle_updates_audio_flags(self):
        g = self._make_game()
        g.state = "settings"
        g.settings_cursor = 1
        g._btnp = MagicMock(side_effect=lambda buttons: buttons == M.CONFIRM_BUTTONS)

        g.update_settings()

        self.assertFalse(g.player["bgm_enabled"])
        g.audio.set_enabled.assert_called_once_with(False)

    def test_settings_toggle_all_updates_all_flags(self):
        g = self._make_game()
        g.state = "settings"
        g.settings_cursor = 0
        g._btnp = MagicMock(side_effect=lambda buttons: buttons == M.CONFIRM_BUTTONS)

        g.update_settings()

        self.assertFalse(g.player["bgm_enabled"])
        self.assertFalse(g.player["sfx_enabled"])
        self.assertFalse(g.player["vfx_enabled"])

    def test_settings_cancel_returns_to_origin(self):
        g = self._make_game()
        g.state = "settings"
        g.settings_origin = "menu"
        g._btnp = MagicMock(side_effect=lambda buttons: buttons == M.CANCEL_BUTTONS)

        g.update_settings()

        self.assertEqual(g.state, "menu")

    def test_title_settings_keeps_title_bgm_scene(self):
        g = self._make_game()
        g.state = "settings"
        g.settings_origin = "title"
        g.battle_enemy = None
        g.battle_enemy_hp = 0
        g.battle_is_glitch_lord = False
        g.battle_phase = "menu"

        g._sync_audio()

        g.audio.play_scene.assert_called_once_with("title")
