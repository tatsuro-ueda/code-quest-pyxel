from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

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
from src.shared.state.player_model import (
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
        """配線：phase 遷移・入力解釈は Presenter に委譲（M3-2 準拠）。

        Presenter は phase 切り替え時にルール本体（do_player_attack /
        do_enemy_attack / victory / defeat / apply_spell_effect /
        on_noise_guardian_defeated）を呼び戻す必要があるため、self を渡す。
        """
        game = self.game
        if game is None:
            return
        self.presenter.update(game, self)

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
            p.defense = s["defense"]
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
        """バトル画面を描画する。Presenter が VM 組立て、View に委譲（M1-1 / M2-2 準拠）。

        テスト用に game 未設定なら phase snapshot を返す。
        """
        game = self.game
        if game is None:
            return self.view.render(phase=self.model.phase)
        vm = self.presenter.build_view_model(game)
        text_writer = getattr(game, "messages", None)
        vfx = getattr(game, "vfx", None)
        self.view.draw(vm, text_writer, vfx)
        return None
