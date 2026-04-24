"""CJG/crash regression: マップタイル判定で各 state 遷移が crash しない（Phase H）。

根拠:
- docs/product-requirements-map.md（T_TOWN / T_CASTLE / T_GLITCH_LORD_TRIGGER の遷移）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

`_check_tile_events(tile, nx, ny)` は explore scene の核心。各タイル種別で
期待される game.state の変化が起きることを fake game で固定化する。

T_TOWN は別 note（test_cjg_town_entry_populates_current_town.py）でカバー済み。
本 note は T_CASTLE / T_GLITCH_LORD_TRIGGER / T_STAIR_UP（ダンジョン出口）を担当。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.explore.scene import ExploreScene
from src.scenes.town.model import TownModel
from src.shared.services.game_state import TownContext
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeMessages:
    entered: list = field(default_factory=list)
    shown: list = field(default_factory=list)

    def enter(self, lines, callback=None):
        self.entered.append((list(lines), callback))

    def show(self, lines):
        self.shown.append(list(lines))

    def dialog_lines(self, *_args, **_kwargs):
        return ["…"]


@dataclass
class _FakeProfessorScene:
    entered_intro: int = 0

    def enter_intro(self):
        self.entered_intro += 1

    def phase(self):
        return "unknown"


@dataclass
class _FakeBattleScene:
    started: list = field(default_factory=list)

    def start(self, data, is_professor=False, is_glitch_lord=False):
        self.started.append({"data": data, "is_glitch_lord": is_glitch_lord})


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    town_model: TownModel = field(default_factory=TownModel)
    current_town: TownContext | None = None
    last_town_pos: tuple[int, int] | None = None
    state: str = "map"
    world_return_x: int = 0
    world_return_y: int = 0
    dungeon_map: Any = None
    debug_mode: bool = True  # ランダムエンカウントを抑える（対象外のフォールスルー対策）
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    professor_scene: _FakeProfessorScene = field(default_factory=_FakeProfessorScene)
    battle_scene: _FakeBattleScene = field(default_factory=_FakeBattleScene)


class CastleTileTest(unittest.TestCase):
    """T_CASTLE タイルを踏むと state が "town" に遷移しメッセージを表示する。"""

    def test_castle_tile_with_glitch_lord_defeated_at_center_enters_professor(self):
        from src.shared.constants.tile_data import T_CASTLE

        game = _FakeGame()
        game.player_model.glitch_lord_defeated = True
        scene = ExploreScene(game=game)

        scene._check_tile_events(T_CASTLE, 25, 6)

        self.assertEqual(game.professor_scene.entered_intro, 1)

    def test_castle_tile_without_glitch_lord_defeated_shows_message(self):
        from src.shared.constants.tile_data import T_CASTLE

        game = _FakeGame()
        game.player_model.glitch_lord_defeated = False
        scene = ExploreScene(game=game)

        scene._check_tile_events(T_CASTLE, 25, 6)

        # 台詞表示 → state を town に
        self.assertEqual(game.state, "town")
        self.assertTrue(
            game.messages.shown,
            "CASTLE で messages.show が呼ばれていない",
        )


class GlitchLordTriggerTileTest(unittest.TestCase):
    """T_GLITCH_LORD_TRIGGER を in_dungeon かつ未撃破状態で踏むと battle_scene.start が呼ばれる。"""

    def test_glitch_lord_trigger_starts_boss_battle_when_not_defeated(self):
        from src.shared.constants.tile_data import T_GLITCH_LORD_TRIGGER

        game = _FakeGame()
        game.player_model.in_dungeon = True
        game.player_model.glitch_lord_defeated = False
        scene = ExploreScene(game=game)

        scene._check_tile_events(T_GLITCH_LORD_TRIGGER, 10, 10)

        self.assertEqual(len(game.battle_scene.started), 1)
        self.assertTrue(game.battle_scene.started[0]["is_glitch_lord"])

    def test_glitch_lord_trigger_skips_when_already_defeated(self):
        from src.shared.constants.tile_data import T_GLITCH_LORD_TRIGGER

        game = _FakeGame()
        game.player_model.in_dungeon = True
        game.player_model.glitch_lord_defeated = True
        scene = ExploreScene(game=game)

        scene._check_tile_events(T_GLITCH_LORD_TRIGGER, 10, 10)

        self.assertEqual(
            game.battle_scene.started,
            [],
            "撃破済みなのに再度ボス戦に入っている",
        )

    def test_glitch_lord_trigger_ignored_outside_dungeon(self):
        """ダンジョン外で踏んでも何も起きない（フィールドに置かれていないはずだが安全網）。"""
        from src.shared.constants.tile_data import T_GLITCH_LORD_TRIGGER

        game = _FakeGame()
        game.player_model.in_dungeon = False
        scene = ExploreScene(game=game)

        scene._check_tile_events(T_GLITCH_LORD_TRIGGER, 10, 10)

        self.assertEqual(game.battle_scene.started, [])


class DungeonStairUpTileTest(unittest.TestCase):
    """ダンジョン内で T_STAIR_UP を踏むとフィールドに戻る。"""

    def test_stair_up_in_dungeon_returns_to_world(self):
        from src.shared.constants.tile_data import T_STAIR_UP

        game = _FakeGame()
        game.player_model.in_dungeon = True
        game.player_model.x = 5
        game.player_model.y = 8
        game.world_return_x = 20
        game.world_return_y = 25
        game.dungeon_map = object()  # 何か入っていれば良い
        scene = ExploreScene(game=game)

        scene._check_tile_events(T_STAIR_UP, 5, 8)

        self.assertFalse(game.player_model.in_dungeon)
        self.assertEqual(game.player_model.x, 20)
        self.assertEqual(game.player_model.y, 25)
        self.assertIsNone(game.dungeon_map)
        self.assertTrue(game.messages.entered, "ダンジョン退出時のメッセージが表示されていない")

    def test_stair_up_outside_dungeon_is_ignored(self):
        from src.shared.constants.tile_data import T_STAIR_UP

        game = _FakeGame()
        game.player_model.in_dungeon = False
        scene = ExploreScene(game=game)

        scene._check_tile_events(T_STAIR_UP, 5, 8)

        # フィールド上では T_STAIR_UP は意味を持たない（messages も呼ばれない）
        self.assertEqual(game.messages.entered, [])


if __name__ == "__main__":
    unittest.main()
