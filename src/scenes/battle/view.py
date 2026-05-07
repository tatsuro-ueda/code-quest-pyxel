from __future__ import annotations

from typing import Any

import pyxel

from src.scenes.battle.view_model import BattleViewModel
from src.shared.services.audio_system import play_bgm_track


# pyxres 内 musics スロット番号（旧 TRACK_ORDER と整合）。
BATTLE_BGM_INDEX = 4
BOSS_BGM_INDEX = 5
VICTORY_BGM_INDEX = 6


def _select_battle_bgm(game) -> int:
    """game.battle_scene.model から戦闘 BGM の musics index を決める純粋関数。"""
    if game is None:
        return BATTLE_BGM_INDEX
    bm = getattr(getattr(game, "battle_scene", None), "model", None)
    if bm is None:
        return BATTLE_BGM_INDEX
    # 勝利フェーズ：phase == "result" かつ敵 HP 0
    if getattr(bm, "phase", None) == "result" and getattr(bm, "enemy_hp", 1) <= 0:
        return VICTORY_BGM_INDEX
    # ボス戦：is_glitch_lord などボス判定
    if getattr(bm, "is_glitch_lord", False):
        return BOSS_BGM_INDEX
    return BATTLE_BGM_INDEX


def play_bgm(game) -> None:
    """戦闘シーンの BGM を冪等に発火する（battle/boss/victory を分岐選択）。

    CJ44 確定版（追加整理）：冪等性は ``audio_system.play_bgm_track`` に集約。
    """
    if game is None:
        return
    play_bgm_track(_select_battle_bgm(game))


class BattleView:
    """バトル画面の描画担当（M1-1 / M2-2：解釈済み ViewModel を受け取って描画のみ）。"""

    def render(self, *, phase: str) -> dict[str, str]:
        """現在のバトルフェーズを描画に必要な辞書として返す（snapshot 用）。"""
        return {"phase": phase}

    def draw(self, vm: BattleViewModel, text_writer: Any, vfx: Any = None) -> None:
        """BattleViewModel を画面に描く。

        ``vfx`` は draw_overlay() を持つ画面エフェクトサービス（描画専用アセット
        参照、M2-1 例外）。None なら overlay スキップ（test 互換）。
        """
        pyxel.cls(1)
        if vm.enemy_sprite_key is None:
            return

        # 敵スプライトを 3x 拡大して中央に
        if vm.image_banks is not None:
            bp = vm.image_banks.sprite_bank.get(vm.enemy_sprite_key)
            if bp:
                sx, sy = bp
                for py in range(16):
                    for px in range(16):
                        c = pyxel.images[1].pget(sx + px, sy + py)
                        if c != 0:
                            for dy in range(3):
                                for dx2 in range(3):
                                    pyxel.pset(104 + px * 3 + dx2, 30 + py * 3 + dy, c)

        # 敵名 + 敵 HP バー
        text_writer.text(80, 10, vm.enemy_name_text, 7)
        bar_x = 80; bar_w = 96
        pyxel.rect(bar_x, 85, bar_w, 8, 0)
        pyxel.rect(bar_x, 85, int(bar_w * vm.enemy_hp_ratio), 8, 8)
        text_writer.text(bar_x + 2, 86, vm.enemy_hp_label, 7)

        # プレイヤーステータス枠
        pyxel.rect(10, 100, 236, 40, 0)
        pyxel.rectb(10, 100, 236, 40, 7)
        text_writer.text(16, 104, vm.player_status_line1, 7)
        text_writer.text(16, 116, vm.player_status_line2, 7)
        pyxel.rect(170, 116, 60, 6, 0)
        pyxel.rect(170, 116, int(60 * vm.player_hp_ratio), 6, vm.player_hp_color)

        # メッセージ枠
        if vm.main_text is not None:
            pyxel.rect(10, 148, 236, 30, 0)
            pyxel.rectb(10, 148, 236, 30, 7)
            text_writer.text(16, 154, vm.main_text, 7)

        # sub_panel（menu / spell_select / item_select）
        sp = vm.sub_panel
        if sp is not None:
            pyxel.rect(10, 190, 236, 56, 0)
            pyxel.rectb(10, 190, 236, 56, 7)
            if sp.info_message is not None:
                text_writer.text(16, 192, sp.info_message, 8)
            if sp.empty_message is not None:
                text_writer.text(16, 200, sp.empty_message, 6)
            elif sp.is_grid:
                # menu: 2x2 grid + cursor を別文字描画
                for i, row in enumerate(sp.rows):
                    cx = 30 + (i % 2) * 110
                    cy = 198 + (i // 2) * 18
                    text_writer.text(cx, cy, row.text, row.color)
                    if row.color == 10:
                        text_writer.text(cx - 12, cy, ">", 10)
            else:
                for i, row in enumerate(sp.rows):
                    cy = 196 + i * 12
                    text_writer.text(30, cy, row.text, row.color)

        if vfx is not None:
            vfx.draw_overlay()
