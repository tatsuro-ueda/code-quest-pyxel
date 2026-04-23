from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pyxel

from src.scenes.shop.model import ShopModel
from src.scenes.shop.presenter import ShopPresenter
from src.scenes.shop.view import ShopView
from src.shared.services.input_bindings import (
    UP_BUTTONS,
    DOWN_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
)


@dataclass
class ShopScene:
    """shop シーン（P1-G5 で Game から 4 メソッドを取り込み）。"""

    name: str = "shop"
    model: ShopModel = field(default_factory=ShopModel)
    view: ShopView = field(default_factory=ShopView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = ShopPresenter(self.model)

    def enter(self, kind: str) -> None:
        """ショップ画面に遷移する。kind は 'weapons' / 'armors' / 'items'。"""
        game = self.game
        import src.runtime.main_runtime as M
        idx = game._current_town_index()
        shop = M.SHOPS[idx]
        self.model.kind = kind
        self.model.inventory = list(shop[kind])
        self.model.cursor = 0
        self.model.message = ""
        game.last_town_pos = game.town_menu_pos
        game.state = "shop"

    def update(self) -> None:
        """ショップのカーソル操作と購入処理。"""
        game = self.game
        if game is None:
            return
        if not self.model.inventory:
            if game._btnp(CANCEL_BUTTONS) or game._btnp(CONFIRM_BUTTONS):
                game.sfx.play("cancel")
                game.state = "town_menu"
            return
        if game._btnp(UP_BUTTONS):
            self.model.cursor = (self.model.cursor - 1) % len(self.model.inventory)
            game.sfx.play("cursor")
            return
        if game._btnp(DOWN_BUTTONS):
            self.model.cursor = (self.model.cursor + 1) % len(self.model.inventory)
            game.sfx.play("cursor")
            return
        if game._btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            game.state = "town_menu"
            return
        if game._btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            self._try_purchase()

    def _try_purchase(self) -> None:
        game = self.game
        import src.runtime.main_runtime as M
        idx = self.model.inventory[self.model.cursor]
        kind = self.model.kind
        if kind == "weapons":
            entry = M.WEAPONS[idx]
        elif kind == "armors":
            entry = M.ARMORS[idx]
        else:
            entry = M.ITEMS[idx]
        price = entry.get("price", 0)
        if kind == "weapons" and game.player["weapon"] == idx:
            self.model.message = "すでに もっています"
            return
        if kind == "armors" and game.player["armor"] == idx:
            self.model.message = "すでに もっています"
            return
        if game.player["gold"] < price:
            self.model.message = "コインが たりません"
            return
        game.player["gold"] -= price
        if kind == "weapons":
            game.player["weapon"] = idx
            self.model.message = entry.get("buy_msg") or f"{entry['name']}を てにいれた！"
        elif kind == "armors":
            game.player["armor"] = idx
            self.model.message = entry.get("buy_msg") or f"{entry['name']}を てにいれた！"
        else:
            for inv in game.player["items"]:
                if inv["id"] == idx:
                    inv["qty"] += 1
                    break
            else:
                game.player["items"].append({"id": idx, "qty": 1})
            self.model.message = f"{entry['name']}を てにいれた！"

    def draw(self) -> None:
        """ショップ画面を描画する。"""
        game = self.game
        if game is None:
            return self.view.render()
        import src.runtime.main_runtime as M
        pyxel.cls(0)
        if game.has_jp_font:
            title_map = {"weapons": "ぶきや", "armors": "ぼうぐや", "items": "どうぐや"}
            title = title_map.get(self.model.kind, "ショップ")
        else:
            title_map = {"weapons": "WEAPONS", "armors": "ARMOR", "items": "ITEMS"}
            title = title_map.get(self.model.kind, "SHOP")
        game.messages.text(8, 6, title, 7)
        game.messages.text(160, 6, f"G:{game.player['gold']}", 10)
        if not self.model.inventory:
            game.messages.text(8, 40, game._t("(ざいこなし)", "(no stock)"), 6)
            return
        for i, idx in enumerate(self.model.inventory):
            owned = False
            if self.model.kind == "weapons":
                e = M.WEAPONS[idx]
                line = f"{game._name(e['name'])}  こうげき+{e['atk']}  {e['price']}G"
                owned = game.player["weapon"] == idx
            elif self.model.kind == "armors":
                e = M.ARMORS[idx]
                line = f"{game._name(e['name'])}  ぼうぎょ+{e['def']}  {e['price']}G"
                owned = game.player["armor"] == idx
            else:
                e = M.ITEMS[idx]
                line = f"{game._name(e['name'])}  {e['price']}G"
            if owned:
                line = f"{line}  [もっています]"
            color = 10 if i == self.model.cursor else 7
            marker = ">" if i == self.model.cursor else " "
            game.messages.text(8, 30 + i * 14, f"{marker} {line}", color)
        if self.model.message:
            game.messages.text(8, 200, self.model.message, 11)
