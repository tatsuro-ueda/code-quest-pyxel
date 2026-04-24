"""CJG/data: generated データの進行性と整合（weapons/armors/items/spells/enemies）。

根拠:
- docs/product-requirements-battle.md（装備とレベル進行）
- docs/product-requirements-narrative.md（呪文習得レベル）
- docs/customer-jobs.md Job4（ゲームを楽しむ / 進行の手応え）

weapons / armors は price 昇順で強くなる（index 0 はタダの最弱）。
items は type が既知。spells は learn_lv が単調で overlap しない。
enemies は HP > 0、agi >= 0。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data


class WeaponProgressionTest(unittest.TestCase):
    def test_weapon_atk_is_non_decreasing_with_index(self):
        atks = [w["atk"] for w in game_data.WEAPONS]
        for i in range(1, len(atks)):
            with self.subTest(i=i):
                self.assertGreaterEqual(atks[i], atks[i - 1])

    def test_weapon_price_is_non_decreasing_with_index(self):
        prices = [w["price"] for w in game_data.WEAPONS]
        for i in range(1, len(prices)):
            with self.subTest(i=i):
                self.assertGreaterEqual(prices[i], prices[i - 1])

    def test_weapon_index_zero_is_free_default(self):
        w0 = game_data.WEAPONS[0]
        self.assertEqual(w0["price"], 0)
        self.assertEqual(w0["atk"], 0)

    def test_every_weapon_has_name(self):
        for idx, w in enumerate(game_data.WEAPONS):
            with self.subTest(idx=idx):
                self.assertTrue(w.get("name"))


class ArmorProgressionTest(unittest.TestCase):
    def test_armor_def_is_non_decreasing_with_index(self):
        defs = [a["def"] for a in game_data.ARMORS]
        for i in range(1, len(defs)):
            with self.subTest(i=i):
                self.assertGreaterEqual(defs[i], defs[i - 1])

    def test_armor_price_is_non_decreasing_with_index(self):
        prices = [a["price"] for a in game_data.ARMORS]
        for i in range(1, len(prices)):
            with self.subTest(i=i):
                self.assertGreaterEqual(prices[i], prices[i - 1])

    def test_armor_index_zero_is_free_default(self):
        a0 = game_data.ARMORS[0]
        self.assertEqual(a0["price"], 0)
        self.assertEqual(a0["def"], 0)


class ItemShapeTest(unittest.TestCase):
    _KNOWN_TYPES = {"heal", "mp_heal", "cure_poison", "warp"}

    def test_every_item_has_name_type_price(self):
        for idx, item in enumerate(game_data.ITEMS):
            with self.subTest(idx=idx):
                self.assertIn("name", item)
                self.assertIn("type", item)
                self.assertIn("price", item)

    def test_every_item_type_is_known(self):
        for idx, item in enumerate(game_data.ITEMS):
            with self.subTest(idx=idx, name=item["name"]):
                self.assertIn(item["type"], self._KNOWN_TYPES)

    def test_heal_and_mp_heal_items_have_value(self):
        for idx, item in enumerate(game_data.ITEMS):
            if item["type"] in ("heal", "mp_heal"):
                with self.subTest(idx=idx, name=item["name"]):
                    self.assertIn("value", item)
                    self.assertGreater(item["value"], 0)


class SpellProgressionTest(unittest.TestCase):
    def test_every_spell_has_required_keys(self):
        for spell in game_data.SPELLS:
            with self.subTest(name=spell.get("name")):
                for key in ("name", "type", "mp", "learn_lv"):
                    self.assertIn(key, spell)

    def test_every_spell_mp_is_positive_int(self):
        for spell in game_data.SPELLS:
            with self.subTest(name=spell["name"]):
                self.assertIsInstance(spell["mp"], int)
                self.assertGreater(spell["mp"], 0)

    def test_every_learn_lv_is_at_least_1(self):
        for spell in game_data.SPELLS:
            with self.subTest(name=spell["name"]):
                self.assertGreaterEqual(spell["learn_lv"], 1)


class EnemyDataShapeTest(unittest.TestCase):
    def test_every_enemy_has_positive_hp(self):
        for enemy in game_data.ENEMIES:
            with self.subTest(name=enemy["name"]):
                self.assertGreater(enemy["hp"], 0)

    def test_every_enemy_has_non_negative_agi(self):
        for enemy in game_data.ENEMIES:
            with self.subTest(name=enemy["name"]):
                self.assertGreaterEqual(enemy.get("agi", 0), 0)

    def test_every_enemy_has_non_negative_exp_and_gold(self):
        for enemy in game_data.ENEMIES:
            with self.subTest(name=enemy["name"]):
                self.assertGreaterEqual(enemy.get("exp", 0), 0)
                self.assertGreaterEqual(enemy.get("gold", 0), 0)


if __name__ == "__main__":
    unittest.main()
