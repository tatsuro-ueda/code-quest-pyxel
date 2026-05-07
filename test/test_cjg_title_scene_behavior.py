"""CJG/title: タイトル画面の cursor 操作と「はじめから / つづきから」分岐。

根拠:
- docs/customer-journeys.md（起動直後の選択体験）
- docs/product-requirements-platform.md（セーブの取り扱い）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

2026-05-07 改訂（CJ44 確定版）：「せってい」項目は撤去。
TitleScene.update は 2 メニューを cursor で選び、「はじめから」で PlayerModel を
new_game で作り直し（AV フラグは存在しない）、「つづきから」で _do_load を呼ぶ。
cursor モジュラー演算（0/1）も固定化する。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.title.scene import TitleScene
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
class _FakeExploreModel:
    a_cooldown: bool = False

    def start_a_cooldown(self) -> None:
        self.a_cooldown = True


@dataclass
class _FakeExploreScene:
    model: _FakeExploreModel = field(default_factory=_FakeExploreModel)


@dataclass
class _FakeMessages:
    shown: list[list[str]] = field(default_factory=list)

    def show(self, lines):
        self.shown.append(list(lines))


@dataclass
class _FakeSaveStore:
    snapshot: Any = None

    def load(self):
        return self.snapshot


@dataclass
class _FakeGame:
    state: str = "title"
    prev_state: str = "map"
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    explore_scene: _FakeExploreScene = field(default_factory=_FakeExploreScene)
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    save_store: _FakeSaveStore = field(default_factory=_FakeSaveStore)
    dungeon_map: Any = None
    _has_save: bool = False


class TitleCursorTest(unittest.TestCase):
    """上下入力で cursor が循環する（0↔1 境界を含む。CJ44 でメニューは 2 項目）。"""

    def test_down_moves_cursor_down_with_wrap(self):
        from src.shared.services.input_bindings import DOWN_BUTTONS

        game = _FakeGame()
        scene = TitleScene(game=game)
        scene.model.cursor = 1

        game.input_state.press(DOWN_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.cursor, 0)
        self.assertIn("cursor", game.sfx.played)

    def test_up_moves_cursor_up_with_wrap(self):
        from src.shared.services.input_bindings import UP_BUTTONS

        game = _FakeGame()
        scene = TitleScene(game=game)
        scene.model.cursor = 0

        game.input_state.press(UP_BUTTONS)
        scene.update()

        self.assertEqual(scene.model.cursor, 1)


class TitleNewGameTest(unittest.TestCase):
    """はじめから（cursor=0 で CONFIRM）が PlayerModel を初期化し state=map に遷移する。"""

    def test_new_game_replaces_player_model_with_new_game(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        # 事前に player_model を書き換えて new_game で戻ることを確認
        game.player_model.gold = 9999
        game.player_model.lv = 99

        game.input_state.press(CONFIRM_BUTTONS)
        scene = TitleScene(game=game)
        scene.model.cursor = 0
        scene.update()

        self.assertEqual(game.state, "map")
        self.assertNotEqual(game.player_model.gold, 9999)
        self.assertEqual(game.player_model.lv, 1)


class TitleContinueTest(unittest.TestCase):
    """つづきから（cursor=1 で CONFIRM）がセーブを読んで state=message に遷移する。"""

    def test_continue_without_save_is_noop(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame(_has_save=False)
        game.input_state.press(CONFIRM_BUTTONS)
        scene = TitleScene(game=game)
        scene.model.cursor = 1

        scene.update()

        # セーブ無しでは state は title のまま
        self.assertEqual(game.state, "title")

    def test_continue_with_valid_save_restores_player_and_advances(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame(_has_save=True)
        # セーブ済みプレイヤー（HP 12 / lv 4）を用意
        saved = PlayerModel.new_game()
        saved.hp = 12
        saved.lv = 4
        game.save_store.snapshot = saved.to_snapshot(town_pos=(30, 22))

        game.input_state.press(CONFIRM_BUTTONS)
        scene = TitleScene(game=game)
        scene.model.cursor = 1
        scene.update()

        self.assertEqual(game.player_model.hp, 12)
        self.assertEqual(game.player_model.lv, 4)
        self.assertEqual((game.player_model.x, game.player_model.y), (30, 22))
        self.assertEqual(game.state, "message")
        self.assertEqual(game.prev_state, "map")
        self.assertTrue(game.explore_scene.model.a_cooldown, "ロード直後は a_cooldown が立つ")

    def test_continue_with_broken_save_falls_back_to_no_record_message(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame(_has_save=True)
        game.save_store.snapshot = None  # load() が None を返す想定

        game.input_state.press(CONFIRM_BUTTONS)
        scene = TitleScene(game=game)
        scene.model.cursor = 1
        scene.update()

        self.assertEqual(game.state, "message")
        self.assertEqual(game.prev_state, "title")
        self.assertFalse(game._has_save)


class TitleNoGameGuardTest(unittest.TestCase):
    def test_update_without_game_is_noop(self):
        scene = TitleScene(game=None)
        scene.update()


if __name__ == "__main__":
    unittest.main()
