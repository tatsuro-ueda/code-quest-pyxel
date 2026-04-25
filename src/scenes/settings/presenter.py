from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.settings.model import SettingsModel
from src.scenes.settings.view_model import SettingsRow, SettingsViewModel


@dataclass
class SettingsPresenter:
    """settings シーンの ViewModel 組立て（M3-1 / M2-2）。"""

    model: SettingsModel

    def build_view_model(self, rows: list[tuple[str, str]], game: Any) -> SettingsViewModel:
        """rows（key, label のペア）を解釈して描画用の行データを組み立てる。"""
        cursor = self.model.cursor
        p = game.player_model
        view_rows: list[SettingsRow] = []
        for i, (key, label) in enumerate(rows):
            color = 10 if i == cursor else 6
            marker = ">" if i == cursor else " "
            if key == "back":
                value = ""
            elif key == "all_av":
                value = "ON" if (p.bgm_enabled and p.sfx_enabled and p.vfx_enabled) else "OFF"
            else:
                value = "ON" if getattr(p, key, True) else "OFF"
            text = f"{marker} {label}"
            if value:
                text = f"{text}: {value}"
            view_rows.append(SettingsRow(label=text, color=color))
        return SettingsViewModel(
            title=game.text_fmt.t("せってい", "SETTINGS"),
            footer=game.text_fmt.t("けっていで きりかえ", "Press confirm to toggle"),
            rows=view_rows,
        )
