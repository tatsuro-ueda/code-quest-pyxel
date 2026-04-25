from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.title.view_model import TitleViewModel


@dataclass
class TitleView:
    """タイトル画面の描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    title: str = "Block Quest"  # snapshot 用の互換属性

    def render(self, *, cursor: int, settings_open: bool) -> dict[str, object]:
        """単体テスト用の snapshot 辞書（Phase 1 互換）。"""
        return {
            "title": self.title,
            "cursor": cursor,
            "settings_open": settings_open,
        }

    def draw(self, vm: TitleViewModel, text_writer: Any) -> None:
        """TitleViewModel を画面に描く。"""
        pyxel.cls(1)
        text_writer.text(70, 80, vm.title_text, 7)
        text_writer.text(50, 110, vm.subtitle_text, 10)
        for i, row in enumerate(vm.menu_rows):
            ly = 150 + i * 16
            text_writer.text(80, ly, row.label, row.color)
        if vm.no_save_message is not None:
            text_writer.text(40, 200, vm.no_save_message, 5)
