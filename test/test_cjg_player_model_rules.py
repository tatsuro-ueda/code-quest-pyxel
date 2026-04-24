"""CJG/player: PlayerModel のビジネスルール（ダメージ / 経験値 / 毒 / 宿 / 購入）。

根拠:
- docs/product-requirements-battle.md（ダメージ / 経験値 / レベルアップ）
- docs/product-requirements-platform.md（セーブ互換）
- docs/customer-jobs.md Job4（ゲームを楽しむ）

PlayerModel は framework-rule.md M4-4 に従い、ルールをメソッドとして持つ。
いずれも Pyxel / Scene に依存しないため、境界値・負値・満タン時などの
コーナーを直接検証する。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import PlayerItem, PlayerModel, exp_for_level


class ApplyDamageTest(unittest.TestCase):
    def test_damage_reduces_hp_by_amount(self):
        pm = PlayerModel.new_game()
        before = pm.hp
        pm.apply_damage(7)
        self.assertEqual(pm.hp, before - 7)

    def test_damage_does_not_go_below_zero(self):
        pm = PlayerModel.new_game()
        pm.apply_damage(9999)
        self.assertEqual(pm.hp, 0)

    def test_zero_damage_is_noop(self):
        pm = PlayerModel.new_game()
        before = pm.hp
        pm.apply_damage(0)
        self.assertEqual(pm.hp, before)


class HealAndMpTest(unittest.TestCase):
    def test_heal_caps_at_max_hp(self):
        pm = PlayerModel.new_game()
        pm.hp = pm.max_hp - 3
        pm.heal(9999)
        self.assertEqual(pm.hp, pm.max_hp)

    def test_restore_mp_caps_at_max_mp(self):
        pm = PlayerModel.new_game()
        pm.mp = 0
        pm.restore_mp(9999)
        self.assertEqual(pm.mp, pm.max_mp)


class CurePoisonTest(unittest.TestCase):
    def test_cure_while_poisoned_returns_true_and_clears_flag(self):
        pm = PlayerModel.new_game()
        pm.poisoned = True

        result = pm.cure_poison()

        self.assertTrue(result)
        self.assertFalse(pm.poisoned)

    def test_cure_while_not_poisoned_returns_false(self):
        pm = PlayerModel.new_game()
        pm.poisoned = False

        result = pm.cure_poison()

        self.assertFalse(result)


class GainExpAndLevelUpTest(unittest.TestCase):
    def test_exp_below_threshold_does_not_level_up(self):
        pm = PlayerModel.new_game()

        leveled = pm.gain_exp(5)

        self.assertFalse(leveled)
        self.assertEqual(pm.lv, 1)

    def test_crossing_threshold_levels_up_once(self):
        pm = PlayerModel.new_game()
        # exp_for_level(2) 以上 exp_for_level(3) 未満を与える
        need = exp_for_level(2)

        leveled = pm.gain_exp(need)

        self.assertTrue(leveled)
        self.assertEqual(pm.lv, 2)
        self.assertEqual(pm.hp, pm.max_hp, "レベルアップ時に HP が全回復していない")
        self.assertEqual(pm.mp, pm.max_mp, "レベルアップ時に MP が全回復していない")

    def test_bulk_exp_levels_up_multiple_times(self):
        pm = PlayerModel.new_game()
        need_for_4 = exp_for_level(4)

        leveled = pm.gain_exp(need_for_4)

        self.assertTrue(leveled)
        self.assertGreaterEqual(pm.lv, 4)


class InnTest(unittest.TestCase):
    def test_pay_inn_heals_and_cures(self):
        pm = PlayerModel.new_game()
        pm.hp = 1
        pm.mp = 0
        pm.poisoned = True
        pm.gold = 500

        ok = pm.stay_at_inn(5)

        self.assertTrue(ok)
        self.assertEqual(pm.gold, 495)
        self.assertEqual(pm.hp, pm.max_hp)
        self.assertEqual(pm.mp, pm.max_mp)
        self.assertFalse(pm.poisoned)

    def test_insufficient_gold_rejects_inn(self):
        pm = PlayerModel.new_game()
        pm.gold = 0
        pm.hp = 1

        ok = pm.stay_at_inn(5)

        self.assertFalse(ok)
        self.assertEqual(pm.hp, 1)


class BuyWeaponArmorTest(unittest.TestCase):
    def test_buy_weapon_sets_slot_and_deducts_gold(self):
        pm = PlayerModel.new_game()
        before = pm.gold

        ok = pm.buy_weapon(3, 10)

        self.assertTrue(ok)
        self.assertEqual(pm.weapon, 3)
        self.assertEqual(pm.gold, before - 10)

    def test_buy_weapon_rejects_when_already_owned(self):
        pm = PlayerModel.new_game()
        pm.weapon = 3
        before = pm.gold

        ok = pm.buy_weapon(3, 10)

        self.assertFalse(ok)
        self.assertEqual(pm.gold, before)

    def test_buy_armor_rejects_when_insufficient_gold(self):
        pm = PlayerModel.new_game()
        pm.gold = 0

        ok = pm.buy_armor(2, 100)

        self.assertFalse(ok)
        self.assertEqual(pm.armor, 0)


class BuyItemStackTest(unittest.TestCase):
    def test_buy_item_adds_new_stack(self):
        pm = PlayerModel.new_game()
        pm.items = []

        ok = pm.buy_item(1, 5)

        self.assertTrue(ok)
        self.assertEqual(len(pm.items), 1)
        self.assertEqual(pm.items[0].id, 1)
        self.assertEqual(pm.items[0].qty, 1)

    def test_buy_same_item_stacks_quantity(self):
        pm = PlayerModel.new_game()
        pm.items = [PlayerItem(id=1, qty=2)]

        ok = pm.buy_item(1, 5)

        self.assertTrue(ok)
        self.assertEqual(len(pm.items), 1)
        self.assertEqual(pm.items[0].qty, 3)


if __name__ == "__main__":
    unittest.main()
