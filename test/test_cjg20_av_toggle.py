"""CJG20: 演出（BGM/SFX/VFX）ON/OFF のトグルでゲーム本体が止まらない（Phase D）。

根拠:
- docs/product-requirements-platform.md CJG20 `Rule: 演出を切ってもゲーム本体は止まらない`
  Scenario: BGM/SFX/VFX をすべて OFF にしてもゲームは正常動作
- docs/product-requirements-platform.md CJG20 `Rule: 演出を戻したら違いがその場で分かる`
  Scenario: 切り替えが即座に反映

SettingsPresenter._toggle と apply_av が PlayerModel の 3 フラグを切り替え、
audio / sfx の set_enabled を呼ぶ。VFX は PlayerModel.vfx_enabled を VfxSystem が
参照する方式（state 描画の直前でチェック）。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeAudio:
    enabled: bool = True

    def set_enabled(self, flag: bool) -> None:
        self.enabled = bool(flag)


@dataclass
class _FakeSfx:
    enabled: bool = True

    def set_enabled(self, flag: bool) -> None:
        self.enabled = bool(flag)


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    audio: _FakeAudio = field(default_factory=_FakeAudio)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)


class CJG20AllDisabledStillPlayableTest(unittest.TestCase):
    """演出を全 OFF にしてもゲーム本体（PlayerModel のルール）が正常動作する。"""

    def test_av_flags_default_on_initial_player(self):
        pm = PlayerModel.new_game()
        self.assertTrue(pm.bgm_enabled)
        self.assertTrue(pm.sfx_enabled)
        self.assertTrue(pm.vfx_enabled)

    def test_disabling_all_flags_does_not_break_core_rules(self):
        """BGM/SFX/VFX を全て OFF にしても PlayerModel のダメージ適用は通常通り動く。"""
        pm = PlayerModel.new_game()
        pm.bgm_enabled = False
        pm.sfx_enabled = False
        pm.vfx_enabled = False

        # ダメージ→回復→アイテム増減が OFF フラグに関係なく通る
        before_hp = pm.hp
        pm.apply_damage(10)
        self.assertEqual(pm.hp, before_hp - 10)

        pm.heal(5)
        self.assertEqual(pm.hp, before_hp - 5)

        pm.buy_weapon(1, 10)  # gold=50 なので 10 G の weapon=1 は買える
        self.assertEqual(pm.weapon, 1)


class CJG20ToggleAppliesImmediatelyTest(unittest.TestCase):
    """settings 画面の _toggle が PlayerModel フラグと audio/sfx を即座に反映する。"""

    def _build_settings(self) -> tuple[Any, _FakeGame]:
        from src.scenes.settings.scene import SettingsScene

        game = _FakeGame()
        scene = SettingsScene(game=game)
        return scene, game

    def test_toggle_bgm_disables_audio(self):
        scene, game = self._build_settings()

        scene._toggle("bgm_enabled")

        self.assertFalse(game.player_model.bgm_enabled)
        self.assertFalse(game.audio.enabled)

    def test_toggle_bgm_back_on_reenables_audio(self):
        scene, game = self._build_settings()
        scene._toggle("bgm_enabled")  # OFF
        scene._toggle("bgm_enabled")  # ON に戻す

        self.assertTrue(game.player_model.bgm_enabled)
        self.assertTrue(game.audio.enabled)

    def test_toggle_sfx_disables_sfx_system(self):
        scene, game = self._build_settings()

        scene._toggle("sfx_enabled")

        self.assertFalse(game.player_model.sfx_enabled)
        self.assertFalse(game.sfx.enabled)

    def test_toggle_all_av_flips_all_three_flags_together(self):
        """`all_av` トグルは BGM/SFX/VFX を同じ値にまとめる。"""
        scene, game = self._build_settings()

        # 初期値は全 True → 全 False に
        scene._toggle("all_av")

        self.assertFalse(game.player_model.bgm_enabled)
        self.assertFalse(game.player_model.sfx_enabled)
        self.assertFalse(game.player_model.vfx_enabled)
        self.assertFalse(game.audio.enabled)
        self.assertFalse(game.sfx.enabled)

        # 再度トグル → 全 True に戻る
        scene._toggle("all_av")

        self.assertTrue(game.player_model.bgm_enabled)
        self.assertTrue(game.player_model.sfx_enabled)
        self.assertTrue(game.player_model.vfx_enabled)
        self.assertTrue(game.audio.enabled)
        self.assertTrue(game.sfx.enabled)

    def test_toggle_vfx_does_not_touch_audio_or_sfx(self):
        """VFX は独立トグル。audio / sfx の状態は変わらない。"""
        scene, game = self._build_settings()

        scene._toggle("vfx_enabled")

        self.assertFalse(game.player_model.vfx_enabled)
        self.assertTrue(game.audio.enabled)
        self.assertTrue(game.sfx.enabled)


class CJG20FlagsSurviveSnapshotTest(unittest.TestCase):
    """AV フラグはセーブ→ロードで保存される（CJG20 前提）。"""

    def test_all_three_flags_persist_through_save_round_trip(self):
        pm = PlayerModel.new_game()
        pm.bgm_enabled = False
        pm.sfx_enabled = False
        pm.vfx_enabled = False

        snap = pm.to_snapshot(town_pos=(25, 6))
        restored, _pos = PlayerModel.from_snapshot(snap)

        self.assertFalse(restored.bgm_enabled)
        self.assertFalse(restored.sfx_enabled)
        self.assertFalse(restored.vfx_enabled)


if __name__ == "__main__":
    unittest.main()
