from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.game_data import ITEMS, SPELL_BY_NAME
from src.scenes.battle.model import BattleModel
from src.scenes.battle.view_model import (
    BattleRow,
    BattleSubPanel,
    BattleViewModel,
)


@dataclass
class BattlePresenter:
    """バトル画面のフェーズ遷移と ViewModel 組立て（M3-1 / M2-2）。"""

    model: BattleModel

    def change_phase(self, phase: str) -> None:
        """バトルの現在フェーズを指定値に差し替える。"""
        self.model.phase = phase

    def build_view_model(self, game: Any) -> BattleViewModel:
        """Model + GameState を解釈して battle VM を組み立てる。"""
        m = self.model
        e = m.enemy
        if not e:
            # enemy なし時は描画を実質スキップする最小 VM
            return BattleViewModel(
                enemy_sprite_key=None,
                enemy_name_text="",
                enemy_hp_label="",
                enemy_hp_ratio=0.0,
                player_status_line1="",
                player_status_line2="",
                player_hp_ratio=0.0,
                player_hp_color=11,
                main_text=None,
                sub_panel=None,
                image_banks=game.image_banks,
            )

        p = game.player_model
        hp_r = p.hp / max(1, p.max_hp)
        return BattleViewModel(
            enemy_sprite_key=e.get("sprite", "slime"),
            enemy_name_text=game.text_fmt.name(e["name"]),
            enemy_hp_label=f"HP {m.enemy_hp}/{e['hp']}",
            enemy_hp_ratio=m.enemy_hp / max(1, e["hp"]),
            player_status_line1=f"{game.text_fmt.t('プログラマー', 'PROGRAMMER')}  レベル{p.lv}",
            player_status_line2=f"HP {p.hp}/{p.max_hp}  MP {p.mp}/{p.max_mp}",
            player_hp_ratio=hp_r,
            player_hp_color=11 if hp_r > 0.3 else 8,
            main_text=m.text or None,
            sub_panel=self._build_sub_panel(game),
            image_banks=game.image_banks,
        )

    def _build_sub_panel(self, game: Any) -> BattleSubPanel | None:
        """phase に応じた sub_panel を組み立てる。"""
        m = self.model
        if m.phase == "menu":
            labels = (
                ["たたかう", "じゅもん", "アイテム", "にげる"]
                if game.has_jp_font
                else ["FIGHT", "SPELL", "ITEM", "RUN"]
            )
            rows: list[BattleRow] = []
            for i, label in enumerate(labels):
                color = 10 if i == m.menu else 6
                # menu はマーカーが行頭ではなく座標で別描画。VM では純粋にラベル + color
                rows.append(BattleRow(text=label, color=color))
            return BattleSubPanel(is_grid=True, rows=rows)
        if m.phase == "spell_select":
            spells = game.player_model.spells
            if not spells:
                return BattleSubPanel(
                    is_grid=False,
                    empty_message=game.text_fmt.t("じゅもんをおぼえていない", "No spells learned"),
                )
            rows = []
            for i, name in enumerate(spells[:4]):
                spell = SPELL_BY_NAME.get(name)
                if spell is None:
                    continue
                color = 10 if i == m.spell_select else 6
                marker = ">" if i == m.spell_select else " "
                rows.append(BattleRow(
                    text=f"{marker} {game.text_fmt.name(name)}  MP{spell['mp']}",
                    color=color,
                ))
            return BattleSubPanel(is_grid=False, rows=rows)
        if m.phase == "item_select":
            items = game.player_model.items
            info = m.text or None
            if not items:
                return BattleSubPanel(
                    is_grid=False,
                    empty_message=game.text_fmt.t("アイテムがない", "No items"),
                    info_message=info,
                )
            rows = []
            for i, item in enumerate(items[:4]):
                idata = ITEMS[item.id]
                color = 10 if i == m.item_select else 6
                marker = ">" if i == m.item_select else " "
                rows.append(BattleRow(
                    text=f"{marker} {game.text_fmt.name(idata['name'])} x{item.qty}",
                    color=color,
                ))
            return BattleSubPanel(is_grid=False, rows=rows, info_message=info)
        return None
