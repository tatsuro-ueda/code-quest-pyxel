from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.message_display import MessageDisplay
from src.shared.state.player_model import PlayerModel

try:
    from src.scenes.page_dialog.scene import PageDialogScene
except ModuleNotFoundError:
    PageDialogScene = None


class _FakeDialog:
    def load_all_lines(self, scene_name, **_kwargs):
        if scene_name == "boss.glitch.prebattle_01":
            return ["page 1", "page 2"]
        return ["fallback"]


class PageDialogSceneTest(unittest.TestCase):
    def make_game(self):
        game = types.SimpleNamespace()
        game.state = "map"
        game.prev_state = "map"
        game.dialog = _FakeDialog()
        game.player_model = PlayerModel.new_game()
        game.input_state = types.SimpleNamespace(btnp=lambda *_args, **_kwargs: False)
        game.messages = MessageDisplay(game=game)
        return game

    def test_page_dialog_scene_enters_fullscreen_dialog_state(self):
        self.assertIsNotNone(PageDialogScene, "page_dialog scene が未実装")
        game = self.make_game()
        scene = PageDialogScene(game=game)

        scene.enter_scene("boss.glitch.prebattle_01")

        self.assertEqual(game.state, "page_dialog")
        self.assertEqual(scene.model.lines, ["page 1", "page 2"])
        self.assertEqual(scene.model.index, 0)

    def test_page_dialog_calls_callback_once_after_last_page(self):
        self.assertIsNotNone(PageDialogScene, "page_dialog scene が未実装")
        game = self.make_game()
        callback = MagicMock()
        scene = PageDialogScene(game=game)
        scene.enter_lines(["page 1", "page 2"], callback=callback)
        game.input_state.btnp = lambda buttons: True

        scene.update()
        scene.update()

        callback.assert_called_once_with()
        self.assertEqual(game.state, "map")


if __name__ == "__main__":
    unittest.main()
