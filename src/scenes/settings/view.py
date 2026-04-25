from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.settings.view_model import SettingsViewModel


@dataclass
class SettingsView:
    """settings シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self, vm: SettingsViewModel, text_writer: Any) -> None:
        """SettingsViewModel を画面に描く。"""
        pyxel.rect(28, 54, 200, 148, 1)
        pyxel.rectb(28, 54, 200, 148, 7)
        text_writer.text(92, 66, vm.title, 10)
        for i, row in enumerate(vm.rows):
            cy = 94 + i * 22
            text_writer.text(44, cy, row.label, row.color)
        text_writer.text(44, 176, vm.footer, 7)
