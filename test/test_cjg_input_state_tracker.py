"""CJG/input_state: InputStateTracker の btnp/btn 集約と状態更新。

根拠:
- docs/framework-rule.md M1-2（入力取得は 1 か所に集約）

InputStateTracker は毎フレーム update(pyxel) して内部状態を作り、
btnp(group) は held の立ち上がり（前フレーム非押下 → 今フレーム押下）で True、
btn(group) は押下中かを返す。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.input_bindings import (
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    InputStateTracker,
    UP_BUTTONS,
)


class _FakePyxel:
    def __init__(self, held=(), pressed=()):
        self._held = set(held)
        self._pressed = set(pressed)

    def __getattr__(self, name):
        return name

    def btn(self, code):
        return code in self._held

    def btnp(self, code):
        return code in self._pressed


class TrackerBtnpTest(unittest.TestCase):
    """btnp は held の立ち上がりを検出する（エッジ）。"""

    def test_btnp_true_on_press_edge(self):
        tracker = InputStateTracker()
        tracker.update(_FakePyxel(held=[UP_BUTTONS[0]]))

        self.assertTrue(tracker.btnp(UP_BUTTONS))

    def test_btnp_false_when_nothing_held(self):
        tracker = InputStateTracker()
        tracker.update(_FakePyxel())

        self.assertFalse(tracker.btnp(UP_BUTTONS))

    def test_btnp_does_not_bleed_between_groups(self):
        tracker = InputStateTracker()
        tracker.update(_FakePyxel(held=[UP_BUTTONS[0]]))

        self.assertFalse(tracker.btnp(DOWN_BUTTONS))
        self.assertFalse(tracker.btnp(CONFIRM_BUTTONS))

    def test_btnp_only_on_first_frame_of_hold(self):
        tracker = InputStateTracker()
        fp = _FakePyxel(held=[UP_BUTTONS[0]])
        tracker.update(fp)
        self.assertTrue(tracker.btnp(UP_BUTTONS))

        tracker.update(fp)  # 同じ held 状態で再 update

        self.assertFalse(tracker.btnp(UP_BUTTONS))
        self.assertTrue(tracker.btn(UP_BUTTONS))


class TrackerBtnTest(unittest.TestCase):
    def test_btn_true_while_held(self):
        tracker = InputStateTracker()
        tracker.update(_FakePyxel(held=[CONFIRM_BUTTONS[0]]))

        self.assertTrue(tracker.btn(CONFIRM_BUTTONS))

    def test_btn_false_after_release(self):
        tracker = InputStateTracker()
        tracker.update(_FakePyxel(held=[CONFIRM_BUTTONS[0]]))
        tracker.update(_FakePyxel())

        self.assertFalse(tracker.btn(CONFIRM_BUTTONS))


class TrackerMultipleBindingsTest(unittest.TestCase):
    def test_second_binding_in_group_also_counts(self):
        tracker = InputStateTracker()
        tracker.update(_FakePyxel(held=[UP_BUTTONS[1]]))

        self.assertTrue(tracker.btnp(UP_BUTTONS))


if __name__ == "__main__":
    unittest.main()
