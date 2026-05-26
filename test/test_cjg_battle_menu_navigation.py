"""CJG/battle: 先頭 2x2 メニューは上下左右で見た目どおりに動く。

根拠:
- steering/2026年5月26日（ブロクエ）メニューを上下左右で選びたい.png
- docs/customer-jobs.md Job4（ゲームを楽しむ）

battle の menu phase は:
- たたかう / じゅもん / アイテム / にげる を 2x2 で表示する
- 上下左右入力で隣接マスへ cursor が動く
- cursor 移動時の SFX は従来どおり鳴る
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.battle.model import BattleModel
from src.scenes.battle.presenter import BattlePresenter
from src.shared.services.input_bindings import (
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    UP_BUTTONS,
)


@dataclass
class _FakeInputState:
    pressed_groups: set[tuple[str, ...]] = field(default_factory=set)

    def btnp(self, button_names) -> bool:
        return button_names in self.pressed_groups

    def press(self, button_names) -> None:
        self.pressed_groups = {button_names}


@dataclass
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeVfx:
    timer: int = 0


@dataclass
class _FakeGame:
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    vfx: _FakeVfx = field(default_factory=_FakeVfx)


class _UnusedScene:
    pass


class BattleMenuNavigationTest(unittest.TestCase):
    def test_right_moves_from_attack_to_spell(self):
        presenter = BattlePresenter(BattleModel(menu=0, phase="menu"))
        game = _FakeGame()
        game.input_state.press(RIGHT_BUTTONS)

        presenter.update(game, _UnusedScene())

        self.assertEqual(presenter.model.menu, 1)
        self.assertIn("cursor", game.sfx.played)

    def test_left_moves_from_spell_to_attack(self):
        presenter = BattlePresenter(BattleModel(menu=1, phase="menu"))
        game = _FakeGame()
        game.input_state.press(LEFT_BUTTONS)

        presenter.update(game, _UnusedScene())

        self.assertEqual(presenter.model.menu, 0)
        self.assertIn("cursor", game.sfx.played)

    def test_down_moves_from_attack_to_item(self):
        presenter = BattlePresenter(BattleModel(menu=0, phase="menu"))
        game = _FakeGame()
        game.input_state.press(DOWN_BUTTONS)

        presenter.update(game, _UnusedScene())

        self.assertEqual(presenter.model.menu, 2)
        self.assertIn("cursor", game.sfx.played)

    def test_up_moves_from_run_to_spell(self):
        presenter = BattlePresenter(BattleModel(menu=3, phase="menu"))
        game = _FakeGame()
        game.input_state.press(UP_BUTTONS)

        presenter.update(game, _UnusedScene())

        self.assertEqual(presenter.model.menu, 1)
        self.assertIn("cursor", game.sfx.played)


if __name__ == "__main__":
    unittest.main()
