from __future__ import annotations

import sys
import unittest
from pathlib import Path

PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))

from src.shared.services.player_state import (
    SAVE_VERSION,
    SAVED_PLAYER_KEYS,
    dump_snapshot,
    restore_snapshot,
)


def _sample_player():
    return {
        "x": 20, "y": 12,
        "hp": 25, "max_hp": 30, "mp": 8, "max_mp": 10,
        "atk": 5, "def": 3, "agi": 5,
        "lv": 2, "exp": 15, "gold": 50,
        "weapon": 1, "armor": 0,
        "items": [{"id": 0, "qty": 3}],
        "spells": [],
        "poisoned": False,
        "in_dungeon": False,
        "glitch_lord_defeated": False,
        "max_zone_reached": 1,
        "landmarkTreeSeen": True,
        "landmarkTowerSeen": False,
        "treeAsked": True,
        "towerNoiseCleared": False,
        "professor_intro_seen": True,
        "professor_defeated": False,
        "professor_ending_seen": False,
        "dialog_flags": {"foo": True},
        "town_talk_idx": [0, 0, 0],
    }


class ProfessorFlagsRoundTripTest(unittest.TestCase):
    def test_professor_flags_are_persisted(self):
        from src.shared.services.player_state import dump_snapshot, restore_snapshot
        player = _sample_player()
        player["professor_intro_seen"] = True
        player["professor_defeated"] = True
        player["professor_ending_seen"] = True
        snap = dump_snapshot(player, town_pos=(25, 6))
        restored = restore_snapshot(snap)
        self.assertTrue(restored["player"]["professor_intro_seen"])
        self.assertTrue(restored["player"]["professor_defeated"])
        self.assertTrue(restored["player"]["professor_ending_seen"])


class PlayerSnapshotTest(unittest.TestCase):
    def test_dump_includes_all_saved_keys(self):
        player = _sample_player()
        snap = dump_snapshot(player, town_pos=(20, 12))
        self.assertEqual(snap["save_version"], SAVE_VERSION)
        self.assertEqual(snap["town_pos"], [20, 12])
        for key in SAVED_PLAYER_KEYS:
            self.assertIn(key, snap["player"])

    def test_dump_excludes_non_saved_keys(self):
        player = _sample_player()
        player["debug_mode"] = True
        player["temp_battle_state"] = "phase_1"
        snap = dump_snapshot(player, town_pos=(20, 12))
        self.assertNotIn("debug_mode", snap["player"])
        self.assertNotIn("temp_battle_state", snap["player"])

    def test_restore_round_trip(self):
        player = _sample_player()
        snap = dump_snapshot(player, town_pos=(20, 12))
        restored = restore_snapshot(snap)
        for key in SAVED_PLAYER_KEYS:
            self.assertEqual(restored["player"][key], player[key], key)
        self.assertEqual(restored["town_pos"], (20, 12))

    def test_restore_drops_legacy_av_settings(self):
        """2026-05-07 改訂（CJ44 確定版）：bgm/sfx/vfx_enabled は撤去済。

        古いセーブに残っていても無視され、復元結果には含まれない。
        """
        snap = {
            "save_version": SAVE_VERSION,
            "town_pos": [20, 12],
            "player": {
                "x": 20,
                "y": 12,
                "bgm_enabled": False,
                "sfx_enabled": False,
                "vfx_enabled": False,
            },
        }

        restored = restore_snapshot(snap)

        self.assertNotIn("bgm_enabled", restored["player"])
        self.assertNotIn("sfx_enabled", restored["player"])
        self.assertNotIn("vfx_enabled", restored["player"])

    def test_restore_does_not_require_all_keys(self):
        player = {"x": 1, "y": 2, "hp": 5}
        snap = dump_snapshot(player, town_pos=(1, 2))
        restored = restore_snapshot(snap)
        self.assertEqual(restored["player"]["hp"], 5)
        self.assertNotIn("max_hp", restored["player"])

    def test_restore_accepts_legacy_boss_defeated_key(self):
        snap = {
            "save_version": SAVE_VERSION,
            "town_pos": [20, 12],
            "player": {
                "x": 20,
                "y": 12,
                "boss_defeated": True,
            },
        }

        restored = restore_snapshot(snap)

        self.assertTrue(restored["player"]["glitch_lord_defeated"])
        self.assertNotIn("boss_defeated", restored["player"])


if __name__ == "__main__":
    unittest.main()
