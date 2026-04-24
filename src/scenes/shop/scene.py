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
        # 町情報は GameState.current_town から受け取る（framework-rule.md M4-3）。
        # shop は town の内部状態（town_model）を直接のぞき込まない。
        if game.current_town is None:
            # フォールバック: 町情報が未設定ならインデックス0の町扱い
            idx = 0
            game.last_town_pos = None
        else:
            idx = game.current_town.index
            game.last_town_pos = game.current_town.pos
        shop = M.SHOPS[idx]
        self.model.kind = kind
        self.model.inventory = list(shop[kind])
        self.model.cursor = 0
        self.model.message = ""
        game.state = "shop"

    def update(self) -> None:
        """ショップのカーソル操作と購入処理。"""
        game = self.game
        if game is None:
            return
        if not self.model.inventory:
            if game.input_state.btnp(CANCEL_BUTTONS) or game.input_state.btnp(CONFIRM_BUTTONS):
                game.sfx.play("cancel")
                game.state = "town_menu"
            return
        if game.input_state.btnp(UP_BUTTONS):
            self.model.cursor = (self.model.cursor - 1) % len(self.model.inventory)
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(DOWN_BUTTONS):
            self.model.cursor = (self.model.cursor + 1) % len(self.model.inventory)
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            game.state = "town_menu"
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
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
        pm = game.player_model
        if kind == "weapons" and pm.weapon == idx:
            self.model.message = "すでに もっています"
            return
        if kind == "armors" and pm.armor == idx:
            self.model.message = "すでに もっています"
            return
        if not pm.can_afford(price):
            self.model.message = "コインが たりません"
            return
        if kind == "weapons":
            pm.buy_weapon(idx, price)
            self.model.message = entry.get("buy_msg") or f"{entry['name']}を てにいれた！"
        elif kind == "armors":
            pm.buy_armor(idx, price)
            self.model.message = entry.get("buy_msg") or f"{entry['name']}を てにいれた！"
        else:
            pm.buy_item(idx, price)
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
        game.messages.text(160, 6, f"G:{game.player_model.gold}", 10)
        if not self.model.inventory:
            game.messages.text(8, 40, game.text_fmt.t("(ざいこなし)", "(no stock)"), 6)
            return
        for i, idx in enumerate(self.model.inventory):
            owned = False
            if self.model.kind == "weapons":
                e = M.WEAPONS[idx]
                line = f"{game.text_fmt.name(e['name'])}  こうげき+{e['atk']}  {e['price']}G"
                owned = game.player_model.weapon == idx
            elif self.model.kind == "armors":
                e = M.ARMORS[idx]
                line = f"{game.text_fmt.name(e['name'])}  ぼうぎょ+{e['def']}  {e['price']}G"
                owned = game.player_model.armor == idx
            else:
                e = M.ITEMS[idx]
                line = f"{game.text_fmt.name(e['name'])}  {e['price']}G"
            if owned:
                line = f"{line}  [もっています]"
            color = 10 if i == self.model.cursor else 7
            marker = ">" if i == self.model.cursor else " "
            game.messages.text(8, 30 + i * 14, f"{marker} {line}", color)
        if self.model.message:
            game.messages.text(8, 200, self.model.message, 11)
