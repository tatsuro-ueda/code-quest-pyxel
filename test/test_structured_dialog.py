from __future__ import annotations

import sys
import unittest
from pathlib import Path


PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))

from src.scenes.dialog.model import (  # noqa: E402
    DialogValidationError,
    StructuredDialogRunner,
)


class StructuredDialogRunnerTest(unittest.TestCase):
    def test_variant_first_match_mutates_state_and_exposes_choices(self):
        data = {
            "variables": ["HasMetFairy", "AcceptedQuest_FindLute"],
            "scenes": {
                "first_meet_fairy": {
                    "variants": [
                        {
                            "when": {"HasMetFairy": False},
                            "speaker": "fairy",
                            "text": "初めまして、旅人さん。",
                            "set": {"HasMetFairy": True},
                            "choices": [
                                {"text": "困っていることは？", "next": "quest_offer_lute"},
                                {"text": "先を急ぐんだ"},
                            ],
                        },
                        {
                            "when": {"HasMetFairy": True},
                            "speaker": "fairy",
                            "text": "また会ったわね。",
                        },
                    ],
                },
                "quest_offer_lute": {
                    "text": "実は…落としたリュートを探してほしいの。",
                },
            },
        }
        state = {"HasMetFairy": False, "AcceptedQuest_FindLute": False}
        runner = StructuredDialogRunner(data)
        step = runner.start("first_meet_fairy", state=state)

        self.assertEqual(step.speaker, "fairy")
        self.assertEqual(step.text, "初めまして、旅人さん。")
        self.assertEqual(
            [choice.text for choice in step.choices],
            ["困っていることは？", "先を急ぐんだ"],
        )
        self.assertTrue(state["HasMetFairy"])

    def test_choose_moves_to_next_scene_and_applies_set(self):
        data = {
            "variables": ["AcceptedQuest_FindLute"],
            "scenes": {
                "quest_offer_lute": {
                    "text": "実は…落としたリュートを探してほしいの。",
                    "choices": [
                        {"text": "引き受ける", "next": "quest_accept_lute"},
                        {"text": "今は無理だ"},
                    ],
                },
                "quest_accept_lute": {
                    "speaker": "hero",
                    "text": "わかった、探してみるよ。",
                    "set": {"AcceptedQuest_FindLute": True},
                },
            },
        }
        state = {"AcceptedQuest_FindLute": False}
        runner = StructuredDialogRunner(data)
        first = runner.start("quest_offer_lute", state=state)
        second = runner.choose(0)

        self.assertEqual(first.text, "実は…落としたリュートを探してほしいの。")
        self.assertEqual(second.speaker, "hero")
        self.assertEqual(second.text, "わかった、探してみるよ。")
        self.assertTrue(state["AcceptedQuest_FindLute"])

    def test_load_all_lines_follows_next_chain_until_end(self):
        data = {
            "variables": ["ProfessorPhase"],
            "scenes": {
                "castle_professor": {
                    "variants": [
                        {
                            "when": {"ProfessorPhase": "early"},
                            "text": "町に立ち寄り、装備を整えよう。",
                            "next": "castle_professor_2",
                        },
                    ],
                },
                "castle_professor_2": {
                    "text": "まずは順番に見ていこう。",
                },
            },
        }
        runner = StructuredDialogRunner(data)
        lines = runner.load_all_lines(
            "castle_professor",
            state={},
            extra_context={"ProfessorPhase": "early"},
        )
        self.assertEqual(
            lines,
            ["町に立ち寄り、装備を整えよう。", "まずは順番に見ていこう。"],
        )

    def test_validation_rejects_scene_level_choices_with_variants(self):
        data = {
            "variables": ["HasMetFairy"],
            "scenes": {
                "first_meet_fairy": {
                    "choices": [
                        {"text": "困っていることは？", "next": "quest_offer_lute"},
                    ],
                    "variants": [
                        {"when": {"HasMetFairy": False}, "text": "初めまして、旅人さん。"},
                    ],
                },
                "quest_offer_lute": {
                    "text": "実は…落としたリュートを探してほしいの。",
                },
            },
        }
        with self.assertRaises(DialogValidationError):
            StructuredDialogRunner(data)

    def test_format_text_interpolates_runtime_values(self):
        data = {
            "variables": [],
            "scenes": {
                "battle.attack": {
                    "text": "{enemy}に{dmg}のダメージ！",
                },
            },
        }
        runner = StructuredDialogRunner(data)
        step = runner.start(
            "battle.attack",
            state={},
            extra_context={"enemy": "スライム", "dmg": 7},
        )
        self.assertEqual(step.text, "スライムに7のダメージ！")


class DialogueDataSmokeTest(unittest.TestCase):
    """src.game_data から読める両言語データの基本動作を検証する。"""

    def setUp(self):
        from src.game_data import DIALOGUE_JA, DIALOGUE_EN
        self.ja_runner = StructuredDialogRunner(DIALOGUE_JA)
        self.en_runner = StructuredDialogRunner(DIALOGUE_EN)

    def test_main_uses_dialogue_data(self):
        text = (PYXEL_ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("DIALOGUE_JA", text)
        self.assertIn("DIALOGUE_EN", text)

    def test_ja_overworld_battle_and_ending_scenes(self):
        runner = self.ja_runner
        self.assertEqual(
            runner.load_all_lines("town.start.entry", state={}),
            [
                "はじめのむらへようこそ！",
                "ここではプログラミングの",
                "きそをまなべます。",
            ],
        )
        self.assertEqual(
            runner.load_all_lines(
                "castle.professor.entry",
                state={},
                extra_context={"ProfessorPhase": "mid"},
            ),
            ["なぜおまえだけがきづくのか、かんがえたことはあるか？"],
        )
        self.assertEqual(
            runner.start(
                "battle.normal.attack.observe",
                state={},
                extra_context={"enemy": "10ほスライム", "dmg": 5},
            ).text,
            "じゅんばんをみなおした。10ほスライムに5のダメージ！",
        )

    def test_en_mirror_has_same_keys(self):
        ja_keys = set(self.ja_runner.scenes)
        en_keys = set(self.en_runner.scenes)
        self.assertEqual(ja_keys, en_keys)

    def test_en_battle_attack_uses_template(self):
        step = self.en_runner.start(
            "battle.normal.attack.observe",
            state={},
            extra_context={"enemy": "10-step Slime", "dmg": 5},
        )
        self.assertIn("10-step Slime", step.text)
        self.assertIn("5 damage", step.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
