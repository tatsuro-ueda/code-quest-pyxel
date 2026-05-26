"""CJG/battle: spell_select は 4 行窓の中で選択中じゅもんを見失わない。

根拠:
- steering/2026年5月24日 戦闘：魔法選択でカーソルが画面外へ出る不具合を直す
- docs/customer-jobs.md Job4（ゲームを楽しむ）

spell_select は:
- 4 件以下では 4 spell + back の 5 行以内表示を保つ
- 5 件目を選ぶと 4 spell 窓が scroll して選択中じゅもんを画面内に残す
- 決定時は、見えている強調行と同じじゅもんに効果が乗る
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
from src.shared.services.input_bindings import CONFIRM_BUTTONS
from src.shared.services.text_format import TextFormat
from src.shared.state.player_model import PlayerModel


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


class BattleSpellSelectWindowTest(unittest.TestCase):
    def test_four_spells_keep_existing_visible_order(self):
        scene, game, spells = _enter_spell_select(4)
        scene.model.spell_select = 2

        vm = scene.presenter.build_view_model(game)

        self.assertIsNotNone(vm.sub_panel)
        self.assertEqual(len(vm.sub_panel.rows), 5)
        self.assertIn(spells[2], vm.sub_panel.rows[2].text)
        self.assertTrue(vm.sub_panel.rows[2].text.startswith("> "))
        self.assertEqual(vm.sub_panel.rows[2].color, 10)
        self.assertEqual(vm.sub_panel.rows[-1].text.strip(), "もどる")

    def test_fifth_spell_scrolls_into_last_visible_row(self):
        scene, game, spells = _enter_spell_select(5)
        scene.model.spell_select = 4

        vm = scene.presenter.build_view_model(game)

        self.assertIsNotNone(vm.sub_panel)
        self.assertEqual(len(vm.sub_panel.rows), 5)
        for row, expected_name in zip(vm.sub_panel.rows[:-1], spells[1:5]):
            self.assertIn(expected_name, row.text)
        self.assertTrue(vm.sub_panel.rows[-2].text.startswith("> "))
        self.assertEqual(vm.sub_panel.rows[-2].color, 10)
        self.assertEqual(vm.sub_panel.rows[-1].text.strip(), "もどる")

    def test_confirm_uses_same_spell_as_visible_highlight_after_scroll(self):
        scene, game, spells = _enter_spell_select(5)
        scene.model.spell_select = 4
        vm = scene.presenter.build_view_model(game)

        self.assertIsNotNone(vm.sub_panel)
        self.assertIn(spells[4], vm.sub_panel.rows[-2].text)
        self.assertTrue(vm.sub_panel.rows[-2].text.startswith("> "))

        game.input_state.pressed_groups = {CONFIRM_BUTTONS}
        scene.update()

        self.assertIn(spells[4], scene.model.text)
        self.assertEqual(scene.model.phase, "player_attack")
        self.assertIn("magic", game.sfx.played)


if __name__ == "__main__":
    unittest.main()
