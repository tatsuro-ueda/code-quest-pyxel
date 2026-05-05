from __future__ import annotations

"""pyxres を world_map の SSoT として尊重しているか検証する。

過去バグ（2026-04-25）：``bake_world_to_tilemap`` が ``pyxres_loaded`` 状態でも
無条件に ``get_path_variant`` の procedural 値を書き戻しており、Code Maker で
編集した道形状（例：(30,21) を縦パスに）が起動時に黙って横一直線へ戻されていた。

修正後の不変性：``pyxres_loaded == True`` のとき、``bake_world_to_tilemap`` は
tilemap の既存ピクセルを上書きしない。pyxres から derive で読み戻した状態が
そのまま描画 SoT になる。
"""

import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from _helpers.imagebank_stub import (  # noqa: E402
    FakeTilemap as _FakeTilemap,
    install_fake_tilemap,
    snapshot_tilemaps,
    restore_tilemaps,
)


def _install_pyxel_stub() -> None:
    if "pyxel" in sys.modules and not getattr(sys.modules["pyxel"], "__IS_TEST_STUB__", False):
        return
    stub = types.ModuleType("pyxel")
    stub.__IS_TEST_STUB__ = True  # type: ignore[attr-defined]
    stub.init = lambda *args, **kwargs: None
    stub.run = lambda *args, **kwargs: None
    stub.load = lambda *args, **kwargs: None
    stub.save = lambda *args, **kwargs: None
    stub.quit = lambda *args, **kwargs: None
    stub.images = [types.SimpleNamespace(pset=lambda *a, **k: None, pget=lambda *a, **k: 0) for _ in range(4)]
    stub.tilemaps = [types.SimpleNamespace(pset=lambda *a, **k: None, pget=lambda *a, **k: (0, 0)) for _ in range(8)]
    stub.sounds = [types.SimpleNamespace(set=lambda *a, **k: None) for _ in range(64)]
    stub.musics = [types.SimpleNamespace(set=lambda *a, **k: None) for _ in range(8)]
    stub.channels = [types.SimpleNamespace(gain=0.125) for _ in range(8)]
    stub.Font = lambda *a, **k: None
    stub.btn = lambda *a, **k: False
    stub.btnp = lambda *a, **k: False
    stub.mouse_x = 0
    stub.mouse_y = 0
    stub.frame_count = 0
    stub.cls = lambda *a, **k: None
    stub.rect = lambda *a, **k: None
    stub.rectb = lambda *a, **k: None
    stub.text = lambda *a, **k: None
    stub.blt = lambda *a, **k: None
    stub.line = lambda *a, **k: None
    stub.pset = lambda *a, **k: None
    stub.circ = lambda *a, **k: None
    stub.play = lambda *a, **k: None
    stub.stop = lambda *a, **k: None
    stub.playm = lambda *a, **k: None
    stub.pal = lambda *a, **k: None
    stub.clip = lambda *a, **k: None
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


class WorldMapSsotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _install_pyxel_stub()
        import src.runtime.main_runtime as M  # noqa: F401
        cls.M = M

    def setUp(self):
        self._original_tilemaps = snapshot_tilemaps()

    def tearDown(self):
        restore_tilemaps(self._original_tilemaps)

    def _make_image_banks(self, pyxres_loaded: bool):
        from src.shared.services.image_banks import ImageBanks
        M = self.M

        class _G:
            pass

        game = _G()
        ib = ImageBanks(game=game)
        ib.tile_bank = {
            M.T_GRASS: (0, 0),
            M.T_PATH: (16, 0),
            M.T_WATER: (32, 0),
        }
        ib.path_variant_bank = {
            id(M.PATH_H): (48, 0),
            id(M.PATH_V): (64, 0),
        }
        ib.shore_variant_bank = {}
        ib.tile_bank_water2 = None
        ib.pyxres_loaded = pyxres_loaded
        return game, ib

    def _patch_generate_world_map(self, fake_wm):
        """image_banks モジュールの generate_world_map を fake_wm 返す関数に差し替える。

        新仕様 (2026-05-05)：regenerate_world_tilemap_fallback が直接
        generate_world_map() を呼ぶため、test 側はモジュールトップの
        参照を patch して固定 wm を注入する。"""
        from src.shared.services import image_banks as ib_module
        original = ib_module.generate_world_map
        ib_module.generate_world_map = lambda: fake_wm
        return original

    def _restore_generate_world_map(self, original):
        from src.shared.services import image_banks as ib_module
        ib_module.generate_world_map = original

    def _install_fake_tilemap(self):
        # 他のテストが ``sys.modules["pyxel"]`` を差し替える副作用に強くするため、
        # image_banks がモジュールレベルで束縛している pyxel 参照に直接差し込む
        # (helper 経由)。
        return install_fake_tilemap()

    def test_regenerate_world_tilemap_fallback_preserves_pyxres_when_loaded(self):
        """``pyxres_loaded`` のとき、fallback は既存 tilemap ピクセルに触れない。"""
        game, ib = self._make_image_banks(pyxres_loaded=True)
        tilemap = self._install_fake_tilemap()

        # pyxres 由来の sentinel 値（procedural が決して書かない値）を配置
        sentinels: dict[tuple[int, int], tuple[int, int]] = {}
        for (wx, wy) in [(30, 21), (28, 20)]:
            for dy in range(2):
                for dx in range(2):
                    px, py = 2 * wx + dx, 2 * wy + dy
                    val = (200 + dx, 200 + dy)
                    tilemap.pset(px, py, val)
                    sentinels[(px, py)] = val

        before = dict(tilemap.calls)
        ib.regenerate_world_tilemap_fallback()
        after = dict(tilemap.calls)

        for pos, expected in sentinels.items():
            self.assertEqual(
                after.get(pos),
                expected,
                f"pyxres pixel at {pos} was overwritten by fallback (BEFORE={before.get(pos)} "
                f"AFTER={after.get(pos)}); fallback must skip when pyxres_loaded",
            )

    def test_regenerate_world_tilemap_fallback_runs_when_pyxres_not_loaded(self):
        """``pyxres_loaded == False`` のとき、fallback は従来通り procedural 描画を行う。

        pyxres 不在時の初回生成 + ``pyxel.save`` フローを壊さないための回帰防止。
        新仕様：``generate_world_map()`` を直呼びするため、test 側で monkeypatch
        して固定 wm を注入する。
        """
        game, ib = self._make_image_banks(pyxres_loaded=False)
        tilemap = self._install_fake_tilemap()

        fake_wm = [[self.M.T_GRASS for _ in range(self.M.MAP_W)] for _ in range(self.M.MAP_H)]
        fake_wm[10][10] = self.M.T_PATH
        fake_wm[10][11] = self.M.T_PATH
        fake_wm[10][12] = self.M.T_PATH

        original = self._patch_generate_world_map(fake_wm)
        try:
            ib.regenerate_world_tilemap_fallback()
        finally:
            self._restore_generate_world_map(original)

        # 横並び 3 連続 → 中央は PATH_H、tile bank は (48, 0) → tu=6, tv=0
        self.assertEqual(tilemap.pget(2 * 11, 2 * 10), (6, 0))


if __name__ == "__main__":
    unittest.main()
