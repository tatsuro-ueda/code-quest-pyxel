from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_main_module():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType("main_for_dialogue_paging_test")
    module.__file__ = str((ROOT / "main.py").resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


class DialoguePagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def make_game(self):
        game = self.main.Game.__new__(self.main.Game)
        self.main.pyxel.rect = lambda *args, **kwargs: None
        self.main.pyxel.rectb = lambda *args, **kwargs: None
        self.main.pyxel.cls = lambda *args, **kwargs: None
        self.main.pyxel.frame_count = 0
        return game

    def test_current_dialog_page_lines_returns_only_current_phrase(self):
        game = self.make_game()

        lines = game._current_dialog_page_lines(
            ["first page", "second page", "third page"],
            0,
            max_chars=28,
            max_rows=3,
        )

        self.assertEqual(lines, ["first page"])

    def test_current_dialog_page_lines_splits_newlines(self):
        game = self.make_game()

        lines = game._current_dialog_page_lines(
            ["top line\nbottom line", "next page"],
            0,
            max_chars=28,
            max_rows=3,
        )

        self.assertEqual(lines, ["top line", "bottom line"])

    def test_advance_dialog_page_reports_when_sequence_finishes(self):
        game = self.make_game()

        next_index, done = game._advance_dialog_page(0, ["a", "b"])
        self.assertEqual((next_index, done), (1, False))

        next_index, done = game._advance_dialog_page(1, ["a", "b"])
        self.assertEqual((next_index, done), (2, True))

    def test_draw_message_window_uses_only_current_page(self):
        game = self.make_game()
        game.msg_lines = ["first page", "second page", "third page"]
        game.msg_index = 0
        captured: list[tuple[int, int, str, int]] = []
        game.text = lambda x, y, s, col: captured.append((x, y, s, col))

        self.main.Game.draw_message_window(game)

        rendered = [text for _, _, text, _ in captured]
        self.assertIn("first page", rendered)
        self.assertNotIn("second page", rendered)
        self.assertNotIn("third page", rendered)

    def test_draw_professor_intro_uses_only_current_page(self):
        game = self.make_game()
        game.professor_intro_lines = ["first line\nsecond line", "later page"]
        game.professor_intro_idx = 0
        game.professor_choice_active = False
        captured: list[tuple[int, int, str, int]] = []
        game.text = lambda x, y, s, col: captured.append((x, y, s, col))

        self.main.Game.draw_professor_intro(game)

        rendered = [text for _, _, text, _ in captured]
        self.assertIn("first line", rendered)
        self.assertIn("second line", rendered)
        self.assertNotIn("later page", rendered)

    def test_update_professor_intro_enters_choice_after_last_page(self):
        game = self.make_game()
        game.professor_intro_lines = ["page 1", "page 2"]
        game.professor_intro_idx = 0
        game.professor_choice_active = False
        game._btnp = lambda *_args, **_kwargs: True

        self.main.Game.update_professor_intro(game)
        self.assertEqual(game.professor_intro_idx, 1)
        self.assertFalse(game.professor_choice_active)

        self.main.Game.update_professor_intro(game)
        self.assertEqual(game.professor_intro_idx, 2)
        self.assertTrue(game.professor_choice_active)


if __name__ == "__main__":
    unittest.main()
