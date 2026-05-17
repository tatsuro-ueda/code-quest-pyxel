"""ai_help scene の描画。

Problems:
    - 描画コードに状態判定が混ざると、見た目を変えるだけのつもりが
      Model 整合性まで考えることになる。
    - Pyxel API が Presenter / Model 側に染み出すとレイヤ境界が崩れ、
      テストでモックしづらくなる。

Solutions:
    - ai_help の View は ViewModel と Pyxel API だけを扱い、
      判断は Presenter 側に閉じ込める。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.ai_help.view_model import AiHelpViewModel


@dataclass
class AiHelpView:
    """ai_help シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    # === Public API ===

    def render(self, vm: AiHelpViewModel, text_writer: Any) -> None:
        """AiHelpViewModel を画面に描く。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        x, y, w, h = 12, 36, 232, 196
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        text_writer.text(x + 8, y + 8, vm.title, 10)
        for i, line in enumerate(vm.body_lines):
            text_writer.text(x + 8, y + 24 + i * 9, line, 7)
