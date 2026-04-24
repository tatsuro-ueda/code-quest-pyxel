"""CJG/shop: ShopScene.update の cursor 移動と CANCEL 挙動。

根拠:
- docs/product-requirements-narrative.md / -map.md（ショップ遷移）
- docs/customer-jobs.md Make3

UP/DOWN で inventory を循環、CANCEL で town_menu に戻る、inventory が空なら
CANCEL / CONFIRM どちらでも town_menu に戻る。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.shop.scene import ShopScene
from src.shared.services.game_state import TownContext
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
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    current_town: TownContext | None = field(
        default_factory=lambda: TownContext(index=0, pos=(25, 6))
    )
    last_town_pos: tuple[int, int] | None = None
    state: str = "shop"
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)


class ShopCursorTest(unittest.TestCase):
    def test_down_moves_cursor_forward(self):
        from src.shared.services.input_bindings import DOWN_BUTTONS

        game = _FakeGame()
        scene = ShopScene(game=game)
        scene.enter("weapons")
        scene.model.cursor = 0

        game.input_state.press(DOWN_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.cursor, 1 % len(scene.model.inventory))

    def test_up_wraps_to_last(self):
        from src.shared.services.input_bindings import UP_BUTTONS

        game = _FakeGame()
        scene = ShopScene(game=game)
        scene.enter("weapons")
        scene.model.cursor = 0

        game.input_state.press(UP_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.cursor, len(scene.model.inventory) - 1)

    def test_cancel_returns_to_town_menu(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame()
        scene = ShopScene(game=game)
        scene.enter("weapons")

        game.input_state.press(CANCEL_BUTTONS)
        scene.update()

        self.assertEqual(game.state, "town_menu")
        self.assertIn("cancel", game.sfx.played)


class ShopEmptyInventoryTest(unittest.TestCase):
    """inventory が空のときは CANCEL でも CONFIRM でも town_menu に戻る。"""

    def test_empty_cancel_returns(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame()
        scene = ShopScene(game=game)
        scene.enter("weapons")
        scene.model.inventory = []

        game.input_state.press(CANCEL_BUTTONS)
        scene.update()

        self.assertEqual(game.state, "town_menu")

    def test_empty_confirm_returns(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        scene = ShopScene(game=game)
        scene.enter("weapons")
        scene.model.inventory = []

        game.input_state.press(CONFIRM_BUTTONS)
        scene.update()

        self.assertEqual(game.state, "town_menu")


class ShopNoGameGuardTest(unittest.TestCase):
    def test_update_without_game_is_noop(self):
        scene = ShopScene(game=None)
        scene.update()  # 例外を投げなければ OK


if __name__ == "__main__":
    unittest.main()
