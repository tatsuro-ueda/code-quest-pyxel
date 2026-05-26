"""battle scene の描画。

Problems:
    - 描画コードに状態判定が混ざると、見た目を変えるだけのつもりが
      Model 整合性まで考えることになる。
    - Pyxel API が Presenter / Model 側に染み出すとレイヤ境界が崩れ、
      テストでモックしづらくなる。

Solutions:
    - battle の View は ViewModel と Pyxel API だけを扱い、
      判断は Presenter 側に閉じ込める。
"""
from __future__ import annotations

from typing import Any

import pyxel

from src.scenes.battle.view_model import BattleViewModel
from src.shared.services.audio_system import play_bgm_track
from src.shared.ui.wrapped_text import resolve_wrapped_lines


# pyxres 内 musics スロット番号（旧 TRACK_ORDER と整合）。
BATTLE_BGM_INDEX = 4
BOSS_BGM_INDEX = 5
VICTORY_BGM_INDEX = 6
MAIN_MESSAGE_WRAP_WIDTH = 28
MAIN_MESSAGE_MAX_ROWS = 2
MAIN_MESSAGE_LINE_HEIGHT = 12
PLAYER_STATUS_BAR_Y = 128


def _select_battle_bgm(game) -> int:
    """game.battle_scene.model から戦闘 BGM の musics index を決める純粋関数。

    Args:
        game: game の値。
    Returns:
        関数の戻り値。
    Postconditions:
        - 副作用とモデル更新は実装どおり。
    """
    if game is None:
        return BATTLE_BGM_INDEX
    bm = getattr(getattr(game, "battle_scene", None), "model", None)
    if bm is None:
        return BATTLE_BGM_INDEX
    # 勝利フェーズ：phase == "result" かつ敵 HP 0
    is_victory_phase = (
        getattr(bm, "phase", None) == "result"
        and getattr(bm, "enemy_hp", 1) <= 0
    )
    if is_victory_phase:
        return VICTORY_BGM_INDEX
    if getattr(bm, "is_glitch_lord", False):
        return BOSS_BGM_INDEX
    return BATTLE_BGM_INDEX


def play_bgm(game) -> None:
    """戦闘シーンの BGM を冪等に発火する（battle/boss/victory を分岐選択）。

    CJ44 確定版（追加整理）：冪等性は ``audio_system.play_bgm_track`` に集約。

    Args:
        game: game の値。
    Postconditions:
        - 副作用とモデル更新は実装どおり。
    """
    _run_play_bgm(game)


def _run_play_bgm(game) -> None:
    """_run_play_bgm() の実装本体。

    Args:
        game: game の値。
    Postconditions:
        - 副作用とモデル更新は実装どおり。
    """
    if game is None:
        return
    play_bgm_track(_select_battle_bgm(game))


