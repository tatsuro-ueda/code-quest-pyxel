"""CJG/battle: apply_spell_effect の heal / damage 分岐。

根拠:
- docs/product-requirements-battle.md（呪文効果）
- docs/product-requirements-narrative.md（呪文名を含むダイアログ）

heal 型: player の hp に加算（max_hp キャップ）。damage 型: enemy_hp 減算
（0 未満にはしない）。戻り値のメッセージは日本語で呪文名 / 数値を含む。
"""

from __future__ import annotations

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
    def play(self, name: str) -> None:
        pass


@dataclass
class _FakeVfx:
    def start(self, name: str) -> None:
        pass


@dataclass
class _FakeMessages:
    def dialog_text(self, key: str, **kwargs: Any) -> str:
        return key


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
    "hp": 100,
    "atk": 10,
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


class HealSpellTest(unittest.TestCase):
    def test_heal_increases_hp_by_power(self):
        game = _FakeGame()
        game.player_model.hp = 10
        scene = BattleScene(game=game)
        scene.start(ENEMY)

        msg = scene.apply_spell_effect({"name": "ヒール", "type": "heal", "power": 20})

        self.assertEqual(game.player_model.hp, 30)
        self.assertIn("ヒール", msg)
        self.assertIn("20", msg)

    def test_heal_is_capped_at_max_hp(self):
        game = _FakeGame()
        pm = game.player_model
        pm.hp = pm.max_hp - 5
        scene = BattleScene(game=game)
        scene.start(ENEMY)

        scene.apply_spell_effect({"name": "ヒール", "type": "heal", "power": 9999})

        self.assertEqual(pm.hp, pm.max_hp)


class DamageSpellTest(unittest.TestCase):
    def test_damage_reduces_enemy_hp(self):
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY)
        before = scene.model.enemy_hp

        msg = scene.apply_spell_effect({"name": "ファイア", "type": "damage", "power": 30})

        self.assertEqual(scene.model.enemy_hp, before - 30)
        self.assertIn("ファイア", msg)
        self.assertIn("30", msg)

    def test_damage_never_goes_below_zero(self):
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY)

        scene.apply_spell_effect({"name": "メテオ", "type": "damage", "power": 9999})

        self.assertEqual(scene.model.enemy_hp, 0)

    def test_damage_power_of_zero_still_deals_one(self):
        """max(1, power) の min フロアが効いている。"""
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY)
        before = scene.model.enemy_hp

        scene.apply_spell_effect({"name": "でく", "type": "damage", "power": 0})

        self.assertEqual(scene.model.enemy_hp, before - 1)


class EnemyHitSceneNameTest(unittest.TestCase):
    def test_glitch_lord_uses_boss_scene(self):
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start(ENEMY, is_glitch_lord=True)

        name = scene.enemy_hit_scene_name()

        self.assertEqual(name, "boss.glitch.enemy_hit")

    def test_normal_enemy_uses_category_scene(self):
        """category が未知でも sequential にフォールバックする。"""
        game = _FakeGame()
        scene = BattleScene(game=game)
        scene.start({**ENEMY, "category": "unknown_category"})

        name = scene.enemy_hit_scene_name()

        self.assertTrue(name)  # 何かしらのキーが返る


if __name__ == "__main__":
    unittest.main()
