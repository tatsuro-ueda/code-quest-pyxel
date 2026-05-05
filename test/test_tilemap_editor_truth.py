from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from _helpers.imagebank_stub import (  # noqa: E402
    FakeTilemap as _FakeTilemap,
    snapshot_tilemaps,
    restore_tilemaps,
)


def _install_pyxel_stub() -> None:
    if "pyxel" in sys.modules:
        return
    stub = types.ModuleType("pyxel")
    stub.init = lambda *args, **kwargs: None
    stub.run = lambda *args, **kwargs: None
    stub.load = lambda *args, **kwargs: None
    stub.save = lambda *args, **kwargs: None
    stub.quit = lambda *args, **kwargs: None
    stub.images = [types.SimpleNamespace(pset=lambda *args, **kwargs: None, pget=lambda *args, **kwargs: 0) for _ in range(4)]
    stub.tilemaps = [types.SimpleNamespace(pset=lambda *args, **kwargs: None, pget=lambda *args, **kwargs: (0, 0)) for _ in range(8)]
    stub.sounds = [types.SimpleNamespace(set=lambda *args, **kwargs: None) for _ in range(64)]
    stub.musics = [types.SimpleNamespace(set=lambda *args, **kwargs: None) for _ in range(8)]
    stub.channels = [types.SimpleNamespace(gain=0.125) for _ in range(8)]
    stub.Font = lambda *args, **kwargs: None
    stub.btn = lambda *args, **kwargs: False
    stub.btnp = lambda *args, **kwargs: False
    stub.mouse_x = 0
    stub.mouse_y = 0
    stub.frame_count = 0
    stub.cls = lambda *args, **kwargs: None
    stub.rect = lambda *args, **kwargs: None
    stub.rectb = lambda *args, **kwargs: None
    stub.text = lambda *args, **kwargs: None
    stub.blt = lambda *args, **kwargs: None
    stub.line = lambda *args, **kwargs: None
    stub.pset = lambda *args, **kwargs: None
    stub.circ = lambda *args, **kwargs: None
    stub.play = lambda *args, **kwargs: None
    stub.stop = lambda *args, **kwargs: None
    stub.playm = lambda *args, **kwargs: None
    stub.pal = lambda *args, **kwargs: None
    stub.clip = lambda *args, **kwargs: None
    stub.width = 256
    stub.height = 256
    for name in (
        "KEY_RETURN", "KEY_SPACE", "KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT",
        "KEY_ESCAPE", "KEY_BACKSPACE", "KEY_X", "KEY_Z", "KEY_S", "KEY_D",
        "KEY_W", "KEY_A", "KEY_M", "KEY_Q",
        "GAMEPAD1_BUTTON_A", "GAMEPAD1_BUTTON_B", "GAMEPAD1_BUTTON_X",
        "GAMEPAD1_BUTTON_DPAD_UP", "GAMEPAD1_BUTTON_DPAD_DOWN",
        "GAMEPAD1_BUTTON_DPAD_LEFT", "GAMEPAD1_BUTTON_DPAD_RIGHT",
        "GAMEPAD1_BUTTON_START",
    ):
        setattr(stub, name, 0)
    sys.modules["pyxel"] = stub


def load_main_module():
    _install_pyxel_stub()
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType("main_for_tilemap_editor_truth_test")
    module.__file__ = str((ROOT / "main.py").resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


class TilemapEditorTruthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def setUp(self):
        self._original_tilemaps = snapshot_tilemaps()

    def tearDown(self):
        restore_tilemaps(self._original_tilemaps)

    def make_game(self):
        import src.runtime.main_runtime as M
        from src.shared.services.image_banks import ImageBanks
        game = self.main.Game.__new__(self.main.Game)
        game.image_banks = ImageBanks(game=game)
        game.image_banks.tile_bank = {
            M.T_GRASS: (0, 0),
            M.T_PATH: (16, 0),
            M.T_WATER: (32, 0),
        }
        game.image_banks.path_variant_bank = {
            id(M.PATH_H): (48, 0),
            id(M.PATH_V): (64, 0),
        }
        game.image_banks.shore_variant_bank = {
            id(M.SHORE_N): (80, 0),
            id(M.SHORE_S): (96, 0),
            id(M.SHORE_W): (112, 0),
            id(M.SHORE_E): (128, 0),
        }
        game.image_banks.tile_bank_water2 = None
        return game

    def _patch_wm(self, fake_wm):
        """新仕様 (2026-05-05): regenerate_world_tilemap_fallback が
        generate_world_map() を直呼びするため、image_banks モジュールの
        関数参照を差し替えて固定 wm を注入する。"""
        from src.shared.services import image_banks as ib_module
        original = ib_module.generate_world_map
        ib_module.generate_world_map = lambda: fake_wm
        return original

    def _restore_wm(self, original):
        from src.shared.services import image_banks as ib_module
        ib_module.generate_world_map = original

    def test_regenerate_world_tilemap_fallback_writes_path_variant_tiles_for_editor(self):
        import src.runtime.main_runtime as M
        game = self.make_game()
        tilemap = _FakeTilemap()
        # 他テストの副作用 (pyxel.tilemaps[0].pget の MagicMock 化) を上書きする
        # ため、image_banks がモジュールレベルで束縛している pyxel 参照に直接
        # 差し込む。
        from src.shared.services import image_banks as ib_module
        ib_module.pyxel.tilemaps = [tilemap for _ in range(8)]

        fake_wm = [[M.T_GRASS for _ in range(M.MAP_W)] for _ in range(M.MAP_H)]
        fake_wm[10][10] = M.T_PATH
        fake_wm[10][11] = M.T_PATH
        fake_wm[10][12] = M.T_PATH

        original = self._patch_wm(fake_wm)
        try:
            game.image_banks.regenerate_world_tilemap_fallback()
        finally:
            self._restore_wm(original)

        self.assertEqual(tilemap.pget(2 * 11, 2 * 10), (6, 0))

    def test_regenerate_world_tilemap_fallback_writes_shore_variant_tiles_for_editor(self):
        import src.runtime.main_runtime as M
        game = self.make_game()
        tilemap = _FakeTilemap()
        # 他テストの副作用 (pyxel.tilemaps[0].pget の MagicMock 化) を上書きする
        # ため、image_banks がモジュールレベルで束縛している pyxel 参照に直接
        # 差し込む。
        from src.shared.services import image_banks as ib_module
        ib_module.pyxel.tilemaps = [tilemap for _ in range(8)]

        fake_wm = [[M.T_GRASS for _ in range(M.MAP_W)] for _ in range(M.MAP_H)]
        fake_wm[20][20] = M.T_WATER

        original = self._patch_wm(fake_wm)
        try:
            game.image_banks.regenerate_world_tilemap_fallback()
        finally:
            self._restore_wm(original)

        self.assertEqual(tilemap.pget(2 * 20, 2 * 20), (10, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
