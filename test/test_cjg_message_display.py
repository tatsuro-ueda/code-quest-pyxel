"""CJG/message: MessageDisplay の show / enter / advance_page / wrap_text / update。

根拠:
- docs/product-requirements-narrative.md（セリフ表示とページ送り）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

MessageDisplay は町・探索・戦闘で広く使われる。wrap_text で折り返しが
壊れると長いセリフで文字化け、advance_page で off-by-one があると
エンディング前に state が戻る／無限ループに入る。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.message_display import MessageDisplay


@dataclass
class _FakeInputState:
    pressed: set[tuple[int, ...]] = field(default_factory=set)

    def btnp(self, buttons) -> bool:
        key = tuple(buttons) if hasattr(buttons, "__iter__") else (buttons,)
        return key in self.pressed

    def press(self, buttons):
        key = tuple(buttons) if hasattr(buttons, "__iter__") else (buttons,)
        self.pressed.add(key)


@dataclass
class _FakeGame:
    state: str = "message"
    prev_state: str = "map"
    input_state: _FakeInputState = field(default_factory=_FakeInputState)


class ShowAndEnterTest(unittest.TestCase):
    def test_show_sets_lines_and_resets_index(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)
        md.index = 5  # リセットされるはず

        md.show(["a", "b", "c"])

        self.assertEqual(md.lines, ["a", "b", "c"])
        self.assertEqual(md.index, 0)
        self.assertIsNone(md.callback)

    def test_show_accepts_callback(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)
        cb = lambda: "ran"

        md.show(["a"], callback=cb)

        self.assertIs(md.callback, cb)

    def test_enter_transitions_to_message_state(self):
        game = _FakeGame(state="map")
        md = MessageDisplay(game=game)

        md.enter(["hello"])

        self.assertEqual(game.state, "message")
        self.assertEqual(game.prev_state, "map")


class AdvancePageTest(unittest.TestCase):
    def test_advance_returns_next_index_and_not_done(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)

        next_idx, done = md.advance_page(0, ["a", "b"])

        self.assertEqual(next_idx, 1)
        self.assertFalse(done)

    def test_advance_last_page_marks_done(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)

        next_idx, done = md.advance_page(1, ["a", "b"])

        self.assertEqual(next_idx, 2)
        self.assertTrue(done)


class WrapTextTest(unittest.TestCase):
    def test_short_text_is_single_line(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)

        out = md.wrap_text("あいうえお", max_chars=28)

        self.assertEqual(out, ["あいうえお"])

    def test_long_text_is_split_into_fixed_width_chunks(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)

        out = md.wrap_text("a" * 60, max_chars=20)

        self.assertEqual(out, ["a" * 20, "a" * 20, "a" * 20])

    def test_explicit_newline_becomes_separate_line(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)

        out = md.wrap_text("line1\nline2", max_chars=28)

        self.assertEqual(out, ["line1", "line2"])

    def test_empty_input_returns_single_empty_line(self):
        """wrap_text は必ず 1 要素以上の list を返す（描画側で IndexError を起こさない）。"""
        game = _FakeGame()
        md = MessageDisplay(game=game)

        out = md.wrap_text("")

        self.assertEqual(out, [""])


class CurrentPageLinesTest(unittest.TestCase):
    def test_returns_wrapped_lines_capped_at_max_rows(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)

        out = md.current_page_lines(["a" * 100], 0, max_chars=10, max_rows=3)

        self.assertEqual(len(out), 3)

    def test_index_out_of_range_returns_empty(self):
        game = _FakeGame()
        md = MessageDisplay(game=game)

        self.assertEqual(md.current_page_lines(["a"], 5), [])
        self.assertEqual(md.current_page_lines([], 0), [])
        self.assertEqual(md.current_page_lines(["a"], -1), [])


class UpdateAdvanceFlowTest(unittest.TestCase):
    def test_confirm_advances_index(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        md = MessageDisplay(game=game)
        md.lines = ["a", "b", "c"]
        game.input_state.press(CONFIRM_BUTTONS)

        md.update()

        self.assertEqual(md.index, 1)
        self.assertEqual(game.state, "message")  # まだ終わっていない

    def test_confirm_on_last_page_returns_to_prev_state(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        md = MessageDisplay(game=game)
        md.lines = ["a"]
        md.index = 0
        game.input_state.press(CONFIRM_BUTTONS)

        md.update()

        self.assertEqual(game.state, game.prev_state)

    def test_callback_is_called_on_completion(self):
        from src.shared.services.input_bindings import CONFIRM_BUTTONS

        game = _FakeGame()
        md = MessageDisplay(game=game)
        md.lines = ["only"]
        md.index = 0
        called = []
        md.callback = lambda: called.append(True)
        game.input_state.press(CONFIRM_BUTTONS)

        md.update()

        self.assertEqual(called, [True])


if __name__ == "__main__":
    unittest.main()
