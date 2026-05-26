"""CJG/battle: spell/item 一覧の末尾に visible な back 行を出す。

根拠:
- docs/customer-jobs.md Job4（ゲームを楽しむ）
- steering/2026年5月26日 メニュー：一覧UIのもどる導線をまとめて揃える.md

battle の spell_select / item_select は:
- 一覧末尾に `もどる` を出す
- confirm on back で menu phase に戻る
- back 行を足しても visible window と highlight を見失わない
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.game_data import SPELLS
from src.scenes.battle.scene import BattleScene
from src.scenes.battle.view import BattleView
from src.scenes.battle.view_model import BattleRow, BattleSubPanel
from src.shared.services.input_bindings import CONFIRM_BUTTONS
from src.shared.services.text_format import TextFormat
from src.shared.state.player_model import PlayerItem, PlayerModel


@dataclass
class _FakeInputState:
    pressed_groups: set[tuple[str, ...]] = field(default_factory=set)

    def btn(self, button_names) -> bool:
        return button_names in self.pressed_groups

    def btnp(self, button_names) -> bool:
        return button_names in self.pressed_groups


@dataclass
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeVfx:
    timer: int = 0
    started: list[str] = field(default_factory=list)

    def start(self, name: str) -> None:
        self.started.append(name)


@dataclass
class _FakeMessages:
    def dialog_text(self, key: str, **kwargs: Any) -> str:
        return key


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    vfx: _FakeVfx = field(default_factory=_FakeVfx)
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    text_fmt: TextFormat = field(default_factory=TextFormat)
    has_jp_font: bool = True
    image_banks: Any = None
    state: str = "battle"
    debug_mode: bool = False

    def __post_init__(self) -> None:
        self.text_fmt.game = self


ENEMY_FIXTURE = {
    "name": "スライム",
    "hp": 30,
    "atk": 5,
    "def": 2,
    "agi": 3,
    "exp": 10,
    "gold": 5,
    "zone": 0,
    "category": "normal",
    "color": 11,
    "sprite": 0,
    "type": "physical",
    "has_sprite": True,
}


def _spell_names(count: int) -> list[str]:
    return [spell["name"] for spell in SPELLS[:count]]


def _enter_spell_select(spell_count: int) -> tuple[BattleScene, _FakeGame, list[str]]:
    game = _FakeGame()
    spells = _spell_names(spell_count)
    game.player_model.spells = spells
    game.player_model.mp = 999
    scene = BattleScene(game=game)
    scene.start(ENEMY_FIXTURE)
    scene.model.phase = "spell_select"
    return scene, game, spells


def _enter_item_select(item_count: int) -> tuple[BattleScene, _FakeGame]:
    game = _FakeGame()
    game.player_model.items = [
        PlayerItem(id=0, qty=i + 1) for i in range(item_count)
    ]
    scene = BattleScene(game=game)
    scene.start(ENEMY_FIXTURE)
    scene.model.phase = "item_select"
    return scene, game


class BattleSpellBackRowTest(unittest.TestCase):
    def test_spell_panel_shows_back_row_after_visible_spells(self):
        scene, game, spells = _enter_spell_select(4)
        scene.model.spell_select = 3

        vm = scene.presenter.build_view_model(game)

        self.assertIsNotNone(vm.sub_panel)
        self.assertEqual(len(vm.sub_panel.rows), 5)
        self.assertIn(spells[3], vm.sub_panel.rows[-2].text)
        self.assertEqual(vm.sub_panel.rows[-1].text.strip(), "もどる")

    def test_spell_panel_keeps_back_row_visible_after_scroll(self):
        scene, game, spells = _enter_spell_select(5)
        scene.model.spell_select = 5

        vm = scene.presenter.build_view_model(game)

        self.assertIsNotNone(vm.sub_panel)
        self.assertEqual(len(vm.sub_panel.rows), 5)
        for row, expected_name in zip(vm.sub_panel.rows[:-1], spells[1:5]):
            self.assertIn(expected_name, row.text)
        self.assertTrue(vm.sub_panel.rows[-1].text.startswith("> "))
        self.assertTrue(vm.sub_panel.rows[-1].text.endswith("もどる"))

    def test_confirm_on_spell_back_row_returns_to_menu_phase(self):
        scene, game, _ = _enter_spell_select(2)
        scene.model.spell_select = 2
        game.input_state.pressed_groups = {CONFIRM_BUTTONS}

        scene.update()

        self.assertEqual(scene.model.phase, "menu")


class BattleItemBackRowTest(unittest.TestCase):
    def test_item_panel_shows_back_row_after_visible_items(self):
        scene, game = _enter_item_select(4)
        scene.model.item_select = 3

        vm = scene.presenter.build_view_model(game)

        self.assertIsNotNone(vm.sub_panel)
        self.assertEqual(len(vm.sub_panel.rows), 5)
        self.assertIn("x4", vm.sub_panel.rows[-2].text)
        self.assertEqual(vm.sub_panel.rows[-1].text.strip(), "もどる")

    def test_item_panel_keeps_back_row_visible_after_scroll(self):
        scene, game = _enter_item_select(5)
        scene.model.item_select = 5

        vm = scene.presenter.build_view_model(game)

        self.assertIsNotNone(vm.sub_panel)
        self.assertEqual(len(vm.sub_panel.rows), 5)
        self.assertIn("x2", vm.sub_panel.rows[0].text)
        self.assertIn("x5", vm.sub_panel.rows[-2].text)
        self.assertTrue(vm.sub_panel.rows[-1].text.startswith("> "))
        self.assertTrue(vm.sub_panel.rows[-1].text.endswith("もどる"))

    def test_confirm_on_item_back_row_returns_to_menu_phase(self):
        scene, game = _enter_item_select(2)
        scene.model.item_select = 2
        game.input_state.pressed_groups = {CONFIRM_BUTTONS}

        scene.update()

        self.assertEqual(scene.model.phase, "menu")


@dataclass
class _RecordingTextWriter:
    calls: list[tuple[int, int, str, int]] = field(default_factory=list)

    def text(self, x: int, y: int, s: str, col: int) -> None:
        self.calls.append((x, y, s, col))


class BattleListLayoutTest(unittest.TestCase):
    def test_five_row_list_keeps_back_row_inside_panel(self):
        view = BattleView()
        writer = _RecordingTextWriter()
        panel = BattleSubPanel(
            is_grid=False,
            rows=[BattleRow(text=f"row{i}", color=7) for i in range(5)],
        )

        view._draw_sub_panel_list(panel, writer)

        ys = [y for _, y, _, _ in writer.calls]
        self.assertEqual(len(ys), 5)
        self.assertLessEqual(ys[-1], 238)


if __name__ == "__main__":
    unittest.main()