class BattleView:
    """バトル画面の描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    # === Public API ===

    def render(self, *, phase: str) -> dict[str, str]:
        """現在のバトルフェーズを描画に必要な辞書として返す（snapshot 用）。

        Args:
            phase: phase の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return {"phase": phase}

    def draw(
        self, vm: BattleViewModel, text_writer: Any, vfx: Any = None
    ) -> None:
        """BattleViewModel を画面に描く。

        ``vfx`` は draw_overlay() を持つ画面エフェクトサービス（描画専用アセット
        参照、M2-1 例外）。None なら overlay スキップ（test 互換）。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
            vfx: vfx の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_draw(vm, text_writer, vfx)

    # === Internal helpers (private) ===

    def _run_draw(
        self, vm: BattleViewModel, text_writer: Any, vfx: Any = None
    ) -> None:
        """_run_draw() の実装本体。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
            vfx: vfx の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        pyxel.cls(1)
        if vm.enemy_sprite_key is None:
            return
        self._draw_enemy_sprite(vm)
        self._draw_enemy_hp_bar(vm, text_writer)
        self._draw_player_status(vm, text_writer)
        self._draw_main_message(vm, text_writer)
        self._draw_sub_panel(vm, text_writer)
        if vfx is not None:
            vfx.draw_overlay()

    @staticmethod
    def _draw_enemy_sprite(vm: BattleViewModel) -> None:
        """敵スプライトを 3x 拡大して描画する。

        Args:
            vm: vm の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if vm.image_banks is None:
            return
        bp = vm.image_banks.sprite_bank.get(vm.enemy_sprite_key)
        if not bp:
            return
        sx, sy = bp
        for py in range(16):
            for px in range(16):
                color = pyxel.images[1].pget(sx + px, sy + py)
                if color == 0:
                    continue
                for dy in range(3):
                    for dx2 in range(3):
                        pyxel.pset(
                            104 + px * 3 + dx2,
                            30 + py * 3 + dy,
                            color,
                        )

    @staticmethod
    def _draw_enemy_hp_bar(vm: BattleViewModel, text_writer: Any) -> None:
        """敵名と HP バーを描画する。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        text_writer.text(80, 10, vm.enemy_name_text, 7)
        bar_x = 80
        bar_w = 96
        pyxel.rect(bar_x, 85, bar_w, 8, 0)
        pyxel.rect(bar_x, 85, int(bar_w * vm.enemy_hp_ratio), 8, 8)
        text_writer.text(bar_x + 2, 86, vm.enemy_hp_label, 7)

    @staticmethod
    def _draw_player_status(vm: BattleViewModel, text_writer: Any) -> None:
        """プレイヤーステータス枠と HP バーを描画する。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        pyxel.rect(10, 100, 236, 40, 0)
        pyxel.rectb(10, 100, 236, 40, 7)
        text_writer.text(16, 104, vm.player_status_line1, 7)
        text_writer.text(16, 116, vm.player_status_line2, 7)
        pyxel.rect(170, PLAYER_STATUS_BAR_Y, 60, 6, 0)
        pyxel.rect(
            170,
            PLAYER_STATUS_BAR_Y,
            int(60 * vm.player_hp_ratio),
            6,
            vm.player_hp_color,
        )

    @staticmethod
    def _draw_main_message(vm: BattleViewModel, text_writer: Any) -> None:
        """メインメッセージ枠を描画する。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if vm.main_text is None:
            return
        pyxel.rect(10, 148, 236, 30, 0)
        pyxel.rectb(10, 148, 236, 30, 7)
        for i, line in enumerate(
            BattleView._resolve_main_message_lines(vm.main_text, text_writer)
        ):
            text_writer.text(
                16,
                154 + i * MAIN_MESSAGE_LINE_HEIGHT,
                line,
                7,
            )

    @staticmethod
    def _resolve_main_message_lines(
        main_text: str, text_writer: Any
    ) -> list[str]:
        """battle の main message を枠内に収まる行列へ変換する。

        Args:
            main_text: 折返し前のメインメッセージ文字列。
            text_writer: ``wrap_text`` を持つ描画補助オブジェクト。
        Returns:
            枠内に表示する最大 2 行の文字列リスト。
        Postconditions:
            - ``text_writer`` に wrap helper が無いときは 1 行のまま返す。
        """
        return resolve_wrapped_lines(
            main_text,
            text_writer,
            max_chars=MAIN_MESSAGE_WRAP_WIDTH,
            max_rows=MAIN_MESSAGE_MAX_ROWS,
        )

    def _draw_sub_panel(
        self, vm: BattleViewModel, text_writer: Any
    ) -> None:
        """sub_panel（menu / spell_select / item_select）を描画する。

        Args:
            vm: vm の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        sp = vm.sub_panel
        if sp is None:
            return
        pyxel.rect(10, 190, 236, 56, 0)
        pyxel.rectb(10, 190, 236, 56, 7)
        if sp.info_message is not None:
            text_writer.text(16, 192, sp.info_message, 8)
        if sp.empty_message is not None:
            text_writer.text(16, 200, sp.empty_message, 6)
            return
        if sp.is_grid:
            self._draw_sub_panel_grid(sp, text_writer)
            return
        self._draw_sub_panel_list(sp, text_writer)

    @staticmethod
    def _draw_sub_panel_grid(sp: Any, text_writer: Any) -> None:
        """menu フェーズの 2x2 グリッド + カーソルを描画する。

        Args:
            sp: sp の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        for i, row in enumerate(sp.rows):
            cx = 30 + (i % 2) * 110
            cy = 198 + (i // 2) * 18
            text_writer.text(cx, cy, row.text, row.color)
            if row.color == 10:
                text_writer.text(cx - 12, cy, ">", 10)

    @staticmethod
    def _draw_sub_panel_list(sp: Any, text_writer: Any) -> None:
        """spell_select / item_select の一覧を描画する。

        Args:
            sp: sp の値。
            text_writer: text_writer の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        row_step = 10 if len(sp.rows) >= 5 else 12
        for i, row in enumerate(sp.rows):
            cy = 196 + i * row_step
            text_writer.text(30, cy, row.text, row.color)
