"""CJG08/CJG10: 敵データ・戦闘の基本契約を固定化する。

根拠:
- docs/product-requirements-battle.md CJG08「敵が強すぎる」Rule: 数値を変えても戦闘の基本は壊れない
- docs/product-requirements-battle.md CJG10「新しい敵を追加したい」Rule: 敵データが戦闘に使える形を保つ

新しい敵を追加したり HP/ATK を調整したりするとき、「戦闘画面に必要な最低限のキーが
足りない / zone に振られていない / ダメージ計算が crash する」と子どもの楽しみが途切れる。
本ファイルは assets/enemies.yaml → src/generated/enemies.py の契約を壊さないための静的チェック。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REQUIRED_ENEMY_KEYS = {
    "name", "sprite", "hp", "atk", "def", "agi", "exp", "gold", "zone",
    "category", "spells",
}


class EnemyDataContractTest(unittest.TestCase):
    """敵 dict に戦闘が必要とするキーが全部そろっていること。"""

    def setUp(self):
        from src.generated.enemies import ENEMIES

        self.ENEMIES = ENEMIES

    def test_each_enemy_has_required_keys(self):
        """CJG10 Rule: 新しい敵は必要な情報をそろえて追加できる。"""
        for i, enemy in enumerate(self.ENEMIES):
            with self.subTest(index=i, name=enemy.get("name", "?")):
                missing = REQUIRED_ENEMY_KEYS - set(enemy.keys())
                self.assertEqual(
                    missing, set(),
                    f"enemies.yaml 由来の第 {i} 敵 '{enemy.get('name','?')}' に欠けているキー: {missing}",
                )

    def test_numeric_stats_are_non_negative_integers(self):
        """CJG08 Rule: 数値を変えても戦闘の基本は壊れない（負値・小数は crash 源）。"""
        for i, enemy in enumerate(self.ENEMIES):
            with self.subTest(index=i, name=enemy["name"]):
                for key in ("hp", "atk", "def", "agi", "exp", "gold"):
                    self.assertIsInstance(
                        enemy[key], int,
                        f"{enemy['name']}.{key} は int でなければならない（現在 {type(enemy[key]).__name__}）",
                    )
                    self.assertGreaterEqual(
                        enemy[key], 0,
                        f"{enemy['name']}.{key} は 0 以上でなければならない（現在 {enemy[key]}）",
                    )

    def test_hp_must_be_positive(self):
        """HP=0 の敵は生成即死で戦闘フロー不成立。"""
        for i, enemy in enumerate(self.ENEMIES):
            with self.subTest(index=i, name=enemy["name"]):
                self.assertGreater(
                    enemy["hp"], 0,
                    f"{enemy['name']} の HP が 0。戦闘開始即勝利で進行破綻",
                )

    def test_zone_is_valid_int(self):
        """CJG10 Rule: 敵は出したい場所にだけ出る。zone は 0 以上の整数。

        zone=0-4 はフィールド（ZONE_NAMES 登録済み）、5/6 は boss / professor 専用の
        非エンカウント zone を示す運用値。負値や未定義値が入ると KeyError の温床。
        """
        for i, enemy in enumerate(self.ENEMIES):
            with self.subTest(index=i, name=enemy["name"]):
                self.assertIsInstance(enemy["zone"], int)
                self.assertGreaterEqual(enemy["zone"], 0)
                self.assertLessEqual(
                    enemy["zone"], 9,
                    f"{enemy['name']}.zone={enemy['zone']} は運用範囲 (0-9) を逸脱",
                )

    def test_category_is_known(self):
        """category は戦闘 AI の分岐に使われる。未知値だと KeyError / 無差別挙動に落ちる。

        現状の assets/enemies.yaml には以下が使われている（2026-04-25 時点）:
        sequential / composite / condition / loop / variable / boss
        追加時はここに列挙する（未定義 category が入ると AI 分岐に落ち穴ができる）。
        """
        allowed = {"sequential", "composite", "condition", "loop", "variable", "boss"}
        for i, enemy in enumerate(self.ENEMIES):
            with self.subTest(index=i, name=enemy["name"]):
                self.assertIn(
                    enemy["category"], allowed,
                    f"{enemy['name']}.category={enemy['category']} は未知。"
                    f"許可: {sorted(allowed)}。追加する場合は本テストも更新する",
                )


class ZoneEnemiesMappingTest(unittest.TestCase):
    """ZONE_ENEMIES は各 zone から敵 index のリストを引く map。"""

    def test_all_encounter_zones_present_in_mapping(self):
        """ZONE_NAMES に登録されているフィールド zone（0-4）には必ず敵が紐付いている。"""
        from src import game_data
        from src.shared.constants.game_config import ZONE_NAMES

        for zone_id in ZONE_NAMES:
            with self.subTest(zone_id=zone_id):
                self.assertIn(
                    zone_id, game_data.ZONE_ENEMIES,
                    f"ZONE_ENEMIES に zone={zone_id} ({ZONE_NAMES[zone_id]}) のエントリが無い",
                )

    def test_each_encounter_zone_has_at_least_one_enemy(self):
        """エンカウント zone に 1 体も敵がいないとエンカウント時に crash するかフリーズ。"""
        from src import game_data
        from src.shared.constants.game_config import ZONE_NAMES

        for zone_id in ZONE_NAMES:
            with self.subTest(zone_id=zone_id, zone_name=ZONE_NAMES[zone_id]):
                self.assertGreater(
                    len(game_data.ZONE_ENEMIES[zone_id]), 0,
                    f"{ZONE_NAMES[zone_id]} に敵が 1 体も紐付いていない",
                )


if __name__ == "__main__":
    unittest.main()
