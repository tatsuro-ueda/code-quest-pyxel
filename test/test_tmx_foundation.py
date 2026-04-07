"""TMX基盤のスモーク＋ユニットテスト.

設計書 §13 のテスト戦略に対応:
  - Unit: tmx_validator（正常/異常TMX）
  - Unit: tiled_loader（サンプルTMXで期待 MapData）
  - Integration: 全マップを CI で validate
  - Smoke: map_registry.load_all で起動シナリオ

実行方法:
    cd code-quest-pyxel
    python -m pytest tests/ -v
  または
    python tests/test_tmx_foundation.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# code-quest-pyxel をimport pathに追加
PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))

from src import tiled_loader, tmx_validator  # noqa: E402
from src.map_registry import MapRegistry  # noqa: E402
from src.tmx_validator import ValidationError  # noqa: E402

MAPS_DIR = PYXEL_ROOT / "assets" / "maps"
TOWN = MAPS_DIR / "town_start.tmx"
DUNGEON = MAPS_DIR / "dungeon_01.tmx"


class ValidatorTest(unittest.TestCase):
    def test_town_start_is_valid(self):
        report = tmx_validator.validate(TOWN)
        self.assertTrue(report.ok, f"errors: {report.errors}")

    def test_dungeon_01_is_valid(self):
        report = tmx_validator.validate(DUNGEON)
        self.assertTrue(report.ok, f"errors: {report.errors}")

    def test_missing_file(self):
        report = tmx_validator.validate(MAPS_DIR / "nonexistent.tmx")
        self.assertFalse(report.ok)

    def test_invalid_layer_name(self, tmpdir=None):
        bad = PYXEL_ROOT / "test" / "_bad_layer.tmx"
        bad.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<map version="1.10" orientation="orthogonal" width="2" height="2" '
            'tilewidth="16" tileheight="16">\n'
            ' <layer id="1" name="floorXXX" width="2" height="2">\n'
            '  <data encoding="csv">1,1,\n1,1</data>\n'
            ' </layer>\n'
            '</map>\n',
            encoding="utf-8",
        )
        try:
            report = tmx_validator.validate(bad)
            self.assertFalse(report.ok)
            self.assertTrue(any("floorXXX" in e for e in report.errors))
        finally:
            bad.unlink(missing_ok=True)

    def test_door_missing_target_is_detected(self):
        bad = PYXEL_ROOT / "test" / "_bad_door.tmx"
        bad.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<map version="1.10" orientation="orthogonal" width="2" height="2" '
            'tilewidth="16" tileheight="16">\n'
            ' <layer id="1" name="ground" width="2" height="2">\n'
            '  <data encoding="csv">1,1,\n1,1</data>\n'
            ' </layer>\n'
            ' <layer id="2" name="collision" width="2" height="2">\n'
            '  <data encoding="csv">0,0,\n0,0</data>\n'
            ' </layer>\n'
            ' <objectgroup id="3" name="objects">\n'
            '  <object id="1" name="d" type="door" x="0" y="0" width="16" height="16"/>\n'
            ' </objectgroup>\n'
            ' <objectgroup id="4" name="spawn">\n'
            '  <object id="2" name="player_start" x="0" y="0"/>\n'
            ' </objectgroup>\n'
            '</map>\n',
            encoding="utf-8",
        )
        try:
            report = tmx_validator.validate(bad)
            self.assertFalse(report.ok)
            self.assertTrue(
                any("target_map" in e for e in report.errors),
                f"errors: {report.errors}",
            )
        finally:
            bad.unlink(missing_ok=True)


class LoaderTest(unittest.TestCase):
    def test_load_town_start(self):
        m = tiled_loader.load(TOWN)
        self.assertEqual(m.name, "town_start")
        self.assertEqual(m.width, 10)
        self.assertEqual(m.height, 8)
        self.assertEqual(m.tile_size, 16)

    def test_ground_contains_grass_and_path(self):
        m = tiled_loader.load(TOWN)
        # gid 1 → tile_id 0 (GRASS), gid 12 → tile_id 11 (PATH)
        self.assertEqual(m.ground[0][0], 0)  # 左上はGRASS
        self.assertEqual(m.ground[0][4], 11)  # col=4 はPATH
        self.assertEqual(m.ground[7][4], 11)

    def test_collision_border_is_wall(self):
        m = tiled_loader.load(TOWN)
        # 四隅は壁
        self.assertTrue(m.collision[0][0])
        self.assertTrue(m.collision[0][9])
        self.assertTrue(m.collision[7][0])
        self.assertTrue(m.collision[7][9])
        # 内側は通れる
        self.assertFalse(m.collision[3][3])
        # 北の門は開いている (row=0, col=4)
        self.assertFalse(m.collision[0][4])

    def test_objects_parsed(self):
        m = tiled_loader.load(TOWN)
        types = {o.type for o in m.objects}
        self.assertIn("npc", types)
        self.assertIn("door", types)
        self.assertIn("chest", types)

        oldman = next(o for o in m.objects if o.name == "oldman")
        self.assertEqual(oldman.properties["dialog_id"], "intro_01")
        self.assertEqual(oldman.tile_x, 3)
        self.assertEqual(oldman.tile_y, 3)

        door = next(o for o in m.objects if o.type == "door")
        self.assertEqual(door.properties["target_map"], "dungeon_01.tmx")

    def test_spawn_points(self):
        m = tiled_loader.load(TOWN)
        self.assertIn("player_start", m.spawn_points)
        self.assertEqual(m.spawn_points["player_start"], (4, 4))


class RegistrySmokeTest(unittest.TestCase):
    def test_load_all_maps(self):
        reg = MapRegistry()
        reg.load_all(MAPS_DIR)
        self.assertIn("town_start", reg.names())
        self.assertIn("dungeon_01", reg.names())

    def test_set_active_and_get(self):
        reg = MapRegistry()
        reg.load_all(MAPS_DIR)
        reg.set_active("town_start")
        active = reg.active()
        self.assertEqual(active.name, "town_start")

    def test_unknown_map_raises(self):
        reg = MapRegistry()
        reg.load_all(MAPS_DIR)
        with self.assertRaises(KeyError):
            reg.get("nonexistent")

    def test_all_tmx_files_are_valid(self):
        """設計書 §13 Integration: 全TMXがCIでvalidateされる."""
        tmx_files = list(MAPS_DIR.glob("*.tmx"))
        self.assertGreater(len(tmx_files), 0)
        for tmx in tmx_files:
            with self.subTest(tmx=tmx.name):
                try:
                    tmx_validator.validate_or_raise(tmx)
                except ValidationError as exc:
                    self.fail(f"{tmx.name} failed validation: {exc}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
