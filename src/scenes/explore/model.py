from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExploreModel:
    """フィールド探索時のモード・移動演出 state を保持する。

    P1-G3 で Game から walk_frame / walk_timer / move_cooldown / a_cooldown
    を scene-local state として取り込んだ（Q2A）。
    """

    mode: str = "map"
    walk_frame: int = 0
    walk_timer: int = 0
    move_cooldown: int = 0
    a_cooldown: bool = False
