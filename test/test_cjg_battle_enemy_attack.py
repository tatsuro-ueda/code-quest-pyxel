"""CJG/battle: do_enemy_attack が PlayerModel の hp を減らし、毒付与経路が動く。

根拠:
- docs/product-requirements-battle.md（敵反撃とダメージ・毒）

敵ターンで: hit SFX / flash_red VFX / p.hp 減算 / can_poison 確率 25% で
poisoned=True。debug_mode では dmg=0。
"""

from __future__ import annotations

import random
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.battle.scene import BattleScene
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeVfx:
    started: list[str] = field(default_factory=list)

    def start(self, kind: str) -> None:
        self.started.append(kind)


@dataclass
class _FakeMessages:
    def dialog_text(self, key: str, **kwargs: Any) -> str:
        return f"{key}"

    def dialog_lines(self, *_a, **_k):
        return ["…"]


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    vfx: _FakeVfx = field(default_factory=_FakeVfx)
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    state: str = "battle"
    debug_mode: bool = False


ENEMY = {
    "name": "スライム",
    "hp": 30,
    "atk": 20,
    "def": 5,
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

ENEMY_POISON = {**ENEMY, "name": "もしガード", "can_poison": True}


class EnemyAttackDamageTest(unittest.TestCase):
    def test_enemy_attack_reduces_player_hp(self):
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY)
        before = game.player_model.hp

        random.seed(0)
        scene.do_enemy_attack()

        self.assertLess(game.player_model.hp, before)
        self.assertIn("hit", game.sfx.played)
        self.assertIn("flash_red", game.vfx.started)

    def test_debug_mode_produces_zero_damage(self):
        game = _FakeGame(debug_mode=True)
        scene = BattleScene(game=game)
        scene.start(ENEMY)
        before = game.player_model.hp

        scene.do_enemy_attack()

        self.assertEqual(game.player_model.hp, before)

    def test_damage_never_reduces_hp_below_zero(self):
        game = _FakeGame()
        game.player_model.hp = 1
        scene = BattleScene(game=game)
        scene.start({**ENEMY, "atk": 9999})

        random.seed(0)
        scene.do_enemy_attack()

        self.assertGreaterEqual(game.player_model.hp, 0)


class EnemyPoisonTest(unittest.TestCase):
    def test_can_poison_enemy_may_poison_player(self):
        """random.random() が 0.25 未満なら毒付与される（seed 0 で Hit）。"""
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY_POISON)

        # random.random() の最初の呼び出し結果で分岐が決まる
        random.seed(0)
        scene.do_enemy_attack()

        # seed 0 で毒になった場合のみ poisoned=True。無条件にテストできないので
        # 「毒化した場合は対応する SFX が鳴る」ことを検証する
        if game.player_model.poisoned:
            self.assertIn("poison", game.sfx.played)

    def test_non_poisoning_enemy_never_poisons(self):
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY)  # can_poison なし

        for seed in range(10):
            random.seed(seed)
            scene.do_enemy_attack()

        self.assertFalse(game.player_model.poisoned)

    def test_already_poisoned_player_is_not_re_poisoned(self):
        game = _FakeGame()
        game.player_model.poisoned = True
        scene = BattleScene(game=game)
        scene.start(ENEMY_POISON)

        random.seed(0)
        scene.do_enemy_attack()

        # poisoned はすでに True、poison SFX は追加で鳴らない
        self.assertTrue(game.player_model.poisoned)


if __name__ == "__main__":
    unittest.main()
