"""CJG/player: レベルアップで PlayerModel に呪文が追加される。

根拠:
- docs/product-requirements-narrative.md（呪文習得レベル）
- docs/product-requirements-battle.md（レベル上昇時の再計算）

battle/scene.py の check_level_up は spell の learn_lv に到達したら
PlayerModel.spells に name を追加する。PlayerModel.gain_exp 単体では
呪文は増えない（spells 追加は battle scene 経由）。本 tests は
BattleScene.check_level_up が spell を追加する流れを固定化する。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data
from src.scenes.battle.scene import BattleScene
from src.shared.state.player_model import PlayerModel, exp_for_level


@dataclass
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)


class LevelUpSpellLearnTest(unittest.TestCase):
    def test_reaching_learn_lv_adds_spell_name(self):
        # learn_lv が最小の呪文を見つける
        spell = min(game_data.SPELLS, key=lambda s: s["learn_lv"])
        target_lv = spell["learn_lv"]

        game = _FakeGame()
        pm = game.player_model
        pm.spells = []
        # level target_lv 到達に必要な exp を与える
        pm.exp = exp_for_level(target_lv)

        BattleScene(game=game).check_level_up()

        self.assertGreaterEqual(pm.lv, target_lv)
        self.assertIn(spell["name"], pm.spells)

    def test_level_below_learn_lv_does_not_add_spell(self):
        spell = min(game_data.SPELLS, key=lambda s: s["learn_lv"])
        # learn_lv より低いレベルではまだ習得しない
        game = _FakeGame()
        pm = game.player_model
        pm.lv = 1
        pm.spells = []

        BattleScene(game=game).check_level_up()

        if spell["learn_lv"] > 1:
            self.assertNotIn(spell["name"], pm.spells)


if __name__ == "__main__":
    unittest.main()
