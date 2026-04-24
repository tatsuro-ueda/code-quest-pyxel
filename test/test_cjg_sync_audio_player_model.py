"""CJG regression: sync_audio が PlayerModel 経由で読んで落ちないこと。

根拠:
- docs/product-requirements-battle.md / docs/product-requirements-av.md（BGM scene 同期）
- docs/customer-jobs.md Make3「ガードレール」
- 2026-04-25 PlayerModel 移行時に `game.player_model.bgm_enabled` / `in_dungeon` /
  `y` への書き換えが取りこぼされていたら、マップ遷移のたびに全画面で落ちる

`sync_audio` は `update()` の毎フレーム末尾で呼ばれる（src/runtime/app.py:128, 200）。
battle_scene.model.enemy / enemy_hp / is_glitch_lord / phase と
player_model.in_dungeon / y / bgm_enabled を読むので、そのどれかで
AttributeError / KeyError が出ると毎フレーム crash する。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@dataclass
class _FakeAudio:
    enabled_calls: list[bool] = field(default_factory=list)
    play_calls: list[str] = field(default_factory=list)

    def set_enabled(self, enabled: bool) -> None:
        self.enabled_calls.append(enabled)

    def play_scene(self, scene: str) -> None:
        self.play_calls.append(scene)


@dataclass
class _FakeBattleModel:
    enemy: dict | None = None
    enemy_hp: int = 0
    is_glitch_lord: bool = False
    phase: str = "menu"


@dataclass
class _FakeBattleScene:
    model: _FakeBattleModel = field(default_factory=_FakeBattleModel)


@dataclass
class _FakeSettingsScene:
    model: Any = None


@dataclass
class _FakeGame:
    state: str = "map"
    audio: _FakeAudio = field(default_factory=_FakeAudio)
    battle_scene: _FakeBattleScene = field(default_factory=_FakeBattleScene)
    settings_scene: _FakeSettingsScene = field(default_factory=_FakeSettingsScene)
    player_model: Any = None


class SyncAudioPlayerModelTest(unittest.TestCase):
    def setUp(self):
        from src.shared.state.player_model import PlayerModel

        self.PlayerModel = PlayerModel

    def _build_game(self, **kwargs):
        pm = self.PlayerModel.new_game()
        for k, v in kwargs.pop("player", {}).items():
            setattr(pm, k, v)
        settings_model = type("SettingsModel", (), {"origin": "menu"})()
        kwargs.setdefault("settings_scene", _FakeSettingsScene(model=settings_model))
        return _FakeGame(player_model=pm, **kwargs)

    def test_sync_audio_completes_on_map_without_exceptions(self):
        """state=map のフレームで sync_audio が落ちないこと。"""
        from src.shared.services.audio_system import sync_audio

        game = self._build_game(state="map")
        sync_audio(game)  # 落ちなければ OK

        self.assertEqual(len(game.audio.enabled_calls), 1)
        self.assertTrue(game.audio.enabled_calls[0])  # PlayerModel.bgm_enabled のデフォルトは True
        self.assertEqual(len(game.audio.play_calls), 1)

    def test_sync_audio_reflects_bgm_disabled_flag(self):
        """player_model.bgm_enabled=False なら audio.set_enabled(False) が渡る。"""
        from src.shared.services.audio_system import sync_audio

        game = self._build_game(state="map", player={"bgm_enabled": False})
        sync_audio(game)

        self.assertEqual(game.audio.enabled_calls, [False])

    def test_sync_audio_in_dungeon_flips_context(self):
        """in_dungeon=True でも crash せず BGM scene を選べる。"""
        from src.shared.services.audio_system import sync_audio

        game = self._build_game(state="map", player={"in_dungeon": True, "y": 20})
        sync_audio(game)

        # BGM scene が選択されている（空でない）こと
        self.assertEqual(len(game.audio.play_calls), 1)
        self.assertTrue(bool(game.audio.play_calls[0]))

    def test_sync_audio_on_battle_state_reads_battle_model(self):
        """state=battle のとき battle_scene.model を読む経路で crash しない。"""
        from src.shared.services.audio_system import sync_audio

        game = self._build_game(state="battle")
        game.battle_scene.model.enemy = {"hp": 30}
        game.battle_scene.model.enemy_hp = 20
        game.battle_scene.model.is_glitch_lord = False
        game.battle_scene.model.phase = "menu"

        sync_audio(game)

        self.assertEqual(len(game.audio.play_calls), 1)

    def test_sync_audio_on_glitch_lord_battle(self):
        """is_glitch_lord=True のラストバトル経路も crash しない。"""
        from src.shared.services.audio_system import sync_audio

        game = self._build_game(state="battle")
        game.battle_scene.model.enemy = {"hp": 200}
        game.battle_scene.model.enemy_hp = 150
        game.battle_scene.model.is_glitch_lord = True
        game.battle_scene.model.phase = "player_turn"

        sync_audio(game)

        self.assertEqual(len(game.audio.play_calls), 1)

    def test_sync_audio_handles_all_field_zones(self):
        """プレイヤー座標を zone 0-3 それぞれで sync_audio が crash しないこと。

        zone 判定（`world_generation.get_zone`）: y<16→0, <28→1, <38→2, else→3。
        zone 4 は in_dungeon フラグで決まるので別テスト。
        """
        from src.shared.services.audio_system import sync_audio

        zone_to_y = {0: 10, 1: 20, 2: 30, 3: 50}
        for zone_id, y in zone_to_y.items():
            with self.subTest(zone_id=zone_id, y=y):
                game = self._build_game(state="map", player={"y": y, "in_dungeon": False})
                sync_audio(game)
                self.assertEqual(len(game.audio.play_calls), 1)
                self.assertTrue(bool(game.audio.play_calls[0]))


if __name__ == "__main__":
    unittest.main()
