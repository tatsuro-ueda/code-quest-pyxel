"""CJG/message_display: say / say_clear デバッグ表示バッファ。

根拠:
- docs/framework-rule.md M3-3（デバッグ情報は view layer で可視化）

say() は引数を say_buffer に積む。say_clear() で空にする。
Scratch の "say" ブロック相当。デバッグモード中の描画に使う。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.message_display import MessageDisplay


@dataclass
class _FakeGame:
    pass


class SayBufferTest(unittest.TestCase):
    def test_initial_buffer_is_empty(self):
        md = MessageDisplay(game=_FakeGame())
        self.assertEqual(md.say_buffer, [])

    def test_say_appends_string_representation(self):
        md = MessageDisplay(game=_FakeGame())

        md.say("hello")

        self.assertEqual(len(md.say_buffer), 1)

    def test_say_with_multiple_args(self):
        md = MessageDisplay(game=_FakeGame())

        md.say("a", "b", "c")

        self.assertEqual(len(md.say_buffer), 1)
        # "a b c" 的な何らかの文字列が入っている
        self.assertIn("a", md.say_buffer[0])

    def test_multiple_say_calls_accumulate(self):
        md = MessageDisplay(game=_FakeGame())

        md.say("first")
        md.say("second")
        md.say("third")

        self.assertEqual(len(md.say_buffer), 3)


if __name__ == "__main__":
    unittest.main()
