from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.splash.view_model import SplashViewModel


@dataclass
class SplashView:
    """splash シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self, vm: SplashViewModel, text_writer: Any) -> None:
        """SplashViewModel を画面に描く。``text_writer`` は描画専用の文字列出力（例：``game.messages``）。"""
        pyxel.cls(0)
        for i in range(8):
            x = 16 + i * 28
            pyxel.rect(x, 100, 12, 12, vm.block_color)
        text_writer.text(80, 80, "BLOCK QUEST", vm.title_color)
        if vm.subtitle_text is not None:
            text_writer.text(50, 130, vm.subtitle_text, 10)
        if vm.presenter_text is not None:
            text_writer.text(70, 160, vm.presenter_text, 6)
        if vm.prompt_eligible and (pyxel.frame_count // 8) % 2 == 1:
            text_writer.text(60, 220, "PRESS ANY KEY", 7)
