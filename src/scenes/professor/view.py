from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel


@dataclass
class ProfessorView:
    """professor シーンの描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self) -> dict[str, object]:
        """描画情報の snapshot を返す（Phase 1 スケルトン互換）。"""
        return {}

    def draw_intro(self, model: Any, game: Any) -> None:
        """Professor intro 画面を描画する。"""
        m = model
        pyxel.cls(0)
        if m.intro_lines and m.intro_idx < len(m.intro_lines):
            for i, sub in enumerate(
                game.messages.current_page_lines(
                    m.intro_lines, m.intro_idx, max_chars=28, max_rows=6,
                )
            ):
                game.messages.text(16, 60 + i * 14, sub, 7)
            if not m.choice_active and (pyxel.frame_count // 15) % 2:
                game.messages.text(228, 200, "v", 7)
        if m.choice_active:
            labels = (
                ["うけいれる", "ことわる"]
                if game.has_jp_font
                else ["ACCEPT", "REFUSE"]
            )
            for i, label in enumerate(labels):
                color = 10 if i == m.choice_cursor else 7
                marker = ">" if i == m.choice_cursor else " "
                game.messages.text(96, 180 + i * 16, f"{marker} {label}", color)

    def draw_ending_main(self, model: Any, game: Any) -> None:
        """Professor ending main 画面を描画する。"""
        m = model
        pyxel.cls(0)
        if m.ending_lines and m.ending_idx < len(m.ending_lines):
            for i, sub in enumerate(
                game.messages.current_page_lines(
                    m.ending_lines, m.ending_idx, max_chars=28, max_rows=6,
                )
            ):
                game.messages.text(16, 80 + i * 14, sub, 10)
            if (pyxel.frame_count // 15) % 2:
                game.messages.text(228, 200, "v", 7)

    def draw_ending_accepted(self, model: Any, game: Any) -> None:
        """Professor 受諾エンド画面を描画する。"""
        m = model
        pyxel.cls(0)
        if m.ending_lines and m.ending_idx < len(m.ending_lines):
            for i, sub in enumerate(
                game.messages.current_page_lines(
                    m.ending_lines, m.ending_idx, max_chars=28, max_rows=6,
                )
            ):
                game.messages.text(16, 90 + i * 14, sub, 6)
            if (pyxel.frame_count // 15) % 2:
                game.messages.text(228, 210, "v", 7)
