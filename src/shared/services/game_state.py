from __future__ import annotations

"""Scene 間で共有する state を抱える単一データオブジェクト。

Q2A / Q3A 決定により、BlockQuestApp が GameState を保有し、set_scene で
scene に DI する。scene-local な state（battle_phase など）はこの class には
入れず、各 scene の model.py に置く。P1-B の state inventory 参照。
"""

from dataclasses import dataclass, field

from src.shared.state.player_model import PlayerModel


@dataclass(frozen=True)
class TownContext:
    """町メニューから shop 等へ渡す町識別情報（framework-rule.md M4-3）。"""
    index: int
    pos: tuple[int, int]


@dataclass
class GameState:
    """scene 跨ぎ共有 state（framework-rule.md M4-3）。"""

    # --- player ---
    player_model: PlayerModel = field(default_factory=PlayerModel)

    # --- progression flags ---
    cave_unblock_shown: bool = False
    tree_cleared_shown: bool = False
    poison_step_counter: int = 0
    has_save: bool = False

    # --- world / dungeon ---
    dungeon_spawn: tuple[int, int] | None = None
    dungeon_template: "object | None" = None
    dungeon_template_rooms: list = field(default_factory=list)

    # --- position / camera ---
    cam_x: int = 0
    cam_y: int = 0
    world_return_x: int = 0
    world_return_y: int = 0
    last_town_pos: tuple[int, int] = (0, 0)

    # --- current town context（shop→town 境界、framework-rule.md M4-3）---
    current_town: TownContext | None = None

    @classmethod
    def from_new_game(cls) -> "GameState":
        """ニューゲーム用の GameState（レベル1プレイヤー）を組み立てる。"""
        return cls(player_model=PlayerModel.new_game())

    @property
    def in_dungeon(self) -> bool:
        return bool(self.player_model.in_dungeon)

    @property
    def glitch_lord_defeated(self) -> bool:
        return bool(self.player_model.glitch_lord_defeated)
