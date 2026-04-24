"""CJG/town: TownModel.move_cursor / reset のロジック。

根拠:
- docs/product-requirements-narrative.md（町メニュー cursor 循環）

move_cursor は cursor を delta 分動かし、label_count でラップする。
label_count <= 0 では何もしない（安全網）。reset は町を出るときの
状態クリアに使う。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.town.model import TownModel


class MoveCursorTest(unittest.TestCase):
    def test_down_delta_increments_within_range(self):
        model = TownModel()
        model.menu_cursor = 0

        model.move_cursor(1, 5)

        self.assertEqual(model.menu_cursor, 1)

    def test_up_delta_from_zero_wraps_to_last(self):
        model = TownModel()
        model.menu_cursor = 0

        model.move_cursor(-1, 5)

        self.assertEqual(model.menu_cursor, 4)

    def test_down_delta_from_last_wraps_to_zero(self):
        model = TownModel()
        model.menu_cursor = 4

        model.move_cursor(1, 5)

        self.assertEqual(model.menu_cursor, 0)

    def test_zero_label_count_does_nothing(self):
        model = TownModel()
        model.menu_cursor = 2

        model.move_cursor(1, 0)

        self.assertEqual(model.menu_cursor, 2)

    def test_negative_label_count_does_nothing(self):
        model = TownModel()
        model.menu_cursor = 2

        model.move_cursor(1, -1)

        self.assertEqual(model.menu_cursor, 2)


class ResetTest(unittest.TestCase):
    def test_reset_clears_menu_pos_and_cursor(self):
        model = TownModel()
        model.menu_pos = (25, 6)
        model.menu_cursor = 3

        model.reset()

        self.assertIsNone(model.menu_pos)
        self.assertEqual(model.menu_cursor, 0)


if __name__ == "__main__":
    unittest.main()
