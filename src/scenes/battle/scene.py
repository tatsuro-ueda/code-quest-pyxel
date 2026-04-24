from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

import pyxel

from src.game_data import (
    ARMORS,
    GLITCH_LORD_PHASE_MESSAGES,
    ITEMS,
    NOISE_GUARDIAN_DATA,
    SPELL_BY_NAME,
    WEAPONS,
    glitch_lord_phase,
)
from src.scenes.battle.model import BattleModel
from src.scenes.battle.presenter import BattlePresenter
from src.scenes.battle.view import BattleView
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)
from src.shared.services.player_state import (
    MAX_LEVEL,
    exp_for_level,
    stats_for_level,
)


@dataclass
class BattleScene:
    """バトル画面（P1-G6 で Game から 15 メソッドを取り込み）。"""

    name: str = "battle"
    model: BattleModel = field(default_factory=BattleModel)
    view: BattleView = field(default_factory=BattleView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = BattlePresenter(self.model)

    def start(self, enemy_template, is_glitch_lord=False, is_professor=False):
        """通常/ボス戦を開始する。"""
        game = self.game
        m = self.model
        game.sfx.play("encounter")
        m.enemy = dict(enemy_template)
        m.enemy_hp = enemy_template["hp"]
        m.menu = 0
        m.phase = "menu"
        m.text = ""
        m.text_timer = 0
        m.item_select = 0
        m.spell_select = 0
        m.is_glitch_lord = is_glitch_lord
        m.is_professor = is_professor
        m.boss_phase = "phase1" if not is_professor else "100"
        if is_glitch_lord:
            m.text = game.messages.dialog_text("boss.glitch.intro")
        game.state = "battle"

    def start_noise_guardian(self):
        """ノイズガーディアン強制戦闘を開始する。"""
        game = self.game
        m = self.model
        m.noise_guardian = True
        self.start(NOISE_GUARDIAN_DATA, is_glitch_lord=False)
        m.text = game.messages.dialog_text("boss.noise_guardian.intro")

    def on_noise_guardian_defeated(self):
        """ノイズガーディアン撃破後の処理。"""
        game = self.game
        game.player_model.towerNoiseCleared = True
        self.model.noise_guardian = False
        game.messages.enter(game.messages.dialog_lines("landmark.tower.epilogue"))

    def check_noise_guardian_phase(self):
        """ノイズガーディアン戦のフェーズメッセージを差し込む。"""
        m = self.model
        max_hp = m.enemy["hp"]
        if max_hp <= 0:
            return
        ratio = m.enemy_hp / max_hp
        ng_phases = {0.75: "75", 0.40: "40", 0.10: "10"}
        for threshold, phase_key in sorted(ng_phases.items()):
            if ratio < threshold:
                new_phase = phase_key
                break
        else:
            new_phase = "100"
        if new_phase != m.boss_phase and new_phase != "100":
            m.boss_phase = new_phase
            msg = self.game.messages.dialog_text(f"boss.noise_guardian.phase_{new_phase}")
            if msg:
                m.text = (m.text + " " + msg).strip()

    def update(self):
        """バトルフェーズに応じて入力処理と状態遷移を行う。"""
        game = self.game
        if game is None:
            return
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
                    self.do_player_attack()
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
                m.text = self.apply_spell_effect(spell)
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
                    from src.shared.services.item_use import use_item as _use_item_fn
                    msg = _use_item_fn(game, item_data)
                    if not msg:
                        m.text = "HPがまんたんで つかえない"
                        m.text_timer = 30
                    else:
                        m.text = msg
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
                    self.victory()
                else:
                    self.do_enemy_attack()

        elif m.phase == "enemy_attack":
            if game.input_state.btn(CONFIRM_BUTTONS) and m.text_timer > 12:
                m.text_timer = 12
            m.text_timer -= 1
            if m.text_timer <= 0:
                if game.player_model.hp <= 0:
                    self.defeat()
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
                            self.on_noise_guardian_defeated()
                            return
                        game.state = "map"

    def do_player_attack(self):
        """たたかう選択時のプレイヤー攻撃処理。"""
        game = self.game
        import src.runtime.main_runtime as M
        m = self.model
        p = game.player_model
        e = m.enemy
        weapon_atk = WEAPONS[p.weapon]["atk"] if p.weapon < len(WEAPONS) else 0
        atk = p.atk + weapon_atk
        dmg = max(1, atk - e["def"] // 2 + random.randint(-2, 2))
        if game.debug_mode:
            dmg = 9999
        game.sfx.play("attack")
        game.vfx.start("flash_white")
        m.enemy_hp = max(0, m.enemy_hp - dmg)
        m.text = game.messages.dialog_text(
            random.choice(M.BATTLE_ATTACK_SCENES),
            enemy=e["name"],
            dmg=dmg,
        )
        self.check_glitch_lord_phase_transition()
        m.phase = "player_attack"
        m.text_timer = 40

    def check_glitch_lord_phase_transition(self):
        """ボスのHPが閾値を跨いだら phase を更新し、移行メッセージを差し込む。"""
        game = self.game
        m = self.model
        if m.enemy is None:
            return
        if m.noise_guardian:
            self.check_noise_guardian_phase()
            return
        if not (m.is_glitch_lord or m.is_professor):
            return
        max_hp = m.enemy["hp"]
        if max_hp <= 0:
            return
        ratio = m.enemy_hp / max_hp
        if m.is_professor:
            new_phase = game.professor_scene.battle_phase(ratio)
            if new_phase != m.boss_phase:
                m.boss_phase = new_phase
                try:
                    transition_msg = game.messages.dialog_text(f"castle.professor.phase_{new_phase}")
                except KeyError:
                    transition_msg = ""
                if transition_msg:
                    m.text = (m.text + " " + transition_msg).strip()
            return
        new_phase = glitch_lord_phase(ratio)
        if new_phase != m.boss_phase:
            m.boss_phase = new_phase
            transition_msg = GLITCH_LORD_PHASE_MESSAGES.get(new_phase)
            if transition_msg:
                m.text = (m.text + " " + transition_msg).strip()

    def do_enemy_attack(self):
        """敵の反撃処理。"""
        game = self.game
        m = self.model
        p = game.player_model
        e = m.enemy
        armor_def = ARMORS[p.armor]["def"] if p.armor < len(ARMORS) else 0
        total_def = p.defense + armor_def
        dmg = max(1, e["atk"] - total_def // 2 + random.randint(-2, 2))
        if game.debug_mode:
            dmg = 0
        game.sfx.play("hit")
        game.vfx.start("flash_red")
        p.hp = max(0, p.hp - dmg)
        m.text = game.messages.dialog_text(
            self.enemy_hit_scene_name(),
            enemy=e["name"],
            dmg=dmg,
        )
        if e.get("can_poison") and not p.poisoned and random.random() < 0.25:
            p.poisoned = True
            game.sfx.play("poison")
            m.text += " バグに汚染された！"
        m.phase = "enemy_attack"
        m.text_timer = 40

    def victory(self):
        """勝利処理。"""
        game = self.game
        m = self.model
        e = m.enemy
        if m.is_professor:
            m.text = game.messages.dialog_text("castle.professor.silent_victory")
            m.phase = "result"
            m.text_timer = 60
            return
        game.sfx.play("victory")
        exp = e["exp"]; gold = e["gold"]
        game.player_model.exp += exp
        game.player_model.gold += gold
        m.text = game.messages.dialog_text(
            self.victory_scene_name(),
            enemy=e["name"],
            exp=exp,
            gold=gold,
        )
        m.phase = "result"
        m.text_timer = 60
        self.check_level_up()

    def defeat(self):
        """敗北処理。"""
        game = self.game
        m = self.model
        game.sfx.play("dead")
        m.text = game.messages.dialog_text("battle.normal.defeat")
        m.phase = "result"
        m.text_timer = 60

    def check_level_up(self):
        """経験値を元にレベルアップと呪文習得を行う。"""
        game = self.game
        import src.runtime.main_runtime as M
        p = game.player_model
        while p.lv < MAX_LEVEL and p.exp >= exp_for_level(p.lv + 1):
            game.sfx.play("levelup")
            p.lv += 1
            s = stats_for_level(p.lv)
            p.max_hp = s["max_hp"]; p.hp = p.max_hp
            p.max_mp = s["max_mp"]; p.mp = p.max_mp
            p.atk = s["atk"]
            p.defense = s["def"]
            p.agi = s["agi"]
            for spell in M.SPELLS:
                if spell["learn_lv"] == p.lv and spell["name"] not in p.spells:
                    p.spells.append(spell["name"])

    def apply_spell_effect(self, spell) -> str:
        """呪文効果を適用する（MP消費は呼び出し側）。"""
        game = self.game
        m = self.model
        p = game.player_model
        if spell["type"] == "heal":
            heal = spell["power"]
            p.hp = min(p.max_hp, p.hp + heal)
            return f'{spell["name"]}を となえた。HPが{heal}回復した！'
        damage = max(1, spell["power"])
        m.enemy_hp = max(0, m.enemy_hp - damage)
        return f'{spell["name"]}！ {damage}のダメージ！'

    def enemy_hit_scene_name(self):
        """敵攻撃時のダイアログ scene 名を返す。"""
        import src.runtime.main_runtime as M
        m = self.model
        if m.is_glitch_lord:
            return "boss.glitch.enemy_hit"
        category = m.enemy.get("category", "sequential")
        return M.ENEMY_HIT_SCENES.get(category, M.ENEMY_HIT_SCENES["sequential"])

    def victory_scene_name(self):
        """勝利時のダイアログ scene 名を返す。"""
        import src.runtime.main_runtime as M
        game = self.game
        m = self.model
        if m.is_glitch_lord:
            return "boss.glitch.defeat"
        zone = M.get_zone(game.player_model.y, game.player_model.in_dungeon)
        return M.VICTORY_SCENES_BY_ZONE.get(zone, "battle.normal.victory.early")

    def draw(self) -> dict | None:
        """バトル画面を描画する。テスト用に game 未設定なら phase snapshot を返す。"""
        game = self.game
        if game is None:
            return self.view.render(phase=self.model.phase)
        m = self.model
        pyxel.cls(1)
        e = m.enemy
        if not e:
            return None

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
                    game.messages.text(30, cy, f"{game.text_fmt.name(idata['name'])} x{item['qty']}", col)
                    if i == m.item_select:
                        game.messages.text(18, cy, ">", 10)

        game.vfx.draw_overlay()
        return None
