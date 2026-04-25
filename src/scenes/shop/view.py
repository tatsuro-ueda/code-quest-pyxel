from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.shop.model import ShopModel


@dataclass
class ShopView:
    """shop シーンの描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self) -> dict[str, object]:
        """描画情報の snapshot を返す（Phase 1 スケルトン互換）。"""
        return {}

    def draw(self, model: ShopModel, game: Any) -> None:
        """ショップ画面を描画する。"""
        import src.runtime.main_runtime as M
        pyxel.cls(0)
        if game.has_jp_font:
            title_map = {"weapons": "ぶきや", "armors": "ぼうぐや", "items": "どうぐや"}
            title = title_map.get(model.kind, "ショップ")
        else:
            title_map = {"weapons": "WEAPONS", "armors": "ARMOR", "items": "ITEMS"}
            title = title_map.get(model.kind, "SHOP")
        game.messages.text(8, 6, title, 7)
        game.messages.text(160, 6, f"G:{game.player_model.gold}", 10)
        if not model.inventory:
            game.messages.text(8, 40, game.text_fmt.t("(ざいこなし)", "(no stock)"), 6)
            return
        for i, idx in enumerate(model.inventory):
            owned = False
            if model.kind == "weapons":
                e = M.WEAPONS[idx]
                line = f"{game.text_fmt.name(e['name'])}  こうげき+{e['atk']}  {e['price']}G"
                owned = game.player_model.weapon == idx
            elif model.kind == "armors":
                e = M.ARMORS[idx]
                line = f"{game.text_fmt.name(e['name'])}  ぼうぎょ+{e['def']}  {e['price']}G"
                owned = game.player_model.armor == idx
            else:
                e = M.ITEMS[idx]
                line = f"{game.text_fmt.name(e['name'])}  {e['price']}G"
            if owned:
                line = f"{line}  [もっています]"
            color = 10 if i == model.cursor else 7
            marker = ">" if i == model.cursor else " "
            game.messages.text(8, 30 + i * 14, f"{marker} {line}", color)
        if model.message:
            game.messages.text(8, 200, model.message, 11)
