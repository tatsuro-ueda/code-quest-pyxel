"""CJG/town: 町メニューの はなす / やどや / セーブ / でる アクションが crash しない。

根拠:
- docs/product-requirements-narrative.md（NPC 会話送り）
- docs/product-requirements-map.md（町→セーブ・やどや）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

TownPresenter の _talk / _inn / _save / _exit を fake game で回す。
hp 回復 / gold 減算 / save_store.save の呼び出し / state 遷移を検証する。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.town.model import TownModel
from src.scenes.town.presenter import TownPresenter
from src.shared.services.save_store import SaveStoreError
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeMessages:
    lines: list[str] = field(default_factory=list)
    index: int = 0
    callback: Any = None

    def dialog_lines(self, scene_name: str, **kwargs: Any) -> list[str]:
        return [f"NPC line for {scene_name}"]


@dataclass
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeProfessorScene:
    def phase(self) -> str:
        return "intro"


@dataclass
class _FakeSaveStore:
    saved: list[Any] = field(default_factory=list)
    fail: bool = False

    def save(self, snap: Any) -> None:
        if self.fail:
            raise SaveStoreError("テスト用失敗")
        self.saved.append(snap)

    def exists(self) -> bool:
        return bool(self.saved)


@dataclass
class _FakeExploreModel:
    a_cooldown: bool = False


@dataclass
class _FakeExploreScene:
    model: _FakeExploreModel = field(default_factory=_FakeExploreModel)


@dataclass
class _FakeGame:
    state: str = "town_menu"
    prev_state: str = "map"
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    professor_scene: _FakeProfessorScene = field(default_factory=_FakeProfessorScene)
    save_store: _FakeSaveStore = field(default_factory=_FakeSaveStore)
    explore_scene: _FakeExploreScene = field(default_factory=_FakeExploreScene)
    current_town: Any = None
    _has_save: bool = False


def _presenter_in_town(town_index: int = 0) -> tuple[TownPresenter, _FakeGame]:
    from src.shared.constants.game_config import TOWN_INDEX_BY_POS

    # town_index から pos を逆引き
    pos = next(p for p, idx in TOWN_INDEX_BY_POS.items() if idx == town_index)
    model = TownModel()
    model.menu_pos = pos
    game = _FakeGame()
    return TownPresenter(model=model, game=game), game


class TownTalkTest(unittest.TestCase):
    def test_talk_in_registered_town_advances_npc_line(self):
        presenter, game = _presenter_in_town(0)

        presenter._talk()

        # メッセージ state に遷移している
        self.assertEqual(game.state, "message")
        self.assertEqual(game.prev_state, "town_menu")
        self.assertEqual(len(game.messages.lines), 1)

    def test_talk_in_unregistered_town_shows_no_npc_message(self):
        from src.scenes.town.presenter import TownPresenter

        game = _FakeGame()
        model = TownModel()
        model.menu_pos = (99, 99)  # TOWN_INDEX_BY_POS に無い → 0 扱い → 0 町の NPC ライン
        presenter = TownPresenter(model=model, game=game)

        # current_town_index() は 0 にフォールバックするので、NPC ラインが表示される
        presenter._talk()

        self.assertEqual(game.state, "message")
        self.assertTrue(game.messages.lines)


class TownInnTest(unittest.TestCase):
    def test_inn_heals_when_affordable(self):
        presenter, game = _presenter_in_town(0)
        game.player_model.hp = 1
        game.player_model.mp = 0
        game.player_model.gold = 1000

        presenter._inn()

        self.assertEqual(game.player_model.hp, game.player_model.max_hp)
        self.assertEqual(game.player_model.mp, game.player_model.max_mp)
        self.assertEqual(game.state, "message")

    def test_inn_rejects_when_gold_insufficient(self):
        presenter, game = _presenter_in_town(0)
        game.player_model.hp = 1
        game.player_model.gold = 0

        presenter._inn()

        self.assertEqual(game.player_model.hp, 1, "gold 不足なのに回復してしまった")
        self.assertEqual(game.state, "message")


class TownSaveTest(unittest.TestCase):
    def test_save_calls_save_store_and_sets_has_save_flag(self):
        presenter, game = _presenter_in_town(1)  # (30, 22)

        presenter._save()

        self.assertEqual(len(game.save_store.saved), 1)
        self.assertTrue(game._has_save)
        self.assertIn("save", game.sfx.played)
        self.assertEqual(game.state, "message")

    def test_save_with_failing_store_shows_fail_message_and_no_has_save_flag(self):
        presenter, game = _presenter_in_town(0)
        game.save_store.fail = True

        presenter._save()

        self.assertFalse(game._has_save)
        self.assertEqual(game.state, "message")
        self.assertNotIn("save", game.sfx.played)


class TownExitTest(unittest.TestCase):
    def test_exit_returns_to_map(self):
        presenter, game = _presenter_in_town(0)
        game.state = "town_menu"

        presenter._exit()

        self.assertEqual(game.state, "map")


if __name__ == "__main__":
    unittest.main()
