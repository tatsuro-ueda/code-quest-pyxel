from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.menu.model import MenuModel
from src.scenes.menu.view_model import MenuRow, MenuSubPanel, MenuViewModel


@dataclass
class MenuPresenter:
    """menu シーンの ViewModel 組立て（M3-1 / M2-2）。"""

    model: MenuModel

    def build_view_model(self, labels: list[str], game: Any) -> MenuViewModel:
        """labels（Scene が i18n 解決済み）と Model + PlayerModel を解釈して VM を組み立てる。"""
        import src.runtime.main_runtime as M
        m = self.model
        p = game.player_model

        main_rows: list[MenuRow] = []
        for i, label in enumerate(labels):
            highlighted = (i == m.cursor and m.sub is None)
            color = 10 if highlighted else 6
            marker = ">" if highlighted else " "
            main_rows.append(MenuRow(text=f"{marker} {label}", color=color))

        sub_panel: MenuSubPanel | None = None
        if m.sub == "status":
            stat_lines = [
                f"レベル {p.lv}  けいけん {p.exp}",
                f"HP {p.hp}/{p.max_hp}",
                f"MP {p.mp}/{p.max_mp}",
                f"こうげき {p.atk + M.WEAPONS[p.weapon]['atk']}  ぼうぎょ {p.defense + M.ARMORS[p.armor]['def']}",
                f"すばやさ {p.agi}",
                f"コイン {p.gold}",
            ]
            sub_panel = MenuSubPanel(
                height=120,
                rows=[MenuRow(text=line, color=7) for line in stat_lines],
            )
        elif m.sub == "items":
            items = p.items
            rows: list[MenuRow] = []
            empty_message: str | None = None
            if not items:
                empty_message = game.text_fmt.t("アイテムがない", "No items")
            else:
                for i, item in enumerate(items[:8]):
                    idata = M.ITEMS[item.id]
                    highlighted = (i == m.item_cursor)
                    color = 10 if highlighted else 6
                    marker = ">" if highlighted else " "
                    rows.append(MenuRow(
                        text=f"{marker} {game.text_fmt.name(idata['name'])} x{item.qty}",
                        color=color,
                    ))
            sub_panel = MenuSubPanel(
                height=120,
                rows=rows,
                empty_message=empty_message,
                info_message=m.message or None,
            )
        elif m.sub == "equip":
            wlbl = game.text_fmt.t("ぶき", "WPN")
            albl = game.text_fmt.t("ぼうぐ", "ARM")
            equip_lines = [
                f"{wlbl}: {game.text_fmt.name(M.WEAPONS[p.weapon]['name'])} (こうげき+{M.WEAPONS[p.weapon]['atk']})",
                f"{albl}: {game.text_fmt.name(M.ARMORS[p.armor]['name'])} (ぼうぎょ+{M.ARMORS[p.armor]['def']})",
            ]
            rows = []
            for i, label in enumerate(equip_lines):
                highlighted = (i == m.item_cursor)
                color = 10 if highlighted else 6
                marker = ">" if highlighted else " "
                rows.append(MenuRow(text=f"{marker} {label}", color=color))
            sub_panel = MenuSubPanel(height=80, rows=rows)

        return MenuViewModel(main_rows=main_rows, sub_panel=sub_panel)
