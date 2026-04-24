"""CJG/ending: エンディング画面が入力でマップに戻り、ダンジョン状態をクリアする。

根拠:
- docs/customer-journeys.md（クリア後の体験）
- docs/customer-jobs.md Job4（最後まで遊べる）

EndingScene.enter はエンディング台詞をロードして state="ending" に。
update の CONFIRM で map に戻り、同時に in_dungeon=False / dungeon_map=None /
explore a_cooldown=True をセットする。これが抜けるとエンディング直後に
ダンジョン内扱いで戻って壁にハマる。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.ending.scene import EndingScene
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeInputState:
    pressed: set[tuple[int, ...]] = field(default_factory=set)

    def btnp(self, buttons) -> bool:
        key = tuple(buttons) if hasattr(buttons, "__iter__") else (buttons,)
        return key in self.pressed

    def press(self, buttons):
        key = tuple(buttons) if hasattr(buttons, "__iter__") else (buttons,)
        self.pressed.add(key)


@dataclass
class _FakeExploreModel:
    a_cooldown: bool = False


@dataclass
class _FakeExploreScene:
    model: _FakeExploreModel = field(default_factory=_FakeExploreModel)


@dataclass
class _FakeMessages:
    def dialog_lines(self, key: str, **_kwargs: Any) -> list[str]:
        return [f"line1 of {key}", "line2"]


@dataclass
class _FakeGame:
    state: str = "map"
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    explore_scene: _FakeExploreScene = field(default_factory=_FakeExploreScene)
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    dungeon_map: Any = None


class EndingEnterTest(unittest.TestCase):
    def test_enter_loads_lines_and_changes_state(self):
        game = _FakeGame()
        scene = EndingScene(game=game)

        scene.enter()

        self.assertEqual(game.state, "ending")
        self.assertTrue(scene.model.lines)
        self.assertIn("ending.main.line01", scene.model.lines[0])


class EndingUpdateTest(unittest.TestCase):
    def test_confirm_returns_to_map_and_clears_dungeon_state(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.player_model.in_dungeon = True
        game.dungeon_map = object()
        game.input_state.press(CONFIRM_BUTTONS)
        scene = EndingScene(game=game)

        scene.update()

        self.assertEqual(game.state, "map")
        self.assertFalse(game.player_model.in_dungeon)
        self.assertIsNone(game.dungeon_map)
        self.assertTrue(game.explore_scene.model.a_cooldown)

    def test_no_input_keeps_state_ending(self):
        game = _FakeGame(state="ending")
        scene = EndingScene(game=game)

        scene.update()

        self.assertEqual(game.state, "ending")

    def test_update_without_game_is_noop(self):
        scene = EndingScene(game=None)
        scene.update()


if __name__ == "__main__":
    unittest.main()
