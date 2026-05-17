"""CJG/town: 町メニューの はなす / やどや / セーブ / でる アクションが crash しない。

根拠:
- docs/product-requirements-narrative.md（NPC 会話送り）
- docs/product-requirements-map.md（町→セーブ・やどや）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

TownPresenter の _talk / _stay_at_inn / _save / _exit を fake game で回す。
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

    def start_a_cooldown(self) -> None:
        self.a_cooldown = True


@dataclass
class _FakeExploreScene:
    model: _FakeExploreModel = field(default_factory=_FakeExploreModel)


@dataclass
class _FakeTextFmt:
    jp: bool = True

    def t(self, jp: str, en: str) -> str:
        return jp if self.jp else en


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
    has_jp_font: bool = True
    text_fmt: _FakeTextFmt = field(default_factory=_FakeTextFmt)


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

        presenter._stay_at_inn()

        self.assertEqual(game.player_model.hp, game.player_model.max_hp)
        self.assertEqual(game.player_model.mp, game.player_model.max_mp)
        self.assertEqual(game.state, "message")

    def test_inn_rejects_when_gold_insufficient(self):
        presenter, game = _presenter_in_town(0)
        game.player_model.hp = 1
        game.player_model.gold = 0

        presenter._stay_at_inn()

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


class TownMenuViewModelLabelTest(unittest.TestCase):
    """まちメニューの「やどや」ラベルに宿代が併記される（シナリオ1〜4）。"""

    def _inn_cost_for_index(self, index: int) -> int:
        from src.shared.constants.game_config import INN_COST
        from src.game_data import INN_PRICES

        return INN_PRICES[index] if index < len(INN_PRICES) else INN_COST

    def test_japanese_label_includes_inn_cost_with_fullwidth_brackets(self):
        presenter, game = _presenter_in_town(0)
        game.has_jp_font = True
        game.text_fmt.jp = True
        cost = self._inn_cost_for_index(0)

        vm = presenter.build_menu_view_model()

        expected_inn = f"やどや（{cost}G）"
        self.assertIn(expected_inn, vm.labels)
        self.assertEqual(vm.labels.count(expected_inn), 1)
        for label in ("はなす", "ぶきや", "ぼうぐや", "どうぐや", "セーブ", "でる"):
            self.assertIn(label, vm.labels, f"{label} がそのまま含まれない")

    def test_english_label_includes_inn_cost_with_halfwidth_brackets(self):
        presenter, game = _presenter_in_town(0)
        game.has_jp_font = False
        game.text_fmt.jp = False
        cost = self._inn_cost_for_index(0)

        vm = presenter.build_menu_view_model()

        expected_inn = f"INN ({cost}G)"
        self.assertIn(expected_inn, vm.labels)
        self.assertEqual(vm.labels.count(expected_inn), 1)
        for label in ("TALK", "WEAPONS", "ARMOR", "ITEMS", "SAVE", "EXIT"):
            self.assertIn(label, vm.labels)

    def test_unregistered_town_position_falls_back_to_inn_cost(self):
        from src.shared.constants.game_config import INN_COST

        game = _FakeGame()
        model = TownModel()
        model.menu_pos = (99, 99)  # TOWN_INDEX_BY_POS に無い → index 0 扱い
        presenter = TownPresenter(model=model, game=game)

        vm = presenter.build_menu_view_model()

        # index 0 で INN_PRICES[0] が引けるか、引けなければ INN_COST が使われる
        from src.game_data import INN_PRICES

        fallback_cost = INN_PRICES[0] if 0 < len(INN_PRICES) else INN_COST
        self.assertIn(f"やどや（{fallback_cost}G）", vm.labels)

    def test_label_count_preserved_and_cursor_gold_unchanged(self):
        presenter, game = _presenter_in_town(0)
        game.player_model.gold = 123
        presenter.model.menu_cursor = 4

        vm = presenter.build_menu_view_model()

        self.assertEqual(len(vm.labels), 7, "メニュー項目数が変わってはいけない")
        self.assertEqual(vm.cursor, 4)
        self.assertEqual(vm.gold, 123)
        self.assertEqual(vm.title, "まちメニュー")


if __name__ == "__main__":
    unittest.main()
