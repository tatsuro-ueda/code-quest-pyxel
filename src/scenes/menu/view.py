"""menu scene の描画。

Problems:
    - 描画コードに状態判定が混ざると、見た目を変えるだけのつもりが
      Model 整合性まで考えることになる。
    - Pyxel API が Presenter / Model 側に染み出すとレイヤ境界が崩れ、
      テストでモックしづらくなる。

Solutions:
    - menu の View は ViewModel と Pyxel API だけを扱い、
      判断は Presenter 側に閉じ込める。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.menu.view_model import MenuViewModel


@dataclass
class MenuView:
    """menu シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    # === Public API ===

    def render(self) -> dict[str, object]:
        """描画情報の snapshot を返す（Phase 1 スケルトン互換）。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return {}

    def draw(self, vm: MenuViewModel, text_writer: Any) -> None:
        """MenuViewModel を画面に描く。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_draw(vm, text_writer)

    # === Internal helpers (private) ===

    def _run_draw(self, vm: MenuViewModel, text_writer: Any) -> None:
        # メインメニュー枠
        """_run_draw() の実装本体。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
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
            is_tall = sp.height == 120
            row_top = 108 if is_tall else 110
            row_step = 13 if is_tall else 20
            row_x = 50 if is_tall else 56
            for i, row in enumerate(sp.rows):
                cy = row_top + i * row_step
                text_writer.text(row_x, cy, row.text, row.color)
        if sp.info_message is not None:
            text_writer.text(50, 210, sp.info_message, 8)
