"""shop scene の描画。

Problems:
    - 描画コードに状態判定が混ざると、見た目を変えるだけのつもりが
      Model 整合性まで考えることになる。
    - Pyxel API が Presenter / Model 側に染み出すとレイヤ境界が崩れ、
      テストでモックしづらくなる。

Solutions:
    - shop の View は ViewModel と Pyxel API だけを扱い、
      判断は Presenter 側に閉じ込める。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.shop.view_model import ShopViewModel


@dataclass
class ShopView:
    """shop シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    # === Public API ===

    def render(self) -> dict[str, object]:
        """描画情報の snapshot を返す（Phase 1 スケルトン互換）。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return {}

    def draw(self, vm: ShopViewModel, text_writer: Any) -> None:
        """ShopViewModel を画面に描く。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_draw(vm, text_writer)

    # === Internal helpers (private) ===

    def _run_draw(self, vm: ShopViewModel, text_writer: Any) -> None:
        """_run_draw() の実装本体。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
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
