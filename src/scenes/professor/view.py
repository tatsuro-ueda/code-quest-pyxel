from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.professor.view_model import ProfessorViewModel


@dataclass
class ProfessorView:
    """professor シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self) -> dict[str, object]:
        """描画情報の snapshot を返す（Phase 1 スケルトン互換）。"""
        return {}

    def draw(self, vm: ProfessorViewModel, text_writer: Any) -> None:
        """ProfessorViewModel を画面に描く。3 phase 共通描画。"""
        pyxel.cls(0)
        for i, line in enumerate(vm.page_lines):
            text_writer.text(16, vm.text_y + i * 14, line, vm.text_color)
        if vm.prompt_xy is not None and (pyxel.frame_count // 15) % 2:
            text_writer.text(vm.prompt_xy[0], vm.prompt_xy[1], "v", 7)
        for i, choice in enumerate(vm.choices):
            text_writer.text(96, 180 + i * 16, choice.label, choice.color)
