"""title scene の描画。

Problems:
    - 描画コードに状態判定が混ざると、見た目を変えるだけのつもりが
      Model 整合性まで考えることになる。
    - Pyxel API が Presenter / Model 側に染み出すとレイヤ境界が崩れ、
      テストでモックしづらくなる。

Solutions:
    - title の View は ViewModel と Pyxel API だけを扱い、
      判断は Presenter 側に閉じ込める。
"""
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
_has_applied_initial_gain = False


def _apply_initial_gain():
    """pyxel チャンネル gain を 1 回だけ初期化する。

    Postconditions:
        - 初回呼び出しで pyxel.channels[0..2].gain を 0.30 / 0.21 / 0.15 にセット。
        - 2 回目以降の呼び出しは no-op。

    Policy:
        - pyxres には保存されないミキサー設定なので、view が起動時に書き込む。
    """
    global _has_applied_initial_gain
    if _has_applied_initial_gain:
        return
    pyxel.channels[0].gain = 0.30
    pyxel.channels[1].gain = 0.21
    pyxel.channels[2].gain = 0.15
    _has_applied_initial_gain = True


def play_bgm(game) -> None:
    """title BGM を冪等に発火する。シーン切替時のみ pyxel.playm を呼ぶ。

    CJ44 確定版（追加整理）：BGM の現在値は ``audio_system._current_bgm_track``
    に集約される。``game`` 引数は legacy 互換のため残す（test 互換）。

    Args:
        game: game の値。
    Postconditions:
        - 副作用とモデル更新は実装どおり。
    """
    _apply_initial_gain()
    play_bgm_track(BGM_MUSIC_INDEX)


@dataclass
class TitleView:
    """タイトル画面の描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    # === Public API ===

    title: str = "Block Quest"  # snapshot 用の互換属性

    def render(self, *, cursor: int) -> dict[str, object]:
        """単体テスト用の snapshot 辞書（Phase 1 互換）。

        Args:
            cursor: cursor の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return {
            "title": self.title,
            "cursor": cursor,
        }

    def draw(self, vm: TitleViewModel, text_writer: Any) -> None:
        """TitleViewModel を画面に描く。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_draw(vm, text_writer)

    # === Internal helpers (private) ===

    def _run_draw(self, vm: TitleViewModel, text_writer: Any) -> None:
        """_run_draw() の実装本体。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        pyxel.cls(1)
        text_writer.text(70, 80, vm.title_text, 7)
        text_writer.text(50, 110, vm.subtitle_text, 10)
        for i, row in enumerate(vm.menu_rows):
            ly = 150 + i * 16
            text_writer.text(80, ly, row.label, row.color)
        if vm.no_save_message is not None:
            text_writer.text(40, 200, vm.no_save_message, 5)
