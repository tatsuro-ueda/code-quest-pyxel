"""CJG/town data: TOWN_MENU_LABELS / SHOP_KIND_BY_LABEL / TOWN_NPC_LINES の整合性。

根拠:
- docs/product-requirements-narrative.md（NPC 会話ラウンドロビン）
- docs/product-requirements-map.md（町メニュー / ショップ遷移）

TOWN_MENU_LABELS と TOWN_MENU_LABELS_EN は同じ長さ。SHOP_KIND_BY_LABEL は
「ぶきや/ぼうぐや/どうぐや」のすべてを含み、値は shop 側 kind と一致する。
TOWN_NPC_LINES は各町に複数セリフを持ち、TOWN_INDEX_BY_POS の町数と揃う。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.constants.game_config import (
    SHOP_KIND_BY_LABEL,
    TOWN_DIALOG_SCENES,
    TOWN_INDEX_BY_POS,
    TOWN_MENU_LABELS,
    TOWN_MENU_LABELS_EN,
    TOWN_NPC_LINES,
    ZONE_NAMES,
    ZONE_NAMES_EN,
)


class MenuLabelAlignmentTest(unittest.TestCase):
    def test_jp_and_en_menu_have_same_length(self):
        self.assertEqual(len(TOWN_MENU_LABELS), len(TOWN_MENU_LABELS_EN))

    def test_menu_contains_expected_labels(self):
        for label in ("はなす", "ぶきや", "ぼうぐや", "どうぐや", "やどや", "セーブ", "でる"):
            with self.subTest(label=label):
                self.assertIn(label, TOWN_MENU_LABELS)


class ShopKindMapTest(unittest.TestCase):
    def test_all_shop_labels_are_in_menu(self):
        for shop_label in SHOP_KIND_BY_LABEL.keys():
            with self.subTest(shop_label=shop_label):
                self.assertIn(shop_label, TOWN_MENU_LABELS)

    def test_all_shop_kinds_are_known(self):
        valid_kinds = {"weapons", "armors", "items"}
        for kind in SHOP_KIND_BY_LABEL.values():
            with self.subTest(kind=kind):
                self.assertIn(kind, valid_kinds)

    def test_three_shops_are_defined(self):
        self.assertEqual(len(SHOP_KIND_BY_LABEL), 3)


class TownNpcLinesTest(unittest.TestCase):
    def test_npc_lines_count_matches_town_count(self):
        self.assertEqual(len(TOWN_NPC_LINES), len(TOWN_INDEX_BY_POS))

    def test_every_town_has_at_least_one_line(self):
        for idx, lines in enumerate(TOWN_NPC_LINES):
            with self.subTest(town_index=idx):
                self.assertGreater(len(lines), 0)
                for line in lines:
                    self.assertIsInstance(line, str)
                    self.assertTrue(line.strip())


class ZoneNamesAlignmentTest(unittest.TestCase):
    def test_jp_and_en_zone_names_have_same_keys(self):
        self.assertEqual(set(ZONE_NAMES.keys()), set(ZONE_NAMES_EN.keys()))

    def test_zone_names_cover_0_to_4(self):
        for zone in range(5):
            with self.subTest(zone=zone):
                self.assertIn(zone, ZONE_NAMES)
                self.assertIn(zone, ZONE_NAMES_EN)


class TownDialogScenesTest(unittest.TestCase):
    def test_castle_scene_is_defined(self):
        self.assertIn((25, 6), TOWN_DIALOG_SCENES)

    def test_all_keys_are_tuples_of_two_ints(self):
        for key in TOWN_DIALOG_SCENES.keys():
            with self.subTest(key=key):
                self.assertIsInstance(key, tuple)
                self.assertEqual(len(key), 2)
                self.assertIsInstance(key[0], int)
                self.assertIsInstance(key[1], int)


if __name__ == "__main__":
    unittest.main()
