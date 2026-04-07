"""Tests for src/game_data loaders."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data  # noqa: E402


class LoadYamlTest(unittest.TestCase):
    def test_load_yaml_returns_dict_or_list(self):
        result = game_data.load_yaml(ROOT / "assets" / "dialogue.yaml")
        self.assertTrue(isinstance(result, (dict, list)))


class LoadEnemiesTest(unittest.TestCase):
    def test_returns_12_enemies(self):
        enemies = game_data.load_enemies()
        self.assertEqual(len(enemies), 12)

    def test_each_enemy_has_required_keys(self):
        required = {"name", "sprite", "hp", "atk", "def", "agi", "exp", "gold", "zone", "category", "desc"}
        for enemy in game_data.load_enemies():
            missing = required - enemy.keys()
            self.assertFalse(missing, f"{enemy.get('name')} missing keys: {missing}")

    def test_boss_flags(self):
        enemies = {e["name"]: e for e in game_data.load_enemies()}
        self.assertTrue(enemies["魔王グリッチ"].get("is_boss"))
        self.assertTrue(enemies["プロフェッサー"].get("is_professor"))
        self.assertTrue(enemies["魔王グリッチのクローン"].get("post_clear_only"))

    def test_zone_distribution(self):
        zones = [e["zone"] for e in game_data.load_enemies()]
        self.assertIn(0, zones)
        self.assertIn(5, zones)
        self.assertIn(6, zones)


class LoadWeaponsTest(unittest.TestCase):
    def test_returns_8_weapons_including_base(self):
        weapons = game_data.load_weapons()
        self.assertEqual(len(weapons), 8)  # 素手 + 7
        self.assertEqual(weapons[0]["name"], "素手")

    def test_each_weapon_has_required_keys(self):
        for w in game_data.load_weapons():
            for key in ("name", "atk", "price", "buy_msg"):
                self.assertIn(key, w)

    def test_weapon_atk_increases_by_tier(self):
        atks = [w["atk"] for w in game_data.load_weapons()]
        for i in range(1, len(atks)):
            self.assertGreater(atks[i], atks[i - 1])


class LoadArmorsTest(unittest.TestCase):
    def test_returns_8_armors_including_base(self):
        armors = game_data.load_armors()
        self.assertEqual(len(armors), 8)
        self.assertEqual(armors[0]["name"], "ふだんぎ")

    def test_each_armor_has_required_keys(self):
        for a in game_data.load_armors():
            for key in ("name", "def", "price", "buy_msg"):
                self.assertIn(key, a)


class LoadItemsTest(unittest.TestCase):
    def test_returns_4_items(self):
        items = game_data.load_items()
        self.assertEqual(len(items), 4)

    def test_item_types_are_supported(self):
        types = {i["type"] for i in game_data.load_items()}
        self.assertEqual(types, {"heal", "mp_heal", "cure_poison", "warp"})

    def test_each_item_has_required_keys(self):
        for i in game_data.load_items():
            for key in ("name", "type", "value", "price", "desc"):
                self.assertIn(key, i)

    def test_cure_poison_item_exists(self):
        names = {i["name"] for i in game_data.load_items() if i["type"] == "cure_poison"}
        self.assertIn("アンチウイルス", names)

    def test_warp_item_exists(self):
        names = {i["name"] for i in game_data.load_items() if i["type"] == "warp"}
        self.assertIn("セーブポイント", names)


class LoadSpellsTest(unittest.TestCase):
    def test_returns_5_spells(self):
        spells = game_data.load_spells()
        self.assertEqual(len(spells), 5)

    def test_each_spell_has_required_keys(self):
        for s in game_data.load_spells():
            for key in ("name", "mp", "type", "power", "desc", "learn_lv"):
                self.assertIn(key, s)

    def test_spell_types_are_heal_or_attack(self):
        for s in game_data.load_spells():
            self.assertIn(s["type"], ("heal", "attack"))

    def test_spells_sorted_by_learn_level(self):
        levels = [s["learn_lv"] for s in game_data.load_spells()]
        self.assertEqual(levels, sorted(levels))


class LoadShopsTest(unittest.TestCase):
    def test_shops_for_3_towns(self):
        data = game_data.load_shops()
        self.assertEqual(len(data["shops"]), 3)

    def test_inn_prices_3_entries(self):
        data = game_data.load_shops()
        self.assertEqual(data["inn_prices"], [5, 15, 40])

    def test_shop_keys(self):
        for shop in game_data.load_shops()["shops"]:
            for key in ("town", "items", "weapons", "armors"):
                self.assertIn(key, shop)


if __name__ == "__main__":
    unittest.main()
