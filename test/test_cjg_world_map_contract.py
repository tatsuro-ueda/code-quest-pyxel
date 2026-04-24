"""CJG/world: 生成されたワールドマップが TOWN_INDEX_BY_POS の座標に町タイルを持つ。

根拠:
- docs/product-requirements-map.md（町タイル配置と shop 連携）

generate_world_map(seed=42) が TOWN_INDEX_BY_POS の 3 座標すべてに
T_TOWN タイルを置いている。無いと町に入れず KeyError で落ちる。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.constants.game_config import TOWN_INDEX_BY_POS
from src.shared.constants.tile_data import T_CASTLE, T_TOWN
from src.shared.services.world_generation import generate_world_map


class WorldMapTownPositionsTest(unittest.TestCase):
    def test_every_town_position_has_town_tile(self):
        world = generate_world_map(seed=42)
        for pos, idx in TOWN_INDEX_BY_POS.items():
            x, y = pos
            with self.subTest(pos=pos, town_index=idx):
                self.assertEqual(
                    world[y][x],
                    T_TOWN,
                    f"町 {idx} の予定座標 {pos} にタイル {world[y][x]} （T_TOWN={T_TOWN} 期待）",
                )

    def test_castle_position_has_castle_tile(self):
        world = generate_world_map(seed=42)
        # castle は (25, 6) に配置される
        self.assertEqual(world[6][25], T_CASTLE)


class WorldMapDimensionsTest(unittest.TestCase):
    def test_world_map_is_at_least_50_x_50(self):
        """TOWN_INDEX_BY_POS の 最大座標 (18, 34) を含むサイズ。"""
        world = generate_world_map()
        self.assertGreaterEqual(len(world), 50)  # 行数
        self.assertGreaterEqual(len(world[0]), 50)  # 列数


if __name__ == "__main__":
    unittest.main()
