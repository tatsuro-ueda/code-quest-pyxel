from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.title.view_model import TitleViewModel
from src.shared.services.audio_system import play_bgm_track


BGM_MUSIC_INDEX = 0
"""title BGM が住む pyxres の musics スロット番号。"""

# title 画面では起動直後に channel gain も初期化する。pyxres には保存
# されないミキサー設定なので、view が 1 回だけ書き込む（旧 AudioManager
# の責務をここに降ろした）。
_INITIAL_GAIN_APPLIED = False


def _apply_initial_gain():
    global _INITIAL_GAIN_APPLIED
    if _INITIAL_GAIN_APPLIED:
        return
    pyxel.channels[0].gain = 0.30
    pyxel.channels[1].gain = 0.21
    pyxel.channels[2].gain = 0.15
    _INITIAL_GAIN_APPLIED = True


def play_bgm(game) -> None:
    """title BGM を冪等に発火する。シーン切替時のみ pyxel.playm を呼ぶ。

    CJ44 確定版（追加整理）：BGM の現在値は ``audio_system._current_bgm_track``
    に集約される。``game`` 引数は legacy 互換のため残す（test 互換）。
    """
    _apply_initial_gain()
    play_bgm_track(BGM_MUSIC_INDEX)


@dataclass
class TitleView:
    """タイトル画面の描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    title: str = "Block Quest"  # snapshot 用の互換属性

    def render(self, *, cursor: int) -> dict[str, object]:
        """単体テスト用の snapshot 辞書（Phase 1 互換）。"""
        return {
            "title": self.title,
            "cursor": cursor,
        }

    def draw(self, vm: TitleViewModel, text_writer: Any) -> None:
        """TitleViewModel を画面に描く。"""
        pyxel.cls(1)
        text_writer.text(70, 80, vm.title_text, 7)
        text_writer.text(50, 110, vm.subtitle_text, 10)
        for i, row in enumerate(vm.menu_rows):
            ly = 150 + i * 16
            text_writer.text(80, ly, row.label, row.color)
        if vm.no_save_message is not None:
            text_writer.text(40, 200, vm.no_save_message, 5)
