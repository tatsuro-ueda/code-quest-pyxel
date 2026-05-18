"""battle scene 本体（Model / View / Presenter の配線）。

Problems:
    - Scene に入力解釈と描画ロジックを直書きすると、レイヤが崩れて
      テスト時に Pyxel まで起動する必要が出る。
    - シーンごとに生成・配線手順がばらばらだと、新しいシーンを
      追加する時に何を持たせるか毎回考え直すことになる。

Solutions:
    - battle の Scene は Model / View / Presenter を保持し、
      update / draw を Presenter / View へ委譲する薄い配線に保つ。
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from src.game_data import (
    ARMORS,
    GLITCH_LORD_PHASE_MESSAGES,
    NOISE_GUARDIAN_DATA,
    WEAPONS,
    glitch_lord_phase,
)
from src.scenes.battle.model import BattleModel
from src.scenes.battle.presenter import BattlePresenter
from src.scenes.battle.view import BattleView, play_bgm as _play_battle_bgm
from src.shared.state.player_model import (
    MAX_LEVEL,
    exp_for_level,
    stats_for_level,
)


def _is_newly_learned(spell: dict, player: Any) -> bool:
    """level up 直後に習得すべき新じゅもんかを判定する。

    Args:
        spell: SPELLS の 1 件。
        player: PlayerModel。
    Returns:
        learn_lv が現在 lv と一致し、まだ未習得なら True。
    Policy:
        - すでに spells に入っているじゅもんは再習得しない。
    """
    if spell["learn_lv"] != player.lv:
        return False
    return spell["name"] not in player.spells


@dataclass
class BattleScene:
    """バトル画面（P1-G6 で Game から 15 メソッドを取り込み）。"""

    # === Public API ===

    name: str = "battle"
    model: BattleModel = field(default_factory=BattleModel)
    view: BattleView = field(default_factory=BattleView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.presenter = BattlePresenter(self.model)

    def start(self, enemy_template, is_glitch_lord=False, is_professor=False):
        """通常/ボス戦を開始する。

        Args:
            enemy_template: enemy_template の値。
            is_glitch_lord: is_glitch_lord の値。
            is_professor: is_professor の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_start(enemy_template, is_glitch_lord, is_professor)

    def start_noise_guardian(self):
        """ノイズガーディアン強制戦闘を開始する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        model = self.model
        model.is_noise_guardian = True
        self.start(NOISE_GUARDIAN_DATA, is_glitch_lord=False)
        model.text = game.messages.dialog_text("boss.noise_guardian.intro")

    def handle_noise_guardian_defeated(self):
        """ノイズガーディアン撃破後の処理。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        game.player_model.towerNoiseCleared = True
        self.model.is_noise_guardian = False
        game.messages.enter(
            game.messages.dialog_lines("landmark.tower.epilogue")
        )

    def check_noise_guardian_phase(self):
        """ノイズガーディアン戦のフェーズメッセージを差し込む。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_check_noise_guardian_phase()

    def update(self):
        """配線：phase 遷移・入力解釈は Presenter に委譲（M3-2 準拠）。

        Presenter は phase 切り替え時にルール本体（do_player_attack /
        do_enemy_attack / victory / defeat / apply_spell_effect /
        handle_noise_guardian_defeated）を呼び戻す必要があるため、self を渡す。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update()

    def do_player_attack(self):
        """たたかう選択時のプレイヤー攻撃処理。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_do_player_attack()

    def check_glitch_lord_phase_transition(self):
        """ボスのHPが閾値を跨いだら phase を更新し、移行メッセージを差し込む。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_check_glitch_lord_phase_transition()

    def do_enemy_attack(self):
        """敵の反撃処理。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_do_enemy_attack()

    def apply_victory(self):
        """勝利処理。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_apply_victory()

    def apply_defeat(self):
        """敗北処理。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        model = self.model
        game.sfx.play("dead")
        model.text = game.messages.dialog_text("battle.normal.defeat")
        model.phase = "result"
        model.text_timer = 60

    def check_level_up(self):
        """経験値を元にレベルアップと呪文習得を行う。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_check_level_up()

    def apply_spell_effect(self, spell) -> str:
        """呪文効果を適用する（MP消費は呼び出し側）。

        Args:
            spell: spell の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_apply_spell_effect(spell)

    def get_enemy_hit_scene_name(self):
        """敵攻撃時のダイアログ scene 名を返す。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_get_enemy_hit_scene_name()

    def get_victory_scene_name(self):
        """勝利時のダイアログ scene 名を返す。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_get_victory_scene_name()

    def draw(self) -> dict | None:
        """バトル画面を描画する。Presenter が VM 組立て、View に委譲（M1-1 / M2-2 準拠）。

        テスト用に game 未設定なら phase snapshot を返す。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_draw()

    # === Internal helpers (private) ===

    def _run_start(
        self, enemy_template, is_glitch_lord=False, is_professor=False
    ):
        """_run_start() の実装本体。

        Args:
            enemy_template: enemy_template の値。
            is_glitch_lord: is_glitch_lord の値。
            is_professor: is_professor の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        model = self.model
        game.sfx.play("encounter")
        model.enemy = dict(enemy_template)
        model.enemy_hp = enemy_template["hp"]
        model.menu = 0
        model.phase = "menu"
        model.text = ""
        model.text_timer = 0
        model.item_select = 0
        model.spell_select = 0
        model.is_glitch_lord = is_glitch_lord
        model.is_professor = is_professor
        model.boss_phase = "phase1" if not is_professor else "100"
        if is_glitch_lord:
            model.text = game.messages.dialog_text("boss.glitch.intro")
        game.state = "battle"

    def _run_check_noise_guardian_phase(self):
        """_run_check_noise_guardian_phase() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        max_hp = model.enemy["hp"]
        if max_hp <= 0:
            return
        new_phase = self._pick_noise_guardian_phase(model.enemy_hp / max_hp)
        if self._is_skipped_phase(new_phase, model.boss_phase):
            return
        self._apply_noise_guardian_phase(new_phase)

    @staticmethod
    def _is_skipped_phase(new_phase: str, current_phase: str) -> bool:
        """phase 遷移をスキップすべきかを判定する。

        Args:
            new_phase: 次の phase キー文字列。
            current_phase: 現在の phase キー文字列。
        Returns:
            同一 phase または初期 "100" ならスキップ True。
        Policy:
            - 初期 "100" は遷移メッセージを表示しない。
        """
        if new_phase == current_phase:
            return True
        return new_phase == "100"

    @staticmethod
    def _pick_noise_guardian_phase(ratio: float) -> str:
        """HP 比率から次のノイズガーディアン phase を決める。

        Args:
            ratio: 現在 HP / 最大 HP。
        Returns:
            phase キー文字列。
        Policy:
            - 閾値テーブルを昇順に走査し、最初に下回ったものを選ぶ。
        """
        ng_phases = {0.75: "75", 0.40: "40", 0.10: "10"}
        for threshold, phase_key in sorted(ng_phases.items()):
            if ratio < threshold:
                return phase_key
        return "100"

    def _apply_noise_guardian_phase(self, new_phase: str) -> None:
        """ノイズガーディアン phase の遷移と台詞付与を適用する。

        Args:
            new_phase: 次の phase キー文字列。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        model.boss_phase = new_phase
        msg = self.game.messages.dialog_text(
            f"boss.noise_guardian.phase_{new_phase}"
        )
        if msg:
            model.text = (model.text + " " + msg).strip()

    def _run_update(self):
        """_run_update() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.update(game, self)

    def _run_do_player_attack(self):
        """_run_do_player_attack() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
            - 乱数呼び出し順は保持する（randint → choice）。
        """
        game = self.game
        import src.runtime.main_runtime as M
        model = self.model
        e = model.enemy
        dmg = self._compute_player_dmg(game, e)
        self._play_attack_fx(game)
        model.enemy_hp = max(0, model.enemy_hp - dmg)
        model.text = game.messages.dialog_text(
            random.choice(M.BATTLE_ATTACK_SCENES),
            enemy=e["name"],
            dmg=dmg,
        )
        self.check_glitch_lord_phase_transition()
        model.phase = "player_attack"
        model.text_timer = 40

    @staticmethod
    def _compute_player_dmg(game: Any, enemy: dict) -> int:
        """プレイヤー攻撃のダメージ値を返す。

        Args:
            game: game の値。
            enemy: 戦闘中の敵データ。
        Returns:
            ダメージ値（debug_mode のときは 9999）。
        Policy:
            - randint(-2, 2) は本関数内で 1 回だけ呼ぶ（乱数順を変えない）。
        """
        player = game.player_model
        weapon_atk = (
            WEAPONS[player.weapon]["atk"]
            if player.weapon < len(WEAPONS) else 0
        )
        atk = player.atk + weapon_atk
        dmg = max(1, atk - enemy["def"] // 2 + random.randint(-2, 2))
        if game.debug_mode:
            return 9999
        return dmg

    @staticmethod
    def _play_attack_fx(game: Any) -> None:
        """プレイヤー攻撃の SFX / VFX を再生する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game.sfx.play("attack")
        game.vfx.start("flash_white")

    def _run_check_glitch_lord_phase_transition(self):
        """_run_check_glitch_lord_phase_transition() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if model.enemy is None:
            return
        if model.is_noise_guardian:
            self.check_noise_guardian_phase()
            return
        if not (model.is_glitch_lord or model.is_professor):
            return
        max_hp = model.enemy["hp"]
        if max_hp <= 0:
            return
        ratio = model.enemy_hp / max_hp
        if model.is_professor:
            self._transition_professor_phase(ratio)
            return
        self._transition_glitch_lord_phase(ratio)

    def _transition_professor_phase(self, ratio: float) -> None:
        """教授戦の phase 遷移を適用する。

        Args:
            ratio: 現在 HP / 最大 HP。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        model = self.model
        new_phase = game.professor_scene.battle_phase(ratio)
        if new_phase == model.boss_phase:
            return
        model.boss_phase = new_phase
        try:
            transition_msg = game.messages.dialog_text(
                f"castle.professor.phase_{new_phase}"
            )
        except KeyError:
            transition_msg = ""
        if transition_msg:
            model.text = (model.text + " " + transition_msg).strip()

    def _transition_glitch_lord_phase(self, ratio: float) -> None:
        """グリッチ卿戦の phase 遷移を適用する。

        Args:
            ratio: 現在 HP / 最大 HP。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        new_phase = glitch_lord_phase(ratio)
        if new_phase == model.boss_phase:
            return
        model.boss_phase = new_phase
        transition_msg = GLITCH_LORD_PHASE_MESSAGES.get(new_phase)
        if transition_msg:
            model.text = (model.text + " " + transition_msg).strip()

    def _run_do_enemy_attack(self):
        """_run_do_enemy_attack() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
            - 乱数呼び出し順は保持する（randint → random）。
        """
        game = self.game
        model = self.model
        player = game.player_model
        e = model.enemy
        dmg = self._compute_enemy_dmg(game, player, e)
        self._play_enemy_attack_fx(game)
        player.hp = max(0, player.hp - dmg)
        model.text = game.messages.dialog_text(
            self.get_enemy_hit_scene_name(),
            enemy=e["name"],
            dmg=dmg,
        )
        self._try_apply_poison(game, player, e)
        model.phase = "enemy_attack"
        model.text_timer = 40

    @staticmethod
    def _compute_enemy_dmg(game: Any, player: Any, enemy: dict) -> int:
        """敵攻撃のダメージ値を返す。

        Args:
            game: game の値。
            player: プレイヤーモデル。
            enemy: 戦闘中の敵データ。
        Returns:
            ダメージ値（debug_mode のときは 0）。
        Policy:
            - randint(-2, 2) は本関数内で 1 回だけ呼ぶ（乱数順を変えない）。
        """
        armor_def = (
            ARMORS[player.armor]["def"]
            if player.armor < len(ARMORS) else 0
        )
        total_def = player.defense + armor_def
        dmg = max(1, enemy["atk"] - total_def // 2 + random.randint(-2, 2))
        if game.debug_mode:
            return 0
        return dmg

    @staticmethod
    def _play_enemy_attack_fx(game: Any) -> None:
        """敵攻撃の SFX / VFX を再生する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game.sfx.play("hit")
        game.vfx.start("flash_red")

    def _try_apply_poison(self, game: Any, player: Any, enemy: dict) -> None:
        """敵が毒持ちで判定に成功したら毒状態にする。

        Args:
            game: game の値。
            player: プレイヤーモデル。
            enemy: 戦闘中の敵データ。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        Policy:
            - random() を呼ぶのは毒持ち敵かつプレイヤー未毒のときだけ（乱数順を変えない）。
        """
        if not enemy.get("can_poison"):
            return
        if player.poisoned:
            return
        if random.random() >= 0.25:
            return
        player.poisoned = True
        game.sfx.play("poison")
        self.model.text += " バグに汚染された！"

    def _run_apply_victory(self):
        """_run_apply_victory() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if model.is_professor:
            self._apply_professor_silent_victory()
            return
        self._apply_normal_victory()
        self.check_level_up()

    def _apply_professor_silent_victory(self) -> None:
        """教授戦の無音勝利演出を model に反映する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        model = self.model
        model.text = game.messages.dialog_text(
            "castle.professor.silent_victory"
        )
        model.phase = "result"
        model.text_timer = 60

    def _apply_normal_victory(self) -> None:
        """通常勝利の SFX・経験値・金・台詞を model に反映する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        model = self.model
        e = model.enemy
        game.sfx.play("victory")
        exp = e["exp"]
        gold = e["gold"]
        game.player_model.exp += exp
        game.player_model.gold += gold
        model.text = game.messages.dialog_text(
            self.get_victory_scene_name(),
            enemy=e["name"],
            exp=exp,
            gold=gold,
        )
        model.phase = "result"
        model.text_timer = 60

    def _run_check_level_up(self):
        """_run_check_level_up() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        player = game.player_model
        while (
            player.lv < MAX_LEVEL
            and player.exp >= exp_for_level(player.lv + 1)
        ):
            self._apply_level_up_step(game, player)

    @staticmethod
    def _apply_level_up_step(game: Any, player: Any) -> None:
        """1 レベル分の上昇とじゅもん習得を適用する。

        Args:
            game: game の値。
            player: プレイヤーモデル。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        game.sfx.play("levelup")
        player.lv += 1
        stats = stats_for_level(player.lv)
        player.max_hp = stats["max_hp"]
        player.hp = player.max_hp
        player.max_mp = stats["max_mp"]
        player.mp = player.max_mp
        player.atk = stats["atk"]
        player.defense = stats["defense"]
        player.agi = stats["agi"]
        for spell in M.SPELLS:
            if _is_newly_learned(spell, player):
                player.spells.append(spell["name"])

    def _run_apply_spell_effect(self, spell) -> str:
        """_run_apply_spell_effect() の実装本体。

        Args:
            spell: spell の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        model = self.model
        player = game.player_model
        if spell["type"] == "heal":
            heal = spell["power"]
            player.hp = min(player.max_hp, player.hp + heal)
            return f'{spell["name"]}を となえた。HPが{heal}回復した！'
        damage = max(1, spell["power"])
        model.enemy_hp = max(0, model.enemy_hp - damage)
        return f'{spell["name"]}！ {damage}のダメージ！'

    def _run_get_enemy_hit_scene_name(self):
        """_run_get_enemy_hit_scene_name() の実装本体。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        model = self.model
        if model.is_glitch_lord:
            return "boss.glitch.enemy_hit"
        category = model.enemy.get("category", "sequential")
        return M.ENEMY_HIT_SCENES.get(
            category, M.ENEMY_HIT_SCENES["sequential"]
        )

    def _run_get_victory_scene_name(self):
        """_run_get_victory_scene_name() の実装本体。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        game = self.game
        model = self.model
        if model.is_glitch_lord:
            return "boss.glitch.defeat"
        zone = M.get_zone(game.player_model.y, game.player_model.in_dungeon)
        return M.VICTORY_SCENES_BY_ZONE.get(
            zone, "battle.normal.victory.early"
        )

    def _run_draw(self) -> dict | None:
        """_run_draw() の実装本体。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return self.view.render(phase=self.model.phase)
        _play_battle_bgm(game)
        vm = self.presenter.build_view_model(game)
        text_writer = getattr(game, "messages", None)
        vfx = getattr(game, "vfx", None)
        self.view.draw(vm, text_writer, vfx)
        return None
