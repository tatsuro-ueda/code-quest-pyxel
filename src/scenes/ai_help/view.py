from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.ai_help.view_model import AiHelpViewModel


@dataclass
class AiHelpView:
    """ai_help シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self, vm: AiHelpViewModel, text_writer: Any) -> None:
        """AiHelpViewModel を画面に描く。"""
        x, y, w, h = 12, 36, 232, 196
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        text_writer.text(x + 8, y + 8, vm.title, 10)
        for i, line in enumerate(vm.body_lines):
            text_writer.text(x + 8, y + 24 + i * 9, line, 7)
