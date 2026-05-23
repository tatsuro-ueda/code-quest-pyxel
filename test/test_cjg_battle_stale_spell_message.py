from __future__ import annotations

import unittest
from dataclasses import dataclass, field

from src.scenes.battle.model import BattleModel
from src.scenes.battle.presenter import BattlePresenter
from src.shared.state.player_model import PlayerItem, PlayerModel


@dataclass
class _FakeSfx:
    calls: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.calls.append(name)


@dataclass
class _FakeVfx:
    timer: int = 0


@dataclass
class _FakeInput:
    confirm_pressed: bool = False

    def btnp(self, buttons) -> bool:
        return self.confirm_pressed


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    vfx: _FakeVfx = field(default_factory=_FakeVfx)
    input_state: _FakeInput = field(default_factory=_FakeInput)


class BattleStaleSpellMessageTest(unittest.TestCase):
    def test_spell_failure_message_is_cleared_when_opening_item_menu(self):
        model = BattleModel(menu=1, phase="menu")
        presenter = BattlePresenter(model)
        game = _FakeGame()
        game.player_model.spells = []
        game.player_model.items = [PlayerItem(id="potion", qty=1)]
        scene = object()

        game.input_state.confirm_pressed = True
        presenter.update(game, scene)

        self.assertEqual(model.text, "まだ じゅもんを おぼえていない")
        self.assertEqual(model.phase, "menu")

        model.menu = 2
        presenter.update(game, scene)

        self.assertEqual(model.phase, "item_select")
        self.assertEqual(model.text, "")


if __name__ == "__main__":
    unittest.main()
