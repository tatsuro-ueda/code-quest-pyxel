"""Tests for landmark scene resolution (world tree / signal tower)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.landmark_events import (  # noqa: E402
    LANDMARK_EVENTS,
    find_landmark_at,
    resolve_scene,
)


def _by_scene(prefix):
    for ev in LANDMARK_EVENTS:
        if ev.scene_name.startswith(prefix):
            return ev
    raise KeyError(prefix)


class WorldTreeResolveTest(unittest.TestCase):
    def setUp(self):
        self.event = _by_scene("landmark.tree")

    def test_first_visit_returns_first_scene(self):
        scene = resolve_scene(self.event, {}, glitch_lord_defeated=False)
        self.assertEqual(scene, "landmark.tree.first")

    def test_repeat_visit_returns_repeat_scene(self):
        scene = resolve_scene(
            self.event,
            {"landmarkTreeSeen": True},
            glitch_lord_defeated=False,
        )
        self.assertEqual(scene, "landmark.tree.repeat")


class TowerResolveTest(unittest.TestCase):
    def setUp(self):
        self.event = _by_scene("landmark.tower")

    def test_first_visit_returns_first_scene(self):
        scene = resolve_scene(self.event, {}, glitch_lord_defeated=False)
        self.assertEqual(scene, "landmark.tower.first")

    def test_repeat_visit_pre_boss_returns_repeat(self):
        scene = resolve_scene(
            self.event,
            {"landmarkTowerSeen": True},
            glitch_lord_defeated=False,
        )
        self.assertEqual(scene, "landmark.tower.repeat")

    def test_post_boss_returns_epilogue_once(self):
        scene = resolve_scene(
            self.event,
            {"landmarkTowerSeen": True},
            glitch_lord_defeated=True,
        )
        self.assertEqual(scene, "landmark.tower.epilogue")

    def test_after_epilogue_returns_repeat(self):
        scene = resolve_scene(
            self.event,
            {"landmarkTowerSeen": True, "towerEpilogueSeen": True},
            glitch_lord_defeated=True,
        )
        self.assertEqual(scene, "landmark.tower.repeat")


class FindLandmarkAtTest(unittest.TestCase):
    def test_finds_tree_within_radius(self):
        ev = _by_scene("landmark.tree")
        self.assertIs(find_landmark_at(ev.x, ev.y), ev)

    def test_returns_none_when_far(self):
        self.assertIsNone(find_landmark_at(0, 0))


if __name__ == "__main__":
    unittest.main()
