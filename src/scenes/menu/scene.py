from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pyxel

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
            if game._btnp(UP_BUTTONS):
                m.cursor = (m.cursor - 1) % len(menu_items)
                game.sfx.play("cursor")
            if game._btnp(DOWN_BUTTONS):
                m.cursor = (m.cursor + 1) % len(menu_items)
                game.sfx.play("cursor")
            if game._btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                game.state = "map"
                return
            if game._btnp(CONFIRM_BUTTONS):
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
                    game._open_settings("menu")
                elif m.cursor == 4:
                    game._enter_ai_help()
                elif m.cursor == 5:
                    game.state = "map"
        elif m.sub == "status":
            if game._btnp(CANCEL_BUTTONS) or game._btnp(CONFIRM_BUTTONS):
                game.sfx.play("cancel")
                m.sub = None
        elif m.sub == "items":
            items = game.player["items"]
            if game._btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                m.sub = None
                return
            if items:
                if game._btnp(UP_BUTTONS):
                    m.item_cursor = max(0, m.item_cursor - 1)
                    m.message = ""
                    game.sfx.play("cursor")
                if game._btnp(DOWN_BUTTONS):
                    m.item_cursor = min(len(items) - 1, m.item_cursor + 1)
                    m.message = ""
                    game.sfx.play("cursor")
                if game._btnp(CONFIRM_BUTTONS):
                    game.sfx.play("select")
                    item = items[m.item_cursor]
                    item_data = M.ITEMS[item["id"]]
                    msg = game._use_item(item_data)
                    if not msg:
                        m.message = "HPがまんたんで つかえない"
                    else:
                        m.message = ""
                        item["qty"] -= 1
                        if item["qty"] <= 0:
                            items.pop(m.item_cursor)
                            m.item_cursor = max(0, min(m.item_cursor, len(items) - 1))
        elif m.sub == "equip":
            if game._btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                m.sub = None
                return
            if game._btnp(UP_BUTTONS):
                m.item_cursor = (m.item_cursor - 1) % 2
                game.sfx.play("cursor")
            if game._btnp(DOWN_BUTTONS):
                m.item_cursor = (m.item_cursor + 1) % 2
                game.sfx.play("cursor")

    def draw(self) -> None:
        """メニュー画面を描画する。"""
        game = self.game
        if game is None:
            return self.view.render()
        import src.runtime.main_runtime as M
        pyxel.rect(20, 30, 216, 200, 1)
        pyxel.rectb(20, 30, 216, 200, 7)

        menu_labels = self._labels()
        m = self.model
        for i, label in enumerate(menu_labels):
            cy = 40 + i * 16
            col = 10 if i == m.cursor and m.sub is None else 6
            game.text(36, cy, label, col)
            if i == m.cursor and m.sub is None:
                game.text(26, cy, ">", 10)

        p = game.player
        if m.sub == "status":
            pyxel.rect(40, 100, 180, 120, 0)
            pyxel.rectb(40, 100, 180, 120, 7)
            lines = [
                f"レベル {p['lv']}  けいけん {p['exp']}",
                f"HP {p['hp']}/{p['max_hp']}",
                f"MP {p['mp']}/{p['max_mp']}",
                f"こうげき {p['atk']+M.WEAPONS[p['weapon']]['atk']}  ぼうぎょ {p['def']+M.ARMORS[p['armor']]['def']}",
                f"すばやさ {p['agi']}",
                f"コイン {p['gold']}",
            ]
            for i, line in enumerate(lines):
                game.text(50, 108 + i * 13, line, 7)
        elif m.sub == "items":
            pyxel.rect(40, 100, 180, 120, 0)
            pyxel.rectb(40, 100, 180, 120, 7)
            items = p["items"]
            if not items:
                game.text(50, 110, game._t("アイテムがない", "No items"), 6)
            else:
                for i, item in enumerate(items[:8]):
                    idata = M.ITEMS[item["id"]]
                    cy = 108 + i * 13
                    col = 10 if i == m.item_cursor else 6
                    game.text(56, cy, f"{game._name(idata['name'])} x{item['qty']}", col)
                    if i == m.item_cursor:
                        game.text(46, cy, ">", 10)
            if m.message:
                game.text(50, 210, m.message, 8)
        elif m.sub == "equip":
            pyxel.rect(40, 100, 180, 80, 0)
            pyxel.rectb(40, 100, 180, 80, 7)
            wlbl = game._t("ぶき", "WPN")
            albl = game._t("ぼうぐ", "ARM")
            labels = [
                f"{wlbl}: {game._name(M.WEAPONS[p['weapon']]['name'])} (こうげき+{M.WEAPONS[p['weapon']]['atk']})",
                f"{albl}: {game._name(M.ARMORS[p['armor']]['name'])} (ぼうぎょ+{M.ARMORS[p['armor']]['def']})",
            ]
            for i, label in enumerate(labels):
                cy = 110 + i * 20
                col = 10 if i == m.item_cursor else 6
                game.text(56, cy, label, col)
                if i == m.item_cursor:
                    game.text(46, cy, ">", 10)
