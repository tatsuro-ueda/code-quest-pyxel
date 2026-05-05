"""ImageBank / pyxel.tilemaps の test 仕込み helper（2026-05-05 SSoT 化対応）。

`game.world_map` / `game.dungeon_map` 撤去後、ExploreModel は
`pyxel.tilemaps[0].pget` と `image_banks.tile_id_by_pixel` を直読する。
test 側はその「DB 直読」が正しい値を返すようにスタブする必要があり、
複数 test で同じ仕込みコードが重複していたので 1 行 helper に集約する。

使い分け:
  - setUp/tearDown で pyxel.tilemaps を差し戻したい:
      install_fake_tilemap() → tearDown で restore_tilemaps(original)
  - regenerate_world_tilemap_fallback の pset 結果を assert したい:
      install_fake_tilemap() で得た FakeTilemap の .calls を見る
  - ExploreModel の DB 直読が特定のマスで指定 tile_id を返すように仕込みたい:
      stub_explore_tilemap_read(image_banks, tile_ids=..., default_tile_id=..., overrides=...)
"""
from __future__ import annotations

from typing import Iterable
from unittest.mock import MagicMock


DUNGEON_TM_OFFSET_Y = 110  # src.shared.services.image_banks.DUNGEON_TM_OFFSET_Y


class FakeTilemap:
    """pyxel.tilemaps[0] 互換の最小 stub。pset 値を dict に蓄積し pget で取り出す。"""

    def __init__(self) -> None:
        self.calls: dict[tuple[int, int], tuple[int, int]] = {}

    def pset(self, x: int, y: int, value: tuple[int, int]) -> None:
        self.calls[(x, y)] = value

    def pget(self, x: int, y: int) -> tuple[int, int]:
        return self.calls.get((x, y), (0, 0))


def install_fake_tilemap(slots: int = 8) -> FakeTilemap:
    """`image_banks` モジュールが束縛している `pyxel.tilemaps` を `FakeTilemap` 配列に差し替える。

    全 slot で同一 instance を共有する（slot 0 の書込みが他 slot からも見える）。
    setUp で `original = ib_module.pyxel.tilemaps; install_fake_tilemap()` の順で呼び、
    tearDown で `restore_tilemaps(original)` する用法を想定。
    """
    from src.shared.services import image_banks as ib_module
    tilemap = FakeTilemap()
    ib_module.pyxel.tilemaps = [tilemap for _ in range(slots)]
    return tilemap


def snapshot_tilemaps():
    """現在の `image_banks.pyxel.tilemaps` を返す（tearDown 用）。"""
    from src.shared.services import image_banks as ib_module
    return ib_module.pyxel.tilemaps


def restore_tilemaps(original) -> None:
    """`snapshot_tilemaps()` で取った値を戻す。"""
    from src.shared.services import image_banks as ib_module
    ib_module.pyxel.tilemaps = original


def stub_explore_tilemap_read(
    image_banks,
    *,
    tile_ids: Iterable,
    default_tile_id,
    overrides: dict[tuple[int, int], object] | None = None,
    dungeon_overrides: dict[tuple[int, int], object] | None = None,
    dungeon_offset: int = DUNGEON_TM_OFFSET_Y,
) -> None:
    """ExploreModel の DB 直読 (`pyxel.tilemaps[0].pget`) を stub する。

    Args:
        image_banks: 仕込み対象 ImageBanks インスタンス。`tile_bank` と
            `tile_id_by_pixel` がここに書き込まれる（既存値は破壊する）。
        tile_ids: ステージで使う全 tile id。pixel 座標 (idx*16, 0) を順に割り当てる。
        default_tile_id: 何も指定がないマスで pget が返す tile（背景）。
            tile_ids に含まれていなければ自動で先頭に追加。
        overrides: world マスの上書き `{(x, y): tile_id}`。
        dungeon_overrides: dungeon マスの上書き `{(x, y): tile_id}`。
            cell 座標は `(2x, dungeon_offset + 2y)` に展開される。
        dungeon_offset: dungeon 領域の Y 開始 cell 座標（`DUNGEON_TM_OFFSET_Y`）。

    効果:
        - `image_banks.tile_bank` / `image_banks.tile_id_by_pixel` を再構築
        - `pyxel.tilemaps[0].pget` を `MagicMock(side_effect=...)` に差し替え
    """
    import pyxel

    ordered = list(dict.fromkeys(tile_ids))  # dedup, keep order
    if default_tile_id not in ordered:
        ordered.insert(0, default_tile_id)

    image_banks.tile_bank = {}
    image_banks.tile_id_by_pixel = {}
    for idx, tid in enumerate(ordered):
        px = idx * 16
        image_banks.tile_bank[tid] = (px, 0)
        image_banks.tile_id_by_pixel[(px, 0)] = tid

    def _cell_of(tile_id) -> tuple[int, int]:
        px, py = image_banks.tile_bank[tile_id]
        return (px // 8, py // 8)

    default_cell = _cell_of(default_tile_id)
    sparse: dict[tuple[int, int], tuple[int, int]] = {}
    for (x, y), tid in (overrides or {}).items():
        sparse[(2 * x, 2 * y)] = _cell_of(tid)
    for (x, y), tid in (dungeon_overrides or {}).items():
        sparse[(2 * x, dungeon_offset + 2 * y)] = _cell_of(tid)

    def _pget(tu, tv):
        return sparse.get((tu, tv), default_cell)

    pyxel.tilemaps[0].pget = MagicMock(side_effect=_pget)
