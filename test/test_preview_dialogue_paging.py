from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_preview_module():
    source = (ROOT / "main_preview.py").read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType("main_preview_for_dialogue_paging_test")
    module.__file__ = str((ROOT / "main_preview.py").resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


class PreviewDialoguePagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preview = load_preview_module()

    def make_game(self):
        game = self.preview.Game.__new__(self.preview.Game)
        self.preview.pyxel.rect = lambda *args, **kwargs: None
        self.preview.pyxel.rectb = lambda *args, **kwargs: None
        self.preview.pyxel.cls = lambda *args, **kwargs: None
        self.preview.pyxel.frame_count = 0
        return game

    def test_draw_professor_intro_uses_choice_prompt(self):
        game = self.make_game()
        game.professor_choice_prompt = "first line\nsecond line"
        game.professor_choice_active = True
        game.professor_choice_cursor = 1
        game.has_jp_font = True
        captured: list[tuple[int, int, str, int]] = []
        game.text = lambda x, y, s, col: captured.append((x, y, s, col))

        self.preview.Game.draw_professor_intro(game)

        rendered = [text for _, _, text, _ in captured]
        self.assertIn("first line", rendered)
        self.assertIn("second line", rendered)
        self.assertTrue(any("うけいれる" in text for text in rendered))
        self.assertTrue(any("ことわる" in text for text in rendered))

    def test_enter_professor_intro_routes_pages_to_fullscreen_dialog(self):
        game = self.make_game()
        game.player = {"professor_intro_seen": False}
        game._dialog_lines = MagicMock(
            return_value=["page 1", "page 2", "どうする？"]
        )
        game._enter_fullscreen_dialog = MagicMock()

        self.preview.Game._enter_professor_intro(game)

        game._dialog_lines.assert_called_once_with("castle.professor.intro_01")
        self.assertEqual(game.professor_choice_prompt, "どうする？")
        game._enter_fullscreen_dialog.assert_called_once()
        args, kwargs = game._enter_fullscreen_dialog.call_args
        self.assertEqual(args[0], ["page 1", "page 2"])
        self.assertEqual(kwargs["on_complete"], game._enter_professor_intro_choice)
