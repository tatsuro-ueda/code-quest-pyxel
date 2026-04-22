from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TitleView:
    """タイトル画面の描画用ビューモデルを組み立てる。"""

    title: str = "Block Quest"

    def render(self, *, cursor: int, settings_open: bool) -> dict[str, object]:
        """現状のカーソルと設定状態から描画に必要な辞書を返す。"""
        return {
            "title": self.title,
            "cursor": cursor,
            "settings_open": settings_open,
        }
