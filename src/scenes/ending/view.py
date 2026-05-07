from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.ending.view_model import EndingViewModel
from src.shared.services.audio_system import play_bgm_track


BGM_MUSIC_INDEX = 7
"""ending BGM が住む pyxres の musics スロット番号。"""


def play_bgm(game) -> None:
    """ending BGM を冪等に発火する。

    CJ44 確定版（追加整理）：冪等性は ``audio_system.play_bgm_track`` に集約。
    """
    play_bgm_track(BGM_MUSIC_INDEX)


@dataclass
class EndingView:
    """ending シーンの描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self, vm: EndingViewModel, text_writer: Any) -> None:
        """EndingViewModel を画面に描く。``text_writer`` は描画専用文字列出力。"""
        pyxel.cls(1)
        if vm.head_line is not None:
            text_writer.text(60, 60, vm.head_line, 10)
        for index, line in enumerate(vm.body_lines):
            text_writer.text(20, 90 + index * 15, line, 7)
        text_writer.text(40, 180, vm.prompt_text, 6)
        # 経過時間は frame_count から view 側で計算（presenter で pyxel 参照は M1-1 違反）
        elapsed_min = pyxel.frame_count // 30 // 60
        text_writer.text(30, 200, f"レベル{vm.level_value} Time:{elapsed_min}m", 6)
