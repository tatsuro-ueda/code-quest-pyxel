from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.menu.model import MenuModel
from src.scenes.menu.view_model import MenuRow, MenuSubPanel, MenuViewModel
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)


@dataclass
class MenuPresenter:
    """menu シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    model: MenuModel

    def labels(self, game: Any) -> list[str]:
        """メニュー表示ラベルの i18n 解決（has_jp_font に応じて切替）。"""
        if game.has_jp_font:
            return ["ステータス", "アイテム", "そうび", "せってい", "AIでしゅうせい", "とじる"]
        return ["STATUS", "ITEMS", "EQUIP", "SETTINGS", "AI HELP", "CLOSE"]

    def update(self, game: Any) -> None:
        """メニュー操作を処理する。sub-state に応じて分岐。"""
        import src.runtime.main_runtime as M
        menu_items = self.labels(game)
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
