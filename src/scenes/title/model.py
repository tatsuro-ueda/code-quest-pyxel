from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TitleModel:
    """タイトル画面の選択状態（カーソル位置）を保持する。

    2026-05-07 改訂（CJ44 確定版）：settings_open は撤去（設定画面ごと撤去）。
    """

    cursor: int = 0
