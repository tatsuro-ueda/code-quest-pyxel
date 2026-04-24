"""CJG/crash regression: 音声選択が全 state × zone 組み合わせで crash しない（Phase I）。

根拠:
- docs/product-requirements-av.md（BGM の切替と SFX の用意）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

choose_bgm_scene は純粋関数で、state × zone × 戦闘状態の組み合わせから BGM
シーン名を返す。欠落や TypeError が出ると各 state 遷移のたびに落ちる。
SFX_DEFINITIONS は SfxSystem._load が全スロットへ流し込む辞書。キーが欠けると
`game.sfx.play("cursor")` などが黙って無音になり体験が壊れる。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.audio_system import (
    CHIPTUNE_TRACKS,
    SFX_DEFINITIONS,
    choose_bgm_scene,
)


class ChooseBgmSceneExhaustiveTest(unittest.TestCase):
    """全ての (state, in_dungeon, zone) 組み合わせで例外を投げず文字列を返す。"""

    _STATES = (
        "splash",
        "title",
        "map",
        "battle",
        "menu",
        "settings",
        "message",
        "town",
        "town_menu",
        "professor_intro",
        "professor_ending_main",
        "professor_ending_accepted",
        "shop",
        "ending",
        "ai_help",
    )

    def test_every_state_zone_combo_returns_known_bgm_scene(self):
        """全組み合わせで CHIPTUNE_TRACKS に存在するシーン名を返す。"""
        for state in self._STATES:
            for in_dungeon in (True, False):
                for zone in range(5):  # zone 0 〜 4（全 5 zone）
                    with self.subTest(state=state, in_dungeon=in_dungeon, zone=zone):
                        scene = choose_bgm_scene(
                            state=state,
                            in_dungeon=in_dungeon,
                            zone=zone,
                        )
                        self.assertIsInstance(scene, str)
                        self.assertIn(
                            scene,
                            CHIPTUNE_TRACKS,
                            f"BGM scene `{scene}` が CHIPTUNE_TRACKS に無い",
                        )

    def test_battle_state_switches_based_on_glitch_lord_and_phase(self):
        """戦闘 state の内部で result/victory / boss / battle 分岐が通る。"""
        scene = choose_bgm_scene(
            state="battle",
            in_dungeon=False,
            zone=0,
            battle_is_glitch_lord=False,
            battle_enemy_hp=10,
            battle_phase="menu",
        )
        self.assertEqual(scene, "battle")

        boss = choose_bgm_scene(
            state="battle",
            in_dungeon=True,
            zone=4,
            battle_is_glitch_lord=True,
        )
        self.assertEqual(boss, "boss")

        victory = choose_bgm_scene(
            state="battle",
            in_dungeon=False,
            zone=0,
            battle_enemy_hp=0,
            battle_phase="result",
        )
        self.assertEqual(victory, "victory")

    def test_dungeon_flag_overrides_field_choice(self):
        """フィールド state でも in_dungeon なら dungeon BGM に切り替わる。"""
        scene = choose_bgm_scene(state="map", in_dungeon=True, zone=0)
        self.assertEqual(scene, "dungeon")


class SfxDefinitionsContractTest(unittest.TestCase):
    """SFX_DEFINITIONS には UI / 戦闘 / 移動で必須のキーが揃う。"""

    _REQUIRED_SFX = (
        "cursor",
        "select",
        "cancel",
        "attack",
        "hit",
        "heal",
        "levelup",
        "victory",
        "save",
        "encounter",
        "miss",
        "dead",
        "magic",
        "poison",
        "cure",
        "dungeon_in",
    )

    def test_required_sfx_names_are_all_defined(self):
        for name in self._REQUIRED_SFX:
            with self.subTest(sfx=name):
                self.assertIn(
                    name,
                    SFX_DEFINITIONS,
                    f"SFX `{name}` が欠けている。UI / 戦闘経路で黙って無音になる",
                )

    def test_every_sfx_entry_has_required_shape(self):
        """全エントリが tone / notes / volume / effect / speed を持つ（SfxSystem._load の契約）。"""
        required_keys = ("tone", "notes", "volume", "effect", "speed")
        for name, definition in SFX_DEFINITIONS.items():
            with self.subTest(sfx=name):
                for key in required_keys:
                    self.assertIn(
                        key,
                        definition,
                        f"SFX `{name}` に {key} が無い",
                    )
                self.assertIsInstance(definition["speed"], int)
                self.assertGreater(definition["speed"], 0)


class ChiptuneTracksContractTest(unittest.TestCase):
    """BGM 辞書が「choose_bgm_scene の戻り値集合」と矛盾しないこと。"""

    def test_all_bgm_return_values_resolve_to_defined_tracks(self):
        """choose_bgm_scene が返しうる値は全て CHIPTUNE_TRACKS に存在する。"""
        return_candidates = {
            "title", "ending", "battle", "boss", "victory",
            "town", "dungeon", "overworld",
        }
        for name in return_candidates:
            with self.subTest(track=name):
                self.assertIn(
                    name,
                    CHIPTUNE_TRACKS,
                    f"choose_bgm_scene が返しうる `{name}` が CHIPTUNE_TRACKS に無い",
                )

    def test_every_track_has_melody_bass_drums_and_speed(self):
        """各 track が必要な譜面 3 系統 + speed を持つ（AudioManager._load_tracks の契約）。"""
        for name, data in CHIPTUNE_TRACKS.items():
            with self.subTest(track=name):
                for key in ("melody", "bass", "drums", "speed", "gain"):
                    self.assertIn(key, data, f"track `{name}` に `{key}` が無い")


if __name__ == "__main__":
    unittest.main()
