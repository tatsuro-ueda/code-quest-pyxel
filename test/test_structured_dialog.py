from __future__ import annotations

import builtins
import importlib
import sys
import textwrap
import unittest
from pathlib import Path


PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))

from src.structured_dialog import (  # noqa: E402
    DialogValidationError,
    StructuredDialogRunner,
)


class StructuredDialogRunnerTest(unittest.TestCase):
    def _write_dialogue(self, name: str, body: str) -> Path:
        path = PYXEL_ROOT / "test" / name
        path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_variant_first_match_mutates_state_and_exposes_choices(self):
        path = self._write_dialogue(
            "_tmp_variants.yaml",
            """
            variables:
              - HasMetFairy
              - AcceptedQuest_FindLute
            scenes:
              first_meet_fairy:
                variants:
                  - when:
                      HasMetFairy: false
                    speaker: fairy
                    text: "初めまして、旅人さん。"
                    set:
                      HasMetFairy: true
                    choices:
                      - text: "困っていることは？"
                        next: quest_offer_lute
                      - text: "先を急ぐんだ"
                  - when:
                      HasMetFairy: true
                    speaker: fairy
                    text: "また会ったわね。"
              quest_offer_lute:
                text: "実は…落としたリュートを探してほしいの。"
            """,
        )
        state = {"HasMetFairy": False, "AcceptedQuest_FindLute": False}

        runner = StructuredDialogRunner(path)
        step = runner.start("first_meet_fairy", state=state)

        self.assertEqual(step.speaker, "fairy")
        self.assertEqual(step.text, "初めまして、旅人さん。")
        self.assertEqual(
            [choice.text for choice in step.choices],
            ["困っていることは？", "先を急ぐんだ"],
        )
        self.assertTrue(state["HasMetFairy"])

    def test_choose_moves_to_next_scene_and_applies_set(self):
        path = self._write_dialogue(
            "_tmp_choices.yaml",
            """
            variables:
              - AcceptedQuest_FindLute
            scenes:
              quest_offer_lute:
                text: "実は…落としたリュートを探してほしいの。"
                choices:
                  - text: "引き受ける"
                    next: quest_accept_lute
                  - text: "今は無理だ"
              quest_accept_lute:
                speaker: hero
                text: "わかった、探してみるよ。"
                set:
                  AcceptedQuest_FindLute: true
            """,
        )
        state = {"AcceptedQuest_FindLute": False}

        runner = StructuredDialogRunner(path)
        first = runner.start("quest_offer_lute", state=state)
        second = runner.choose(0)

        self.assertEqual(first.text, "実は…落としたリュートを探してほしいの。")
        self.assertEqual(second.speaker, "hero")
        self.assertEqual(second.text, "わかった、探してみるよ。")
        self.assertTrue(state["AcceptedQuest_FindLute"])

    def test_load_all_lines_follows_next_chain_until_end(self):
        path = self._write_dialogue(
            "_tmp_linear.yaml",
            """
            variables:
              - ProfessorPhase
            scenes:
              castle_professor:
                variants:
                  - when:
                      ProfessorPhase: early
                    text: "町に立ち寄り、装備を整えよう。"
                    next: castle_professor_2
              castle_professor_2:
                text: "まずは順番に見ていこう。"
            """,
        )

        runner = StructuredDialogRunner(path)
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
        path = self._write_dialogue(
            "_tmp_invalid.yaml",
            """
            variables:
              - HasMetFairy
            scenes:
              first_meet_fairy:
                choices:
                  - text: "困っていることは？"
                    next: quest_offer_lute
                variants:
                  - when:
                      HasMetFairy: false
                    text: "初めまして、旅人さん。"
              quest_offer_lute:
                text: "実は…落としたリュートを探してほしいの。"
            """,
        )

        with self.assertRaises(DialogValidationError):
            StructuredDialogRunner(path)

    def test_format_text_interpolates_runtime_values(self):
        path = self._write_dialogue(
            "_tmp_template.yaml",
            """
            variables: []
            scenes:
              battle.attack:
                text: "{enemy}に{dmg}のダメージ！"
            """,
        )

        runner = StructuredDialogRunner(path)
        step = runner.start(
            "battle.attack",
            state={},
            extra_context={"enemy": "スライム", "dmg": 7},
        )

        self.assertEqual(step.text, "スライムに7のダメージ！")


