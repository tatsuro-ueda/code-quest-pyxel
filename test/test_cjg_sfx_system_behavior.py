"""CJG/sfx: SfxSystem の play / slot 管理。

根拠:
- docs/product-requirements-av.md（SFX）
- docs/customer-jobs.md Make3

2026-05-07 改訂（CJ44 確定版）：set_enabled 機構は撤去済（SFX は常に ON）。
play() は未定義名を黙って無視（KeyError にならない）。init 時に空スロットへは
fallback 定義を set する（import 済み SFX は上書きしない）。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.audio_system import SfxSystem


class _FakeSound:
    def __init__(self, has_content: bool = False):
        self._has = has_content
        self.set_calls: list[tuple] = []

    @property
    def notes(self):
        return "c3c3" if self._has else ""

    @property
    def tones(self):
        return "" if self._has else ""

    def set(self, notes, tones, volumes, effects, speed):
        self.set_calls.append((notes, tones, volumes, effects, speed))


class _FakeChannel:
    def __init__(self):
        self.gain = 0.5


class _FakePyxel:
    def __init__(self):
        self.sounds = [_FakeSound() for _ in range(64)]
        self.channels = [_FakeChannel() for _ in range(4)]
        self.play_calls: list = []
        self.stop_calls: list = []

    def play(self, ch, slot, loop=False):
        self.play_calls.append((ch, slot, loop))

    def stop(self, ch=None):
        self.stop_calls.append(ch)


class SfxPlayTest(unittest.TestCase):
    def test_unknown_name_is_silently_ignored(self):
        fp = _FakePyxel()
        sfx = SfxSystem(fp)

        sfx.play("nonexistent_sound")

        self.assertEqual(fp.play_calls, [])

    def test_known_name_triggers_pyxel_play(self):
        fp = _FakePyxel()
        sfx = SfxSystem(fp)

        sfx.play("cursor")

        self.assertEqual(len(fp.play_calls), 1)

class SfxLoadTest(unittest.TestCase):
    def test_load_populates_empty_slots(self):
        fp = _FakePyxel()
        SfxSystem(fp)

        # 1 つ以上のスロットに set が呼ばれている
        total_sets = sum(len(s.set_calls) for s in fp.sounds)
        self.assertGreater(total_sets, 0)

    def test_existing_content_is_not_overwritten(self):
        fp = _FakePyxel()
        # 最初のスロット（SFX_BASE_SLOT）に既に content ありとする
        fp.sounds[33] = _FakeSound(has_content=True)

        SfxSystem(fp)

        # そのスロットには set が呼ばれていない（skip された）
        self.assertEqual(fp.sounds[33].set_calls, [])


if __name__ == "__main__":
    unittest.main()
