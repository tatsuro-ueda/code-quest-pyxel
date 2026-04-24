"""CJG/player: PlayerModel.items の境界（buy_item の gold 不足 / use_item で qty 減算なし）。

根拠:
- docs/product-requirements-battle.md
- docs/customer-jobs.md Job4

buy_item は gold 不足で False を返し、items は変わらない。
use_item は PlayerModel 単体では qty 減算しない（呼び出し側の責務）。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import PlayerItem, PlayerModel


class BuyItemGoldShortageTest(unittest.TestCase):
    def test_buy_item_insufficient_gold_returns_false(self):
        pm = PlayerModel.new_game()
        pm.gold = 0
        pm.items = []

        ok = pm.buy_item(1, 10)

        self.assertFalse(ok)
        self.assertEqual(pm.items, [])

    def test_buy_item_exact_gold_succeeds(self):
        pm = PlayerModel.new_game()
        pm.gold = 10
        pm.items = []

        ok = pm.buy_item(1, 10)

        self.assertTrue(ok)
        self.assertEqual(pm.gold, 0)


class UseItemDoesNotConsumeTest(unittest.TestCase):
    """PlayerModel.use_item は qty を減らさない（呼び出し側が管理）。"""

    def test_heal_use_item_does_not_modify_items(self):
        pm = PlayerModel.new_game()
        pm.hp = 1
        pm.items = [PlayerItem(id=0, qty=3)]

        pm.use_item({"type": "heal", "value": 10, "name": "やくそう"})

        self.assertEqual(pm.items[0].qty, 3)


class CanAffordTest(unittest.TestCase):
    def test_affording_exact_amount_returns_true(self):
        pm = PlayerModel.new_game()
        pm.gold = 100

        self.assertTrue(pm.can_afford(100))

    def test_zero_cost_is_always_affordable(self):
        pm = PlayerModel.new_game()
        pm.gold = 0

        self.assertTrue(pm.can_afford(0))

    def test_negative_cost_is_affordable(self):
        """can_afford は >= 比較なので、負のコストも常に True。"""
        pm = PlayerModel.new_game()
        pm.gold = 0

        self.assertTrue(pm.can_afford(-10))


if __name__ == "__main__":
    unittest.main()
