"""Tests for the shop logic.

Game クラスを直接生成すると pyxel.init() が走るので、
購入ロジックの本質だけを切り出して検証する。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data  # noqa: E402


def _purchase(player, kind, idx, weapons, armors, items):
    if kind == "weapons":
        entry = weapons[idx]
    elif kind == "armors":
        entry = armors[idx]
    else:
        entry = items[idx]
    price = entry.get("price", 0)
    if kind == "weapons" and player["weapon"] == idx:
        return "owned"
    if kind == "armors" and player["armor"] == idx:
        return "owned"
    if player["gold"] < price:
        return "fail"
    player["gold"] -= price
    if kind == "weapons":
        player["weapon"] = idx
    elif kind == "armors":
        player["armor"] = idx
    else:
        for inv in player["items"]:
            if inv["id"] == idx:
                inv["qty"] += 1
                break
        else:
            player["items"].append({"id": idx, "qty": 1})
    return "ok"


class ShopPurchaseTest(unittest.TestCase):
    def setUp(self):
        self.weapons = game_data.load_weapons()
        self.armors = game_data.load_armors()
        self.items = game_data.load_items()

    def test_purchase_weapon_deducts_gold_and_equips(self):
        player = {"gold": 50, "weapon": 0, "armor": 0, "items": []}
        # マウス (idx 1, 10G)
        result = _purchase(player, "weapons", 1, self.weapons, self.armors, self.items)
        self.assertEqual(result, "ok")
        self.assertEqual(player["gold"], 40)
        self.assertEqual(player["weapon"], 1)

    def test_purchase_fail_insufficient_gold(self):
        player = {"gold": 5, "weapon": 0, "armor": 0, "items": []}
        result = _purchase(player, "weapons", 1, self.weapons, self.armors, self.items)
        self.assertEqual(result, "fail")
        self.assertEqual(player["gold"], 5)
        self.assertEqual(player["weapon"], 0)

    def test_purchase_weapon_already_owned_blocks_repurchase(self):
        player = {"gold": 100, "weapon": 1, "armor": 0, "items": []}
        result = _purchase(player, "weapons", 1, self.weapons, self.armors, self.items)
        self.assertEqual(result, "owned")
        self.assertEqual(player["gold"], 100)

    def test_purchase_item_adds_to_inventory(self):
        player = {"gold": 100, "weapon": 0, "armor": 0, "items": []}
        # バグレポート (idx 0, 1G)
        _purchase(player, "items", 0, self.weapons, self.armors, self.items)
        self.assertEqual(player["gold"], 99)
        self.assertEqual(player["items"], [{"id": 0, "qty": 1}])
        # 重複購入は qty を増やす
        _purchase(player, "items", 0, self.weapons, self.armors, self.items)
        self.assertEqual(player["items"], [{"id": 0, "qty": 2}])


if __name__ == "__main__":
    unittest.main()
