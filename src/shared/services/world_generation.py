from __future__ import annotations

"""World map / dungeon 生成ロジック（Phase 1.5 以降で完全抽出予定）。

Phase 1 のスコープでは、main_runtime.py 内に以下が残っている：
- タイル ID 定数（T_GRASS, T_WATER, T_TREE, ...、line ~400）
- DECORATION_TILES
- PATH / SHORE ビットマップ定数（PATH_V, PATH_H, SHORE_N, ...、line ~712-1073）
- _PATH_VARIANTS, _SHORE_VARIANTS
- MAP_W, MAP_H, DUNGEON_W, DUNGEON_H
- CASTLE_POS, TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO, CAVE_GLITCH
- BIGTREE_POS, TOWER_POS
- _ZONE_DECORATIONS
- 生成関数群：get_path_variant, get_shore_variant, _make_empty,
  _carve_winding_path, _place_forests, _place_decorations, _place_landmarks,
  generate_world_map, generate_dungeon, get_zone

なぜここで抽出しないか：
- T_* や PATH_* / SHORE_* 定数は Game クラスの _tile_iter（タイル描画）でも使う
- ナイーブに `from src.runtime.main_runtime import T_*` すると循環 import
- 綺麗に分けるには neutral な `src/shared/constants/tiles.py` 的モジュールが必要で、
  それ自体が P1 の範囲外（Q5A の image_banks.py と同じ判断：深追いしない）

移行計画：
- Phase 1.5 で `src/shared/constants/tiles.py` を新設して T_* を移す
- その後に world_generation.py へ生成関数群を移す
- または P1-G13（image_banks 抽出）と併せて tile 周りを一括で整理する
"""

# NOTE: 実装はまだここに無い。main_runtime.py 内に残っている。
