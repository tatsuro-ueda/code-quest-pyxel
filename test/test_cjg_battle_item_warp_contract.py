"""CJG/battle: 戦闘中の warp アイテム分岐が壊れない（Phase F）。

根拠:
- docs/product-requirements-battle.md（戦闘中にアイテムを使う）
- docs/customer-jobs.md Make3（crash で好循環が途絶）

battle/scene.py:195 の `if item_data["type"] == "warp"` で「せんとうちゅうは
つかえない」に分岐する。この branch が機能するためには:
1. ITEMS 辞書に "type" == "warp" のアイテムが少なくとも 1 つ存在する
2. warp 以外の heal / mp_heal / cure_poison は use_item service 経由で効果が出る
3. battle/scene.py に「せんとうちゅうはつかえない」の文字列が残っている

ITEMS の shape が壊れると `item_data["type"]` で KeyError、または分岐漏れで
warp 効果が戦闘中に走ってしまう（マップに強制ワープ）危険がある。
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data


class ItemsContractTest(unittest.TestCase):
    """ITEMS 生データが battle/menu の両方で触れる shape を満たす。"""

    _REQUIRED_KEYS = ("name", "type", "price")
    _KNOWN_TYPES = {"heal", "mp_heal", "cure_poison", "warp"}

    def test_every_item_has_required_keys(self):
        for idx, item in enumerate(game_data.ITEMS):
            with self.subTest(idx=idx, name=item.get("name")):
                for key in self._REQUIRED_KEYS:
                    self.assertIn(
                        key,
                        item,
                        f"ITEMS[{idx}] に {key} が無い。battle/menu 経路で KeyError になる",
                    )

    def test_every_item_type_is_recognized(self):
        """各 item の type は battle/menu/item_use が扱える種別のどれかに属する。"""
        for idx, item in enumerate(game_data.ITEMS):
            with self.subTest(idx=idx, name=item.get("name")):
                self.assertIn(
                    item["type"],
                    self._KNOWN_TYPES,
                    f"ITEMS[{idx}] の type `{item['type']}` は battle/menu/item_use で扱えない",
                )

    def test_at_least_one_warp_item_exists(self):
        """battle/scene.py:195 の warp 分岐を踏めるアイテムが必ず存在する。"""
        warp_items = [it for it in game_data.ITEMS if it.get("type") == "warp"]
        self.assertGreater(
            len(warp_items),
            0,
            "warp タイプのアイテムが 1 つも無い。battle の `せんとうちゅうはつかえない` 分岐が dead code になる",
        )


class BattleSceneWarpBranchExistsTest(unittest.TestCase):
    """battle/scene.py のソースに warp 拒否の文字列と分岐が残っていること。"""

    def test_battle_scene_contains_warp_refusal_message(self):
        path = ROOT / "src" / "scenes" / "battle" / "scene.py"
        text = path.read_text(encoding="utf-8")

        self.assertIn(
            "せんとうちゅうはつかえない",
            text,
            "戦闘中 warp 拒否メッセージが battle/scene.py から消えている",
        )

    def test_battle_scene_checks_item_type_warp(self):
        path = ROOT / "src" / "scenes" / "battle" / "scene.py"
        text = path.read_text(encoding="utf-8")

        self.assertRegex(
            text,
            r'item_data\[["\']type["\']\]\s*==\s*["\']warp["\']',
            "battle/scene.py で item_data['type'] == 'warp' の分岐が無い",
        )


if __name__ == "__main__":
    unittest.main()
