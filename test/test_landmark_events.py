from __future__ import annotations

import sys
import unittest
from pathlib import Path


PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))


class LandmarkEventRoutingTest(unittest.TestCase):
    def _load_module(self):
        try:
            from src.shared.services.landmark_events import find_landmark_event
        except ImportError as exc:
            self.fail(f"missing landmark_events module: {exc}")
        return find_landmark_event

    def test_world_tree_triggers_when_player_is_close_and_unseen(self):
        find_landmark_event = self._load_module()

        event = find_landmark_event(
            player_x=31,
            player_y=9,
            flags={"landmarkTreeSeen": False, "landmarkTowerSeen": False},
        )

        self.assertIsNotNone(event)
        self.assertEqual(event.scene_name, "landmark.tree.first")
        self.assertEqual(event.flag_name, "landmarkTreeSeen")

    def test_signal_tower_triggers_when_player_is_close_and_unseen(self):
        find_landmark_event = self._load_module()

        event = find_landmark_event(
            player_x=39,
            player_y=32,
            flags={"landmarkTreeSeen": True, "landmarkTowerSeen": False},
        )

        self.assertIsNotNone(event)
        self.assertEqual(event.scene_name, "landmark.tower.first")
        self.assertEqual(event.flag_name, "landmarkTowerSeen")

    def test_seen_or_distant_landmarks_do_not_trigger(self):
        find_landmark_event = self._load_module()

        self.assertIsNone(
            find_landmark_event(
                player_x=20,
                player_y=20,
                flags={"landmarkTreeSeen": False, "landmarkTowerSeen": False},
            )
        )
        self.assertIsNone(
            find_landmark_event(
                player_x=32,
                player_y=9,
                flags={"landmarkTreeSeen": True, "landmarkTowerSeen": False},
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
