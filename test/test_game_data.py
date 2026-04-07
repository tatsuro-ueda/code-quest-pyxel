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


if __name__ == "__main__":
    unittest.main()
