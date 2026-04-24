"""CJG/dialog_runner: StructuredDialogRunner の start / choose / continue。

根拠:
- docs/product-requirements-narrative.md（分岐会話）

最小限のテスト: start で最初のステップを返し、continue_dialog で next を辿り、
choose で choice.next_scene に進み、終端で None を返す。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.dialog_runner import (
    DialogValidationError,
    StructuredDialogRunner,
)


SAMPLE = {
    "variables": ["mood"],
    "scenes": {
        "start": {
            "text": "はじまりの話",
            "next": "middle",
        },
        "middle": {
            "text": "つぎの話",
            "choices": [
                {"text": "進む", "next": "good"},
                {"text": "戻る", "next": "bad"},
            ],
        },
        "good": {"text": "よい結末"},
        "bad": {"text": "わるい結末"},
    },
}


class StartAndContinueTest(unittest.TestCase):
    def test_start_returns_first_scene(self):
        runner = StructuredDialogRunner(SAMPLE)

        step = runner.start("start")

        self.assertEqual(step.text, "はじまりの話")
        self.assertEqual(step.next_scene, "middle")

    def test_continue_dialog_follows_next_scene(self):
        runner = StructuredDialogRunner(SAMPLE)
        runner.start("start")

        step = runner.continue_dialog()

        self.assertIsNotNone(step)
        self.assertEqual(step.text, "つぎの話")
        self.assertEqual(len(step.choices), 2)


class ChoiceTest(unittest.TestCase):
    def test_choose_advances_to_choice_scene(self):
        runner = StructuredDialogRunner(SAMPLE)
        runner.start("middle")

        step = runner.choose(0)

        self.assertIsNotNone(step)
        self.assertEqual(step.text, "よい結末")

    def test_choose_out_of_range_raises_index_error(self):
        runner = StructuredDialogRunner(SAMPLE)
        runner.start("middle")

        with self.assertRaises(IndexError):
            runner.choose(99)

    def test_choose_without_choices_raises_runtime_error(self):
        runner = StructuredDialogRunner(SAMPLE)
        runner.start("start")  # choices は無い

        with self.assertRaises(RuntimeError):
            runner.choose(0)

    def test_choose_before_start_raises_runtime_error(self):
        runner = StructuredDialogRunner(SAMPLE)

        with self.assertRaises(RuntimeError):
            runner.choose(0)


class LoadAllLinesTest(unittest.TestCase):
    def test_load_all_lines_collects_chain_text(self):
        runner = StructuredDialogRunner(SAMPLE)

        lines = runner.load_all_lines("start")

        self.assertIn("はじまりの話", lines)
        # middle に choices があるので middle で止まる（choices を越えない）
        self.assertIn("つぎの話", lines)
        self.assertNotIn("よい結末", lines)


class ValidationTest(unittest.TestCase):
    def test_non_dict_source_raises(self):
        with self.assertRaises(DialogValidationError):
            StructuredDialogRunner(["not", "a", "dict"])

    def test_empty_scenes_raises(self):
        with self.assertRaises(DialogValidationError):
            StructuredDialogRunner({"variables": [], "scenes": {}})


if __name__ == "__main__":
    unittest.main()
