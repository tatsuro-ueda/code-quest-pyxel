"""CJG/player: PlayerModel.new_game のファクトリ契約。

根拠:
- docs/product-requirements-platform.md（ニューゲーム時の初期ステータス）
- docs/customer-jobs.md Job4（最初から遊び始める）

new_game(start_x, start_y) はレベル 1 でフル HP/MP・やくそう x3 を持ち、
装備は 0 番（素手 / ふだんぎ）。任意の start 座標を受け取り、在庫が
常に 1 つ（やくそう）は含まれる（序盤の安全網）。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import PlayerItem, PlayerModel


class NewGameDefaultsTest(unittest.TestCase):
    def test_default_level_is_one(self):
        pm = PlayerModel.new_game()
        self.assertEqual(pm.lv, 1)
        self.assertEqual(pm.exp, 0)

    def test_full_hp_and_mp_at_start(self):
        pm = PlayerModel.new_game()
        self.assertEqual(pm.hp, pm.max_hp)
        self.assertEqual(pm.mp, pm.max_mp)

    def test_default_weapon_and_armor_are_index_zero(self):
        pm = PlayerModel.new_game()
        self.assertEqual(pm.weapon, 0)
        self.assertEqual(pm.armor, 0)

    def test_starting_gold_is_positive(self):
        pm = PlayerModel.new_game()
        self.assertGreater(pm.gold, 0)

    def test_has_at_least_one_item(self):
        pm = PlayerModel.new_game()
        self.assertGreater(len(pm.items), 0)
        for item in pm.items:
            self.assertIsInstance(item, PlayerItem)
            self.assertGreater(item.qty, 0)


class NewGameStartPositionTest(unittest.TestCase):
    def test_default_start_position(self):
        pm = PlayerModel.new_game()
        self.assertEqual(pm.x, 25)
        self.assertEqual(pm.y, 6)

    def test_custom_start_position(self):
        pm = PlayerModel.new_game(start_x=10, start_y=20)
        self.assertEqual(pm.x, 10)
        self.assertEqual(pm.y, 20)


class NewGameFlagsTest(unittest.TestCase):
    def test_no_progression_flags_are_set_at_start(self):
        pm = PlayerModel.new_game()
        self.assertFalse(pm.in_dungeon)
        self.assertFalse(pm.glitch_lord_defeated)
        self.assertFalse(pm.professor_intro_seen)
        self.assertFalse(pm.professor_ending_seen)
        self.assertFalse(pm.landmarkTreeSeen)
        self.assertFalse(pm.landmarkTowerSeen)
        self.assertFalse(pm.poisoned)


if __name__ == "__main__":
    unittest.main()
