"""CJG/shop: _try_purchase が gold / 所持判定 / inventory 更新を正しく行う。

根拠:
- docs/customer-journeys.md CJ 本番プレイ「買い物で進行する」
- docs/customer-jobs.md Job4（ゲームを楽しむ）
- steering/done/20260425-shop-keyerror-shop-list-unpack.md（shop の regression）

ShopScene._try_purchase は:
- 所持中の装備を再購入しない
- gold 不足を弾く
- 成功時は PlayerModel.gold を減らし weapon/armor/items を更新
- message に結果文字列を入れる

shop.enter は既存 test_cjg_shop_enter_regression.py で担保済み。本 note は
「購入処理のルール」を担当する。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.shop.scene import ShopScene
from src.shared.services.game_state import TownContext
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    current_town: TownContext | None = None
    last_town_pos: tuple[int, int] | None = None
    state: str = "shop"


def _new_shop(weapons_inventory=None, armors_inventory=None, items_inventory=None) -> tuple[ShopScene, _FakeGame]:
    game = _FakeGame(current_town=TownContext(index=0, pos=(25, 6)))
    scene = ShopScene(game=game)
    return scene, game


class WeaponPurchaseTest(unittest.TestCase):
    def test_successful_weapon_buy_deducts_gold_and_equips(self):
        from src import game_data

        scene, game = _new_shop()
        # 町 0 の weapons = [1, 2]
        scene.enter("weapons")
        # cursor=0 → idx=1（price 10）を狙う
        price = game_data.WEAPONS[scene.model.inventory[0]]["price"]
        before = game.player_model.gold

        scene._try_purchase()

        self.assertEqual(game.player_model.gold, before - price)
        self.assertEqual(game.player_model.weapon, scene.model.inventory[0])
        self.assertTrue(scene.model.message)

    def test_buying_already_equipped_weapon_is_rejected(self):
        scene, game = _new_shop()
        scene.enter("weapons")
        game.player_model.weapon = scene.model.inventory[0]
        before_gold = game.player_model.gold

        scene._try_purchase()

        self.assertEqual(game.player_model.gold, before_gold)
        self.assertIn("もっています", scene.model.message)

    def test_insufficient_gold_blocks_purchase(self):
        scene, game = _new_shop()
        scene.enter("weapons")
        game.player_model.gold = 0

        scene._try_purchase()

        self.assertEqual(game.player_model.gold, 0)
        self.assertEqual(game.player_model.weapon, 0)  # デフォルト
        self.assertIn("たりません", scene.model.message)


class ArmorPurchaseTest(unittest.TestCase):
    def test_successful_armor_buy_updates_armor_slot(self):
        from src import game_data

        scene, game = _new_shop()
        scene.enter("armors")
        idx = scene.model.inventory[0]
        price = game_data.ARMORS[idx]["price"]
        before = game.player_model.gold

        scene._try_purchase()

        self.assertEqual(game.player_model.gold, before - price)
        self.assertEqual(game.player_model.armor, idx)


class ItemPurchaseTest(unittest.TestCase):
    def test_buying_item_adds_to_inventory_list(self):
        scene, game = _new_shop()
        scene.enter("items")
        idx = scene.model.inventory[0]

        scene._try_purchase()

        found = [it for it in game.player_model.items if it.id == idx]
        self.assertEqual(len(found), 1)
        self.assertGreaterEqual(found[0].qty, 1)

    def test_buying_item_twice_increments_quantity_on_same_entry(self):
        scene, game = _new_shop()
        scene.enter("items")
        idx = scene.model.inventory[0]

        scene._try_purchase()
        qty_after_first = next(it.qty for it in game.player_model.items if it.id == idx)
        scene._try_purchase()
        qty_after_second = next(it.qty for it in game.player_model.items if it.id == idx)

        self.assertEqual(qty_after_second, qty_after_first + 1)


if __name__ == "__main__":
    unittest.main()
