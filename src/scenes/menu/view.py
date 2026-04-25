from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel


@dataclass
class MenuView:
    """menu シーンの描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self) -> dict[str, object]:
        """描画情報の snapshot を返す（Phase 1 スケルトン互換）。"""
        return {}

    def draw(self, *, labels: list[str], model: Any, game: Any) -> None:
        """メニュー画面とサブパネルを描画する。"""
        import src.runtime.main_runtime as M
        pyxel.rect(20, 30, 216, 200, 1)
        pyxel.rectb(20, 30, 216, 200, 7)

        m = model
        for i, label in enumerate(labels):
            cy = 40 + i * 16
            col = 10 if i == m.cursor and m.sub is None else 6
            game.messages.text(36, cy, label, col)
            if i == m.cursor and m.sub is None:
                game.messages.text(26, cy, ">", 10)

        p = game.player_model
        if m.sub == "status":
            pyxel.rect(40, 100, 180, 120, 0)
            pyxel.rectb(40, 100, 180, 120, 7)
            lines = [
                f"レベル {p.lv}  けいけん {p.exp}",
                f"HP {p.hp}/{p.max_hp}",
                f"MP {p.mp}/{p.max_mp}",
                f"こうげき {p.atk+M.WEAPONS[p.weapon]['atk']}  ぼうぎょ {p.defense+M.ARMORS[p.armor]['def']}",
                f"すばやさ {p.agi}",
                f"コイン {p.gold}",
            ]
            for i, line in enumerate(lines):
                game.messages.text(50, 108 + i * 13, line, 7)
        elif m.sub == "items":
            pyxel.rect(40, 100, 180, 120, 0)
            pyxel.rectb(40, 100, 180, 120, 7)
            items = p.items
            if not items:
                game.messages.text(50, 110, game.text_fmt.t("アイテムがない", "No items"), 6)
            else:
                for i, item in enumerate(items[:8]):
                    idata = M.ITEMS[item.id]
                    cy = 108 + i * 13
                    col = 10 if i == m.item_cursor else 6
                    game.messages.text(56, cy, f"{game.text_fmt.name(idata['name'])} x{item.qty}", col)
                    if i == m.item_cursor:
                        game.messages.text(46, cy, ">", 10)
            if m.message:
                game.messages.text(50, 210, m.message, 8)
        elif m.sub == "equip":
            pyxel.rect(40, 100, 180, 80, 0)
            pyxel.rectb(40, 100, 180, 80, 7)
            wlbl = game.text_fmt.t("ぶき", "WPN")
            albl = game.text_fmt.t("ぼうぐ", "ARM")
            equip_labels = [
                f"{wlbl}: {game.text_fmt.name(M.WEAPONS[p.weapon]['name'])} (こうげき+{M.WEAPONS[p.weapon]['atk']})",
                f"{albl}: {game.text_fmt.name(M.ARMORS[p.armor]['name'])} (ぼうぎょ+{M.ARMORS[p.armor]['def']})",
            ]
            for i, label in enumerate(equip_labels):
                cy = 110 + i * 20
                col = 10 if i == m.item_cursor else 6
                game.messages.text(56, cy, label, col)
                if i == m.item_cursor:
                    game.messages.text(46, cy, ">", 10)
