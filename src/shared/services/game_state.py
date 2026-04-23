from __future__ import annotations

"""Scene 間で共有する state を抱える単一データオブジェクト。

Q2A / Q3A 決定により、BlockQuestApp が GameState を保有し、set_scene で
scene に DI する。scene-local な state（battle_phase など）はこの class には
入れず、各 scene の model.py に置く。P1-B の state inventory 参照。
"""

from dataclasses import dataclass, field
from typing import Any

from src.shared.services.player_state import create_initial_player


def _default_player() -> dict[str, Any]:
    """空の player dict。実値は from_new_game() か from_snapshot() が埋める。"""
    return {}


@dataclass
class GameState:
    """scene 跨ぎ共有 state（20 フィールド、P1-B inventory で確定）。"""

    # --- player ---
    player: dict[str, Any] = field(default_factory=_default_player)

    # --- progression flags ---
    cave_unblock_shown: bool = False
    tree_cleared_shown: bool = False
    poison_step_counter: int = 0
    has_save: bool = False

    # --- world / dungeon ---
    world_map: list = field(default_factory=list)
    dungeon_map: list | None = None
    dungeon_rooms: list = field(default_factory=list)
    dungeon_spawn: tuple[int, int] | None = None
    dungeon_template: Any = None
    dungeon_template_rooms: list = field(default_factory=list)

    # --- position / camera ---
    cam_x: int = 0
    cam_y: int = 0
    world_return_x: int = 0
    world_return_y: int = 0
    last_town_pos: tuple[int, int] = (0, 0)

    # --- scene tracking ---
    state: str = ""
    prev_state: str = ""

    # --- debug ---
    debug_mode: bool = False
    debug_seq: list = field(default_factory=list)

    @classmethod
    def from_new_game(cls) -> "GameState":
        """ニューゲーム用の GameState（レベル1プレイヤー）を組み立てる。"""
        return cls(player=create_initial_player())

    @property
    def in_dungeon(self) -> bool:
        """player dict 内の in_dungeon を安全に参照する（欠損時は False）。"""
        return bool(self.player.get("in_dungeon", False))

    @property
    def glitch_lord_defeated(self) -> bool:
        """player dict 内の glitch_lord_defeated を安全に参照する（欠損時は False）。"""
        return bool(self.player.get("glitch_lord_defeated", False))
