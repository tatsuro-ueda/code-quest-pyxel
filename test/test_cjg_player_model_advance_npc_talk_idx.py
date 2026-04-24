"""CJG/player: PlayerModel.advance_npc_talk_idx のラウンドロビン挙動。

根拠:
- docs/product-requirements-narrative.md（町 NPC 会話の A→B→C→A...）

advance_npc_talk_idx(town_index, line_count) は現在値を返しつつ、
内部 town_talk_idx を次の値へ進める。line_count=0 は safe に 0 を返す。
town_index 範囲外は 0 を返す。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import PlayerModel


class AdvanceNpcTalkIdxTest(unittest.TestCase):
    def test_first_call_returns_zero_and_advances(self):
        pm = PlayerModel.new_game()

        result = pm.advance_npc_talk_idx(0, 3)

        self.assertEqual(result, 0)
        self.assertEqual(pm.town_talk_idx[0], 1)

    def test_second_call_returns_one(self):
        pm = PlayerModel.new_game()
        pm.advance_npc_talk_idx(0, 3)

        result = pm.advance_npc_talk_idx(0, 3)

        self.assertEqual(result, 1)

    def test_cycle_wraps_around(self):
        pm = PlayerModel.new_game()
        # 3 回呼んだら 0, 1, 2、次で 0 に戻る
        for expected in (0, 1, 2, 0, 1, 2, 0):
            with self.subTest(expected=expected):
                self.assertEqual(pm.advance_npc_talk_idx(0, 3), expected)

    def test_line_count_zero_returns_zero_without_mutation(self):
        pm = PlayerModel.new_game()
        before = list(pm.town_talk_idx)

        result = pm.advance_npc_talk_idx(0, 0)

        self.assertEqual(result, 0)
        self.assertEqual(pm.town_talk_idx, before)

    def test_each_town_advances_independently(self):
        pm = PlayerModel.new_game()

        pm.advance_npc_talk_idx(0, 3)
        pm.advance_npc_talk_idx(0, 3)
        pm.advance_npc_talk_idx(1, 3)

        self.assertEqual(pm.town_talk_idx[0], 2)
        self.assertEqual(pm.town_talk_idx[1], 1)
        self.assertEqual(pm.town_talk_idx[2], 0)

    def test_out_of_range_town_index_returns_zero(self):
        pm = PlayerModel.new_game()

        result = pm.advance_npc_talk_idx(99, 3)

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
