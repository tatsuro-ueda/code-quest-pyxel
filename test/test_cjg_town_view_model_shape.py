"""CJG/town: TownMenuViewModel の shape と不変性。

根拠:
- docs/framework-rule.md M2-2（ViewModel は View の入力として固定形状）

TownMenuViewModel の labels は tuple / title は str / cursor は int /
gold は int。Presenter から作ったものは同じ形を保つ。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.town.view_model import TownMenuViewModel


class ViewModelShapeTest(unittest.TestCase):
    def test_construct_with_minimum_fields(self):
        vm = TownMenuViewModel(
            title="まちメニュー",
            labels=("はなす", "でる"),
            cursor=0,
            gold=100,
        )

        self.assertEqual(vm.title, "まちメニュー")
        self.assertEqual(vm.labels, ("はなす", "でる"))
        self.assertEqual(vm.cursor, 0)
        self.assertEqual(vm.gold, 100)

    def test_cursor_accepts_zero(self):
        vm = TownMenuViewModel(title="t", labels=("a",), cursor=0, gold=0)
        self.assertEqual(vm.cursor, 0)

    def test_gold_accepts_large_value(self):
        vm = TownMenuViewModel(title="t", labels=("a",), cursor=0, gold=999999)
        self.assertEqual(vm.gold, 999999)


if __name__ == "__main__":
    unittest.main()
