from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BattleModel:
    """バトル画面の状態（P1-G6 で Game.battle_* を取り込み）。"""

    enemy: Any = None
    enemy_hp: int = 0
    menu: int = 0
    phase: str = "menu"  # menu/spell_select/item_select/player_attack/enemy_attack/result
    text: str = ""
    text_timer: int = 0
    item_select: int = 0
    spell_select: int = 0
    is_glitch_lord: bool = False
    is_professor: bool = False
    boss_phase: str = "phase1"
    noise_guardian: bool = False
