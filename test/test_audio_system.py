from __future__ import annotations

import sys
import unittest
from pathlib import Path


PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))


class _FakeSound:
    def __init__(self):
        self.set_calls: list[tuple] = []

    def set(self, notes, tones, volumes, effects, speed):
        self.set_calls.append((notes, tones, volumes, effects, speed))


class _FakeMusic:
    def __init__(self):
        self.set_calls: list[tuple] = []

    def set(self, seqs0, seqs1, seqs2, seqs3):
        self.set_calls.append((seqs0, seqs1, seqs2, seqs3))


class _FakeChannel:
    def __init__(self):
        self.gain = 0.125


class _FakePyxel:
    def __init__(self):
        self.sounds = [_FakeSound() for _ in range(64)]
        self.musics = [_FakeMusic() for _ in range(8)]
        self.channels = [_FakeChannel() for _ in range(4)]
        self.play_calls: list[tuple] = []
        self.playm_calls: list[tuple] = []
        self.stop_calls: list = []

    def play(self, ch, snd, loop=False):
        self.play_calls.append((ch, snd, loop))

    def playm(self, music_idx, loop=False):
        self.playm_calls.append((music_idx, loop))

    def stop(self, ch=None):
        self.stop_calls.append(ch)


class AudioSystemTest(unittest.TestCase):
    def setUp(self):
        from src.audio_system import (
            AudioManager,
            BASS_CHANNEL,
            DRUM_CHANNEL,
            MELODY_CHANNEL,
            bass_slot,
            choose_bgm_scene,
            drum_slot,
            melody_slot,
            music_index,
            track_slot,
        )

        self.AudioManager = AudioManager
        self.choose_bgm_scene = choose_bgm_scene
        self.melody_slot = melody_slot
        self.bass_slot = bass_slot
        self.drum_slot = drum_slot
        self.music_index = music_index
        self.track_slot = track_slot
        self.MELODY_CHANNEL = MELODY_CHANNEL
        self.BASS_CHANNEL = BASS_CHANNEL
        self.DRUM_CHANNEL = DRUM_CHANNEL

    def test_choose_bgm_scene_for_title_map_and_dungeon(self):
        self.assertEqual(
            self.choose_bgm_scene(state="title", in_dungeon=False, zone=0),
            "title",
        )
        self.assertEqual(
            self.choose_bgm_scene(state="map", in_dungeon=False, zone=0),
            "town",
        )
        # zone1/2/3 はすべて overworld にマップされる
        for z in (1, 2, 3, 4):
            self.assertEqual(
                self.choose_bgm_scene(state="map", in_dungeon=False, zone=z),
                "overworld",
            )
        self.assertEqual(
            self.choose_bgm_scene(state="map", in_dungeon=True, zone=4),
            "dungeon",
        )

    def test_choose_bgm_scene_for_battle_glitch_lord_and_ending(self):
        self.assertEqual(
            self.choose_bgm_scene(
                state="battle",
                in_dungeon=False,
                zone=1,
                battle_is_glitch_lord=False,
                battle_enemy_hp=30,
                battle_enemy_max_hp=100,
                battle_phase="menu",
            ),
            "battle",
        )
        # ボスはフェーズによらず常に "boss"
        self.assertEqual(
            self.choose_bgm_scene(
                state="battle",
                in_dungeon=True,
                zone=4,
                battle_is_glitch_lord=True,
                battle_enemy_hp=250,
                battle_enemy_max_hp=500,
                battle_phase="menu",
            ),
            "boss",
        )
        self.assertEqual(
            self.choose_bgm_scene(
                state="battle",
                in_dungeon=True,
                zone=4,
                battle_is_glitch_lord=True,
                battle_enemy_hp=150,
                battle_enemy_max_hp=500,
                battle_phase="enemy_attack",
            ),
            "boss",
        )
        self.assertEqual(
            self.choose_bgm_scene(
                state="battle",
                in_dungeon=True,
                zone=4,
                battle_is_glitch_lord=True,
                battle_enemy_hp=0,
                battle_enemy_max_hp=500,
                battle_phase="result",
            ),
            "victory",
        )
        self.assertEqual(
            self.choose_bgm_scene(state="ending", in_dungeon=False, zone=0),
            "ending",
        )

    def test_audio_manager_loads_chiptune_tracks_into_three_slots_per_scene(self):
        fake_pyxel = _FakePyxel()
        self.AudioManager(fake_pyxel)

        # title のメロディスロットに pulse トーンの set() が走っているはず
        title_melody = fake_pyxel.sounds[self.melody_slot("title")].set_calls
        self.assertEqual(len(title_melody), 1)
        notes, tones, _, _, _ = title_melody[0]
        self.assertIn("e2", notes)
        self.assertEqual(tones, "p")

        # title のベーススロットは triangle
        title_bass = fake_pyxel.sounds[self.bass_slot("title")].set_calls
        self.assertEqual(title_bass[0][1], "t")

        # title のドラムスロットは noise
        title_drum = fake_pyxel.sounds[self.drum_slot("title")].set_calls
        self.assertEqual(title_drum[0][1], "n")

    def test_audio_manager_populates_music_slots(self):
        fake_pyxel = _FakePyxel()
        self.AudioManager(fake_pyxel)

        # title music slot は [m_slot], [b_slot], [d_slot], [] で set される
        title_music = fake_pyxel.musics[self.music_index("title")].set_calls
        self.assertEqual(len(title_music), 1)
        seqs0, seqs1, seqs2, seqs3 = title_music[0]
        self.assertEqual(seqs0, [self.melody_slot("title")])
        self.assertEqual(seqs1, [self.bass_slot("title")])
        self.assertEqual(seqs2, [self.drum_slot("title")])
        self.assertEqual(seqs3, [])  # ch3 は SFX 用に空

    def test_play_scene_uses_playm_and_skips_duplicate_calls(self):
        fake_pyxel = _FakePyxel()
        manager = self.AudioManager(fake_pyxel)

        manager.play_scene("title")
        manager.play_scene("title")  # 重複呼び出しは無視
        manager.play_scene("overworld")

        # playm が2回（重複は無視）
        self.assertEqual(
            fake_pyxel.playm_calls,
            [
                (self.music_index("title"), True),
                (self.music_index("overworld"), True),
            ],
        )

    def test_track_slot_aliases_melody_slot(self):
        from src.audio_system import TRACK_ORDER

        for scene in TRACK_ORDER:
            self.assertEqual(self.track_slot(scene), self.melody_slot(scene))

    def test_track_count_fits_pyxel_music_slots(self):
        from src.audio_system import TRACK_ORDER

        # Pyxel は musics[0..7] の8スロットしか持たない
        self.assertLessEqual(len(TRACK_ORDER), 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
