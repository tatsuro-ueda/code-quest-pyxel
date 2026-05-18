"""Scene 間で共有する state を抱える単一データオブジェクト。

このファイルに含まれる関数・クラス：

- TownContext: 町メニューから shop 等へ渡す町識別情報を保持する不変レコード
- GameState: scene 跨ぎで共有する可変 state を束ねるデータクラス
  - from_new_game: ニューゲーム用の GameState を組み立てるファクトリ
  - in_dungeon: player_model.in_dungeon を bool に正規化して返す
  - glitch_lord_defeated: player_model.glitch_lord_defeated を bool に正規化して返す

Problems:
    - scene-local な値と scene 跨ぎで共有したい値を同じ場所に書くと、
      どの scene が何を読み書きしてよいかが曖昧になる。
    - 各 scene が独自に runtime root の属性を生やすと、保存・復元の対象が
      ばらけて、セーブデータの整合が崩れる。

Solutions:
    - 共有 state は GameState 1 箇所に集約し、scene-local な state は
      各 scene の model.py に置く（framework-rule.md M4-3）。
    - player 由来のフラグは property 経由で player_model を参照し、
      参照経路を 1 本化する。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.shared.state.player_model import PlayerModel


@dataclass(frozen=True)
class TownContext:
    """町メニューから shop 等へ渡す町識別情報（framework-rule.md M4-3）。"""

    # === Public API ===

    index: int
    pos: tuple[int, int]


@dataclass
class GameState:
    """scene 跨ぎ共有 state（framework-rule.md M4-3）。"""

    # === Public API ===

    # --- player ---
    player_model: PlayerModel = field(default_factory=PlayerModel)

    # --- progression flags ---
    cave_unblock_shown: bool = False  # noqa: CR101
    tree_cleared_shown: bool = False  # noqa: CR101
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
    def from_new_game(cls) -> "GameState":  # noqa: CR100
        """ニューゲーム用の GameState（レベル1プレイヤー）を組み立てる。

        Returns:
            PlayerModel.new_game() を埋め込んだ GameState インスタンス。
        Policy:
            - factory 名 from_new_game は外部テスト・呼び出し側で固定参照されているため変更しない。
            - player_model 以外のフィールドは dataclass デフォルト値に委ねる。
        """
        return cls(player_model=PlayerModel.new_game())

    @property
    def in_dungeon(self) -> bool:  # noqa: CR100
        """player_model.in_dungeon を bool に正規化して返す。

        Returns:
            プレイヤーがダンジョン内にいるなら True。
        Policy:
            - property 名 in_dungeon は scene / test から固定参照されているため変更しない。
            - 真偽判定は player_model 側の値に委ね、ここでは bool() による正規化のみ行う。
        """
        return bool(self.player_model.in_dungeon)

    @property
    def glitch_lord_defeated(self) -> bool:  # noqa: CR100
        """player_model.glitch_lord_defeated を bool に正規化して返す。

        Returns:
            ラスボス（glitch lord）を撃破済みなら True。
        Policy:
            - property 名 glitch_lord_defeated は scene / test で固定参照されているため変更しない。
            - 真偽判定は player_model 側の値に委ね、ここでは bool() による正規化のみ行う。
        """
        return bool(self.player_model.glitch_lord_defeated)
