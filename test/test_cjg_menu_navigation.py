"""CJG/menu: メニュー画面のカーソル / サブメニュー遷移 / アイテム消費。

根拠:
- docs/customer-journeys.md（冒険中のメニュー操作）
- docs/product-requirements-battle.md（menu でアイテム使用が安全に動くこと）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

MenuScene.update は 6 メニュー（status / items / equip / settings / ai_help / close）
を cursor で循環し、CONFIRM で sub メニューに入る。items サブでは item_use サービス
を通して PlayerModel を更新し、qty=0 になると inventory から取り除く。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.menu.scene import MenuScene
from src.shared.state.player_model import PlayerItem, PlayerModel


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
class _FakeMessages:
    def dialog_text(self, key: str, **kwargs: Any) -> str:
        return f"{key}::{kwargs}"


@dataclass
class _FakeSettingsScene:
    opened: list[str] = field(default_factory=list)

    def open(self, origin: str):
        self.opened.append(origin)


@dataclass
class _FakeAiHelpScene:
    entered: int = 0

    def enter(self):
        self.entered += 1


@dataclass
class _FakeGame:
    state: str = "menu"
    has_jp_font: bool = True
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    settings_scene: _FakeSettingsScene = field(default_factory=_FakeSettingsScene)
    ai_help_scene: _FakeAiHelpScene = field(default_factory=_FakeAiHelpScene)


class MenuCursorTest(unittest.TestCase):
    def test_down_cycles_from_last_to_first(self):
        from src.shared.services.input_bindings import DOWN_BUTTONS

        game = _FakeGame()
        scene = MenuScene(game=game)
        scene.model.cursor = 5  # 最後（とじる）

        game.input_state.press(DOWN_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.cursor, 0)

    def test_up_cycles_from_first_to_last(self):
        from src.shared.services.input_bindings import UP_BUTTONS

        game = _FakeGame()
        scene = MenuScene(game=game)
        scene.model.cursor = 0

        game.input_state.press(UP_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.cursor, 5)

    def test_cancel_from_root_returns_to_map(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame()
        game.input_state.press(CANCEL_BUTTONS)
        scene = MenuScene(game=game)

        scene.update()

        self.assertEqual(game.state, "map")


class MenuSubEntryTest(unittest.TestCase):
    def test_confirm_on_status_enters_status_sub(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.input_state.press(CONFIRM_BUTTONS)
        scene = MenuScene(game=game)
        scene.model.cursor = 0
        scene.update()

        self.assertEqual(scene.model.sub, "status")

    def test_confirm_on_items_enters_items_sub_with_cursor_reset(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.input_state.press(CONFIRM_BUTTONS)
        scene = MenuScene(game=game)
        scene.model.cursor = 1
        scene.model.item_cursor = 7
        scene.update()

        self.assertEqual(scene.model.sub, "items")
        self.assertEqual(scene.model.item_cursor, 0)

    def test_confirm_on_settings_calls_settings_scene_open_with_menu_origin(self):
        """menu から settings_scene.open('menu') を直接呼ぶ（存在しない game._open_settings を呼ばない）。"""
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.input_state.press(CONFIRM_BUTTONS)
        scene = MenuScene(game=game)
        scene.model.cursor = 3
        scene.update()

        self.assertEqual(game.settings_scene.opened, ["menu"])

    def test_confirm_on_ai_help_calls_ai_help_scene_enter(self):
        """menu から ai_help_scene.enter() を直接呼ぶ（存在しない game._enter_ai_help を呼ばない）。"""
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.input_state.press(CONFIRM_BUTTONS)
        scene = MenuScene(game=game)
        scene.model.cursor = 4
        scene.update()

        self.assertEqual(game.ai_help_scene.entered, 1)

    def test_confirm_on_close_returns_to_map(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.input_state.press(CONFIRM_BUTTONS)
        scene = MenuScene(game=game)
        scene.model.cursor = 5
        scene.update()

        self.assertEqual(game.state, "map")


class MenuItemSubUseTest(unittest.TestCase):
    def test_using_heal_item_when_not_full_consumes_one(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.player_model.hp = 1  # 満タンでない
        game.player_model.items = [PlayerItem(id=0, qty=3)]
        scene = MenuScene(game=game)
        scene.model.sub = "items"
        scene.model.item_cursor = 0
        game.input_state.press(CONFIRM_BUTTONS)

        scene.update()

        self.assertGreater(game.player_model.hp, 1)
        # qty が 2 に減る
        self.assertEqual(game.player_model.items[0].qty, 2)

    def test_using_heal_item_at_full_hp_shows_fail_message(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        # HP 満タン
        game.player_model.items = [PlayerItem(id=0, qty=3)]
        scene = MenuScene(game=game)
        scene.model.sub = "items"
        scene.model.item_cursor = 0
        game.input_state.press(CONFIRM_BUTTONS)

        scene.update()

        self.assertEqual(game.player_model.items[0].qty, 3)  # 減らない
        self.assertIn("まんたん", scene.model.message)

    def test_using_last_item_removes_entry_from_inventory(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        game.player_model.hp = 1
        game.player_model.items = [PlayerItem(id=0, qty=1)]
        scene = MenuScene(game=game)
        scene.model.sub = "items"
        scene.model.item_cursor = 0
        game.input_state.press(CONFIRM_BUTTONS)

        scene.update()

        self.assertEqual(game.player_model.items, [])

    def test_cancel_from_items_sub_returns_to_root(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame()
        scene = MenuScene(game=game)
        scene.model.sub = "items"
        game.input_state.press(CANCEL_BUTTONS)

        scene.update()

        self.assertIsNone(scene.model.sub)


class MenuEquipSubCursorTest(unittest.TestCase):
    """equip サブは weapon / armor の 2 択カーソルで循環する。"""

    def test_down_wraps_between_weapon_and_armor(self):
        from src.shared.services.input_bindings import DOWN_BUTTONS

        game = _FakeGame()
        scene = MenuScene(game=game)
        scene.model.sub = "equip"
        scene.model.item_cursor = 1

        game.input_state.press(DOWN_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.item_cursor, 0)

    def test_cancel_from_equip_sub_returns_to_root(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame()
        scene = MenuScene(game=game)
        scene.model.sub = "equip"
        game.input_state.press(CANCEL_BUTTONS)

        scene.update()

        self.assertIsNone(scene.model.sub)


class MenuDoesNotCallNonexistentGameShimTest(unittest.TestCase):
    """menu/scene.py が Game に存在しない shim メソッドを呼んでいないこと（実機 crash 再発防止）。

    2026-04-25 に game._open_settings / _enter_ai_help の AttributeError で
    実機落ちが発覚した。同じ穴を踏まないように、menu/scene.py のソースに
    Game クラスに実在するメソッドだけが現れることを静的に保証する。
    """

    _BANNED_PATTERNS = (
        r"\bgame\._open_settings\(",
        r"\bgame\._enter_ai_help\(",
        r"\bgame\.use_item\(",  # menu/battle は item_use サービス直呼びに統一済み
    )

    def test_menu_scene_does_not_call_banned_shims(self):
        import re

        path = ROOT / "src" / "scenes" / "menu" / "scene.py"
        text = path.read_text(encoding="utf-8")

        for pattern in self._BANNED_PATTERNS:
            with self.subTest(pattern=pattern):
                self.assertIsNone(
                    re.search(pattern, text),
                    f"menu/scene.py に禁止 shim `{pattern}` の呼び出しが復活している",
                )


if __name__ == "__main__":
    unittest.main()
