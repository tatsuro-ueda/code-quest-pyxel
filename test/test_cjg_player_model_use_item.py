"""CJG/player: PlayerModel.use_item が kind ごとに期待効果を返す。

根拠:
- docs/product-requirements-battle.md / -narrative.md（heal/mp_heal/cure/warp の
  分岐）
- docs/customer-jobs.md Make3

PlayerModel.use_item(item_data) は以下の戻り値を返す純粋ルール：
- "heal" : HP 増加（満タン時は ""）
- "mp_heal" : MP 増加
- "cure_poison_ok" : 毒解除成功
- "cure_poison_none" : 毒なし
- "warp" : 呼び出し側で座標更新（Model 自身は座標を触らない）
- "" : 効果無し
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import PlayerModel


class HealUseItemTest(unittest.TestCase):
    def test_heal_below_full_returns_heal_and_increases_hp(self):
        pm = PlayerModel.new_game()
        pm.hp = 1

        result = pm.use_item({"type": "heal", "value": 20, "name": "やくそう"})

        self.assertEqual(result, "heal")
        self.assertGreater(pm.hp, 1)

    def test_heal_at_full_returns_empty_and_does_not_consume(self):
        pm = PlayerModel.new_game()
        # 満タン
        result = pm.use_item({"type": "heal", "value": 20, "name": "やくそう"})

        self.assertEqual(result, "")
        self.assertEqual(pm.hp, pm.max_hp)

    def test_heal_value_is_capped_at_max_hp(self):
        pm = PlayerModel.new_game()
        pm.hp = 1

        pm.use_item({"type": "heal", "value": 9999, "name": "ちょうやくそう"})

        self.assertEqual(pm.hp, pm.max_hp)


class MpHealUseItemTest(unittest.TestCase):
    def test_mp_heal_increases_mp(self):
        pm = PlayerModel.new_game()
        pm.mp = 0

        result = pm.use_item({"type": "mp_heal", "value": 10, "name": "まりょくのたね"})

        self.assertEqual(result, "mp_heal")
        self.assertEqual(pm.mp, 10)


class CurePoisonUseItemTest(unittest.TestCase):
    def test_cure_poison_when_poisoned_returns_ok(self):
        pm = PlayerModel.new_game()
        pm.poisoned = True

        result = pm.use_item({"type": "cure_poison", "name": "どくけしそう"})

        self.assertEqual(result, "cure_poison_ok")
        self.assertFalse(pm.poisoned)

    def test_cure_poison_when_not_poisoned_returns_none(self):
        pm = PlayerModel.new_game()
        pm.poisoned = False

        result = pm.use_item({"type": "cure_poison", "name": "どくけしそう"})

        self.assertEqual(result, "cure_poison_none")


class WarpUseItemTest(unittest.TestCase):
    def test_warp_returns_warp_marker(self):
        """warp は座標を Model 内で更新せず呼び出し側に委ねる。"""
        pm = PlayerModel.new_game()
        pm.x = 10
        pm.y = 20

        result = pm.use_item({"type": "warp", "name": "まちのいし"})

        self.assertEqual(result, "warp")
        # 座標は変わらない（caller が game.last_town_pos を使って更新する）
        self.assertEqual((pm.x, pm.y), (10, 20))


class UnknownKindTest(unittest.TestCase):
    def test_unknown_type_returns_empty_string(self):
        """未定義 kind は "" を返し副作用なし（将来追加に対する安全網）。"""
        pm = PlayerModel.new_game()

        result = pm.use_item({"type": "mystery", "name": "ふしぎなもの"})

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
