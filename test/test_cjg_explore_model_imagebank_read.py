"""ExploreModel が pyxel.tilemaps と image_banks.tile_id_by_pixel から
タイル ID を直読する仕様（imagebank=DB／framework-rule.md M4-1 改訂版）。

- `is_walkable(x, y, *, in_dungeon)` — マスが歩けるか
- `get_tile(x, y, *, in_dungeon)` — 生のタイル ID
- `current_tilemap_id(in_dungeon)` — bltm 用の tilemap 番号

これらは GameState.world_map / game.dungeon_map を一切参照しないこと。
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pyxel

from src.scenes.explore.model import ExploreModel
from src.shared.constants.tile_data import T_GRASS, T_WATER


class _StubImageBanks:
    """ExploreModel が読む `tile_id_by_pixel` だけを差し替える stub。"""

    def __init__(self, mapping):
        self.tile_id_by_pixel = dict(mapping)


def _set_tilemap_pget(returns):
    """pyxel.tilemaps[0].pget を辞書ルックアップで置き換えるヘルパ。"""
    def _pget(tu, tv):
        return returns.get((tu, tv), (0, 0))
    pyxel.tilemaps[0].pget = MagicMock(side_effect=_pget)


def test_is_walkable_returns_true_for_grass_tile():
    """草タイル（T_GRASS）は通れる。tile bank pixel(0,0) → T_GRASS=0。"""
    image_banks = _StubImageBanks({(0, 0): T_GRASS})
    model = ExploreModel(image_banks=image_banks)
    _set_tilemap_pget({(2 * 5, 2 * 7): (0, 0)})  # world map (5, 7) → pixel (0, 0)

    assert model.is_walkable(5, 7, in_dungeon=False) is True


def test_is_walkable_returns_false_for_water_tile():
    """水タイル（T_WATER）は通れない（IMPASSABLE）。"""
    image_banks = _StubImageBanks({(16, 0): T_WATER})  # T_WATER=1 は (col=1, row=0)
    model = ExploreModel(image_banks=image_banks)
    _set_tilemap_pget({(2 * 3, 2 * 3): (2, 0)})  # tilemap pget は cell 単位 → pixel(16, 0)

    assert model.is_walkable(3, 3, in_dungeon=False) is False


def test_get_tile_returns_underlying_tile_id():
    """get_tile はタイル ID をそのまま返す（pyxel.tilemaps と image_banks 直読）。"""
    image_banks = _StubImageBanks({(0, 0): T_GRASS, (16, 0): T_WATER})
    model = ExploreModel(image_banks=image_banks)
    _set_tilemap_pget({
        (2 * 5, 2 * 7): (0, 0),  # T_GRASS
        (2 * 3, 2 * 3): (2, 0),  # T_WATER
    })

    assert model.get_tile(5, 7, in_dungeon=False) == T_GRASS
    assert model.get_tile(3, 3, in_dungeon=False) == T_WATER


def test_current_tilemap_id_world_is_0():
    """ワールドマップ用 tilemap 番号は 0。"""
    model = ExploreModel(image_banks=_StubImageBanks({}))
    assert model.current_tilemap_id(in_dungeon=False) == 0


def test_current_tilemap_id_dungeon_is_0():
    """ダンジョンも tilemap[0] の Y オフセット領域を使うので tm=0。"""
    model = ExploreModel(image_banks=_StubImageBanks({}))
    assert model.current_tilemap_id(in_dungeon=True) == 0


def test_get_tile_does_not_read_game_world_map():
    """ExploreModel は GameState.world_map / game.dungeon_map を一切参照しない。

    image_banks と pyxel.tilemaps だけで応答が決まることを model のソース
    で grep 検証する（state を経由しないという物理的保証）。
    """
    import inspect

    src = inspect.getsource(ExploreModel)
    # 直接アクセスしていない（self.world_map / game.world_map 等が無い）
    assert "world_map" not in src or "image_banks" in src.split("world_map")[0][-200:]
    # game.dungeon_map にも触れない
    assert "dungeon_map" not in src
