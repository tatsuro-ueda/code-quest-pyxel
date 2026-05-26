"""CJG/battle: player status box の HP バーは数値行と重ならない。"""

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


def _build_vm() -> BattleViewModel:
    return BattleViewModel(
        enemy_sprite_key="loop_ghost",
        enemy_name_text="ループゴースト",
        enemy_hp_label="HP 0/16",
        enemy_hp_ratio=0.0,
        player_status_line1="プログラマー  レベル6",
        player_status_line2="HP 112/120  MP 46/48",
        player_hp_ratio=0.5,
        player_hp_color=11,
        main_text=None,
        sub_panel=None,
        image_banks=None,
    )


class BattlePlayerStatusBarLayoutTest(unittest.TestCase):
    def test_player_status_text_keeps_existing_positions(self) -> None:
        vm = _build_vm()
        text_writer = _FakeTextWriter()

        with patch("src.scenes.battle.view.pyxel.rect"), patch(
            "src.scenes.battle.view.pyxel.rectb"
        ):
            BattleView._draw_player_status(vm, text_writer)

        self.assertEqual(
            text_writer.drawn,
            [
                (16, 104, "プログラマー  レベル6", 7),
                (16, 116, "HP 112/120  MP 46/48", 7),
            ],
        )

    def test_player_hp_bar_moves_below_status_line2(self) -> None:
        vm = _build_vm()
        text_writer = _FakeTextWriter()

        with patch("src.scenes.battle.view.pyxel.rect") as rect_mock, patch(
            "src.scenes.battle.view.pyxel.rectb"
        ):
            BattleView._draw_player_status(vm, text_writer)

        self.assertEqual(
            rect_mock.call_args_list[1:],
            [
                ((170, 128, 60, 6, 0),),
                ((170, 128, 30, 6, 11),),
            ],
        )


if __name__ == "__main__":
    unittest.main()
