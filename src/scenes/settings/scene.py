from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pyxel

from src.scenes.settings.model import SettingsModel
from src.scenes.settings.presenter import SettingsPresenter
from src.scenes.settings.view import SettingsView
from src.shared.services.input_bindings import (
    UP_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
)


@dataclass
class SettingsScene:
    """設定画面（P1-G8 で Game から 7 メソッドを取り込み）。"""

    name: str = "settings"
    model: SettingsModel = field(default_factory=SettingsModel)
    view: SettingsView = field(default_factory=SettingsView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = SettingsPresenter(self.model)

    def open(self, origin: str) -> None:
        """設定画面に入る。origin は 'menu' か 'title'。"""
        game = self.game
        self.model.origin = origin
        self.model.cursor = 0
        game.menu_scene.model.sub = None
        game.state = "settings"

    def _rows(self) -> list[tuple[str, str]]:
        game = self.game
        return [
            ("all_av", game.text_fmt.t("ぜんぶ", "ALL")),
            ("bgm_enabled", game.text_fmt.t("BGM", "BGM")),
            ("sfx_enabled", game.text_fmt.t("こうかおん", "SFX")),
            ("vfx_enabled", game.text_fmt.t("ひかり", "FLASH")),
            ("back", game.text_fmt.t("もどる", "BACK")),
        ]

    def _return_state(self) -> str:
        return "menu" if self.model.origin == "menu" else "title"

    def apply_av(self) -> None:
        """player の AV 設定を audio / sfx に反映する。"""
        game = self.game
        game.audio.set_enabled(game.player_model.bgm_enabled)
        game.sfx.set_enabled(game.player_model.sfx_enabled)

    def _toggle(self, key: str) -> None:
        game = self.game
        p = game.player_model
        if key == "all_av":
            next_value = not (p.bgm_enabled and p.sfx_enabled and p.vfx_enabled)
            p.bgm_enabled = next_value
            p.sfx_enabled = next_value
            p.vfx_enabled = next_value
            self.apply_av()
            return
        setattr(p, key, not getattr(p, key, True))
        self.apply_av()

    def update(self) -> None:
        """設定画面の入力処理。"""
        game = self.game
        if game is None:
            return
        rows = self._rows()
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
        if game.input_state.btnp(LEFT_BUTTONS) or game.input_state.btnp(RIGHT_BUTTONS) or game.input_state.btnp(CONFIRM_BUTTONS):
            key, _label = rows[self.model.cursor]
            if key == "back":
                game.state = self._return_state()
                return
            self._toggle(key)

    def draw(self) -> None:
        """設定画面を描画する。"""
        game = self.game
        if game is None:
            return
        pyxel.rect(28, 54, 200, 148, 1)
        pyxel.rectb(28, 54, 200, 148, 7)
        game.messages.text(92, 66, game.text_fmt.t("せってい", "SETTINGS"), 10)
        for i, (key, label) in enumerate(self._rows()):
            cy = 94 + i * 22
            col = 10 if i == self.model.cursor else 6
            marker = ">" if i == self.model.cursor else " "
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
