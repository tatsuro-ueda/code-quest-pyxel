"""CJG/battle: 戦闘の start / attack / victory / defeat / level-up が crash しない（Phase F）。

根拠:
- docs/product-requirements-battle.md（戦闘の進行）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

BattleScene のコア遷移を fake game で回し、PlayerModel が期待どおり更新される
ことと、AttributeError / KeyError / ZeroDivisionError が出ないことを固定化する。
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
from src.shared.state.player_model import PlayerModel, exp_for_level


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
        return f"{key}::{sorted(kwargs.items())}"

    def dialog_lines(self, *_args, **_kwargs):
        return ["…"]

    def enter(self, *_args, **_kwargs):
        pass


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    vfx: _FakeVfx = field(default_factory=_FakeVfx)
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    state: str = "map"
    debug_mode: bool = False
    last_town_pos: tuple[int, int] | None = None


ENEMY_FIXTURE = {
    "name": "スライム",
    "hp": 30,
    "atk": 5,
    "def": 2,
    "agi": 3,
    "exp": 100,
    "gold": 20,
    "zone": 0,
    "category": "normal",
    "color": 11,
    "sprite": 0,
    "type": "physical",
    "has_sprite": True,
}


class BattleStartTest(unittest.TestCase):
    """BattleScene.start で enemy state が正しくセットされる。"""

    def test_start_sets_enemy_hp_and_state_to_battle(self):
        game = _FakeGame()
        scene = BattleScene(game=game)

        scene.start(ENEMY_FIXTURE)

        self.assertEqual(game.state, "battle")
        self.assertEqual(scene.model.enemy_hp, ENEMY_FIXTURE["hp"])
        self.assertEqual(scene.model.enemy["name"], "スライム")
        self.assertEqual(scene.model.phase, "menu")
        self.assertIn("encounter", game.sfx.played)

    def test_start_glitch_lord_sets_intro_text(self):
        game = _FakeGame()
        scene = BattleScene(game=game)

        scene.start(ENEMY_FIXTURE, is_glitch_lord=True)

        self.assertTrue(scene.model.is_glitch_lord)
        self.assertTrue(scene.model.text)  # intro text がセットされる


class PlayerAttackTest(unittest.TestCase):
    """do_player_attack で enemy_hp が減り attack SFX と VFX が鳴る。"""

    def test_debug_mode_one_shot_reduces_enemy_hp_to_zero(self):
        game = _FakeGame(debug_mode=True)
        scene = BattleScene(game=game)
        scene.start(ENEMY_FIXTURE)

        random.seed(0)  # attack 乱数は dmg 決定に使われるが debug_mode でキャンセルされる
        scene.do_player_attack()

        self.assertEqual(scene.model.enemy_hp, 0)
        self.assertIn("attack", game.sfx.played)
        self.assertIn("flash_white", game.vfx.started)
        self.assertEqual(scene.model.phase, "player_attack")

    def test_player_attack_reduces_enemy_hp_by_positive_amount(self):
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY_FIXTURE)

        random.seed(42)
        before = scene.model.enemy_hp
        scene.do_player_attack()

        self.assertLess(scene.model.enemy_hp, before)
        self.assertGreaterEqual(scene.model.enemy_hp, 0)


class VictoryAwardsExpAndGoldTest(unittest.TestCase):
    """victory で PlayerModel の exp / gold が加算され、phase=result に進む。"""

    def test_victory_grants_enemy_exp_and_gold(self):
        game = _FakeGame()
        pm = game.player_model
        before_exp = pm.exp
        before_gold = pm.gold
        scene = BattleScene(game=game)
        scene.start(ENEMY_FIXTURE)

        scene.victory()

        self.assertEqual(pm.exp, before_exp + ENEMY_FIXTURE["exp"])
        self.assertEqual(pm.gold, before_gold + ENEMY_FIXTURE["gold"])
        self.assertEqual(scene.model.phase, "result")
        self.assertIn("victory", game.sfx.played)

    def test_victory_against_professor_uses_silent_victory_text(self):
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY_FIXTURE, is_professor=True)

        # is_professor なので exp/gold 付与ではなく silent_victory 分岐
        before_gold = game.player_model.gold
        scene.victory()

        self.assertEqual(game.player_model.gold, before_gold)
        self.assertEqual(scene.model.phase, "result")
        self.assertIn("silent_victory", scene.model.text)


class DefeatDoesNotCrashTest(unittest.TestCase):
    """defeat() は result phase に遷移して dead SFX を鳴らす。"""

    def test_defeat_sets_result_and_plays_dead(self):
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY_FIXTURE)

        scene.defeat()

        self.assertEqual(scene.model.phase, "result")
        self.assertIn("dead", game.sfx.played)


class LevelUpCheckTest(unittest.TestCase):
    """check_level_up が exp 閾値でレベルアップさせ max_hp / max_mp を再計算する。"""

    def test_level_up_happens_when_exp_crosses_threshold(self):
        game = _FakeGame()
        pm = game.player_model
        self.assertEqual(pm.lv, 1)

        # Level 2 に必要な exp まで積む
        pm.exp = exp_for_level(2)

        scene = BattleScene(game=game)
        scene.check_level_up()

        self.assertEqual(pm.lv, 2)
        self.assertEqual(pm.hp, pm.max_hp)  # レベルアップで全回復
        self.assertIn("levelup", game.sfx.played)

    def test_no_level_up_when_exp_below_threshold(self):
        game = _FakeGame()
        pm = game.player_model
        pm.exp = 0

        scene = BattleScene(game=game)
        scene.check_level_up()

        self.assertEqual(pm.lv, 1)
        self.assertNotIn("levelup", game.sfx.played)


class SpellHealEffectTest(unittest.TestCase):
    """apply_spell_effect の heal 呪文が HP を max_hp を超えない範囲で回復する。"""

    def test_heal_spell_restores_hp_capped_at_max(self):
        game = _FakeGame()
        pm = game.player_model
        pm.hp = 1
        scene = BattleScene(game=game)
        scene.start(ENEMY_FIXTURE)

        msg = scene.apply_spell_effect({"name": "ヒール", "type": "heal", "power": 9999})

        self.assertEqual(pm.hp, pm.max_hp)
        self.assertIn("回復", msg)


if __name__ == "__main__":
    unittest.main()
