"""Tests for spell learning and effect application.

Game クラスを直接生成すると pyxel.init() が走るので、
本質ロジックだけを切り出して検証する。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data  # noqa: E402
from src.player_factory import create_initial_player  # noqa: E402


def _learn_for_level(player, spells, level):
    for spell in spells:
        if spell["learn_lv"] == level and spell["name"] not in player["spells"]:
            player["spells"].append(spell["name"])


def _apply_heal(player, spell):
    player["hp"] = min(player["max_hp"], player["hp"] + spell["power"])


def _apply_attack(enemy_hp, spell):
    return max(0, enemy_hp - spell["power"])


class SpellLearningTest(unittest.TestCase):
    def setUp(self):
        self.spells = game_data.load_spells()

    def test_no_spell_at_lv1(self):
        p = create_initial_player()
        _learn_for_level(p, self.spells, 1)
        self.assertEqual(p["spells"], [])

    def test_learn_debug_at_lv3(self):
        p = create_initial_player()
        _learn_for_level(p, self.spells, 3)
        self.assertIn("デバッグ", p["spells"])

    def test_learn_compile_at_lv20(self):
        p = create_initial_player()
        _learn_for_level(p, self.spells, 20)
        self.assertIn("コンパイル", p["spells"])

    def test_no_duplicate_learn(self):
        p = create_initial_player()
        _learn_for_level(p, self.spells, 3)
        _learn_for_level(p, self.spells, 3)
        self.assertEqual(p["spells"].count("デバッグ"), 1)


class SpellEffectTest(unittest.TestCase):
    def setUp(self):
        self.spells = {s["name"]: s for s in game_data.load_spells()}

    def test_heal_spell_recovers_hp(self):
        p = create_initial_player()
        p["hp"] = 10
        _apply_heal(p, self.spells["デバッグ"])  # power 60
        self.assertEqual(p["hp"], min(p["max_hp"], 70))

    def test_heal_does_not_exceed_max(self):
        p = create_initial_player()
        p["hp"] = p["max_hp"] - 1
        _apply_heal(p, self.spells["デバッグ"])
        self.assertEqual(p["hp"], p["max_hp"])

    def test_attack_spell_damages_enemy(self):
        enemy_hp = 100
        new_hp = _apply_attack(enemy_hp, self.spells["プリント"])  # power 40
        self.assertEqual(new_hp, 60)

    def test_attack_floors_at_zero(self):
        enemy_hp = 5
        new_hp = _apply_attack(enemy_hp, self.spells["コンパイル"])  # power 140
        self.assertEqual(new_hp, 0)


if __name__ == "__main__":
    unittest.main()
