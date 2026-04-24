"""CJG/crash regression: shop.enter が SHOPS dict vs SHOP_LIST 混同で KeyError を投げない。

根拠:
- docs/customer-jobs.md Make3「ガードレール: Buy3 の壊れた出力を子どもに届けない」
- steering/done/20260425-shop-keyerror-shop-list-unpack.md（2026-04-25 実機バグ）

shop.enter は町 index から M.SHOP_LIST[idx] を引いて inventory を埋める。
かつて `M.SHOPS[idx]` と書かれていて、SHOPS が dict 形状（`{'shops': [...], 'inn_prices': [...]}`）
のため KeyError: 0 で落ちていた。同じ穴を踏まないように固定化する。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.shop.scene import ShopScene
from src.shared.services.game_state import TownContext


@dataclass
class _FakeGame:
    """ShopScene.enter が触る最小限の game 相当。"""

    current_town: TownContext | None = None
    last_town_pos: tuple[int, int] | None = None
    state: str = "town_menu"


class ShopEnterRegressionTest(unittest.TestCase):
    def test_enter_weapons_with_current_town_loads_inventory_without_keyerror(self):
        """current_town が populated な状態で ShopScene.enter が落ちないこと。"""
        game = _FakeGame(
            current_town=TownContext(index=0, pos=(25, 6)),
        )
        scene = ShopScene(game=game)

        scene.enter("weapons")

        self.assertEqual(scene.model.kind, "weapons")
        self.assertIsInstance(scene.model.inventory, list)
        self.assertGreater(len(scene.model.inventory), 0)
        self.assertEqual(game.state, "shop")
        self.assertEqual(game.last_town_pos, (25, 6))

    def test_enter_armors_and_items_also_succeed(self):
        """weapons 以外の kind（armors / items）でも KeyError を出さないこと。"""
        for kind in ("armors", "items"):
            with self.subTest(kind=kind):
                game = _FakeGame(current_town=TownContext(index=0, pos=(25, 6)))
                scene = ShopScene(game=game)

                scene.enter(kind)

                self.assertEqual(scene.model.kind, kind)
                self.assertIsInstance(scene.model.inventory, list)

    def test_enter_falls_back_to_town_zero_when_current_town_is_none(self):
        """current_town=None でも index=0 扱いで入れる（フォールバック経路）。"""
        game = _FakeGame(current_town=None)
        scene = ShopScene(game=game)

        scene.enter("weapons")

        self.assertEqual(scene.model.kind, "weapons")
        self.assertIsInstance(scene.model.inventory, list)
        self.assertIsNone(game.last_town_pos)

    def test_enter_reads_index_from_current_town_for_second_and_third_towns(self):
        """2 つめ以降の町でも KeyError を出さず、各町固有の inventory が読めること。"""
        from src import game_data

        for idx in range(len(game_data.SHOP_LIST)):
            with self.subTest(town_index=idx):
                game = _FakeGame(current_town=TownContext(index=idx, pos=(0, 0)))
                scene = ShopScene(game=game)

                scene.enter("weapons")

                expected = list(game_data.SHOP_LIST[idx]["weapons"])
                self.assertEqual(scene.model.inventory, expected)


if __name__ == "__main__":
    unittest.main()
