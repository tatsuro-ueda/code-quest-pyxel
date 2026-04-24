"""CJG/landmark: find_landmark_at / find_landmark_event が座標で正しく分岐する。

根拠:
- docs/product-requirements-map.md（ランドマーク接触イベント）
- docs/product-requirements-narrative.md（初回/再訪のセリフ切替）

LANDMARK_EVENTS に登録された座標（tree=(32,9) / tower=(40,32)）の radius=3 以内で
反応する。マンハッタン距離を使うため、座標境界の挙動を固定化する。
find_landmark_event は flags で訪問済みなら None を返す（未訪問のみ検出）。
find_landmark_at は訪問済みも含めて常に検出する（再訪セリフのため）。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.landmark_events import (
    LANDMARK_EVENTS,
    find_landmark_at,
    find_landmark_event,
)


class FindLandmarkAtDistanceTest(unittest.TestCase):
    """find_landmark_at は訪問済みも検出する（常時ヒット）。"""

    def test_exact_tree_position_hits(self):
        lm = find_landmark_at(32, 9)
        self.assertIsNotNone(lm)
        self.assertEqual(lm.flag_name, "landmarkTreeSeen")

    def test_within_radius_hits_tree(self):
        for x, y in ((30, 9), (32, 12), (34, 9), (33, 8)):
            with self.subTest(x=x, y=y):
                self.assertIsNotNone(find_landmark_at(x, y))

    def test_outside_radius_is_none(self):
        # tree (32,9) radius=3 → マンハッタン距離 4 以上
        self.assertIsNone(find_landmark_at(36, 9))
        self.assertIsNone(find_landmark_at(32, 13))

    def test_tower_position_hits_tower(self):
        lm = find_landmark_at(40, 32)
        self.assertIsNotNone(lm)
        self.assertEqual(lm.flag_name, "landmarkTowerSeen")


class FindLandmarkEventFlagFilterTest(unittest.TestCase):
    """find_landmark_event は flags で訪問済みなら除外（未訪問のみ）。"""

    def test_unvisited_landmark_is_found(self):
        lm = find_landmark_event(player_x=32, player_y=9, flags={})
        self.assertIsNotNone(lm)

    def test_visited_landmark_returns_none(self):
        lm = find_landmark_event(
            player_x=32, player_y=9, flags={"landmarkTreeSeen": True}
        )
        self.assertIsNone(lm)

    def test_visited_tree_but_near_tower_returns_tower(self):
        lm = find_landmark_event(
            player_x=40, player_y=32, flags={"landmarkTreeSeen": True}
        )
        self.assertIsNotNone(lm)
        self.assertEqual(lm.flag_name, "landmarkTowerSeen")


class LandmarkDataContractTest(unittest.TestCase):
    """LANDMARK_EVENTS 定義がすべて必要なフィールドを持ち radius>0。"""

    def test_every_event_has_positive_radius(self):
        for event in LANDMARK_EVENTS:
            with self.subTest(flag=event.flag_name):
                self.assertGreater(event.radius, 0)

    def test_every_flag_name_is_unique(self):
        flags = [event.flag_name for event in LANDMARK_EVENTS]
        self.assertEqual(len(flags), len(set(flags)), "flag_name が重複している")

    def test_every_scene_name_is_non_empty(self):
        for event in LANDMARK_EVENTS:
            with self.subTest(flag=event.flag_name):
                self.assertTrue(event.scene_name)


if __name__ == "__main__":
    unittest.main()
