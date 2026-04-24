"""CJG/audio: AudioManager の enabled / play_scene 挙動。

根拠:
- docs/product-requirements-av.md（BGM の切替）
- docs/customer-jobs.md Make3（crash 回避）

AudioManager は enabled=False のとき play_scene が stop を呼ぶ。
同じシーンを連続で play_scene しても再度 playm は呼ばない。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.audio_system import AudioManager, CHIPTUNE_TRACKS


class _FakeSound:
    def __init__(self):
        self.set_calls: list[tuple] = []

    def set(self, *args, **kwargs):
        self.set_calls.append((args, kwargs))


class _FakeChannel:
    def __init__(self):
        self.gain = 0.125


class _FakePyxel:
    def __init__(self):
        self.sounds = [_FakeSound() for _ in range(64)]
        self.musics = [_FakeSound() for _ in range(8)]
        self.channels = [_FakeChannel() for _ in range(4)]
        self.playm_calls: list = []
        self.stop_calls: list = []

    def playm(self, music_id, loop=False):
        self.playm_calls.append((music_id, loop))

    def stop(self, ch=None):
        self.stop_calls.append(ch)


class AudioManagerPlaySceneTest(unittest.TestCase):
    def test_play_scene_starts_music_when_enabled(self):
        fp = _FakePyxel()
        mgr = AudioManager(fp)

        # 最初のロードで playm は呼ばれていない
        calls_before = len(fp.playm_calls)
        mgr.play_scene("title")

        self.assertGreater(len(fp.playm_calls), calls_before)
        self.assertEqual(mgr.current_scene, "title")

    def test_play_scene_same_scene_twice_does_not_restart(self):
        fp = _FakePyxel()
        mgr = AudioManager(fp)
        mgr.play_scene("title")
        calls_after_first = len(fp.playm_calls)

        mgr.play_scene("title")

        self.assertEqual(len(fp.playm_calls), calls_after_first)

    def test_set_enabled_false_stops_music(self):
        fp = _FakePyxel()
        mgr = AudioManager(fp)
        mgr.play_scene("title")

        mgr.set_enabled(False)

        self.assertFalse(mgr.enabled)
        self.assertGreater(len(fp.stop_calls), 0)

    def test_play_scene_while_disabled_does_nothing_new(self):
        fp = _FakePyxel()
        mgr = AudioManager(fp)
        mgr.set_enabled(False)
        calls_before = len(fp.playm_calls)

        mgr.play_scene("battle")

        self.assertEqual(len(fp.playm_calls), calls_before)


class AudioManagerLoadsAllTracksTest(unittest.TestCase):
    def test_init_sets_music_and_sound_for_every_track(self):
        """_load_tracks が CHIPTUNE_TRACKS の全 scene を roundtrip でロードする。"""
        fp = _FakePyxel()
        AudioManager(fp)  # init で _load_tracks が走る

        # ざっくり全 scene 分の sound.set 呼び出しが起きている
        total_sound_sets = sum(len(s.set_calls) for s in fp.sounds)
        self.assertGreaterEqual(total_sound_sets, len(CHIPTUNE_TRACKS) * 3)  # melody+bass+drums


if __name__ == "__main__":
    unittest.main()
