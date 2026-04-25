from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.shop.model import ShopModel
from src.scenes.shop.view_model import ShopRow, ShopViewModel


@dataclass
class ShopPresenter:
    """shop シーンの ViewModel 組立て（M3-1 / M2-2）。"""

    model: ShopModel

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
