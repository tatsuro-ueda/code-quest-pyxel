from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel


@dataclass
class SettingsView:
    """settings シーンの描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self, *, rows: list[tuple[str, str]], cursor: int, game: Any) -> None:
        """設定画面のパネル枠と各行を描画する。"""
        pyxel.rect(28, 54, 200, 148, 1)
        pyxel.rectb(28, 54, 200, 148, 7)
        game.messages.text(92, 66, game.text_fmt.t("せってい", "SETTINGS"), 10)
        for i, (key, label) in enumerate(rows):
            cy = 94 + i * 22
            col = 10 if i == cursor else 6
            marker = ">" if i == cursor else " "
            if key == "back":
                value = ""
            elif key == "all_av":
                value = "ON" if (
                    game.player_model.bgm_enabled
                    and game.player_model.sfx_enabled
                    and game.player_model.vfx_enabled
                ) else "OFF"
            else:
                value = "ON" if getattr(game.player_model, key, True) else "OFF"
            row = f"{marker} {label}"
            if value:
                row = f"{row}: {value}"
            game.messages.text(44, cy, row, col)
        game.messages.text(44, 176, game.text_fmt.t("けっていで きりかえ", "Press confirm to toggle"), 7)
