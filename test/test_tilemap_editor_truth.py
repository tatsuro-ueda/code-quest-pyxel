from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


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


class _FakeTilemap:
    def __init__(self):
        self.calls: dict[tuple[int, int], tuple[int, int]] = {}

    def pset(self, x: int, y: int, value: tuple[int, int]) -> None:
        self.calls[(x, y)] = value

    def pget(self, x: int, y: int) -> tuple[int, int]:
        return self.calls.get((x, y), (0, 0))


class TilemapEditorTruthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def make_game(self):
        game = self.main.Game.__new__(self.main.Game)
        game.world_map = [
            [self.main.T_GRASS for _ in range(self.main.MAP_W)]
            for _ in range(self.main.MAP_H)
        ]
        game.tile_bank = {
            self.main.T_GRASS: (0, 0),
            self.main.T_PATH: (16, 0),
            self.main.T_WATER: (32, 0),
        }
        game.path_variant_bank = {
            id(self.main.PATH_H): (48, 0),
            id(self.main.PATH_V): (64, 0),
        }
        game.shore_variant_bank = {
            id(self.main.SHORE_N): (80, 0),
            id(self.main.SHORE_S): (96, 0),
            id(self.main.SHORE_W): (112, 0),
            id(self.main.SHORE_E): (128, 0),
        }
        game.tile_bank_water2 = None
        return game

    def test_bake_world_tilemap_writes_path_variant_tiles_for_editor(self):
        game = self.make_game()
        tilemap = _FakeTilemap()
        self.main.pyxel.tilemaps = [tilemap for _ in range(8)]

        game.world_map[10][10] = self.main.T_PATH
        game.world_map[10][11] = self.main.T_PATH
        game.world_map[10][12] = self.main.T_PATH

        self.main.Game._bake_world_to_tilemap(game)

        self.assertEqual(tilemap.pget(2 * 11, 2 * 10), (6, 0))

    def test_bake_world_tilemap_writes_shore_variant_tiles_for_editor(self):
        game = self.make_game()
        tilemap = _FakeTilemap()
        self.main.pyxel.tilemaps = [tilemap for _ in range(8)]

        game.world_map[20][20] = self.main.T_WATER

        self.main.Game._bake_world_to_tilemap(game)

        self.assertEqual(tilemap.pget(2 * 20, 2 * 20), (10, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