class StructuredDialogFileSmokeTest(unittest.TestCase):
    def test_main_uses_assets_dialogue_yaml_path(self):
        text = (PYXEL_ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn('StructuredDialogRunner("assets/dialogue.yaml")', text)

    def test_dialogue_yaml_contains_overworld_battle_and_ending_scenes(self):
        runner = StructuredDialogRunner(PYXEL_ROOT / "assets" / "dialogue.yaml")

        self.assertEqual(
            runner.load_all_lines("town.start.entry", state={}),
            [
                "はじめの村へようこそ！",
                "ここではプログラミングの",
                "基礎を学べます。",
            ],
        )
        self.assertEqual(
            runner.load_all_lines(
                "castle.professor.entry",
                state={},
                extra_context={"ProfessorPhase": "mid"},
            ),
            ["なぜお前だけが気づくのか、考えたことはあるか？"],
        )
        self.assertEqual(
            runner.load_all_lines("dungeon.glitch.enter", state={}),
            ["グリッチのサーバーに侵入した…エラーメッセージが飛び交う。ここに、すべての原因がある。"],
        )
        self.assertEqual(
            runner.load_all_lines("dungeon.glitch.exit", state={}),
            ["サーバーから脱出した。外の空気が、少し違って感じる。"],
        )
        self.assertEqual(
            runner.load_all_lines("landmark.tree.first", state={}),
            ["世界樹だ。なぜか落ち着く。気持ちが、考えが、自由だ。"],
        )
        self.assertEqual(
            runner.load_all_lines("landmark.tower.first", state={}),
            ["通信塔だ。声が流れてくる。「そんなに考えなくていい」「みんなと同じでいい」"],
        )
        self.assertEqual(
            runner.start(
                "battle.normal.attack.observe",
                state={},
                extra_context={"enemy": "10ほスライム", "dmg": 5},
            ).text,
            "順番を見直した。10ほスライムに5のダメージ！",
        )
        self.assertEqual(
            runner.start(
                "battle.normal.victory.early",
                state={},
                extra_context={"enemy": "10ほスライム", "exp": 5, "gold": 3},
            ).text,
            "10ほスライムを理解した！少し分かった。5EXPと3Cを手に入れた！",
        )
        self.assertEqual(
            runner.load_all_lines("ending.main.line01", state={})[:2],
            ["おめでとう！", "魔王グリッチを倒した！"],
        )

    def test_dialogue_yaml_loads_without_external_yaml_package(self):
        structured_dialog_name = "src.structured_dialog"
        original_yaml_module = sys.modules.pop("yaml", None)
        original_structured_dialog = sys.modules.pop(structured_dialog_name, None)
        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "yaml":
                raise ModuleNotFoundError("No module named 'yaml'")
            return real_import(name, globals, locals, fromlist, level)

        try:
            builtins.__import__ = fake_import
            module = importlib.import_module(structured_dialog_name)
            runner = module.StructuredDialogRunner(PYXEL_ROOT / "assets" / "dialogue.yaml")
            lines = runner.load_all_lines("town.start.entry", state={})
        finally:
            builtins.__import__ = real_import
            sys.modules.pop(structured_dialog_name, None)
            if original_structured_dialog is not None:
                sys.modules[structured_dialog_name] = original_structured_dialog
            if original_yaml_module is not None:
                sys.modules["yaml"] = original_yaml_module

        self.assertEqual(
            lines,
            [
                "はじめの村へようこそ！",
                "ここではプログラミングの",
                "基礎を学べます。",
            ],
        )

    def test_dialogue_yaml_skips_pyyaml_import_on_emscripten(self):
        structured_dialog_name = "src.structured_dialog"
        original_yaml_module = sys.modules.pop("yaml", None)
        original_structured_dialog = sys.modules.pop(structured_dialog_name, None)
        original_platform = sys.platform
        real_import = builtins.__import__
        yaml_import_attempts = []

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "yaml":
                yaml_import_attempts.append(name)
                raise AssertionError("emscripten path must not import yaml")
            return real_import(name, globals, locals, fromlist, level)

        try:
            sys.platform = "emscripten"
            builtins.__import__ = fake_import
            module = importlib.import_module(structured_dialog_name)
            runner = module.StructuredDialogRunner(PYXEL_ROOT / "assets" / "dialogue.yaml")
            lines = runner.load_all_lines("town.start.entry", state={})
        finally:
            builtins.__import__ = real_import
            sys.platform = original_platform
            sys.modules.pop(structured_dialog_name, None)
            if original_structured_dialog is not None:
                sys.modules[structured_dialog_name] = original_structured_dialog
            if original_yaml_module is not None:
                sys.modules["yaml"] = original_yaml_module

        self.assertEqual(yaml_import_attempts, [])
        self.assertEqual(
            lines,
            [
                "はじめの村へようこそ！",
                "ここではプログラミングの",
                "基礎を学べます。",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
