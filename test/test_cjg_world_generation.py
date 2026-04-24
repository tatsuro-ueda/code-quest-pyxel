"""CJG/world: generate_world_map と get_zone が決定的に crash なく動く。

根拠:
- docs/product-requirements-map.md（マップ生成とゾーン判定）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

generate_world_map(seed) は固定 seed で同じマップを返す純粋関数（疑似乱数）。
get_zone(y, in_dungeon) は y 座標を 4 分割してゾーン ID を返す（in_dungeon は
zone 4）。audio_system.sync_audio が zone を参照するので、境界で KeyError /
IndexError を出すと全 state で即 crash する。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.world_generation import (
    generate_dungeon,
    generate_world_map,
    get_zone,
)


class GetZoneTest(unittest.TestCase):
    """get_zone の境界値が期待どおり 0/1/2/3 に分かれ、in_dungeon は 4。"""

    def test_in_dungeon_always_returns_4(self):
        for y in range(0, 64, 8):
            with self.subTest(y=y):
                self.assertEqual(get_zone(y, in_dungeon=True), 4)

    def test_zone_0_from_y_0_to_15(self):
        for y in (0, 1, 10, 15):
            with self.subTest(y=y):
                self.assertEqual(get_zone(y), 0)

    def test_zone_1_from_y_16_to_27(self):
        for y in (16, 20, 27):
            with self.subTest(y=y):
                self.assertEqual(get_zone(y), 1)

    def test_zone_2_from_y_28_to_37(self):
        for y in (28, 33, 37):
            with self.subTest(y=y):
                self.assertEqual(get_zone(y), 2)

    def test_zone_3_from_y_38_onwards(self):
        for y in (38, 50, 99):
            with self.subTest(y=y):
                self.assertEqual(get_zone(y), 3)


class GenerateWorldMapTest(unittest.TestCase):
    def test_world_map_is_2d_grid_with_positive_dimensions(self):
        world = generate_world_map()
        self.assertGreater(len(world), 0)
        self.assertGreater(len(world[0]), 0)
        # すべての行が同じ幅
        width = len(world[0])
        for row in world:
            self.assertEqual(len(row), width, "world map の行幅が揃っていない")

    def test_same_seed_produces_identical_map(self):
        a = generate_world_map(seed=42)
        b = generate_world_map(seed=42)
        self.assertEqual(a, b, "同じ seed で異なる map が返るのは NG")

    def test_different_seeds_produce_different_maps(self):
        a = generate_world_map(seed=42)
        b = generate_world_map(seed=123)
        self.assertNotEqual(a, b, "異なる seed で完全一致する map は疑似乱数の不具合")

    def test_map_cells_are_int_or_tile_ids(self):
        world = generate_world_map()
        for y, row in enumerate(world):
            for x, cell in enumerate(row):
                with self.subTest(x=x, y=y):
                    self.assertIsInstance(cell, int, "map セルが int ではない")


class GenerateDungeonTest(unittest.TestCase):
    def test_dungeon_returns_grid_and_rooms(self):
        grid, rooms = generate_dungeon(seed=99)
        self.assertGreater(len(grid), 0)
        self.assertGreater(len(rooms), 0)

    def test_same_seed_produces_identical_dungeon(self):
        a_grid, a_rooms = generate_dungeon(seed=99)
        b_grid, b_rooms = generate_dungeon(seed=99)
        self.assertEqual(a_grid, b_grid)
        self.assertEqual(a_rooms, b_rooms)


if __name__ == "__main__":
    unittest.main()
