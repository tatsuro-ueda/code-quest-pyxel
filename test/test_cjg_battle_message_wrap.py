"""CJG/battle: 長い結果メッセージは枠内で改行して描画する。"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.battle.view import BattleView
from src.scenes.battle.view_model import BattleViewModel


@dataclass
class _FakeTextWriter:
    drawn: list[tuple[int, int, str, int]] = field(default_factory=list)

    def text(self, x: int, y: int, s: str, col: int) -> None:
        self.drawn.append((x, y, s, col))

    def wrap_text(self, text: str, max_chars: int = 28) -> list[str]:
        if text == "ループゴーストをりかいした！なぜそうなるかわかった。けいけん":
            return ["ループゴーストをりかいした！", "なぜそうなるかわかった。けいけん"]
        return [text]


def _build_vm(main_text: str) -> BattleViewModel:
    return BattleViewModel(
        enemy_sprite_key="loop_ghost",
        enemy_name_text="ループゴースト",
        enemy_hp_label="HP 0/16",
        enemy_hp_ratio=0.0,
        player_status_line1="プログラマー  レベル4",
        player_status_line2="HP 88/90  MP 34/34",
        player_hp_ratio=1.0,
        player_hp_color=11,
        main_text=main_text,
        sub_panel=None,
        image_banks=None,
    )


class BattleMessageWrapTest(unittest.TestCase):
    def test_long_main_message_uses_multiple_lines(self) -> None:
        vm = _build_vm("ループゴーストをりかいした！なぜそうなるかわかった。けいけん")
        text_writer = _FakeTextWriter()

        with patch("src.scenes.battle.view.pyxel.rect"), patch(
            "src.scenes.battle.view.pyxel.rectb"
        ):
            BattleView._draw_main_message(vm, text_writer)

        self.assertEqual(
            text_writer.drawn,
            [
                (16, 154, "ループゴーストをりかいした！", 7),
                (16, 166, "なぜそうなるかわかった。けいけん", 7),
            ],
        )

    def test_short_main_message_keeps_single_line_position(self) -> None:
        vm = _build_vm("スライムをりかいした！")
        text_writer = _FakeTextWriter()

        with patch("src.scenes.battle.view.pyxel.rect"), patch(
            "src.scenes.battle.view.pyxel.rectb"
        ):
            BattleView._draw_main_message(vm, text_writer)

        self.assertEqual(
            text_writer.drawn,
            [(16, 154, "スライムをりかいした！", 7)],
        )


if __name__ == "__main__":
    unittest.main()
