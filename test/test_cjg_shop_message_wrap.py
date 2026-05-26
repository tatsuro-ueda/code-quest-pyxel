"""CJG/shop: 長い購入メッセージは下部枠で改行して描画する。"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.shop.view import ShopView
from src.scenes.shop.view_model import ShopViewModel


LONG_MESSAGE = (
    "コードエディタをてにいれた。"
    "いろがつく。インデントがそろう。それだけでうそみたいにうれしい。"
)


@dataclass
class _FakeTextWriter:
    drawn: list[tuple[int, int, str, int]] = field(default_factory=list)

    def text(self, x: int, y: int, s: str, col: int) -> None:
        self.drawn.append((x, y, s, col))

    def wrap_text(self, text: str, max_chars: int = 28) -> list[str]:
        if text == LONG_MESSAGE:
            return [
                "コードエディタをてにいれた。いろがつく。",
                "インデントがそろう。それだけでうそみたいにうれしい。",
            ]
        return [text]


def _build_vm(message: str) -> ShopViewModel:
    return ShopViewModel(
        title="ぶきや",
        gold_label="G:999",
        rows=[],
        empty_message=None,
        message=message,
    )


class ShopMessageWrapTest(unittest.TestCase):
    def test_long_message_uses_multiple_lines(self) -> None:
        vm = _build_vm(LONG_MESSAGE)
        text_writer = _FakeTextWriter()

        with patch("src.scenes.shop.view.pyxel.cls"):
            ShopView().draw(vm, text_writer)

        self.assertEqual(
            text_writer.drawn[-2:],
            [
                (8, 200, "コードエディタをてにいれた。いろがつく。", 11),
                (8, 212, "インデントがそろう。それだけでうそみたいにうれしい。", 11),
            ],
        )

    def test_short_message_keeps_single_line_position(self) -> None:
        vm = _build_vm("すでに もっています")
        text_writer = _FakeTextWriter()

        with patch("src.scenes.shop.view.pyxel.cls"):
            ShopView().draw(vm, text_writer)

        self.assertEqual(
            text_writer.drawn[-1:],
            [(8, 200, "すでに もっています", 11)],
        )


if __name__ == "__main__":
    unittest.main()
