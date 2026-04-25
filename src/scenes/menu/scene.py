from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.menu.model import MenuModel
from src.scenes.menu.presenter import MenuPresenter
from src.scenes.menu.view import MenuView
from src.shared.services.input_bindings import (
    UP_BUTTONS,
    DOWN_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
)


@dataclass
class MenuScene:
    """menu シーン（P1-G7 で Game から 3 メソッドを取り込み）。"""

    name: str = "menu"
    model: MenuModel = field(default_factory=MenuModel)
    view: MenuView = field(default_factory=MenuView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = MenuPresenter(self.model)

    def _labels(self) -> list[str]:
        game = self.game
        if game.has_jp_font:
            return ["ステータス", "アイテム", "そうび", "せってい", "AIでしゅうせい", "とじる"]
        return ["STATUS", "ITEMS", "EQUIP", "SETTINGS", "AI HELP", "CLOSE"]

    def update(self) -> None:
        """メニュー操作を処理する。"""
        game = self.game
        if game is None:
            return
        import src.runtime.main_runtime as M
        menu_items = self._labels()
        m = self.model
        if m.sub is None:
            if game.input_state.btnp(UP_BUTTONS):
                m.cursor = (m.cursor - 1) % len(menu_items)
                game.sfx.play("cursor")
            if game.input_state.btnp(DOWN_BUTTONS):
                m.cursor = (m.cursor + 1) % len(menu_items)
                game.sfx.play("cursor")
            if game.input_state.btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                game.state = "map"
                return
            if game.input_state.btnp(CONFIRM_BUTTONS):
                game.sfx.play("select")
                if m.cursor == 0:
                    m.sub = "status"
                elif m.cursor == 1:
                    m.sub = "items"
                    m.item_cursor = 0
                elif m.cursor == 2:
                    m.sub = "equip"
                    m.item_cursor = 0
                elif m.cursor == 3:
                    game.settings_scene.open("menu")
                elif m.cursor == 4:
                    game.ai_help_scene.enter()
                elif m.cursor == 5:
                    game.state = "map"
        elif m.sub == "status":
            if game.input_state.btnp(CANCEL_BUTTONS) or game.input_state.btnp(CONFIRM_BUTTONS):
                game.sfx.play("cancel")
                m.sub = None
        elif m.sub == "items":
            items = game.player_model.items
            if game.input_state.btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                m.sub = None
                return
            if items:
                if game.input_state.btnp(UP_BUTTONS):
                    m.item_cursor = max(0, m.item_cursor - 1)
                    m.message = ""
                    game.sfx.play("cursor")
                if game.input_state.btnp(DOWN_BUTTONS):
                    m.item_cursor = min(len(items) - 1, m.item_cursor + 1)
                    m.message = ""
                    game.sfx.play("cursor")
                if game.input_state.btnp(CONFIRM_BUTTONS):
                    game.sfx.play("select")
                    item = items[m.item_cursor]
                    item_data = M.ITEMS[item.id]
                    from src.shared.services.item_use import use_item as _use_item_fn
                    msg = _use_item_fn(game, item_data)
                    if not msg:
                        m.message = "HPがまんたんで つかえない"
                    else:
                        m.message = ""
                        item.qty -= 1
                        if item.qty <= 0:
                            items.pop(m.item_cursor)
                            m.item_cursor = max(0, min(m.item_cursor, len(items) - 1))
        elif m.sub == "equip":
            if game.input_state.btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                m.sub = None
                return
            if game.input_state.btnp(UP_BUTTONS):
                m.item_cursor = (m.item_cursor - 1) % 2
                game.sfx.play("cursor")
            if game.input_state.btnp(DOWN_BUTTONS):
                m.item_cursor = (m.item_cursor + 1) % 2
                game.sfx.play("cursor")

    def draw(self) -> None:
        """メニュー画面を描画する。描画本体は View に委譲（M1-1 準拠）。"""
        game = self.game
        if game is None:
            return self.view.render()
        vm = self.presenter.build_view_model(self._labels(), game)
        self.view.draw(vm, game.messages)
