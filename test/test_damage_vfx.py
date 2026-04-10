"""Tests for J18 Damage VFX (screen flash on damage).

pyxel をモックして main.py をインポートし、VFX関連の定数・メソッドをテストする。
"""

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _setup_pyxel_mock():
    """pyxel モジュールをモックして main.py をインポート可能にする。"""
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

try:
    import main as M
    IMPORTED = True
except Exception as e:
    print(f"Warning: main.py import failed: {e}")
    IMPORTED = False


@unittest.skipUnless(IMPORTED, "main.py import failed")
class TestVfxFlashConstant(unittest.TestCase):
    """VFX_FLASH 定数が正しく定義されている。"""

    def test_flash_white_exists(self):
        self.assertIn("flash_white", M.VFX_FLASH)
        self.assertEqual(M.VFX_FLASH["flash_white"]["color"], 7)
        self.assertGreater(M.VFX_FLASH["flash_white"]["duration"], 0)

    def test_flash_red_exists(self):
        self.assertIn("flash_red", M.VFX_FLASH)
        self.assertEqual(M.VFX_FLASH["flash_red"]["color"], 8)
        self.assertGreater(M.VFX_FLASH["flash_red"]["duration"], 0)


@unittest.skipUnless(IMPORTED, "main.py import failed")
class TestStartVfx(unittest.TestCase):
    """_start_vfx がタイマーとタイプを正しく設定する。"""

    def _make_game(self):
        g = object.__new__(M.Game)
        g.vfx_timer = 0
        g.vfx_type = ""
        return g

    def test_start_flash_white(self):
        g = self._make_game()
        g._start_vfx("flash_white")
        self.assertEqual(g.vfx_type, "flash_white")
        self.assertEqual(g.vfx_timer, M.VFX_FLASH["flash_white"]["duration"])

    def test_start_flash_red(self):
        g = self._make_game()
        g._start_vfx("flash_red")
        self.assertEqual(g.vfx_type, "flash_red")
        self.assertEqual(g.vfx_timer, M.VFX_FLASH["flash_red"]["duration"])

    def test_start_unknown_type_does_nothing(self):
        g = self._make_game()
        g._start_vfx("nonexistent")
        self.assertEqual(g.vfx_timer, 0)
        self.assertEqual(g.vfx_type, "")


@unittest.skipUnless(IMPORTED, "main.py import failed")
class TestDrawVfxOverlay(unittest.TestCase):
    """_draw_vfx_overlay が正しくオーバーレイを描画する。"""

    def _make_game(self):
        g = object.__new__(M.Game)
        g.vfx_timer = 0
        g.vfx_type = ""
        return g

    def test_no_overlay_when_timer_zero(self):
        import pyxel
        pyxel.rect.reset_mock()
        g = self._make_game()
        g._draw_vfx_overlay()
        pyxel.rect.assert_not_called()

    def test_overlay_drawn_on_even_frame(self):
        import pyxel
        pyxel.rect.reset_mock()
        g = self._make_game()
        g.vfx_timer = 4
        g.vfx_type = "flash_white"
        g._draw_vfx_overlay()
        pyxel.rect.assert_called_once_with(0, 0, 256, 256, 7)

    def test_no_overlay_on_odd_frame(self):
        import pyxel
        pyxel.rect.reset_mock()
        g = self._make_game()
        g.vfx_timer = 3
        g.vfx_type = "flash_white"
        g._draw_vfx_overlay()
        pyxel.rect.assert_not_called()

    def test_red_flash_uses_color_8(self):
        import pyxel
        pyxel.rect.reset_mock()
        g = self._make_game()
        g.vfx_timer = 2
        g.vfx_type = "flash_red"
        g._draw_vfx_overlay()
        pyxel.rect.assert_called_once_with(0, 0, 256, 256, 8)


if __name__ == "__main__":
    unittest.main()
