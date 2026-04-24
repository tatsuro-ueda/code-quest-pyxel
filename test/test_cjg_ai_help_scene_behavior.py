"""CJG/ai_help: AI ヘルプ画面の enter / update が crash しない。

根拠:
- docs/customer-journeys.md CJ3「子どもが詰まったら AI に頼む」系
- docs/customer-jobs.md Job5（プログラミングを学ぶ）

AiHelpScene.enter は環境判定（js / subprocess / fallback）のいずれかを
返す。ローカル pytest 環境では subprocess fallback か最終 fallback の
どちらかに落ちるので、少なくとも空文字列でない status が付くことを
期待する。update は CONFIRM / CANCEL で menu に戻る。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.ai_help.scene import AiHelpScene


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
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeGame:
    state: str = "menu"
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)


class AiHelpEnterTest(unittest.TestCase):
    """enter() が例外なく完走し、status と state を書き換える。"""

    def test_enter_sets_state_and_assigns_non_empty_status(self):
        game = _FakeGame(state="menu")
        scene = AiHelpScene(game=game)

        scene.enter()

        self.assertEqual(game.state, "ai_help")
        self.assertTrue(
            scene.model.status,
            "enter 後に status が空のまま。環境判定が何も返していない",
        )


class AiHelpUpdateExitTest:
    """update() で CONFIRM / CANCEL が menu に戻る。"""


class AiHelpUpdateTest(unittest.TestCase):
    def test_cancel_returns_to_menu_and_plays_cancel_sfx(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame(state="ai_help")
        game.input_state.press(CANCEL_BUTTONS)
        scene = AiHelpScene(game=game)

        scene.update()

        self.assertEqual(game.state, "menu")
        self.assertIn("cancel", game.sfx.played)

    def test_confirm_also_returns_to_menu(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame(state="ai_help")
        game.input_state.press(CONFIRM_BUTTONS)
        scene = AiHelpScene(game=game)

        scene.update()

        self.assertEqual(game.state, "menu")

    def test_no_input_keeps_state_ai_help(self):
        game = _FakeGame(state="ai_help")
        scene = AiHelpScene(game=game)

        scene.update()

        self.assertEqual(game.state, "ai_help")
        self.assertEqual(game.sfx.played, [])

    def test_update_without_game_is_noop(self):
        scene = AiHelpScene(game=None)
        scene.update()  # 例外を投げなければ OK


if __name__ == "__main__":
    unittest.main()
