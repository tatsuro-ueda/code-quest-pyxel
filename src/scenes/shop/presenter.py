from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.shop.model import ShopModel
from src.scenes.shop.view_model import ShopRow, ShopViewModel
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)


@dataclass
class ShopPresenter:
    """shop シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    model: ShopModel

    def update(self, game: Any) -> None:
        """ショップのカーソル操作と購入処理。"""
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
            self.try_purchase(game)

    def try_purchase(self, game: Any) -> None:
        """購入を試みる。所持／資金不足／購入成功の各分岐で message を更新。"""
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

    def build_view_model(self, game: Any) -> ShopViewModel:
        """Model + ゲームデータを解釈してショップ画面 VM を組み立てる。"""
        import src.runtime.main_runtime as M
        m = self.model
        if game.has_jp_font:
            title_map = {"weapons": "ぶきや", "armors": "ぼうぐや", "items": "どうぐや"}
            title = title_map.get(m.kind, "ショップ")
        else:
            title_map = {"weapons": "WEAPONS", "armors": "ARMOR", "items": "ITEMS"}
            title = title_map.get(m.kind, "SHOP")
        gold_label = f"G:{game.player_model.gold}"
        empty_message: str | None = None
        rows: list[ShopRow] = []
        if not m.inventory:
            empty_message = game.text_fmt.t("(ざいこなし)", "(no stock)")
        else:
            for i, idx in enumerate(m.inventory):
                owned = False
                if m.kind == "weapons":
                    e = M.WEAPONS[idx]
                    line = f"{game.text_fmt.name(e['name'])}  こうげき+{e['atk']}  {e['price']}G"
                    owned = game.player_model.weapon == idx
                elif m.kind == "armors":
                    e = M.ARMORS[idx]
                    line = f"{game.text_fmt.name(e['name'])}  ぼうぎょ+{e['def']}  {e['price']}G"
                    owned = game.player_model.armor == idx
                else:
                    e = M.ITEMS[idx]
                    line = f"{game.text_fmt.name(e['name'])}  {e['price']}G"
                if owned:
                    line = f"{line}  [もっています]"
                color = 10 if i == m.cursor else 7
                marker = ">" if i == m.cursor else " "
                rows.append(ShopRow(label=f"{marker} {line}", color=color))
        return ShopViewModel(
            title=title,
            gold_label=gold_label,
            rows=rows,
            empty_message=empty_message,
            message=m.message or None,
        )
