from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.menu.view_model import MenuViewModel


@dataclass
class MenuView:
    """menu シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self) -> dict[str, object]:
        """描画情報の snapshot を返す（Phase 1 スケルトン互換）。"""
        return {}

    def draw(self, vm: MenuViewModel, text_writer: Any) -> None:
        """MenuViewModel を画面に描く。"""
        # メインメニュー枠
        pyxel.rect(20, 30, 216, 200, 1)
        pyxel.rectb(20, 30, 216, 200, 7)
        for i, row in enumerate(vm.main_rows):
            cy = 40 + i * 16
            text_writer.text(36, cy, row.text, row.color)

        # サブパネル
        sp = vm.sub_panel
        if sp is None:
            return
        pyxel.rect(40, 100, 180, sp.height, 0)
        pyxel.rectb(40, 100, 180, sp.height, 7)
        if sp.empty_message is not None:
            text_writer.text(50, 110, sp.empty_message, 6)
        else:
            for i, row in enumerate(sp.rows):
                cy = (108 if sp.height == 120 else 110) + i * (13 if sp.height == 120 else 20)
                text_writer.text(50 if sp.height == 120 else 56, cy, row.text, row.color)
        if sp.info_message is not None:
            text_writer.text(50, 210, sp.info_message, 8)
