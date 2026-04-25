from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.shop.view_model import ShopViewModel


@dataclass
class ShopView:
    """shop シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self) -> dict[str, object]:
        """描画情報の snapshot を返す（Phase 1 スケルトン互換）。"""
        return {}

    def draw(self, vm: ShopViewModel, text_writer: Any) -> None:
        """ShopViewModel を画面に描く。"""
        pyxel.cls(0)
        text_writer.text(8, 6, vm.title, 7)
        text_writer.text(160, 6, vm.gold_label, 10)
        if vm.empty_message is not None:
            text_writer.text(8, 40, vm.empty_message, 6)
            return
        for i, row in enumerate(vm.rows):
            text_writer.text(8, 30 + i * 14, row.label, row.color)
        if vm.message is not None:
            text_writer.text(8, 200, vm.message, 11)
