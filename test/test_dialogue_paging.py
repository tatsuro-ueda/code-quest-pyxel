from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from src.scenes.explore.scene import ExploreScene


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


def _pm_from_dict(d):
    from src.shared.state.player_model import PlayerModel, PlayerItem
    pm = PlayerModel()
    for k, v in d.items():
        attr = "defense" if k == "def" else k
        if attr == "items":
            v = [PlayerItem(id=i["id"], qty=i["qty"]) for i in v]
        setattr(pm, attr, v)
    return pm


class DialoguePagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def make_game(self):
        from src.scenes.ending.scene import EndingScene
        from src.scenes.professor.scene import ProfessorScene
        from src.shared.services.message_display import MessageDisplay
        from src.shared.services.input_bindings import InputStateTracker
        game = self.main.Game.__new__(self.main.Game)
        game.messages = MessageDisplay(game=game)
        game.input_state = InputStateTracker()
        game.explore_scene = ExploreScene(game=game)
        game.ending_scene = EndingScene(game=game)
        game.professor_scene = ProfessorScene(game=game)
        self.main.pyxel.rect = lambda *args, **kwargs: None
        self.main.pyxel.rectb = lambda *args, **kwargs: None
        self.main.pyxel.cls = lambda *args, **kwargs: None
        self.main.pyxel.frame_count = 0
        return game

    def test_current_dialog_page_lines_returns_only_current_phrase(self):
        game = self.make_game()

        lines = game.messages.current_page_lines(
            ["first page", "second page", "third page"],
            0,
            max_chars=28,
            max_rows=3,
        )

        self.assertEqual(lines, ["first page"])

    def test_current_dialog_page_lines_splits_newlines(self):
        game = self.make_game()

        lines = game.messages.current_page_lines(
            ["top line\nbottom line", "next page"],
            0,
            max_chars=28,
            max_rows=3,
        )

        self.assertEqual(lines, ["top line", "bottom line"])

    def test_advance_dialog_page_reports_when_sequence_finishes(self):
        game = self.make_game()

        next_index, done = game.messages.advance_page(0, ["a", "b"])
        self.assertEqual((next_index, done), (1, False))

        next_index, done = game.messages.advance_page(1, ["a", "b"])
        self.assertEqual((next_index, done), (2, True))

    def test_draw_message_window_uses_only_current_page(self):
        game = self.make_game()
        game.messages.lines = ["first page", "second page", "third page"]
        game.messages.index = 0
        captured: list[tuple[int, int, str, int]] = []
        game.messages.text = lambda x, y, s, col: captured.append((x, y, s, col))

        game.messages.draw_window()

        rendered = [text for _, _, text, _ in captured]
        self.assertIn("first page", rendered)
        self.assertNotIn("second page", rendered)
        self.assertNotIn("third page", rendered)

    def test_draw_professor_intro_uses_only_current_page(self):
        game = self.make_game()
        game.professor_scene.model.intro_lines = ["first line\nsecond line", "later page"]
        game.professor_scene.model.intro_idx = 0
        game.professor_scene.model.choice_active = False
        captured: list[tuple[int, int, str, int]] = []
        game.messages.text = lambda x, y, s, col: captured.append((x, y, s, col))

        game.professor_scene.draw_intro()

        rendered = [text for _, _, text, _ in captured]
        self.assertIn("first line", rendered)
        self.assertIn("second line", rendered)
        self.assertNotIn("later page", rendered)

    def test_update_professor_intro_enters_choice_after_last_page(self):
        game = self.make_game()
        game.professor_scene.model.intro_lines = ["page 1", "page 2"]
        game.professor_scene.model.intro_idx = 0
        game.professor_scene.model.choice_active = False
        game.input_state.btnp = lambda *_args, **_kwargs: True

        game.professor_scene.update_intro()
        self.assertEqual(game.professor_scene.model.intro_idx, 1)
        self.assertFalse(game.professor_scene.model.choice_active)

        game.professor_scene.update_intro()
        self.assertEqual(game.professor_scene.model.intro_idx, 2)
        self.assertTrue(game.professor_scene.model.choice_active)

    def test_update_ending_returns_post_boss_clear_to_map(self):
        game = self.make_game()
        game.player_model = _pm_from_dict({
            "glitch_lord_defeated": True,
            "professor_intro_seen": False,
            "professor_defeated": False,
            "in_dungeon": True,
            "x": 40,
            "y": 32,
        })
        game.explore_scene.model.a_cooldown = False
        game.input_state.btnp = lambda buttons: buttons == self.main.CONFIRM_BUTTONS
        game.state = "ending"

        game.ending_scene.update()

        self.assertEqual(game.state, "map")
        self.assertFalse(game.player_model.in_dungeon)
        self.assertEqual((game.player_model.x, game.player_model.y), (40, 32))
        self.assertTrue(game.explore_scene.model.a_cooldown)


if __name__ == "__main__":
    unittest.main()
