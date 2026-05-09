from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from src.game_data import ITEMS, SPELL_BY_NAME
from src.scenes.battle.model import BattleModel
from src.scenes.battle.view_model import (
    BattleRow,
    BattleSubPanel,
    BattleViewModel,
)
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)


def _item_use_message(game: Any, item_data: dict, result: str) -> str:
    if result == "heal":
        return game.messages.dialog_text(
            "battle.normal.item.heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if result == "mp_heal":
        return game.messages.dialog_text(
            "battle.normal.item.mp_heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if result == "cure_poison_ok":
        return f'{item_data["name"]}を使った。バグ汚染が消えた！'
    if result == "cure_poison_none":
        return f'{item_data["name"]}を使った。だが今は必要なかった。'
    return ""


@dataclass
class BattlePresenter:
    """バトル画面の入力解釈・フェーズ遷移・ViewModel 組立て（M3-1 / M2-2）。

    戦闘ルール本体（do_player_attack / do_enemy_attack / victory / defeat /
    apply_spell_effect 等）は引き続き Scene 側にあるため、phase 遷移の指揮で
    ``scene`` を呼び戻す（Phase 1 transitional pattern；将来 Model 側に
    移管する案件は判断待ち）。
    """

    model: BattleModel

    def change_phase(self, phase: str) -> None:
        """バトルの現在フェーズを指定値に差し替える。"""
        self.model.phase = phase

    def update(self, game: Any, scene: Any) -> None:
        """バトルフェーズに応じて入力処理と状態遷移を行う。

        ``scene`` はルール本体を持つ BattleScene。do_player_attack /
        do_enemy_attack / victory / defeat / apply_spell_effect /
        on_noise_guardian_defeated を呼び戻すために必要。
        """
        import src.runtime.main_runtime as M
        m = self.model
        if game.vfx.timer > 0:
            game.vfx.timer -= 1
        if m.phase == "menu":
            if game.input_state.btnp(UP_BUTTONS):
                m.menu = (m.menu - 1) % 4
                game.sfx.play("cursor")
            if game.input_state.btnp(DOWN_BUTTONS):
                m.menu = (m.menu + 1) % 4
                game.sfx.play("cursor")
            if game.input_state.btnp(CONFIRM_BUTTONS):
                game.sfx.play("select")
                if m.menu == 0:  # Attack
                    scene.do_player_attack()
                elif m.menu == 1:  # じゅもん
                    if game.player_model.spells:
                        m.phase = "spell_select"
                        m.spell_select = 0
                    else:
                        m.text = "まだ じゅもんを おぼえていない"
                elif m.menu == 2:  # Item
                    m.phase = "item_select"
                    m.item_select = 0
                elif m.menu == 3:  # Run
                    if not m.is_glitch_lord and random.random() < 0.5:
                        m.text = game.messages.dialog_text("battle.normal.run.success")
                        m.phase = "result"
                        m.text_timer = 60
                    else:
                        scene_name = (
                            "boss.glitch.run.fail"
                            if m.is_glitch_lord
                            else "battle.normal.run.fail"
                        )
                        m.text = game.messages.dialog_text(scene_name)
                        m.phase = "player_attack"
                        m.text_timer = 30

        elif m.phase == "spell_select":
            spells = game.player_model.spells
            if not spells:
                m.phase = "menu"
                return
            if game.input_state.btnp(UP_BUTTONS):
                m.spell_select = max(0, m.spell_select - 1)
                game.sfx.play("cursor")
            if game.input_state.btnp(DOWN_BUTTONS):
                m.spell_select = min(len(spells) - 1, m.spell_select + 1)
                game.sfx.play("cursor")
            if game.input_state.btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                m.phase = "menu"
            if game.input_state.btnp(CONFIRM_BUTTONS):
                game.sfx.play("select")
                spell_name = spells[m.spell_select]
                spell = SPELL_BY_NAME.get(spell_name)
                if spell is None:
                    m.phase = "menu"
                    return
                if game.player_model.mp < spell["mp"]:
                    m.text = "MPが たりない！"
                    return
                game.player_model.mp -= spell["mp"]
                game.sfx.play("magic")
                game.vfx.start("flash_white")
                m.text = scene.apply_spell_effect(spell)
                m.phase = "player_attack"
                m.text_timer = 30

        elif m.phase == "item_select":
            items = game.player_model.items
            if not items:
                m.phase = "menu"
                return
            if game.input_state.btnp(UP_BUTTONS):
                m.item_select = max(0, m.item_select - 1)
                game.sfx.play("cursor")
            if game.input_state.btnp(DOWN_BUTTONS):
                m.item_select = min(len(items) - 1, m.item_select + 1)
                game.sfx.play("cursor")
            if game.input_state.btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                m.phase = "menu"
            if game.input_state.btnp(CONFIRM_BUTTONS):
                game.sfx.play("select")
                item = items[m.item_select]
                item_data = ITEMS[item.id]
                if item_data["type"] == "warp":
                    m.text = "せんとうちゅうはつかえない…"
                    m.phase = "enemy_attack"
                    m.text_timer = 30
                else:
                    result = game.player_model.use_item(item_data)
                    if not result:
                        m.text = "HPがまんたんで つかえない"
                        m.text_timer = 30
                    else:
                        if result in {"heal", "mp_heal"}:
                            game.sfx.play("heal")
                        elif result == "cure_poison_ok":
                            game.sfx.play("cure")
                        m.text = _item_use_message(game, item_data, result)
                        item.qty -= 1
                        if item.qty <= 0:
                            items.pop(m.item_select)
                        m.phase = "enemy_attack"
                        m.text_timer = 30

        elif m.phase == "player_attack":
            if game.input_state.btn(CONFIRM_BUTTONS) and m.text_timer > 12:
                m.text_timer = 12
            m.text_timer -= 1
            if m.text_timer <= 0:
                if m.enemy_hp <= 0:
                    scene.victory()
                else:
                    scene.do_enemy_attack()

        elif m.phase == "enemy_attack":
            if game.input_state.btn(CONFIRM_BUTTONS) and m.text_timer > 12:
                m.text_timer = 12
            m.text_timer -= 1
            if m.text_timer <= 0:
                if game.player_model.hp <= 0:
                    scene.defeat()
                else:
                    m.phase = "menu"

        elif m.phase == "result":
            if game.input_state.btn(CONFIRM_BUTTONS) and m.text_timer > 12:
                m.text_timer = 12
            m.text_timer -= 1
            if m.text_timer <= 0:
                if game.input_state.btn(CONFIRM_BUTTONS) or game.input_state.btnp(CONFIRM_BUTTONS) or m.text_timer < -30:
                    if game.player_model.hp <= 0:
                        game.player_model.gold = game.player_model.gold // 2
                        game.player_model.hp = game.player_model.max_hp
                        game.player_model.x, game.player_model.y = M.CASTLE_POS
                        game.player_model.in_dungeon = False
                        game.state = "map"
                    elif m.is_professor and m.enemy_hp <= 0:
                        game.player_model.professor_defeated = True
                        game.professor_scene.enter_ending_main()
                    else:
                        if m.is_glitch_lord and m.enemy_hp <= 0:
                            game.sfx.play("boss_defeat")
                            game.player_model.glitch_lord_defeated = True
                        if m.noise_guardian and m.enemy_hp <= 0:
                            scene.on_noise_guardian_defeated()
                            return
                        game.state = "map"

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
