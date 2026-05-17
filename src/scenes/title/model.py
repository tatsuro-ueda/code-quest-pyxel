"""title scene の local state。

Problems:
    - シーンの局所状態を Game に直書きすると、画面追加で状態が
      散らばってどこを直すか分かりにくくなる。
    - state 値や cursor 位置を View / Presenter から直接書き換えると
      不正な遷移を作りやすい。

Solutions:
    - title シーンの局所状態を TitleModel に集約し、Presenter から
      渡された変更だけを受ける。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TitleModel:
    """タイトル画面の選択状態（カーソル位置）を保持する。

    2026-05-07 改訂（CJ44 確定版）：settings_open は撤去（設定画面ごと撤去）。
    """

    # === Public API ===

    cursor: int = 0
