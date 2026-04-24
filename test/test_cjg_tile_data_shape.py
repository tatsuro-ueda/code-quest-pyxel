"""CJG/tile_data: TILE_DATA の各エントリが 16 行 × 16 列で色値 0〜15。

根拠:
- docs/product-requirements-platform.md（16x16 タイル / Pyxel パレット）

Pyxel のイメージバンクに貼る前提で、各タイルが 16x16 でなければ描画位置がずれる。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.constants.tile_data import TILE_DATA


class TileShapeTest(unittest.TestCase):
    def test_every_tile_has_16_rows(self):
        for tid, tile in TILE_DATA.items():
            with self.subTest(tid=tid):
                self.assertEqual(len(tile), 16, f"tile {tid} が {len(tile)} 行")

    def test_every_row_has_16_columns(self):
        for tid, tile in TILE_DATA.items():
            for row_idx, row in enumerate(tile):
                with self.subTest(tid=tid, row=row_idx):
                    self.assertEqual(len(row), 16)

    def test_every_pixel_is_0_to_15(self):
        for tid, tile in TILE_DATA.items():
            for row_idx, row in enumerate(tile):
                for col_idx, value in enumerate(row):
                    with self.subTest(tid=tid, row=row_idx, col=col_idx):
                        self.assertIsInstance(value, int)
                        self.assertGreaterEqual(value, 0)
                        self.assertLessEqual(value, 15)


if __name__ == "__main__":
    unittest.main()
