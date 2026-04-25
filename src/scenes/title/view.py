from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel


@dataclass
class TitleView:
    """タイトル画面の描画用ビューモデルを組み立てる。"""

    title: str = "Block Quest"

    def render(self, *, cursor: int, settings_open: bool) -> dict[str, object]:
        """現状のカーソルと設定状態から描画に必要な辞書を返す（snapshot 用）。"""
        return {
            "title": self.title,
            "cursor": cursor,
            "settings_open": settings_open,
        }

    def draw(self, *, model: Any, game: Any) -> None:
        """タイトル画面を Pyxel に描画する（M1-1：Pyxel API は View のみ）。"""
        pyxel.cls(1)
        game.messages.text(70, 80, "BLOCK QUEST", 7)
        game.messages.text(50, 110, game.text_fmt.t("- コードのぼうけん -", "- A Coding Quest -"), 10)
        labels = [
            game.text_fmt.t("はじめから", "NEW GAME"),
            game.text_fmt.t("つづきから", "CONTINUE"),
            game.text_fmt.t("せってい", "SETTINGS"),
        ]
        for i, label in enumerate(labels):
            ly = 150 + i * 16
            enabled = (i != 1) or game._has_save
            base_color = 7 if enabled else 5
            color = 10 if (i == model.cursor and enabled) else base_color
            marker = ">" if i == model.cursor else " "
            game.messages.text(80, ly, f"{marker} {label}", color)
        if model.cursor == 1 and not game._has_save:
            game.messages.text(
                40, 200, game.text_fmt.t("(まだなにもかきとめていない)", "(no save yet)"), 5
            )
