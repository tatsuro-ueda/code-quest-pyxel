from __future__ import annotations

from typing import Any

import pyxel

from src.game_data import ITEMS, SPELL_BY_NAME


class BattleView:
    """バトル画面の描画担当（M1-1：Pyxel API は View のみ）。"""

    def render(self, *, phase: str) -> dict[str, str]:
        """現在のバトルフェーズを描画に必要な辞書として返す（snapshot 用）。"""
        return {"phase": phase}

    def draw(self, model: Any, game: Any) -> None:
        """バトル画面を描画する。"""
        m = model
        pyxel.cls(1)
        e = m.enemy
        if not e:
            return

        sprite_key = e.get("sprite", "slime")
        bp = game.image_banks.sprite_bank.get(sprite_key)
        if bp:
            sx, sy = bp
            for py in range(16):
                for px in range(16):
                    c = pyxel.images[1].pget(sx + px, sy + py)
                    if c != 0:
                        for dy in range(3):
                            for dx2 in range(3):
                                pyxel.pset(104 + px * 3 + dx2, 30 + py * 3 + dy, c)

        game.messages.text(80, 10, game.text_fmt.name(e["name"]), 7)
        bar_x = 80; bar_w = 96
        pyxel.rect(bar_x, 85, bar_w, 8, 0)
        hp_ratio = m.enemy_hp / max(1, e["hp"])
        pyxel.rect(bar_x, 85, int(bar_w * hp_ratio), 8, 8)
        game.messages.text(bar_x + 2, 86, f"HP {m.enemy_hp}/{e['hp']}", 7)

        p = game.player_model
        pyxel.rect(10, 100, 236, 40, 0)
        pyxel.rectb(10, 100, 236, 40, 7)
        game.messages.text(16, 104, f"{game.text_fmt.t('プログラマー', 'PROGRAMMER')}  レベル{p.lv}", 7)
        game.messages.text(16, 116, f"HP {p.hp}/{p.max_hp}  MP {p.mp}/{p.max_mp}", 7)
        pyxel.rect(170, 116, 60, 6, 0)
        hp_r = p.hp / max(1, p.max_hp)
        pyxel.rect(170, 116, int(60 * hp_r), 6, 11 if hp_r > 0.3 else 8)

        if m.text:
            pyxel.rect(10, 148, 236, 30, 0)
            pyxel.rectb(10, 148, 236, 30, 7)
            game.messages.text(16, 154, m.text, 7)

        if m.phase == "menu":
            menu_labels = (
                ["たたかう", "じゅもん", "アイテム", "にげる"]
                if game.has_jp_font
                else ["FIGHT", "SPELL", "ITEM", "RUN"]
            )
            pyxel.rect(10, 190, 236, 56, 0)
            pyxel.rectb(10, 190, 236, 56, 7)
            for i, label in enumerate(menu_labels):
                cx = 30 + (i % 2) * 110
                cy = 198 + (i // 2) * 18
                col = 10 if i == m.menu else 6
                game.messages.text(cx, cy, label, col)
                if i == m.menu:
                    game.messages.text(cx - 12, cy, ">", 10)

        elif m.phase == "spell_select":
            spells = game.player_model.spells
            pyxel.rect(10, 190, 236, 56, 0)
            pyxel.rectb(10, 190, 236, 56, 7)
            if not spells:
                game.messages.text(16, 200, game.text_fmt.t("じゅもんをおぼえていない", "No spells learned"), 6)
            else:
                for i, name in enumerate(spells[:4]):
                    spell = SPELL_BY_NAME.get(name)
                    if spell is None:
                        continue
                    cy = 196 + i * 12
                    col = 10 if i == m.spell_select else 6
                    game.messages.text(30, cy, f"{game.text_fmt.name(name)}  MP{spell['mp']}", col)
                    if i == m.spell_select:
                        game.messages.text(18, cy, ">", 10)

        elif m.phase == "item_select":
            items = game.player_model.items
            pyxel.rect(10, 190, 236, 56, 0)
            pyxel.rectb(10, 190, 236, 56, 7)
            if m.text:
                game.messages.text(16, 192, m.text, 8)
            if not items:
                game.messages.text(16, 200, game.text_fmt.t("アイテムがない", "No items"), 6)
            else:
                for i, item in enumerate(items[:4]):
                    idata = ITEMS[item.id]
                    cy = 196 + i * 12
                    col = 10 if i == m.item_select else 6
                    game.messages.text(30, cy, f"{game.text_fmt.name(idata['name'])} x{item.qty}", col)
                    if i == m.item_select:
                        game.messages.text(18, cy, ">", 10)

        game.vfx.draw_overlay()
