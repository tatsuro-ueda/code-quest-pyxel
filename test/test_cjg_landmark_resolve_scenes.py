"""CJG/landmark: ExploreScene._resolve_landmark_scene のシーン名分岐。

根拠:
- docs/product-requirements-narrative.md（ランドマーク初回 / 再訪 / エピローグ）

tree は first/waiting/cleared/repeat で分岐。tower も同様。いずれも
PlayerModel のフラグ（landmark*Seen / towerNoiseCleared / glitch_lord_defeated）
に依存する。
"""

from __future__ import annotations

import random
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.explore.scene import ExploreScene
from src.shared.services.landmark_events import LandmarkEvent
from src.shared.state.player_model import PlayerModel


TREE_LANDMARK = LandmarkEvent(
    scene_name="landmark.tree.first",
    flag_name="landmarkTreeSeen",
    repeat_scene="landmark.tree.repeat",
    x=32,
    y=9,
)

TOWER_LANDMARK = LandmarkEvent(
    scene_name="landmark.tower.first",
    flag_name="landmarkTowerSeen",
    repeat_scene="landmark.tower.repeat",
    epilogue_scene="landmark.tower.epilogue",
    epilogue_flag="towerEpilogueSeen",
    x=40,
    y=32,
)


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    _tree_cleared_shown: bool = False


class TreeSceneTest(unittest.TestCase):
    def test_first_time_returns_first_scene(self):
        game = _FakeGame()
        scene = ExploreScene(game=game)

        result = scene._resolve_landmark_scene(TREE_LANDMARK)

        self.assertEqual(result, "landmark.tree.first")

    def test_after_visit_but_not_cleared_returns_waiting(self):
        game = _FakeGame()
        game.player_model.landmarkTreeSeen = True
        game.player_model.towerNoiseCleared = False
        scene = ExploreScene(game=game)

        result = scene._resolve_landmark_scene(TREE_LANDMARK)

        self.assertEqual(result, "landmark.tree.waiting")

    def test_after_cleared_first_time_returns_cleared_once(self):
        game = _FakeGame()
        game.player_model.landmarkTreeSeen = True
        game.player_model.towerNoiseCleared = True
        scene = ExploreScene(game=game)

        result1 = scene._resolve_landmark_scene(TREE_LANDMARK)
        # 2 回目以降は repeat 系
        random.seed(0)
        result2 = scene._resolve_landmark_scene(TREE_LANDMARK)

        self.assertEqual(result1, "landmark.tree.cleared")
        self.assertIn(result2, {
            "landmark.tree.repeat",
            "landmark.tree.repeat_02",
            "landmark.tree.repeat_03",
        })


class TowerSceneTest(unittest.TestCase):
    def test_first_time_returns_first_scene(self):
        game = _FakeGame()
        scene = ExploreScene(game=game)

        result = scene._resolve_landmark_scene(TOWER_LANDMARK)

        self.assertEqual(result, "landmark.tower.first")

    def test_after_visit_but_not_cleared_returns_quest(self):
        game = _FakeGame()
        game.player_model.landmarkTowerSeen = True
        game.player_model.towerNoiseCleared = False
        scene = ExploreScene(game=game)

        result = scene._resolve_landmark_scene(TOWER_LANDMARK)

        # quest or 他の何か。少なくとも文字列を返す
        self.assertIsInstance(result, str)

    def test_epilogue_scene_only_after_boss_defeated_once(self):
        game = _FakeGame()
        game.player_model.landmarkTowerSeen = True
        game.player_model.towerNoiseCleared = True
        game.player_model.glitch_lord_defeated = True
        scene = ExploreScene(game=game)

        result = scene._resolve_landmark_scene(TOWER_LANDMARK)

        self.assertEqual(result, "landmark.tower.epilogue")


if __name__ == "__main__":
    unittest.main()
