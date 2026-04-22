from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data  # noqa: E402
from tools import gen_data, sync_main_data  # noqa: E402


class DialogueGenDataTest(unittest.TestCase):
    def test_dialogue_target_is_registered(self):
        self.assertIn("dialogue", gen_data.TARGETS)


class DialogueLoaderTest(unittest.TestCase):
    def test_load_dialogue_returns_ja_and_en_data(self):
        ja = game_data.load_dialogue("ja")
        en = game_data.load_dialogue("en")

        self.assertEqual(
            ja["scenes"]["town.start.entry"]["text"],
            "はじめのむらへようこそ！",
        )
        self.assertEqual(
            en["scenes"]["town.start.entry"]["text"],
            "Welcome to the starter village!",
        )

    def test_load_dialogue_rejects_unknown_language(self):
        with self.assertRaises(ValueError):
            game_data.load_dialogue("fr")


class SyncMainDialogueTest(unittest.TestCase):
    def test_build_inlined_dialogue_section_contains_generated_constants(self):
        section = sync_main_data.build_inlined_dialogue_section()

        self.assertIn("DIALOGUE_JA", section)
        self.assertIn("DIALOGUE_EN", section)
        self.assertIn("generated from assets/dialogue.yaml", section)

    def test_sync_file_updates_preview_like_bundle_dialogue_section(self):
        stub = """header
# === inlined: src/game_data.py ===
OLD_GAME_DATA

# === inlined: src/generated/dialogue.py ===
OLD_DIALOGUE_DATA

# === inlined: src/jp_font_data.py ===
footer
"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "main_development.py"
            target.write_text(stub, encoding="utf-8")

            result = sync_main_data.sync_file(target)

            self.assertEqual(result, 0)
            content = target.read_text(encoding="utf-8")
            self.assertIn("DIALOGUE_JA", content)
            self.assertIn("DIALOGUE_EN", content)
            self.assertIn("'boss.glitch.prebattle_01': {", content)
            self.assertNotIn("OLD_DIALOGUE_DATA", content)


if __name__ == "__main__":
    unittest.main()
