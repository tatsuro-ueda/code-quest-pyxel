"""battle scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - battle の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
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

VISIBLE_LIST_ROWS = 4
BACK_LABEL_JP = "もどる"
BACK_LABEL_EN = "BACK"


def _build_item_use_message(game: Any, item_data: dict, result: str) -> str:
    """アイテム使用結果メッセージを組み立てる。

    Args:
        game: ``messages`` を持つ Game オブジェクト。
        item_data: 使ったアイテムのデータ。``name`` / ``value`` を参照する。
        result: ``use_item`` の戻り値（``heal`` / ``mp_heal`` /
            ``cure_poison_ok`` / ``cure_poison_none`` のいずれか）。

    Returns:
        プレイヤー向け日本語メッセージ。未知の result なら空文字列。

    Postconditions:
        - 副作用なし。
    """
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

    # === Public API ===

    model: BattleModel

    def change_phase(self, phase: str) -> None:
        """バトルの現在フェーズを指定値に差し替える。

        Args:
            phase: phase の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.model.phase = phase

    def update(self, game: Any, scene: Any) -> None:
        """バトルフェーズに応じて入力処理と状態遷移を行う。

        ``scene`` はルール本体を持つ BattleScene。do_player_attack /
        do_enemy_attack / victory / defeat / apply_spell_effect /
        handle_noise_guardian_defeated を呼び戻すために必要。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._tick_vfx_timer(game)
        self._dispatch_phase(game, scene)

    def build_view_model(self, game: Any) -> BattleViewModel:
        """Model + GameState を解釈して battle VM を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._resolve_view_model(game)

    # === Internal helpers (private) ===

    def _resolve_view_model(self, game: Any) -> BattleViewModel:
        """敵の有無に応じた VM を返すディスパッチャ。

        Args:
            game: game の値。
        Returns:
            描画用 BattleViewModel。
        Policy:
            - 敵未設定なら空 VM、設定済みなら完全 VM を返す。
        """
        enemy = self.model.enemy
        if not enemy:
            return self._build_empty_view_model(game)
        return self._build_full_view_model(game, enemy)

    @staticmethod
    def _build_empty_view_model(game: Any) -> BattleViewModel:
        """敵が未設定の最小 VM を返す。

        Args:
            game: game の値。
        Returns:
            描画を実質スキップする BattleViewModel。
        Policy:
            - 文字列はすべて空、色はデフォルト 11 のまま。
        """
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

    def _build_full_view_model(
        self, game: Any, enemy: dict
    ) -> BattleViewModel:
        """敵が設定済みのときの BattleViewModel を返す。

        Args:
            game: game の値。
            enemy: 戦闘中の敵データ。
        Returns:
            描画用 BattleViewModel。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        line1, line2, hp_ratio = self._build_player_status(game)
        return BattleViewModel(
            enemy_sprite_key=enemy.get("sprite", "slime"),
            enemy_name_text=game.text_fmt.name(enemy["name"]),
            enemy_hp_label=f"HP {model.enemy_hp}/{enemy['hp']}",
            enemy_hp_ratio=model.enemy_hp / max(1, enemy["hp"]),
            player_status_line1=line1,
            player_status_line2=line2,
            player_hp_ratio=hp_ratio,
            player_hp_color=11 if hp_ratio > 0.3 else 8,
            main_text=model.text or None,
            sub_panel=self._build_sub_panel(game),
            image_banks=game.image_banks,
        )

    @staticmethod
    def _build_player_status(game: Any) -> tuple[str, str, float]:
        """player の status 2 行と HP 比率を返す。

        Args:
            game: game の値。
        Returns:
            (line1, line2, hp_ratio) の組。
        Policy:
            - HP 比率は 0 除算を避けて max(1, max_hp) で割る。
        """
        player = game.player_model
        hp_ratio = player.hp / max(1, player.max_hp)
        line1 = (
            f"{game.text_fmt.t('プログラマー', 'PROGRAMMER')}"
            f"  レベル{player.lv}"
        )
        line2 = (
            f"HP {player.hp}/{player.max_hp}"
            f"  MP {player.mp}/{player.max_mp}"
        )
        return line1, line2, hp_ratio

    @staticmethod
    def _tick_vfx_timer(game: Any) -> None:
        """VFX タイマーを 1 減らす。0 以下なら何もしない。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.vfx.timer > 0:
            game.vfx.timer -= 1

    def _dispatch_phase(self, game: Any, scene: Any) -> None:
        """現在 phase のハンドラを呼ぶ。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        handler = self._PHASE_HANDLERS.get(self.model.phase)
        if handler is None:
            return
        handler(self, game, scene)

    def _handle_phase_menu(self, game: Any, scene: Any) -> None:
        """menu フェーズの入力処理。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._move_menu_cursor(game)
        if not game.input_state.btnp(CONFIRM_BUTTONS):
            return
        game.sfx.play("select")
        self._confirm_menu(game, scene)

    def _move_menu_cursor(self, game: Any) -> None:
        """menu フェーズの上下移動を処理する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if game.input_state.btnp(UP_BUTTONS):
            model.menu = (model.menu - 1) % 4
            game.sfx.play("cursor")
        if game.input_state.btnp(DOWN_BUTTONS):
            model.menu = (model.menu + 1) % 4
            game.sfx.play("cursor")

    def _confirm_menu(self, game: Any, scene: Any) -> None:
        """menu フェーズで決定を押したときの遷移。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if model.menu == 0:
            scene.do_player_attack()
            return
        if model.menu == 1:
            self._select_spell_menu(game)
            return
        if model.menu == 2:
            self._open_item_menu()
            return
        if model.menu == 3:
            self._select_run(game)

    def _select_spell_menu(self, game: Any) -> None:
        """じゅもんメニューを選んだときの遷移。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if game.player_model.spells:
            self._open_spell_menu()
            return
        model.text = "まだ じゅもんを おぼえていない"

    def _open_spell_menu(self) -> None:
        """spell submenu へ入り、menu 由来の stale text を消す。"""
        model = self.model
        model.phase = "spell_select"
        model.spell_select = 0
        model.text = ""

    def _open_item_menu(self) -> None:
        """item submenu へ入り、menu 由来の stale text を消す。"""
        model = self.model
        model.phase = "item_select"
        model.item_select = 0
        model.text = ""

    def _select_run(self, game: Any) -> None:
        """にげる選択時の処理。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if self._can_escape_normally(model):
            model.text = game.messages.dialog_text("battle.normal.run.success")
            model.phase = "result"
            model.text_timer = 60
            return
        scene_name = (
            "boss.glitch.run.fail"
            if model.is_glitch_lord
            else "battle.normal.run.fail"
        )
        model.text = game.messages.dialog_text(scene_name)
        model.phase = "player_attack"
        model.text_timer = 30

    @staticmethod
    def _can_escape_normally(model: BattleModel) -> bool:
        """通常戦で逃走判定に成功するかを返す。

        Args:
            model: model の値。
        Returns:
            通常戦かつ確率判定に成功なら True。
        Policy:
            - グリッチ卿戦と確率判定の失敗は False を返す。
        """
        if model.is_glitch_lord:
            return False
        return random.random() < 0.5

    def _handle_phase_spell_select(self, game: Any, scene: Any) -> None:
        """spell_select フェーズの入力処理。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        spells = game.player_model.spells
        if not spells:
            model.phase = "menu"
            return
        self._move_spell_cursor(game, spells)
        self._handle_spell_cancel(game)
        if not game.input_state.btnp(CONFIRM_BUTTONS):
            return
        game.sfx.play("select")
        self._confirm_spell(game, scene, spells)

    def _move_spell_cursor(self, game: Any, spells: list) -> None:
        """spell カーソル移動を処理する。

        Args:
            game: game の値。
            spells: 利用可能なじゅもん一覧。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if game.input_state.btnp(UP_BUTTONS):
            model.spell_select = max(0, model.spell_select - 1)
            game.sfx.play("cursor")
        if game.input_state.btnp(DOWN_BUTTONS):
            model.spell_select = min(len(spells), model.spell_select + 1)
            game.sfx.play("cursor")

    def _handle_spell_cancel(self, game: Any) -> None:
        """spell_select でキャンセル入力を処理する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if not game.input_state.btnp(CANCEL_BUTTONS):
            return
        game.sfx.play("cancel")
        self.model.phase = "menu"

    def _confirm_spell(self, game: Any, scene: Any, spells: list) -> None:
        """spell 決定時の MP 消費と効果適用を処理する。

        Args:
            game: game の値。
            scene: scene の値。
            spells: 利用可能なじゅもん一覧。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if model.spell_select == len(spells):
            model.phase = "menu"
            return
        spell_name = spells[model.spell_select]
        spell = SPELL_BY_NAME.get(spell_name)
        if spell is None:
            model.phase = "menu"
            return
        if game.player_model.mp < spell["mp"]:
            model.text = "MPが たりない！"
            return
        game.player_model.mp -= spell["mp"]
        game.sfx.play("magic")
        game.vfx.start("flash_white")
        model.text = scene.apply_spell_effect(spell)
        model.phase = "player_attack"
        model.text_timer = 30

    def _handle_phase_item_select(self, game: Any, scene: Any) -> None:
        """item_select フェーズの入力処理。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        items = game.player_model.items
        if not items:
            model.phase = "menu"
            return
        self._move_item_cursor(game, items)
        self._handle_item_cancel(game)
        if not game.input_state.btnp(CONFIRM_BUTTONS):
            return
        game.sfx.play("select")
        self._confirm_item(game, items)

    def _move_item_cursor(self, game: Any, items: list) -> None:
        """item カーソル移動を処理する。

        Args:
            game: game の値。
            items: 所持アイテム一覧。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if game.input_state.btnp(UP_BUTTONS):
            model.item_select = max(0, model.item_select - 1)
            game.sfx.play("cursor")
        if game.input_state.btnp(DOWN_BUTTONS):
            model.item_select = min(len(items), model.item_select + 1)
            game.sfx.play("cursor")

    def _handle_item_cancel(self, game: Any) -> None:
        """item_select でキャンセル入力を処理する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if not game.input_state.btnp(CANCEL_BUTTONS):
            return
        game.sfx.play("cancel")
        self.model.phase = "menu"

    def _confirm_item(self, game: Any, items: list) -> None:
        """item 決定時の使用処理と SFX 再生。

        Args:
            game: game の値。
            items: 所持アイテム一覧。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if model.item_select == len(items):
            model.phase = "menu"
            return
        item = items[model.item_select]
        item_data = ITEMS[item.id]
        if item_data["type"] == "warp":
            self._reject_warp_item(model)
            return
        result = game.player_model.use_item(item_data)
        if not result:
            self._reject_full_hp_item(model)
            return
        self._play_item_sfx(game, result)
        self._apply_item_use(game, items, item, item_data, result)

    @staticmethod
    def _reject_warp_item(model: BattleModel) -> None:
        """戦闘中の warp アイテム使用を拒否する。

        Args:
            model: model の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model.text = "せんとうちゅうはつかえない…"
        model.phase = "enemy_attack"
        model.text_timer = 30

    @staticmethod
    def _reject_full_hp_item(model: BattleModel) -> None:
        """HP 満タンで回復アイテムを拒否する。

        Args:
            model: model の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model.text = "HPがまんたんで つかえない"
        model.text_timer = 30

    def _apply_item_use(
        self,
        game: Any,
        items: list,
        item: Any,
        item_data: dict,
        result: str,
    ) -> None:
        """アイテム使用結果を model と所持リストに反映する。

        Args:
            game: game の値。
            items: 所持アイテム一覧。
            item: 使用したアイテムインスタンス。
            item_data: アイテム定義データ。
            result: 使用結果コード。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        model.text = _build_item_use_message(game, item_data, result)
        item.qty -= 1
        if item.qty <= 0:
            items.pop(model.item_select)
        model.phase = "enemy_attack"
        model.text_timer = 30

    @staticmethod
    def _play_item_sfx(game: Any, result: str) -> None:
        """アイテム使用結果に応じた SFX を鳴らす。

        Args:
            game: game の値。
            result: 使用結果コード（"heal" 等）。
        Policy:
            - 該当しない結果は何も鳴らさない。
        """
        if result in {"heal", "mp_heal"}:
            game.sfx.play("heal")
        elif result == "cure_poison_ok":
            game.sfx.play("cure")

    def _handle_phase_player_attack(self, game: Any, scene: Any) -> None:
        """player_attack フェーズの入力処理。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if self._can_fastforward_text(game, model):
            model.text_timer = 12
        model.text_timer -= 1
        if model.text_timer > 0:
            return
        if model.enemy_hp <= 0:
            scene.apply_victory()
            return
        scene.do_enemy_attack()

    def _handle_phase_enemy_attack(self, game: Any, scene: Any) -> None:
        """enemy_attack フェーズの入力処理。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if self._can_fastforward_text(game, model):
            model.text_timer = 12
        model.text_timer -= 1
        if model.text_timer > 0:
            return
        if game.player_model.hp <= 0:
            scene.apply_defeat()
            return
        model.phase = "menu"

    def _handle_phase_result(self, game: Any, scene: Any) -> None:
        """result フェーズの入力処理。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if self._can_fastforward_text(game, model):
            model.text_timer = 12
        model.text_timer -= 1
        if model.text_timer > 0:
            return
        if not self._can_advance_result(game, model):
            return
        if game.player_model.hp <= 0:
            self._resolve_player_dead(game)
            return
        if self._is_professor_victory(model):
            game.player_model.professor_defeated = True
            game.professor_scene.enter_ending_main()
            return
        self._resolve_normal_victory(game, scene)

    @staticmethod
    def _can_fastforward_text(game: Any, model: BattleModel) -> bool:
        """CONFIRM 押下中かつ text_timer > 12 ならテキスト送り早送りを返す。

        Args:
            game: game の値。
            model: model の値。
        Returns:
            条件を満たすなら True。
        Policy:
            - text_timer は呼び出し側で 12 にセットする。
        """
        if not game.input_state.btn(CONFIRM_BUTTONS):
            return False
        return model.text_timer > 12

    @staticmethod
    def _can_advance_result(game: Any, model: BattleModel) -> bool:
        """result phase の確定タイミングかを返す。

        Args:
            game: game の値。
            model: model の値。
        Returns:
            CONFIRM 入力中か、待ち時間超過なら True。
        Policy:
            - btn 押下 / btnp 押下 / text_timer < -30 を OR でまとめる。
        """
        return (
            game.input_state.btn(CONFIRM_BUTTONS)
            or game.input_state.btnp(CONFIRM_BUTTONS)
            or model.text_timer < -30
        )

    @staticmethod
    def _is_professor_victory(model: BattleModel) -> bool:
        """professor 戦の勝利状態かを返す。

        Args:
            model: model の値。
        Returns:
            professor 戦で敵 HP 0 なら True。
        Policy:
            - 通常戦・ボス戦・ノイズ戦は False を返す。
        """
        return model.is_professor and model.enemy_hp <= 0

    @staticmethod
    def _resolve_player_dead(game: Any) -> None:
        """プレイヤー死亡時の復活処理。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        game.player_model.gold = game.player_model.gold // 2
        game.player_model.hp = game.player_model.max_hp
        game.player_model.x, game.player_model.y = M.CASTLE_POS
        game.player_model.in_dungeon = False
        game.state = "map"

    def _resolve_normal_victory(self, game: Any, scene: Any) -> None:
        """通常/ボス戦勝利時の戻り遷移。

        Args:
            game: game の値。
            scene: scene の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if self._has_glitch_lord_been_defeated(model):
            game.sfx.play("boss_defeat")
            game.player_model.glitch_lord_defeated = True
        if self._has_noise_guardian_been_defeated(model):
            scene.handle_noise_guardian_defeated()
            return
        game.state = "map"

    @staticmethod
    def _has_glitch_lord_been_defeated(model: BattleModel) -> bool:
        """グリッチ卿戦で敵 HP 0 かを返す。

        Args:
            model: model の値。
        Returns:
            True のとき glitch_lord_defeated を立てるべき。
        Policy:
            - is_glitch_lord と enemy_hp <= 0 の AND を確認する。
        """
        if not model.is_glitch_lord:
            return False
        return model.enemy_hp <= 0

    @staticmethod
    def _has_noise_guardian_been_defeated(model: BattleModel) -> bool:
        """ノイズガーディアン戦で敵 HP 0 かを返す。

        Args:
            model: model の値。
        Returns:
            True のとき noise_guardian 撃破処理が必要。
        Policy:
            - is_noise_guardian と enemy_hp <= 0 の AND を確認する。
        """
        if not model.is_noise_guardian:
            return False
        return model.enemy_hp <= 0

    _PHASE_HANDLERS = {
        "menu": _handle_phase_menu,
        "spell_select": _handle_phase_spell_select,
        "item_select": _handle_phase_item_select,
        "player_attack": _handle_phase_player_attack,
        "enemy_attack": _handle_phase_enemy_attack,
        "result": _handle_phase_result,
    }

    def _build_sub_panel(self, game: Any) -> BattleSubPanel | None:
        """phase に応じた sub_panel を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        phase = self.model.phase
        if phase == "menu":
            return self._build_menu_panel(game)
        if phase == "spell_select":
            return self._build_spell_panel(game)
        if phase == "item_select":
            return self._build_item_panel(game)
        return None

    def _build_menu_panel(self, game: Any) -> BattleSubPanel:
        """menu phase の sub_panel を返す。

        Args:
            game: game の値。
        Returns:
            描画用 BattleSubPanel。
        Policy:
            - phase 単位で sub_panel を組み立てる。
        """
        model = self.model
        labels = (
            ["たたかう", "じゅもん", "アイテム", "にげる"]
            if game.has_jp_font
            else ["FIGHT", "SPELL", "ITEM", "RUN"]
        )
        rows: list[BattleRow] = []
        for i, label in enumerate(labels):
            color = 10 if i == model.menu else 6
            rows.append(BattleRow(text=label, color=color))
        return BattleSubPanel(is_grid=True, rows=rows)

    def _build_spell_panel(self, game: Any) -> BattleSubPanel:
        """spell_select phase の sub_panel を返す。

        Args:
            game: game の値。
        Returns:
            描画用 BattleSubPanel。
        Policy:
            - phase 単位で sub_panel を組み立てる。
        """
        spells = game.player_model.spells
        if not spells:
            return BattleSubPanel(
                is_grid=False,
                empty_message=game.text_fmt.t(
                    "じゅもんをおぼえていない", "No spells learned"
                ),
            )
        rows = self._build_spell_rows(game, spells)
        return BattleSubPanel(is_grid=False, rows=rows)

    def _build_spell_rows(self, game: Any, spells: list) -> list:
        """spell_select 用の行リストを組み立てる。

        Args:
            game: game の値。
            spells: 利用可能なじゅもん一覧。
        Returns:
            BattleRow のリスト。
        Policy:
            - 未登録じゅもんは行に出さない。
        """
        model = self.model
        rows: list[BattleRow] = []
        window_start = self._compute_visible_window_start(
            selected_index=min(
                model.spell_select,
                max(0, len(spells) - 1),
            ),
            item_count=len(spells),
        )
        visible_spells = spells[
            window_start:window_start + VISIBLE_LIST_ROWS
        ]
        for i, name in enumerate(visible_spells, start=window_start):
            spell = SPELL_BY_NAME.get(name)
            if spell is None:
                continue
            color = 10 if i == model.spell_select else 6
            marker = ">" if i == model.spell_select else " "
            spell_name = game.text_fmt.name(name)
            rows.append(BattleRow(
                text=f"{marker} {spell_name}  MP{spell['mp']}",
                color=color,
            ))
        rows.append(self._build_back_row(
            game=game,
            is_highlighted=(model.spell_select == len(spells)),
        ))
        return rows

    @staticmethod
    def _compute_visible_window_start(
        selected_index: int, item_count: int
    ) -> int:
        """4 行窓で選択中行を見失わない先頭 index を返す。

        Args:
            selected_index: 現在の absolute cursor index。
            item_count: 一覧全体の件数。
        Returns:
            描画に使う 4 行窓の先頭 index。
        Policy:
            - 4 件以下では 0 固定。
            - 5 件目以降は選択行が最下段に入るよう窓を 1 行ずつ送る。
        """
        if item_count <= VISIBLE_LIST_ROWS:
            return 0
        max_start = item_count - VISIBLE_LIST_ROWS
        return min(
            max(0, selected_index - VISIBLE_LIST_ROWS + 1),
            max_start,
        )

    def _build_item_panel(self, game: Any) -> BattleSubPanel:
        """item_select phase の sub_panel を返す。

        Args:
            game: game の値。
        Returns:
            描画用 BattleSubPanel。
        Policy:
            - phase 単位で sub_panel を組み立てる。
        """
        model = self.model
        items = game.player_model.items
        info_text = model.text if model.text else None
        if not items:
            return BattleSubPanel(
                is_grid=False,
                empty_message=game.text_fmt.t("アイテムがない", "No items"),
                info_message=info_text,
            )
        rows = self._build_item_rows(game, items)
        return BattleSubPanel(
            is_grid=False, rows=rows, info_message=info_text
        )

    def _build_item_rows(self, game: Any, items: list) -> list:
        """item_select 用の行リストを組み立てる。

        Args:
            game: game の値。
            items: 所持アイテム一覧。
        Returns:
            BattleRow のリスト。
        Policy:
            - 先頭 4 件まで表示する。
        """
        model = self.model
        rows: list[BattleRow] = []
        window_start = self._compute_visible_window_start(
            selected_index=min(
                model.item_select,
                max(0, len(items) - 1),
            ),
            item_count=len(items),
        )
        visible_items = items[
            window_start:window_start + VISIBLE_LIST_ROWS
        ]
        for i, item in enumerate(visible_items, start=window_start):
            idata = ITEMS[item.id]
            color = 10 if i == model.item_select else 6
            marker = ">" if i == model.item_select else " "
            item_name = game.text_fmt.name(idata["name"])
            rows.append(BattleRow(
                text=f"{marker} {item_name} x{item.qty}",
                color=color,
            ))
        rows.append(self._build_back_row(
            game=game,
            is_highlighted=(model.item_select == len(items)),
        ))
        return rows

    @staticmethod
    def _build_back_row(game: Any, is_highlighted: bool) -> BattleRow:
        """一覧末尾の back 行を返す。"""
        back_label = game.text_fmt.t(BACK_LABEL_JP, BACK_LABEL_EN)
        return BattleRow(
            text=f"{'>' if is_highlighted else ' '} {back_label}",
            color=10 if is_highlighted else 6,
        )
