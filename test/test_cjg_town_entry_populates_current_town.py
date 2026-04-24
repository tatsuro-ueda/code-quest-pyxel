"""CJG/crash regression: マップ上で町タイルを踏むと current_town が populated される。

根拠:
- docs/customer-jobs.md Make3「ガードレール: クラッシュで好循環が途絶」
- docs/product-requirements-map.md（町遷移）
- steering/done/20260424-town-framework-rule-align.md（shop が town の内部状態を
  直接のぞき込む M4-1 違反 → GameState.current_town 経由に切り替え）

explore scene が T_TOWN タイルを処理すると次のすべてが成立しなければならない:
  - `game.current_town.index` がその座標の町インデックスと一致
  - `game.current_town.pos` が踏んだ座標と一致
  - `game.state == "town_menu"` に遷移
  - `game.town_model.menu_pos` / `menu_cursor` も同期されている（既存 town/model 互換）

この連携が壊れると shop.enter が町を見失い、KeyError や fallback 0 の町を開いて
まちがった inventory を出す。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.explore.scene import ExploreScene
from src.scenes.shop.scene import ShopScene
from src.scenes.town.model import TownModel
from src.shared.services.game_state import TownContext
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeGame:
    """explore / shop が共有で触る最小限の game 相当。"""

    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    town_model: TownModel = field(default_factory=TownModel)
    current_town: TownContext | None = None
    last_town_pos: tuple[int, int] | None = None
    state: str = "map"


class TownEntryPopulatesCurrentTownTest(unittest.TestCase):
    def _build_scene(self) -> tuple[ExploreScene, _FakeGame]:
        game = _FakeGame()
        scene = ExploreScene(game=game)
        return scene, game

    def test_town_tile_sets_current_town_index_and_pos(self):
        """TOWN_INDEX_BY_POS に登録された全ての町座標で current_town が正しくセットされる。"""
        from src.shared.constants.game_config import TOWN_INDEX_BY_POS
        from src.shared.constants.tile_data import T_TOWN

        for pos, expected_index in TOWN_INDEX_BY_POS.items():
            with self.subTest(pos=pos):
                scene, game = self._build_scene()

                scene._check_tile_events(T_TOWN, pos[0], pos[1])

                self.assertIsNotNone(game.current_town)
                self.assertEqual(game.current_town.index, expected_index)
                self.assertEqual(game.current_town.pos, pos)
                self.assertEqual(game.state, "town_menu")

    def test_town_tile_off_registered_position_falls_back_to_index_zero(self):
        """TOWN_INDEX_BY_POS にないタイルを踏んだら index=0 扱いになる（KeyError を出さない）。"""
        from src.shared.constants.tile_data import T_TOWN

        scene, game = self._build_scene()
        unregistered_pos = (99, 99)

        scene._check_tile_events(T_TOWN, *unregistered_pos)

        self.assertIsNotNone(game.current_town)
        self.assertEqual(game.current_town.index, 0)
        self.assertEqual(game.current_town.pos, unregistered_pos)

    def test_town_tile_also_populates_legacy_town_model_fields(self):
        """既存 town_model.menu_pos / menu_cursor も同期更新される。"""
        from src.shared.constants.game_config import TOWN_INDEX_BY_POS
        from src.shared.constants.tile_data import T_TOWN

        scene, game = self._build_scene()
        (pos, _), *_ = TOWN_INDEX_BY_POS.items()

        scene._check_tile_events(T_TOWN, pos[0], pos[1])

        self.assertEqual(game.town_model.menu_pos, pos)
        self.assertEqual(game.town_model.menu_cursor, 0)


class ShopReadsCurrentTownAfterEntryTest(unittest.TestCase):
    """town 入場 → shop 突入 の連携が KeyError を出さずに通る。"""

    def test_enter_town_then_enter_shop_uses_correct_town_index(self):
        from src import game_data
        from src.shared.constants.game_config import TOWN_INDEX_BY_POS
        from src.shared.constants.tile_data import T_TOWN

        for pos, expected_index in TOWN_INDEX_BY_POS.items():
            with self.subTest(pos=pos):
                game = _FakeGame()
                explore = ExploreScene(game=game)
                shop = ShopScene(game=game)

                explore._check_tile_events(T_TOWN, pos[0], pos[1])
                # town_menu 状態から shop に入ったことを模擬
                shop.enter("weapons")

                expected_inventory = list(
                    game_data.SHOP_LIST[expected_index]["weapons"]
                )
                self.assertEqual(shop.model.inventory, expected_inventory)
                self.assertEqual(game.last_town_pos, pos)
                self.assertEqual(game.state, "shop")


if __name__ == "__main__":
    unittest.main()
