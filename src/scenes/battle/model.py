"""battle scene の local state。

Problems:
    - シーンの局所状態を Game に直書きすると、画面追加で状態が
      散らばってどこを直すか分かりにくくなる。
    - state 値や cursor 位置を View / Presenter から直接書き換えると
      不正な遷移を作りやすい。

Solutions:
    - battle シーンの局所状態を BattleModel に集約し、Presenter から
      渡された変更だけを受ける。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BattleModel:
    """バトル画面の状態（P1-G6 で Game.battle_* を取り込み）。"""

    # === Public API ===

    enemy: Any = None
    enemy_hp: int = 0
    menu: int = 0
    # menu/spell_select/item_select/player_attack/enemy_attack/result
    phase: str = "menu"
    text: str = ""
    text_timer: int = 0
    item_select: int = 0
    spell_select: int = 0
    is_glitch_lord: bool = False
    is_professor: bool = False
    boss_phase: str = "phase1"
    is_noise_guardian: bool = False
