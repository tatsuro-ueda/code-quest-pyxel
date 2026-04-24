"""Unit tests for src.shared.state.player_model.PlayerModel."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import (  # noqa: E402
    MAX_LEVEL,
    SAVE_VERSION,
    PlayerItem,
    PlayerModel,
    exp_for_level,
    stats_for_level,
)


class ExpAndStatsTest(unittest.TestCase):
    def test_exp_for_level_special_case(self):
        self.assertEqual(exp_for_level(2), 26)

    def test_exp_for_level_formula(self):
        self.assertEqual(exp_for_level(3), 108)
        self.assertEqual(exp_for_level(10), 1060)

    def test_max_level_constant(self):
        self.assertEqual(MAX_LEVEL, 100)

    def test_stats_for_level_1(self):
        self.assertEqual(
            stats_for_level(1),
            {"max_hp": 45, "max_mp": 16, "atk": 7, "defense": 6, "agi": 7},
        )

    def test_stats_for_level_5(self):
        self.assertEqual(
            stats_for_level(5),
            {"max_hp": 105, "max_mp": 40, "atk": 15, "defense": 18, "agi": 15},
        )


class PlayerModelNewGameTest(unittest.TestCase):
    def test_new_game_defaults(self):
        p = PlayerModel.new_game()
        self.assertEqual((p.x, p.y), (25, 6))
        self.assertEqual(p.lv, 1)
        self.assertEqual(p.exp, 0)
        self.assertEqual(p.gold, 50)
        self.assertEqual(p.hp, p.max_hp)
        self.assertEqual(p.mp, p.max_mp)
        self.assertEqual(p.items, [PlayerItem(id=0, qty=3)])
        self.assertTrue(p.bgm_enabled)
        self.assertTrue(p.sfx_enabled)
        self.assertTrue(p.vfx_enabled)

    def test_new_game_custom_start_position(self):
        p = PlayerModel.new_game(start_x=10, start_y=20)
        self.assertEqual((p.x, p.y), (10, 20))


class PlayerModelDamageAndHealTest(unittest.TestCase):
    def test_apply_damage_floors_at_zero(self):
        p = PlayerModel.new_game()
        p.apply_damage(1000)
        self.assertEqual(p.hp, 0)

    def test_heal_caps_at_max(self):
        p = PlayerModel.new_game()
        p.hp = 10
        p.heal(1000)
        self.assertEqual(p.hp, p.max_hp)

    def test_restore_mp_caps_at_max(self):
        p = PlayerModel.new_game()
        p.mp = 1
        p.restore_mp(100)
        self.assertEqual(p.mp, p.max_mp)

    def test_cure_poison(self):
        p = PlayerModel.new_game()
        p.poisoned = True
        self.assertTrue(p.cure_poison())
        self.assertFalse(p.poisoned)
        self.assertFalse(p.cure_poison())


class PlayerModelExpTest(unittest.TestCase):
    def test_gain_exp_below_threshold(self):
        p = PlayerModel.new_game()
        leveled = p.gain_exp(10)
        self.assertFalse(leveled)
        self.assertEqual(p.lv, 1)
        self.assertEqual(p.exp, 10)

    def test_gain_exp_triggers_level_up(self):
        p = PlayerModel.new_game()
        leveled = p.gain_exp(26)
        self.assertTrue(leveled)
        self.assertEqual(p.lv, 2)
        self.assertEqual(p.hp, p.max_hp)
        self.assertEqual(p.mp, p.max_mp)


class PlayerModelShopAndInnTest(unittest.TestCase):
    def test_stay_at_inn_success(self):
        p = PlayerModel.new_game()
        p.hp = 10
        p.mp = 5
        p.poisoned = True
        self.assertTrue(p.stay_at_inn(10))
        self.assertEqual(p.gold, 40)
        self.assertEqual(p.hp, p.max_hp)
        self.assertEqual(p.mp, p.max_mp)
        self.assertFalse(p.poisoned)

    def test_stay_at_inn_insufficient_gold(self):
        p = PlayerModel.new_game()
        p.gold = 5
        self.assertFalse(p.stay_at_inn(10))
        self.assertEqual(p.gold, 5)

    def test_buy_weapon_new(self):
        p = PlayerModel.new_game()
        self.assertTrue(p.buy_weapon(weapon_id=1, price=20))
        self.assertEqual(p.weapon, 1)
        self.assertEqual(p.gold, 30)

    def test_buy_weapon_already_owned(self):
        p = PlayerModel.new_game()
        p.weapon = 1
        self.assertFalse(p.buy_weapon(weapon_id=1, price=20))
        self.assertEqual(p.gold, 50)

    def test_buy_weapon_insufficient_gold(self):
        p = PlayerModel.new_game()
        p.gold = 5
        self.assertFalse(p.buy_weapon(weapon_id=1, price=20))
        self.assertEqual(p.weapon, 0)

    def test_buy_item_stacks_existing(self):
        p = PlayerModel.new_game()
        self.assertTrue(p.buy_item(item_id=0, price=10))
        self.assertEqual(len(p.items), 1)
        self.assertEqual(p.items[0].qty, 4)
        self.assertEqual(p.gold, 40)

    def test_buy_item_new_id(self):
        p = PlayerModel.new_game()
        self.assertTrue(p.buy_item(item_id=2, price=10))
        self.assertEqual(p.items[-1], PlayerItem(id=2, qty=1))


class PlayerModelItemUseTest(unittest.TestCase):
    def test_use_heal_when_full_returns_empty(self):
        p = PlayerModel.new_game()
        result = p.use_item({"type": "heal", "value": 10, "name": "やくそう"})
        self.assertEqual(result, "")
        self.assertEqual(p.hp, p.max_hp)

    def test_use_heal_applies(self):
        p = PlayerModel.new_game()
        p.hp = 5
        result = p.use_item({"type": "heal", "value": 20, "name": "やくそう"})
        self.assertEqual(result, "heal")
        self.assertEqual(p.hp, 25)

    def test_use_mp_heal(self):
        p = PlayerModel.new_game()
        p.mp = 2
        result = p.use_item({"type": "mp_heal", "value": 5, "name": "まほうのみず"})
        self.assertEqual(result, "mp_heal")
        self.assertEqual(p.mp, 7)

    def test_use_cure_poison_when_poisoned(self):
        p = PlayerModel.new_game()
        p.poisoned = True
        result = p.use_item({"type": "cure_poison", "name": "どくけし"})
        self.assertEqual(result, "cure_poison_ok")
        self.assertFalse(p.poisoned)

    def test_use_cure_poison_when_healthy(self):
        p = PlayerModel.new_game()
        result = p.use_item({"type": "cure_poison", "name": "どくけし"})
        self.assertEqual(result, "cure_poison_none")

    def test_use_warp(self):
        p = PlayerModel.new_game()
        result = p.use_item({"type": "warp", "name": "きろくのいし"})
        self.assertEqual(result, "warp")


class PlayerModelSnapshotTest(unittest.TestCase):
    def test_to_snapshot_round_trip(self):
        p = PlayerModel.new_game()
        p.hp = 20
        p.defense = 10
        p.landmarkTreeSeen = True
        p.dialog_flags = {"foo": True}
        p.town_talk_idx = [1, 2, 0]
        snap = p.to_snapshot(town_pos=(25, 6))
        self.assertEqual(snap["save_version"], SAVE_VERSION)
        self.assertEqual(snap["town_pos"], [25, 6])
        # defense → def に変換されてセーブされる
        self.assertIn("def", snap["player"])
        self.assertEqual(snap["player"]["def"], 10)

        restored, town_pos = PlayerModel.from_snapshot(snap)
        self.assertEqual(restored.hp, 20)
        self.assertEqual(restored.defense, 10)
        self.assertTrue(restored.landmarkTreeSeen)
        self.assertEqual(restored.dialog_flags, {"foo": True})
        self.assertEqual(restored.town_talk_idx, [1, 2, 0])
        self.assertEqual(town_pos, (25, 6))

    def test_from_snapshot_legacy_boss_defeated(self):
        snap = {
            "save_version": SAVE_VERSION,
            "town_pos": [25, 6],
            "player": {"x": 25, "y": 6, "boss_defeated": True},
        }
        restored, _ = PlayerModel.from_snapshot(snap)
        self.assertTrue(restored.glitch_lord_defeated)

    def test_from_snapshot_missing_av_defaults(self):
        snap = {
            "save_version": SAVE_VERSION,
            "town_pos": [25, 6],
            "player": {"x": 25, "y": 6},
        }
        restored, _ = PlayerModel.from_snapshot(snap)
        self.assertTrue(restored.bgm_enabled)
        self.assertTrue(restored.sfx_enabled)
        self.assertTrue(restored.vfx_enabled)

    def test_items_are_restored_as_player_items(self):
        snap = {
            "save_version": SAVE_VERSION,
            "town_pos": [25, 6],
            "player": {
                "x": 25,
                "y": 6,
                "items": [{"id": 1, "qty": 2}, {"id": 3, "qty": 5}],
            },
        }
        restored, _ = PlayerModel.from_snapshot(snap)
        self.assertEqual(
            restored.items,
            [PlayerItem(id=1, qty=2), PlayerItem(id=3, qty=5)],
        )


class PlayerModelNpcTalkTest(unittest.TestCase):
    def test_advance_rotates(self):
        p = PlayerModel.new_game()
        self.assertEqual(p.advance_npc_talk_idx(town_index=0, line_count=3), 0)
        self.assertEqual(p.advance_npc_talk_idx(town_index=0, line_count=3), 1)
        self.assertEqual(p.advance_npc_talk_idx(town_index=0, line_count=3), 2)
        self.assertEqual(p.advance_npc_talk_idx(town_index=0, line_count=3), 0)

    def test_advance_out_of_range_returns_zero(self):
        p = PlayerModel.new_game()
        self.assertEqual(p.advance_npc_talk_idx(town_index=99, line_count=3), 0)


if __name__ == "__main__":
    unittest.main()
