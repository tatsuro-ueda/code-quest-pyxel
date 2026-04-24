"""CJG/crash regression: 町タイルに入ると GameState.current_town が populate される。

根拠:
- docs/customer-jobs.md Make3「ガードレール」
- steering/done/20260424-town-framework-rule-align.md（shop→town 受け渡し方式 (B) GameState）
- steering/done/20260425-shop-keyerror-shop-list-unpack.md

shop は town の内部を直接見ない（framework-rule.md M4-1 / M4-3）。
shop→town 間の橋渡しは `GameState.current_town: TownContext | None` 経由のみ。
このテストは「explore scene が T_TOWN タイルに入ったら current_town に index/pos を
書き込む」ことと、「その直後に shop.enter が index を読み出せる」ことを固定化する。
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
class _FakeMessages:
    shown: list[Any] = field(default_factory=list)

    def enter(self, lines, callback=None):
        self.shown.append(("enter", lines))

    def show(self, lines):
        self.shown.append(("show", lines))

    def dialog_lines(self, key, **kwargs):
        return [f"{key}"]


@dataclass
class _FakeGame:
    """_check_tile_events / ShopScene.enter が触る最小限の game 相当。"""

    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    town_model: TownModel = field(default_factory=TownModel)
    current_town: TownContext | None = None
    last_town_pos: tuple[int, int] | None = None
    state: str = "map"
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    # 以下は _check_tile_events が T_TOWN 以外の分岐で読むだけなので、
    # テストで踏まない分岐はデフォルト空でよい。
    world_return_x: int = 0
    world_return_y: int = 0
    dungeon_map: Any = None
    _cave_unblock_shown: bool = False


class TownEntrySetsCurrentTownTest(unittest.TestCase):
    def test_stepping_on_town_tile_populates_current_town(self):
        """T_TOWN タイルを踏むと game.current_town に index/pos が入ること。"""
        import src.runtime.main_runtime as M

        game = _FakeGame()
        scene = ExploreScene(game=game)

        # はじめのむら（TOWN_INDEX_BY_POS で 0）に相当する座標を 1 つ選ぶ
        first_town_pos = next(
            (pos for pos, idx in M.TOWN_INDEX_BY_POS.items() if idx == 0),
            None,
        )
        self.assertIsNotNone(first_town_pos, "TOWN_INDEX_BY_POS に index=0 の町が無い")

        scene._check_tile_events(M.T_TOWN, first_town_pos[0], first_town_pos[1])

        self.assertIsNotNone(game.current_town)
        self.assertEqual(game.current_town.pos, first_town_pos)
        self.assertEqual(game.current_town.index, 0)
        self.assertEqual(game.state, "town_menu")
        self.assertEqual(game.town_model.menu_pos, first_town_pos)
        self.assertEqual(game.town_model.menu_cursor, 0)

    def test_second_town_index_is_reflected(self):
        """2 つめの町（index=1）でも current_town の index が正しく入ること。"""
        import src.runtime.main_runtime as M

        game = _FakeGame()
        scene = ExploreScene(game=game)

        second_town_pos = next(
            (pos for pos, idx in M.TOWN_INDEX_BY_POS.items() if idx == 1),
            None,
        )
        self.assertIsNotNone(second_town_pos, "TOWN_INDEX_BY_POS に index=1 の町が無い")

        scene._check_tile_events(M.T_TOWN, second_town_pos[0], second_town_pos[1])

        self.assertEqual(game.current_town.index, 1)

    def test_shop_enter_reads_current_town_written_by_explore(self):
        """explore が current_town を書き、shop が読む連携が成立すること。"""
        import src.runtime.main_runtime as M

        game = _FakeGame()
        explore = ExploreScene(game=game)
        shop = ShopScene(game=game)

        # 1) 町タイルを踏んで current_town を populate
        first_town_pos = next(
            (pos for pos, idx in M.TOWN_INDEX_BY_POS.items() if idx == 0),
        )
        explore._check_tile_events(M.T_TOWN, first_town_pos[0], first_town_pos[1])

        # 2) shop がその index でインベントリを読めること
        shop.enter("weapons")

        self.assertIsInstance(shop.model.inventory, list)
        self.assertEqual(game.last_town_pos, first_town_pos)
        self.assertEqual(game.state, "shop")

    def test_unknown_town_pos_falls_back_to_index_zero(self):
        """TOWN_INDEX_BY_POS に登録されていない座標でも KeyError で落ちず index=0 に倒れる。"""
        import src.runtime.main_runtime as M

        game = _FakeGame()
        scene = ExploreScene(game=game)
        unknown_pos = (999, 999)

        scene._check_tile_events(M.T_TOWN, unknown_pos[0], unknown_pos[1])

        self.assertEqual(game.current_town.index, 0)
        self.assertEqual(game.current_town.pos, unknown_pos)


if __name__ == "__main__":
    unittest.main()
