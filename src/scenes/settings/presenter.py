from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.settings.model import SettingsModel
from src.scenes.settings.view_model import SettingsRow, SettingsViewModel
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    UP_BUTTONS,
)


@dataclass
class SettingsPresenter:
    """settings シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    model: SettingsModel

    def update(self, game: Any) -> None:
        """設定画面の入力を処理する。"""
        rows = self._rows(game)
        if game.input_state.btnp(UP_BUTTONS):
            self.model.cursor = (self.model.cursor - 1) % len(rows)
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(DOWN_BUTTONS):
            self.model.cursor = (self.model.cursor + 1) % len(rows)
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.state = self._return_state()
            return
        if (
            game.input_state.btnp(LEFT_BUTTONS)
            or game.input_state.btnp(RIGHT_BUTTONS)
            or game.input_state.btnp(CONFIRM_BUTTONS)
        ):
            key, _label = rows[self.model.cursor]
            if key == "back":
                game.state = self._return_state()
                return
            self._toggle(game, key)

    def apply_av(self, game: Any) -> None:
        """player の AV 設定を audio / sfx に反映する。"""
        game.audio.set_enabled(game.player_model.bgm_enabled)
        game.sfx.set_enabled(game.player_model.sfx_enabled)

    def _return_state(self) -> str:
        return "menu" if self.model.origin == "menu" else "title"

    def _toggle(self, game: Any, key: str) -> None:
        p = game.player_model
        if key == "all_av":
            next_value = not (p.bgm_enabled and p.sfx_enabled and p.vfx_enabled)
            p.bgm_enabled = next_value
            p.sfx_enabled = next_value
            p.vfx_enabled = next_value
        else:
            setattr(p, key, not getattr(p, key, True))
        self.apply_av(game)

    def _rows(self, game: Any) -> list[tuple[str, str]]:
        return [
            ("all_av", game.text_fmt.t("ぜんぶ", "ALL")),
            ("bgm_enabled", game.text_fmt.t("BGM", "BGM")),
            ("sfx_enabled", game.text_fmt.t("こうかおん", "SFX")),
            ("vfx_enabled", game.text_fmt.t("ひかり", "FLASH")),
            ("back", game.text_fmt.t("もどる", "BACK")),
        ]

    def build_view_model(self, game: Any) -> SettingsViewModel:
        """設定画面の VM を組み立てる（rows は内部で解決）。"""
        rows = self._rows(game)
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
