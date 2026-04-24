"""CJG/input_bindings: 各 BUTTONS 定数が非空で、複数バインドを持つ。

根拠:
- docs/product-requirements-platform.md（キーボード / ゲームパッド両対応）

UP/DOWN/LEFT/RIGHT/CONFIRM/CANCEL/TITLE_START は全て複数のキーにマップされる。
これが空だと入力が全く効かず、誤って 1 つだけにマップされるとゲームパッド非対応
になる。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services import input_bindings as IB


class ButtonBindingsNonEmptyTest(unittest.TestCase):
    _BUTTON_GROUPS = (
        "UP_BUTTONS", "DOWN_BUTTONS", "LEFT_BUTTONS", "RIGHT_BUTTONS",
        "CONFIRM_BUTTONS", "CANCEL_BUTTONS", "TITLE_START_BUTTONS",
    )

    def test_every_group_is_non_empty_tuple_or_list(self):
        for name in self._BUTTON_GROUPS:
            with self.subTest(group=name):
                self.assertTrue(hasattr(IB, name), f"{name} が存在しない")
                value = getattr(IB, name)
                self.assertTrue(hasattr(value, "__iter__"))
                self.assertGreater(len(list(value)), 0)

    def test_every_group_has_at_least_2_bindings(self):
        """キーボード + ゲームパッドの両方を想定しているため、2 つ以上のキーを持つ。"""
        for name in self._BUTTON_GROUPS:
            with self.subTest(group=name):
                value = getattr(IB, name)
                self.assertGreaterEqual(
                    len(list(value)),
                    2,
                    f"{name} は 2 つ以上のキーバインドを持つべき（キーボード + ゲームパッド想定）",
                )


class ButtonBindingsDoNotOverlapTest(unittest.TestCase):
    """方向ボタンと決定/キャンセルが同じキーを共有しないこと。"""

    def test_confirm_and_cancel_do_not_share(self):
        confirm_set = set(IB.CONFIRM_BUTTONS)
        cancel_set = set(IB.CANCEL_BUTTONS)

        self.assertEqual(
            confirm_set & cancel_set,
            set(),
            "CONFIRM と CANCEL が同じキーを共有している",
        )

    def test_directional_buttons_do_not_overlap(self):
        up = set(IB.UP_BUTTONS)
        down = set(IB.DOWN_BUTTONS)
        left = set(IB.LEFT_BUTTONS)
        right = set(IB.RIGHT_BUTTONS)

        for a, b in ((up, down), (left, right), (up, left), (up, right)):
            with self.subTest():
                self.assertEqual(a & b, set())


if __name__ == "__main__":
    unittest.main()
