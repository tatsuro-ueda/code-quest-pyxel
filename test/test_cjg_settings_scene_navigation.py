"""CJG/settings: 設定画面の open / cursor / CONFIRM / CANCEL / back 行動。

根拠:
- docs/product-requirements-platform.md CJG20（演出 ON/OFF）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

SettingsScene は 5 行（ぜんぶ / BGM / こうかおん / ひかり / もどる）を
cursor で循環し、LEFT/RIGHT/CONFIRM でトグル、`もどる` か CANCEL で
origin（title / menu）に戻る。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.settings.scene import SettingsScene
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
    enabled: bool = True

    def play(self, name: str) -> None:
        self.played.append(name)

    def set_enabled(self, flag: bool) -> None:
        self.enabled = bool(flag)


@dataclass
class _FakeAudio:
    enabled: bool = True

    def set_enabled(self, flag: bool) -> None:
        self.enabled = bool(flag)


@dataclass
class _FakeTextFormat:
    def t(self, jp: str, en: str) -> str:
        return jp


@dataclass
class _FakeMenuModel:
    sub: str | None = "items"

    def clear_sub(self) -> None:
        self.sub = None


@dataclass
class _FakeMenuScene:
    model: _FakeMenuModel = field(default_factory=_FakeMenuModel)


@dataclass
class _FakeGame:
    state: str = "settings"
    has_jp_font: bool = True
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    audio: _FakeAudio = field(default_factory=_FakeAudio)
    text_fmt: _FakeTextFormat = field(default_factory=_FakeTextFormat)
    menu_scene: _FakeMenuScene = field(default_factory=_FakeMenuScene)


class SettingsOpenTest(unittest.TestCase):
    def test_open_from_title_sets_origin_and_state(self):
        game = _FakeGame(state="title")
        scene = SettingsScene(game=game)

        scene.open("title")

        self.assertEqual(game.state, "settings")
        self.assertEqual(scene.model.origin, "title")
        self.assertEqual(scene.model.cursor, 0)

    def test_open_from_menu_resets_menu_sub_to_none(self):
        game = _FakeGame()
        game.menu_scene.model.sub = "items"
        scene = SettingsScene(game=game)

        scene.open("menu")

        self.assertIsNone(game.menu_scene.model.sub)


class SettingsCursorTest(unittest.TestCase):
    def test_down_cycles_through_5_rows(self):
        from src.shared.services.input_bindings import DOWN_BUTTONS

        game = _FakeGame()
        scene = SettingsScene(game=game)
        scene.model.cursor = 4  # もどる

        game.input_state.press(DOWN_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.cursor, 0)
        self.assertIn("cursor", game.sfx.played)

    def test_up_wraps_around(self):
        from src.shared.services.input_bindings import UP_BUTTONS

        game = _FakeGame()
        scene = SettingsScene(game=game)
        scene.model.cursor = 0

        game.input_state.press(UP_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.cursor, 4)


class SettingsToggleViaConfirmTest(unittest.TestCase):
    def test_confirm_on_bgm_row_toggles_bgm_flag(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        scene = SettingsScene(game=game)
        scene.model.cursor = 1  # BGM
        self.assertTrue(game.player_model.bgm_enabled)

        game.input_state.press(CONFIRM_BUTTONS)
        scene.update()

        self.assertFalse(game.player_model.bgm_enabled)
        self.assertFalse(game.audio.enabled)

    def test_left_also_toggles(self):
        from src.shared.services.input_bindings import LEFT_BUTTONS

        game = _FakeGame()
        scene = SettingsScene(game=game)
        scene.model.cursor = 2  # SFX

        game.input_state.press(LEFT_BUTTONS)
        scene.update()

        self.assertFalse(game.player_model.sfx_enabled)

    def test_right_also_toggles(self):
        from src.shared.services.input_bindings import RIGHT_BUTTONS

        game = _FakeGame()
        scene = SettingsScene(game=game)
        scene.model.cursor = 3  # VFX

        game.input_state.press(RIGHT_BUTTONS)
        scene.update()

        self.assertFalse(game.player_model.vfx_enabled)


class SettingsBackTest(unittest.TestCase):
    def test_cancel_returns_to_title_when_origin_title(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame()
        scene = SettingsScene(game=game)
        scene.model.origin = "title"

        game.input_state.press(CANCEL_BUTTONS)
        scene.update()

        self.assertEqual(game.state, "title")

    def test_cancel_returns_to_menu_when_origin_menu(self):
        from src.shared.services.input_bindings import CANCEL_BUTTONS

        game = _FakeGame()
        scene = SettingsScene(game=game)
        scene.model.origin = "menu"

        game.input_state.press(CANCEL_BUTTONS)
        scene.update()

        self.assertEqual(game.state, "menu")

    def test_confirm_on_back_row_returns_to_origin(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        scene = SettingsScene(game=game)
        scene.model.origin = "menu"
        scene.model.cursor = 4  # もどる

        game.input_state.press(CONFIRM_BUTTONS)
        scene.update()

        self.assertEqual(game.state, "menu")


if __name__ == "__main__":
    unittest.main()
