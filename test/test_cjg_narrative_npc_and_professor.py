"""CJG/narrative: NPC 会話と教授イベントが state を正しく進める。

根拠:
- docs/product-requirements-narrative.md（NPC 会話 / 教授 intro / ending の進行）
- docs/customer-jobs.md Job4 / Job5（ゲームを楽しむ / 学ぶ）
- steering/done/20260425-player-dict-residue-crash-fix.md（professor_intro_seen / ending_seen 参照の取りこぼし）

NPC の話し送りは「同じ町で何周でも話せる」体験の担保、教授の intro/ending は
初回と再訪で台詞が切り替わる（`professor_intro_seen` / `professor_ending_seen`）。
前者は PlayerModel.advance_npc_talk_idx、後者は PlayerModel 属性で表現される。
2026-04-25 の player dict 取りこぼしで後者が壊れかけたので、attr アクセスで
state が進むことを固定化する。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import PlayerModel


class AdvanceNpcTalkIdxTest(unittest.TestCase):
    """町の NPC 会話カーソルが循環すること。"""

    def test_first_call_returns_zero_and_advances_to_one(self):
        pm = PlayerModel.new_game()
        current = pm.advance_npc_talk_idx(town_index=0, line_count=3)
        self.assertEqual(current, 0)
        self.assertEqual(pm.town_talk_idx[0], 1)

    def test_wraps_around_after_full_cycle(self):
        pm = PlayerModel.new_game()
        seen = [pm.advance_npc_talk_idx(0, 3) for _ in range(7)]
        self.assertEqual(seen, [0, 1, 2, 0, 1, 2, 0])

    def test_each_town_has_independent_cursor(self):
        pm = PlayerModel.new_game()
        pm.advance_npc_talk_idx(town_index=0, line_count=3)
        pm.advance_npc_talk_idx(town_index=0, line_count=3)
        pm.advance_npc_talk_idx(town_index=1, line_count=3)

        self.assertEqual(pm.town_talk_idx[0], 2)
        self.assertEqual(pm.town_talk_idx[1], 1)

    def test_line_count_zero_returns_zero_without_side_effect(self):
        """会話行が無い町でも KeyError / ZeroDivisionError を吐かないこと。"""
        pm = PlayerModel.new_game()
        original = list(pm.town_talk_idx)

        current = pm.advance_npc_talk_idx(town_index=0, line_count=0)

        self.assertEqual(current, 0)
        self.assertEqual(list(pm.town_talk_idx), original)

    def test_out_of_range_town_index_returns_zero(self):
        """未定義の town_index（学び用データ不整合）でも crash しない。"""
        pm = PlayerModel.new_game()
        current = pm.advance_npc_talk_idx(town_index=99, line_count=3)
        self.assertEqual(current, 0)


class ProfessorIntroSeenFlagTest(unittest.TestCase):
    """教授 intro / ending のフラグが 1 回目と 2 回目で分岐すること。"""

    def test_initial_flags_are_false(self):
        pm = PlayerModel.new_game()
        self.assertFalse(pm.professor_intro_seen)
        self.assertFalse(pm.professor_ending_seen)

    def test_flag_can_be_flipped_and_persists_through_snapshot(self):
        """1 回目は intro、2 回目以降は revisit に切り替える運用。snapshot でも保持される。"""
        pm = PlayerModel.new_game()
        pm.professor_intro_seen = True
        pm.professor_ending_seen = True

        snap = pm.to_snapshot(town_pos=(25, 6))
        restored, _town_pos = PlayerModel.from_snapshot(snap)

        self.assertTrue(restored.professor_intro_seen)
        self.assertTrue(restored.professor_ending_seen)

    def test_flag_is_bool_not_dict_style(self):
        """professor_intro_seen は attr アクセス（M4-4）。dict 形式の残渣があれば必ず検知する。"""
        import re

        path = ROOT / "src" / "scenes" / "professor" / "scene.py"
        text = path.read_text(encoding="utf-8")

        # professor_intro_seen / ending_seen が dict 形式（p["professor_intro_seen"] 等）で残っていないこと
        dict_access = re.search(
            r"\[\s*['\"]professor_(?:intro|ending)_seen['\"]\s*\]",
            text,
        )
        self.assertIsNone(
            dict_access,
            f"professor/scene.py に professor_*_seen の dict 風アクセスが残っている: {dict_access}",
        )

        # attr 形式で参照されていること（1 箇所以上）
        self.assertIsNotNone(
            re.search(r"\.professor_intro_seen\b", text),
            "professor/scene.py が professor_intro_seen を attr 経由で読んでいない",
        )


if __name__ == "__main__":
    unittest.main()
