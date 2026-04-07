"""Tests for src/player_factory."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.player_factory import (  # noqa: E402
    MAX_LEVEL,
    create_initial_player,
    exp_for_level,
    stats_for_level,
)


class ExpForLevelTest(unittest.TestCase):
    def test_level_2_special_case(self):
        # JS: if(lv===2)return 26
        self.assertEqual(exp_for_level(2), 26)

    def test_level_3_formula(self):
        # 10*9 + 6*3 = 108
        self.assertEqual(exp_for_level(3), 108)

    def test_level_10(self):
        # 10*100 + 60 = 1060
        self.assertEqual(exp_for_level(10), 1060)

    def test_max_level_constant(self):
        self.assertEqual(MAX_LEVEL, 100)


class StatsForLevelTest(unittest.TestCase):
    def test_level_1(self):
        s = stats_for_level(1)
        self.assertEqual(s["max_hp"], 45)  # 30+15
        self.assertEqual(s["max_mp"], 16)  # 10+6
        self.assertEqual(s["atk"], 7)      # 5+2
        self.assertEqual(s["def"], 6)      # 3+3
        self.assertEqual(s["agi"], 7)      # 5+2

    def test_level_5(self):
        s = stats_for_level(5)
        self.assertEqual(s["max_hp"], 105)
        self.assertEqual(s["max_mp"], 40)
        self.assertEqual(s["atk"], 15)
        self.assertEqual(s["def"], 18)
        self.assertEqual(s["agi"], 15)


class CreateInitialPlayerTest(unittest.TestCase):
    def test_required_keys_present(self):
        p = create_initial_player()
        for key in (
            "x", "y", "hp", "max_hp", "mp", "max_mp",
            "atk", "def", "agi", "lv", "exp", "gold",
            "weapon", "armor", "items", "spells",
            "poisoned", "in_dungeon", "boss_defeated",
            "max_zone_reached", "landmarkTreeSeen", "landmarkTowerSeen",
            "dialog_flags",
        ):
            self.assertIn(key, p)

    def test_initial_stats_match_level_1(self):
        p = create_initial_player()
        s1 = stats_for_level(1)
        self.assertEqual(p["max_hp"], s1["max_hp"])
        self.assertEqual(p["max_mp"], s1["max_mp"])
        self.assertEqual(p["atk"], s1["atk"])
        self.assertEqual(p["def"], s1["def"])
        self.assertEqual(p["agi"], s1["agi"])
        self.assertEqual(p["hp"], p["max_hp"])
        self.assertEqual(p["mp"], p["max_mp"])

    def test_starts_at_level_1(self):
        p = create_initial_player()
        self.assertEqual(p["lv"], 1)
        self.assertEqual(p["exp"], 0)


if __name__ == "__main__":
    unittest.main()
