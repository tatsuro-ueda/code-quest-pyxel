"""CJG/player: stats_for_level と exp_for_level の進行性。

根拠:
- docs/product-requirements-battle.md（レベルアップによるステータス上昇）

各 level の max_hp / max_mp / atk / def / agi は level が上がると
単調非減少。exp_for_level は lv が増えると必要 exp が増える。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import (
    MAX_LEVEL,
    exp_for_level,
    stats_for_level,
)


class ExpForLevelMonotonicTest(unittest.TestCase):
    def test_exp_is_non_decreasing_as_level_grows(self):
        prev = -1
        for lv in range(2, MAX_LEVEL + 1):
            with self.subTest(lv=lv):
                need = exp_for_level(lv)
                self.assertGreater(need, prev)
                prev = need


class StatsForLevelProgressionTest(unittest.TestCase):
    def test_max_hp_is_non_decreasing(self):
        prev = -1
        for lv in range(1, MAX_LEVEL + 1):
            with self.subTest(lv=lv):
                s = stats_for_level(lv)
                self.assertGreaterEqual(s["max_hp"], prev)
                prev = s["max_hp"]

    def test_max_mp_is_non_decreasing(self):
        prev = -1
        for lv in range(1, MAX_LEVEL + 1):
            with self.subTest(lv=lv):
                s = stats_for_level(lv)
                self.assertGreaterEqual(s["max_mp"], prev)
                prev = s["max_mp"]

    def test_atk_is_non_decreasing(self):
        prev = -1
        for lv in range(1, MAX_LEVEL + 1):
            with self.subTest(lv=lv):
                s = stats_for_level(lv)
                self.assertGreaterEqual(s["atk"], prev)
                prev = s["atk"]

    def test_level_1_has_positive_stats(self):
        s = stats_for_level(1)
        self.assertGreater(s["max_hp"], 0)
        self.assertGreater(s["max_mp"], 0)
        self.assertGreater(s["atk"], 0)


if __name__ == "__main__":
    unittest.main()
