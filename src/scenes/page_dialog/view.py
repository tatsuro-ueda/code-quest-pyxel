"""page_dialog scene の描画。

Problems:
    - 魔王戦前会話の full-screen 描画を explore 側へ直書きすると、Pyxel API
      が presenter / runtime へにじみ出る。
    - 短い overlay message と full-screen page dialog が同じ描画責務を持つと、
      子ども向けの読みやすい会話画面を独立に調整しにくい。

Solutions:
    - page_dialog の View は ViewModel と Pyxel API だけを扱い、会話文の
      折返しや prompt 判定は presenter 側で済ませる。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.page_dialog.view_model import PageDialogViewModel


@dataclass
class PageDialogView:
    """full-screen page dialog の描画担当。"""

    # === Public API ===

    def draw(self, vm: PageDialogViewModel, text_writer: Any) -> None:
        """PageDialogViewModel を画面へ描く。"""
        self._run_draw(vm, text_writer)

    # === Internal helpers (private) ===

    def _run_draw(self, vm: PageDialogViewModel, text_writer: Any) -> None:
        pyxel.cls(0)
        for i, line in enumerate(vm.page_lines):
            text_writer.text(16, vm.text_y + i * 14, line, vm.text_color)
        is_prompt_visible = (
            vm.prompt_xy is not None and pyxel.frame_count // 15 % 2
        )
        if is_prompt_visible:
            text_writer.text(vm.prompt_xy[0], vm.prompt_xy[1], "v", 7)
