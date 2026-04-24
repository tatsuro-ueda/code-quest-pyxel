"""CJG/constants: tile_data の T_* 定数が一意で TILE_DATA に対応する。

根拠:
- docs/product-requirements-map.md（タイル判定）
- docs/framework-rule.md M5-1（定数の健全性）

T_WATER / T_GRASS / T_PATH / T_FLOOR / T_WALL / T_CASTLE / T_TOWN / T_CAVE /
T_STAIR_UP / T_GLITCH_LORD_TRIGGER などの integer 定数が一意。TILE_DATA に
登録されている tile id が重複しない。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.constants import tile_data as T


class TileConstantsUniqueTest(unittest.TestCase):
    def test_all_T_constants_have_unique_values(self):
        names = [name for name in dir(T) if name.startswith("T_") and name.isupper()]
        values = [getattr(T, name) for name in names]
        # 各定数が int であり、重複が無い
        for name, val in zip(names, values):
            with self.subTest(name=name):
                self.assertIsInstance(val, int)
        self.assertEqual(
            len(values),
            len(set(values)),
            f"T_* 定数に重複がある: {[(n, v) for n, v in zip(names, values) if values.count(v) > 1]}",
        )


class TileDataShapeTest(unittest.TestCase):
    def test_tile_data_covers_expected_tiles(self):
        """TILE_DATA が主要タイル（T_GRASS / T_WATER / T_PATH / T_CASTLE / T_TOWN）を含む。"""
        expected = (
            T.T_GRASS,
            T.T_WATER,
            T.T_PATH,
            T.T_CASTLE,
            T.T_TOWN,
        )
        for tid in expected:
            with self.subTest(tid=tid):
                self.assertIn(tid, T.TILE_DATA)

    def test_every_tile_data_entry_is_list_or_tuple(self):
        for tid, data in T.TILE_DATA.items():
            with self.subTest(tid=tid):
                self.assertTrue(isinstance(data, (list, tuple)))
                self.assertGreater(len(data), 0)


if __name__ == "__main__":
    unittest.main()
