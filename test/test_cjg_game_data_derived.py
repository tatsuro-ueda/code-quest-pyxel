"""CJG/game_data: ZONE_ENEMIES・ボス辞書・SPELL_BY_NAME・glitch_lord_phase。

根拠:
- docs/product-requirements-battle.md（ゾーン別エンカウント / ボス遷移）
- docs/product-requirements-narrative.md（呪文と経験値に関するダイアログキー）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

game_data.py は起動時に ENEMIES / SHOPS / SPELLS から派生データを組み立てる。
- ZONE_ENEMIES: ボスやイベント敵を除外したゾーン別エンカウント辞書
- GLITCH_LORD_DATA / PROFESSOR_DATA / GLITCH_CLONE_DATA / NOISE_GUARDIAN_DATA:
  各種イベント戦の敵（起動時に next(...) で 1 件決定）
- SPELL_BY_NAME: 呪文名 → データ
- glitch_lord_phase: ボス HP 比から phase1/2/3 を決定
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data


class ZoneEnemiesTest(unittest.TestCase):
    """ZONE_ENEMIES は通常エンカウント対象のみで構成される。"""

    def test_every_zone_has_at_least_one_encounter(self):
        """全ゾーン（0〜3）に少なくとも 1 種類の敵が登録されている。"""
        for zone in range(4):
            with self.subTest(zone=zone):
                self.assertIn(zone, game_data.ZONE_ENEMIES)
                self.assertGreater(len(game_data.ZONE_ENEMIES[zone]), 0)

    def test_zone_enemies_excludes_event_bosses(self):
        """ボス / 教授 / クローン / ノイズガーディアンは通常エンカウントに混ざらない。"""
        for zone, enemies in game_data.ZONE_ENEMIES.items():
            for enemy in enemies:
                with self.subTest(zone=zone, name=enemy.get("name")):
                    self.assertFalse(enemy.get("is_glitch_lord"))
                    self.assertFalse(enemy.get("is_professor"))
                    self.assertFalse(enemy.get("post_clear_only"))
                    self.assertFalse(enemy.get("is_noise_guardian"))


class BossDataSingletonsTest(unittest.TestCase):
    """起動時 next(...) で 1 件決定されるボス定義が実データと一致する。"""

    def test_glitch_lord_data_is_flagged_is_glitch_lord(self):
        self.assertTrue(game_data.GLITCH_LORD_DATA.get("is_glitch_lord"))

    def test_professor_data_is_flagged_is_professor(self):
        self.assertTrue(game_data.PROFESSOR_DATA.get("is_professor"))

    def test_glitch_clone_data_is_post_clear_only(self):
        self.assertTrue(game_data.GLITCH_CLONE_DATA.get("post_clear_only"))

    def test_noise_guardian_is_flagged_is_noise_guardian(self):
        self.assertTrue(game_data.NOISE_GUARDIAN_DATA.get("is_noise_guardian"))


class SpellByNameTest(unittest.TestCase):
    def test_lookup_matches_spells_entries(self):
        for spell in game_data.SPELLS:
            with self.subTest(name=spell["name"]):
                self.assertIs(game_data.SPELL_BY_NAME[spell["name"]], spell)

    def test_no_duplicate_spell_names(self):
        names = [s["name"] for s in game_data.SPELLS]
        self.assertEqual(len(names), len(set(names)))


class GlitchLordPhaseTest(unittest.TestCase):
    def test_above_60_percent_is_phase1(self):
        self.assertEqual(game_data.glitch_lord_phase(1.0), "phase1")
        self.assertEqual(game_data.glitch_lord_phase(0.61), "phase1")

    def test_between_30_and_60_is_phase2(self):
        self.assertEqual(game_data.glitch_lord_phase(0.6), "phase2")
        self.assertEqual(game_data.glitch_lord_phase(0.31), "phase2")

    def test_below_30_is_phase3(self):
        self.assertEqual(game_data.glitch_lord_phase(0.3), "phase3")
        self.assertEqual(game_data.glitch_lord_phase(0.0), "phase3")


class InnPricesAndShopListTest(unittest.TestCase):
    """INN_PRICES と SHOP_LIST の長さが一致し、TOWN_INDEX_BY_POS と揃う。"""

    def test_inn_prices_count_matches_shop_list_count(self):
        self.assertEqual(len(game_data.INN_PRICES), len(game_data.SHOP_LIST))

    def test_each_town_has_all_three_categories(self):
        for idx, shop in enumerate(game_data.SHOP_LIST):
            with self.subTest(idx=idx):
                for category in ("weapons", "armors", "items"):
                    self.assertIn(category, shop, f"town {idx} に {category} が無い")

    def test_town_count_matches_town_index_by_pos(self):
        from src.shared.constants.game_config import TOWN_INDEX_BY_POS

        self.assertEqual(len(game_data.SHOP_LIST), len(TOWN_INDEX_BY_POS))


if __name__ == "__main__":
    unittest.main()
