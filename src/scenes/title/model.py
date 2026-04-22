from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TitleModel:
    """タイトル画面の選択状態（カーソル位置・設定モーダル開閉）を保持する。"""

    cursor: int = 0
    settings_open: bool = False
