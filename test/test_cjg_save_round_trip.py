"""CJG/crash regression: セーブ往復が全属性を保持する（Phase H）。

根拠:
- docs/product-requirements-map.md（セーブ・ロードの整合）
- docs/product-requirements-platform.md（セーブ互換）
- docs/customer-jobs.md Make3「クラッシュで好循環が途絶」

to_snapshot と from_snapshot の往復で PlayerModel の全 SAVED_FIELDS が
保持される。装備番号・HP/MP の現在値・レベル・経験値・ダンジョン在籍・
各種フラグが欠落すると「セーブしたつもりが復元できない」体験につながる。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.state.player_model import (
    SAVED_FIELDS,
    PlayerItem,
    PlayerModel,
)


class SaveRoundTripAllFieldsTest(unittest.TestCase):
    """SAVED_FIELDS に列挙された全属性が to_snapshot → from_snapshot で保持される。"""

    def _modified_player(self) -> PlayerModel:
        """デフォルトから全フィールドを別値に変えたプレイヤー。"""
        pm = PlayerModel.new_game()
        pm.x = 123
        pm.y = 45
        pm.hp = 7
        pm.max_hp = 99
        pm.mp = 3
        pm.max_mp = 55
        pm.atk = 41
        pm.defense = 32
        pm.agi = 27
        pm.lv = 18
        pm.exp = 5000
        pm.gold = 77777
        pm.weapon = 4
        pm.armor = 3
        pm.items = [PlayerItem(id=0, qty=9), PlayerItem(id=2, qty=2)]
        pm.spells = ["heal", "fire"] if hasattr(pm, "spells") else pm.spells
        pm.poisoned = True
        pm.in_dungeon = True
        pm.glitch_lord_defeated = True
        pm.max_zone_reached = 3
        pm.landmarkTreeSeen = True
        pm.landmarkTowerSeen = True
        pm.treeAsked = True
        pm.towerNoiseCleared = True
        pm.professor_intro_seen = True
        pm.professor_defeated = True
        pm.professor_ending_seen = True
        pm.dialog_flags = {"castle.first_visit": True}
        pm.town_talk_idx = [1, 2, 3]
        return pm

    def test_round_trip_preserves_all_saved_fields(self):
        pm = self._modified_player()

        snap = pm.to_snapshot(town_pos=(30, 22))
        restored, town_pos = PlayerModel.from_snapshot(snap)

        self.assertEqual(town_pos, (30, 22))
        for attr in SAVED_FIELDS:
            with self.subTest(attr=attr):
                original = getattr(pm, attr)
                after = getattr(restored, attr)
                if attr == "items":
                    # items は dataclass 再構築なので個別比較
                    self.assertEqual(
                        [(it.id, it.qty) for it in original],
                        [(it.id, it.qty) for it in after],
                    )
                else:
                    self.assertEqual(original, after, f"{attr} が round-trip で消えた")

    def test_round_trip_preserves_empty_and_zero_values(self):
        pm = PlayerModel.new_game()
        pm.items = []
        pm.gold = 0
        pm.hp = 0
        pm.poisoned = False

        snap = pm.to_snapshot(town_pos=(25, 6))
        restored, _pos = PlayerModel.from_snapshot(snap)

        self.assertEqual(restored.items, [])
        self.assertEqual(restored.gold, 0)
        self.assertEqual(restored.hp, 0)
        self.assertFalse(restored.poisoned)

    def test_snapshot_includes_save_version(self):
        pm = PlayerModel.new_game()
        snap = pm.to_snapshot(town_pos=(25, 6))

        self.assertIn("save_version", snap)
        self.assertIsInstance(snap["save_version"], int)

    def test_snapshot_serializes_items_as_plain_dicts(self):
        """items は PlayerItem dataclass ではなく dict のリストに直列化される（JSON 互換）。"""
        import json

        pm = PlayerModel.new_game()
        pm.items = [PlayerItem(id=0, qty=3), PlayerItem(id=1, qty=1)]
        snap = pm.to_snapshot(town_pos=(25, 6))

        # json.dumps が通ることで、ブラウザ側 LocalStorageSaveStore でも扱える
        serialized = json.dumps(snap)
        self.assertIn('"id": 0', serialized)
        self.assertIn('"qty": 3', serialized)


class FromSnapshotLegacyKeyTest(unittest.TestCase):
    """旧フォーマット（`def` → `defense` 変換 / `boss_defeated` → `glitch_lord_defeated`）との互換。"""

    def test_legacy_def_key_is_restored_to_defense_attr(self):
        snapshot = {
            "save_version": 1,
            "town_pos": [25, 6],
            "player": {
                "x": 25, "y": 6,
                "hp": 30, "max_hp": 30, "mp": 10, "max_mp": 10,
                "atk": 5, "def": 4, "agi": 3,
                "lv": 1, "exp": 0, "gold": 0,
                "weapon": 0, "armor": 0,
                "items": [],
                "poisoned": False,
                "in_dungeon": False,
                "glitch_lord_defeated": False,
            },
        }

        restored, _pos = PlayerModel.from_snapshot(snapshot)
        self.assertEqual(restored.defense, 4)

    def test_legacy_boss_defeated_key_maps_to_glitch_lord_defeated(self):
        snapshot = {
            "save_version": 1,
            "town_pos": [25, 6],
            "player": {
                "x": 25, "y": 6,
                "hp": 30, "max_hp": 30, "mp": 10, "max_mp": 10,
                "atk": 5, "def": 4, "agi": 3,
                "lv": 1, "exp": 0, "gold": 0,
                "weapon": 0, "armor": 0,
                "items": [],
                "poisoned": False,
                "in_dungeon": False,
                "boss_defeated": True,  # 旧キー
            },
        }

        restored, _pos = PlayerModel.from_snapshot(snapshot)
        self.assertTrue(restored.glitch_lord_defeated)


if __name__ == "__main__":
    unittest.main()
