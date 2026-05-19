"""World map / dungeon 生成ロジック（Phase 1.5 実装）。

このファイルに含まれる関数・クラス：

- get_path_variant: PATH タイルの auto-tile variant を 4 近傍から選ぶ
- get_shore_variant: WATER タイルの shore variant を 4 近傍から選ぶ
- get_zone: ワールド Y 座標と dungeon フラグからゾーン ID を返す
- generate_world_map: 固定 seed の疑似乱数で 50x50 world grid を返す
- generate_dungeon: 固定 seed の疑似乱数で dungeon grid と rooms を返す
- _is_world_path: world_map[y][x] が PATH か（範囲外は False）
- _is_world_land: world_map[y][x] が非 WATER か（範囲外は False）
- _is_in_grid: (x, y) が grid の有効範囲かを返す
- _get_grid_dimensions: grid の (width, height) を返す
- _compute_path_neighbors: PATH variant 判定用の (N,E,S,W) を返す
- _compute_shore_neighbors: SHORE variant 判定用の (N,E,S,W) を返す
- _has_any_neighbor: 近傍タプルに True が 1 つ以上あるかを返す
- _pick_path_variant: 近傍タプルから PATH variant を選ぶ
- _get_fallback_path_variant: 辞書未登録時の PATH fallback variant を返す
- _has_vertical_neighbor: 縦方向に PATH があるかを返す
- _has_horizontal_neighbor: 横方向に PATH があるかを返す
- _pick_shore_variant: 近傍タプルから SHORE variant を選ぶ
- _get_fallback_shore_variant: 辞書未登録時の SHORE fallback variant を返す
- _is_dungeon_flag: get_zone の in_dungeon を bool に正規化する
- _compute_zone: get_zone の本体（dungeon を優先し world は y で分岐）
- _zone_for_y: world Y 座標を 0-3 のゾーン ID に写す純粋関数
- _make_empty: 全マスが fill な w x h grid を作る
- _carve_winding_path: 始点から終点へ蛇行する PATH を彫る
- _is_at_destination: 現在位置が終点と一致するかの述語
- _can_zigzag: PATH 彫り進みでジグザグするかの述語
- _is_zigzag_eligible: roll と座標からジグザグ条件成立かを返す
- _is_offset_in_both_axes: X/Y どちらも終点と異なるかを返す
- _step_toward: PATH 彫り進みの 1 ステップ移動座標を返す
- _step_random_axis: ランダムに X か Y で 1 マス進める
- _step_longer_axis: 残距離が長い方の軸で 1 マス進める
- _sign_toward: target へ近づく 1 マスの符号を返す
- _place_forests: ゾーンごとの密度で GRASS を TREE へ置換
- _grow_tree_if_eligible: 1 マス GRASS を密度判定して TREE に置換
- _zone_forest_density: ゾーン別の TREE 密度を返す純粋関数
- _is_y_outside_forest: 森を生やさない上下端 y かを返す
- _place_decorations: ゾーン別装飾タイルを密度ブースト付きで配置
- _collect_structure_neighborhood: 拠点周辺マスの set を返す
- _collect_path_neighborhood: PATH 沿いマスの set を返す
- _add_3x3_neighborhood: set に 3x3 マスを追加する
- _decorate_row: 1 行ぶんの装飾タイル配置を行う
- _decorate_cell: 1 セルぶんの装飾タイル配置を行う
- _pick_deco_density: (x, y) の装飾配置密度を返す
- _place_landmarks: 2x2 マルチタイルランドマークを配置
- _install_bigtree: 世界樹 4 マスを配置
- _install_tower: 通信塔 4 マスを配置
- _clear_landmark_surroundings: ランドマーク周辺の通行不可を除去
- _clear_obstacles_around: 1 ランドマーク周辺の 4x4 障害物を除去
- _replace_obstacle_with_grass: 1 マスの TREE/MOUNTAIN を GRASS に置換
- _build_world_base_grid: 海・山・橋・砂の地形ベースを敷く
- _carve_world_water_border: 周縁 3 マスを WATER で囲う
- _is_world_border: (x, y) が WATER 縁かを返す
- _is_y_at_world_edge: Y が上下縁かを返す
- _is_x_at_world_edge: X が左右縁かを返す
- _carve_world_mountain_pass: 中央山脈と峠を彫る
- _carve_world_bridge_river: 中央河川と橋を敷く
- _convert_south_to_sand: 南端 10 行を SAND に置換
- _place_world_structures: 城・町・洞窟を配置
- _get_world_passable_for_road: 道彫りで上書き可能なタイル set を返す
- _carve_world_road_network: 拠点間を蛇行 PATH でつなぐ
- _get_world_structure_positions: 拠点位置リストを返す
- _open_structure_walkable_ring: 拠点周辺の障害物を除去
- _open_one_structure_ring: 1 拠点周辺 8 マスから障害物を除去
- _clear_ring_cell: 周辺 1 マスを条件に応じて GRASS に置換
- _is_center_cell: オフセットが中心 (0, 0) かを返す
- _refresh_structure_centers: 城・町・洞窟の中心タイルを再敷設
- _build_dungeon_rooms: 重複しない部屋を最大 6 つ取得
- _is_dungeon_room_overlapping: 既存 rooms と矩形が重なるか
- _is_rect_overlap: 2 矩形が 1 マスマージン付きで重なるか
- _is_x_axis_overlap: X 軸での重なりを返す
- _is_y_axis_overlap: Y 軸での重なりを返す
- _paint_dungeon_room: 1 部屋を FLOOR で塗る
- _carve_dungeon_corridors: 隣接 room 間に L 字 corridor を彫る
- _carve_corridor_between: 2 部屋を L 字で結ぶ
- _room_center: room の中心座標を返す
- _carve_horizontal_corridor: 水平 corridor を彫る
- _carve_vertical_corridor: 垂直 corridor を彫る
- _place_dungeon_stairs_and_boss: 階段とボストリガーを配置
- _resolve_boss_position: 階段と同じマスを避けたボス座標を返す
- _is_same_cell: 2 つのセル座標が一致するかを返す

Problems:
    - PATH/SHORE variant 選択や world/dungeon 生成は分岐とループが密に
      組み合わさり、public 関数に直書きすると CR203/CR204 が止まらず
      入口契約と乱数副作用が同じスコープに混じる。
    - 装飾・ランドマーク配置・部屋生成のような長い手順を 1 関数に書くと
      CR202（20 行超）と CR302/CR303（複合条件）が連発し、AI でも人でも
      レビュー観点を分けにくい。
    - sprite_data の wildcard 再 import や未使用 tile id を残すと F401/F403
      が出続け、flake8-cr 0 件を維持できない。

Solutions:
    - public 関数（get_path_variant / get_shore_variant / get_zone /
      generate_world_map / generate_dungeon）はいずれも「述語 + private
      委譲 + return」のステップ列に揃え、判定と書き換えは private helper に
      閉じ込める。
    - 20 行超の private helper は責務単位（近傍計算・密度決定・行内配置・
      ランドマーク 1 棟）に分割し、乱数呼び出し順は元のループ順を維持する。
    - 未使用 tile id と sprite_data wildcard import を撤去し、必要な定数のみ
      tile_data から明示 import する。
"""

from __future__ import annotations

import random

from src.shared.constants.tile_data import (
    # タイル ID
    T_GRASS, T_WATER, T_TREE, T_SAND, T_FLOOR, T_WALL, T_CASTLE, T_TOWN,
    T_CAVE, T_MOUNTAIN, T_BRIDGE, T_PATH, T_STAIR_UP,
    T_BIGTREE_TL, T_BIGTREE_TR, T_BIGTREE_BL, T_BIGTREE_BR,
    T_TOWER_TL, T_TOWER_TR, T_TOWER_BL, T_TOWER_BR,
    T_GLITCH_LORD_TRIGGER,
    # PATH / SHORE variants
    PATH_V, PATH_H,
    SHORE_N, SHORE_S, SHORE_W, SHORE_E,
    # マップサイズ
    MAP_W, MAP_H, DUNGEON_W, DUNGEON_H,
    # 位置定数
    CASTLE_POS, TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO, CAVE_GLITCH,
    BIGTREE_POS, TOWER_POS,
    DECORATION_TILES,
)
from src.shared.constants.tile_data import (
    _PATH_VARIANTS, _SHORE_VARIANTS, _ZONE_DECORATIONS,
)


# === Public API ===


def get_path_variant(world_map, mx, my):
    """PATH タイルの auto-tile variant を 4 近傍から選ぶ。

    Args:
        world_map: 2D タイル ID grid。
        mx: PATH タイルの X 座標。
        my: PATH タイルの Y 座標。
    Returns:
        変種定数（PATH_V 等）。
    Policy:
        - 4 近傍判定は ``_compute_path_neighbors`` に委譲する。
        - variant 選択は ``_pick_path_variant`` に委譲し、本体は委譲のみ。
    """
    neighbors = _compute_path_neighbors(world_map, mx, my)
    return _pick_path_variant(neighbors)


def get_shore_variant(world_map, mx, my):
    """WATER タイルの shore variant を 4 近傍から選ぶ。

    Args:
        world_map: 2D タイル ID grid。
        mx: WATER タイルの X 座標。
        my: WATER タイルの Y 座標。
    Returns:
        変種定数 / None（陸地が一つもない場合）。
    Policy:
        - 4 近傍判定は ``_compute_shore_neighbors`` に委譲する。
        - variant 選択は ``_pick_shore_variant`` に委譲し、本体は委譲のみ。
    """
    neighbors = _compute_shore_neighbors(world_map, mx, my)
    return _pick_shore_variant(neighbors)


def get_zone(tile_y, in_dungeon=False):
    """world Y 座標と dungeon フラグからゾーン ID を返す。

    Args:
        tile_y: ワールド側 Y 座標。
        in_dungeon: dungeon シーンなら True。
    Returns:
        int: 0-3 が world ゾーン、4 が dungeon。
    Policy:
        - 判定は ``_compute_zone`` に委譲し、本体は委譲のみ。
    """
    return _compute_zone(tile_y, in_dungeon)


def generate_world_map(seed=42):
    """固定 seed の疑似乱数で 50x50 world grid を返す。

    Args:
        seed: random.Random に渡す seed（既定 42）。
    Returns:
        2D list[list[int]]。
    Policy:
        - ベース地形 -> 森 -> 拠点 -> 道 -> 拠点周辺の開放 -> 拠点再敷設 ->
          装飾 -> ランドマークの順を維持し、乱数呼び出し順を変えない。
        - 個別の手続きは ``_build_world_base_grid`` 以下の private helper に
          委譲する。
    """
    rng = random.Random(seed)
    grid = _build_world_base_grid()
    _place_forests(grid, rng)
    _place_world_structures(grid)
    _carve_world_road_network(grid, rng)
    _open_structure_walkable_ring(grid)
    _refresh_structure_centers(grid)
    _place_decorations(grid, rng, _get_world_structure_positions())
    _place_landmarks(grid)
    return grid


def generate_dungeon(seed=99):
    """固定 seed の疑似乱数で dungeon grid と rooms を返す。

    Args:
        seed: random.Random に渡す seed（既定 99）。
    Returns:
        tuple[list[list[int]], list[tuple[int, int, int, int]]]。
    Policy:
        - 部屋生成 -> corridor 接続 -> 階段とボストリガー配置の順で、
          乱数呼び出し順を ``_build_dungeon_rooms`` 内に閉じ込める。
    """
    rng = random.Random(seed)
    grid = _make_empty(DUNGEON_W, DUNGEON_H, T_WALL)
    rooms = _build_dungeon_rooms(grid, rng)
    _carve_dungeon_corridors(grid, rooms)
    _place_dungeon_stairs_and_boss(grid, rooms)
    return grid, rooms


# === Internal helpers (private) ===


def _is_world_path(world_map, x, y, width, height):
    """world_map[y][x] が PATH かを返す（範囲外は False）。

    Args:
        world_map: 2D タイル ID grid。
        x: X 座標。
        y: Y 座標。
        width: grid の横幅。
        height: grid の縦幅。
    Returns:
        bool。
    Policy:
        - 範囲外は False で打ち切る（呼び出し側を簡素化）。
    """
    if not _is_in_grid(x, y, width, height):
        return False
    return world_map[y][x] == T_PATH


def _is_world_land(world_map, x, y, width, height):
    """world_map[y][x] が非 WATER（陸地）かを返す（範囲外は False）。

    Args:
        world_map: 2D タイル ID grid。
        x: X 座標。
        y: Y 座標。
        width: grid の横幅。
        height: grid の縦幅。
    Returns:
        bool。
    Policy:
        - 範囲外は陸地ではないとみなし False を返す。
    """
    if not _is_in_grid(x, y, width, height):
        return False
    return world_map[y][x] != T_WATER


def _is_in_grid(x, y, width, height):
    """(x, y) が grid の有効範囲かを返す。

    Args:
        x: X 座標。
        y: Y 座標。
        width: grid 横幅。
        height: grid 縦幅。
    Returns:
        bool。
    Policy:
        - 0 <= x < width かつ 0 <= y < height のときだけ True。
    """
    return 0 <= x < width and 0 <= y < height


def _get_grid_dimensions(grid):
    """grid の (width, height) を返す。

    Args:
        grid: 2D list。
    Returns:
        tuple[int, int]: (width, height)。
    Policy:
        - 空 grid は (0, 0) を返す。
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    return width, height


def _compute_path_neighbors(world_map, mx, my):
    """PATH variant 判定用の (N, E, S, W) bool タプルを返す。

    Args:
        world_map: 2D タイル ID grid。
        mx: 注目タイル X。
        my: 注目タイル Y。
    Returns:
        tuple[bool, bool, bool, bool]。
    Policy:
        - 各方向で ``_is_world_path`` を呼ぶだけの薄い委譲。
    """
    width, height = _get_grid_dimensions(world_map)
    north = _is_world_path(world_map, mx, my - 1, width, height)
    east = _is_world_path(world_map, mx + 1, my, width, height)
    south = _is_world_path(world_map, mx, my + 1, width, height)
    west = _is_world_path(world_map, mx - 1, my, width, height)
    return (north, east, south, west)


def _compute_shore_neighbors(world_map, mx, my):
    """SHORE variant 判定用の (N, E, S, W) bool タプルを返す。

    Args:
        world_map: 2D タイル ID grid。
        mx: 注目タイル X。
        my: 注目タイル Y。
    Returns:
        tuple[bool, bool, bool, bool]。
    Policy:
        - 各方向で ``_is_world_land`` を呼ぶだけの薄い委譲。
    """
    width, height = _get_grid_dimensions(world_map)
    north = _is_world_land(world_map, mx, my - 1, width, height)
    east = _is_world_land(world_map, mx + 1, my, width, height)
    south = _is_world_land(world_map, mx, my + 1, width, height)
    west = _is_world_land(world_map, mx - 1, my, width, height)
    return (north, east, south, west)


def _has_any_neighbor(neighbors):
    """近傍タプルに 1 つでも True が含まれるかを返す。

    Args:
        neighbors: (N, E, S, W) bool タプル。
    Returns:
        bool。
    Policy:
        - any() の薄いラッパで CR302/CR303 を回避する。
    """
    return any(neighbors)


def _pick_path_variant(neighbors):
    """近傍タプルから PATH variant を選ぶ。

    Args:
        neighbors: (N, E, S, W) bool タプル。
    Returns:
        PATH variant 定数。
    Policy:
        - まず辞書から完全一致を引き、無ければ縦/横の優先で fallback。
    """
    variant = _PATH_VARIANTS.get(neighbors)
    if variant:
        return variant
    return _get_fallback_path_variant(neighbors)


def _get_fallback_path_variant(neighbors):
    """辞書未登録の場合の PATH fallback variant を返す。

    Args:
        neighbors: (N, E, S, W) bool タプル。
    Returns:
        PATH_V / PATH_H のいずれか。
    Policy:
        - 縦方向の近傍があれば PATH_V、横方向のみなら PATH_H、
          どちらも無ければ PATH_V を返す。
    """
    north, east, south, west = neighbors
    if _has_vertical_neighbor(north, south):
        return PATH_V
    if _has_horizontal_neighbor(east, west):
        return PATH_H
    return PATH_V


def _has_vertical_neighbor(north, south):
    """縦方向に PATH があるかを返す。

    Args:
        north: 北側 bool。
        south: 南側 bool。
    Returns:
        bool。
    Policy:
        - or を 1 箇所に閉じ込めて CR303 を回避する。
    """
    return north or south


def _has_horizontal_neighbor(east, west):
    """横方向に PATH があるかを返す。

    Args:
        east: 東側 bool。
        west: 西側 bool。
    Returns:
        bool。
    Policy:
        - or を 1 箇所に閉じ込めて CR303 を回避する。
    """
    return east or west


def _pick_shore_variant(neighbors):
    """近傍タプルから SHORE variant を選ぶ。

    Args:
        neighbors: (N, E, S, W) bool タプル。
    Returns:
        SHORE variant 定数 / None。
    Policy:
        - 陸地が無ければ None。辞書一致を優先し、無ければ 4 方向順で fallback。
    """
    if not _has_any_neighbor(neighbors):
        return None
    variant = _SHORE_VARIANTS.get(neighbors)
    if variant:
        return variant
    return _get_fallback_shore_variant(neighbors)


def _get_fallback_shore_variant(neighbors):
    """辞書未登録の場合の SHORE fallback variant を返す。

    Args:
        neighbors: (N, E, S, W) bool タプル。
    Returns:
        SHORE_N / S / W / E のいずれか、無ければ None。
    Policy:
        - N -> S -> W -> E の優先順で最初に True の方向を採用する。
    """
    north, east, south, west = neighbors
    if north:
        return SHORE_N
    if south:
        return SHORE_S
    if west:
        return SHORE_W
    if east:
        return SHORE_E
    return None


def _is_dungeon_flag(in_dungeon):
    """get_zone に渡された in_dungeon フラグを truthy 述語化する。

    Args:
        in_dungeon: 任意のオブジェクト。
    Returns:
        bool。
    Policy:
        - bool 化のみ。``_compute_zone`` のガード成立用。
    """
    return bool(in_dungeon)


def _compute_zone(tile_y, in_dungeon):
    """get_zone の本体ロジック。dungeon フラグを最優先、その後 Y 判定。

    Args:
        tile_y: world Y 座標。
        in_dungeon: dungeon フラグ。
    Returns:
        int。
    Policy:
        - dungeon なら 4、そうでなければ ``_zone_for_y`` の結果を返す。
    """
    if _is_dungeon_flag(in_dungeon):
        return 4
    return _zone_for_y(tile_y)


def _zone_for_y(tile_y):
    """world Y 座標を 0-3 のゾーン ID に写す純粋関数。

    Args:
        tile_y: world Y。
    Returns:
        int。
    Policy:
        - 境界値 16/28/38 で 0/1/2/3 を返す。
    """
    if tile_y < 16:
        return 0
    if tile_y < 28:
        return 1
    if tile_y < 38:
        return 2
    return 3


def _make_empty(w, h, fill):
    """全マスが ``fill`` な w x h grid を返す。

    Args:
        w: 横幅。
        h: 縦幅。
        fill: 初期値タイル ID。
    Returns:
        2D list。
    Policy:
        - リスト内包を 1 行だけ書く薄いヘルパ。
    """
    return [[fill] * w for _ in range(h)]


def _carve_winding_path(grid, x1, y1, x2, y2, rng, passable=None):
    """始点 (x1, y1) から終点 (x2, y2) へ蛇行する PATH を彫る。

    Args:
        grid: 2D タイル ID grid。
        x1: 始点 X。
        y1: 始点 Y。
        x2: 終点 X。
        y2: 終点 Y。
        rng: random.Random（疑似乱数）。
        passable: 上書き可能なタイル ID set。None なら {GRASS, SAND}。
    Policy:
        - max_iter で打ち切り、各ステップで X/Y のいずれかを 1 マス進める。
        - 乱数呼び出し順を保ったまま判定を private helper に切り出す。
    """
    if passable is None:
        passable = {T_GRASS, T_SAND}
    cx, cy = x1, y1
    max_iter = (abs(x2 - x1) + abs(y2 - y1)) * 4 + 50
    for _ in range(max_iter):
        if _is_at_destination(cx, cy, x2, y2):
            break
        cx, cy = _step_toward(cx, cy, x2, y2, rng)
        cx = max(1, min(MAP_W - 2, cx))
        cy = max(1, min(MAP_H - 2, cy))
        if grid[cy][cx] in passable:
            grid[cy][cx] = T_PATH


def _is_at_destination(cx, cy, x2, y2):
    """現在位置が終点と一致するかを返す。

    Args:
        cx: 現在 X。
        cy: 現在 Y。
        x2: 終点 X。
        y2: 終点 Y。
    Returns:
        bool。
    Policy:
        - and を 1 箇所に閉じ込めて CR303 を回避する。
    """
    return cx == x2 and cy == y2


def _can_zigzag(rng, cx, cy, x2, y2):
    """PATH 彫り進みでジグザグするかの述語。

    Args:
        rng: random.Random。
        cx: 現在 X。
        cy: 現在 Y。
        x2: 終点 X。
        y2: 終点 Y。
    Returns:
        bool。
    Policy:
        - 30% の確率で、なおかつ X/Y どちらも終点と異なる場合のみジグザグ。
        - 乱数を 1 回消費する（順序保存のために必ず呼ぶ）。
    """
    roll = rng.random()
    return _is_zigzag_eligible(roll, cx, cy, x2, y2)


def _is_zigzag_eligible(roll, cx, cy, x2, y2):
    """roll と現在/終点座標からジグザグ条件を満たすかを返す。

    Args:
        roll: rng.random() の戻り値。
        cx: 現在 X。
        cy: 現在 Y。
        x2: 終点 X。
        y2: 終点 Y。
    Returns:
        bool。
    Policy:
        - 30% の確率かつ X/Y がいずれも終点と異なるときのみ True。
    """
    if roll >= 0.3:
        return False
    return _is_offset_in_both_axes(cx, cy, x2, y2)


def _is_offset_in_both_axes(cx, cy, x2, y2):
    """現在位置が終点と X/Y どちらも異なるかを返す。

    Args:
        cx: 現在 X。
        cy: 現在 Y。
        x2: 終点 X。
        y2: 終点 Y。
    Returns:
        bool。
    Policy:
        - and を 1 箇所に閉じ込めて CR303 を回避する。
    """
    return cx != x2 and cy != y2


def _step_toward(cx, cy, x2, y2, rng):
    """PATH 彫り進みの 1 ステップ分の (cx, cy) を返す。

    Args:
        cx: 現在 X。
        cy: 現在 Y。
        x2: 終点 X。
        y2: 終点 Y。
        rng: random.Random。
    Returns:
        tuple[int, int]: 進めた後の (cx, cy)。
    Policy:
        - まず ``_can_zigzag`` で乱数を消費し、True ならランダム軸で 1 マス、
          False なら距離の長い軸で 1 マス進める。
        - 元実装の乱数呼び出し順（random() → ジグザグなら random()）を保つ。
    """
    if _can_zigzag(rng, cx, cy, x2, y2):
        return _step_random_axis(cx, cy, x2, y2, rng)
    return _step_longer_axis(cx, cy, x2, y2)


def _step_random_axis(cx, cy, x2, y2, rng):
    """ランダムに X か Y のどちらか 1 軸で 1 マス進める。

    Args:
        cx: 現在 X。
        cy: 現在 Y。
        x2: 終点 X。
        y2: 終点 Y。
        rng: random.Random。
    Returns:
        tuple[int, int]: 進めた後の (cx, cy)。
    Policy:
        - 50% で X、50% で Y を選ぶ。乱数を 1 回消費する。
    """
    if rng.random() < 0.5:
        cx += _sign_toward(cx, x2)
    else:
        cy += _sign_toward(cy, y2)
    return cx, cy


def _step_longer_axis(cx, cy, x2, y2):
    """X/Y のうち残距離が長い方を 1 マス進める。

    Args:
        cx: 現在 X。
        cy: 現在 Y。
        x2: 終点 X。
        y2: 終点 Y。
    Returns:
        tuple[int, int]: 進めた後の (cx, cy)。
    Policy:
        - 同距離なら Y を進める（元実装の `>` 比較を維持）。
    """
    if abs(x2 - cx) > abs(y2 - cy):
        cx += _sign_toward(cx, x2)
    else:
        cy += _sign_toward(cy, y2)
    return cx, cy


def _sign_toward(current, target):
    """current から target へ近づく 1 マスの符号 (+1 / -1) を返す。

    Args:
        current: 現在座標。
        target: 目標座標。
    Returns:
        int: +1 または -1。
    Policy:
        - target == current のときは +1 を返す（元実装と同じ）。
    """
    if target > current:
        return 1
    return -1


def _place_forests(grid, rng):
    """ゾーンごとの密度で GRASS を TREE へ置換する。

    Args:
        grid: 2D タイル ID grid。
        rng: random.Random。
    Policy:
        - 行ごとに ``_zone_forest_density`` で密度を決め、GRASS マスにだけ
          rng.random() を撒いて TREE へ置換する。
        - 乱数呼び出し順（行 y 内で x 昇順）を維持する。
    """
    for y in range(MAP_H):
        density_val = _zone_forest_density(y)
        for x in range(MAP_W):
            _grow_tree_if_eligible(grid, x, y, rng, density_val)


def _grow_tree_if_eligible(grid, x, y, rng, density_val):
    """grid[y][x] が GRASS で密度判定に当たれば TREE に置換する。

    Args:
        grid: 2D タイル ID grid。
        x: 列 X。
        y: 行 Y。
        rng: random.Random。
        density_val: 当該行の密度（float）。
    Policy:
        - 短絡評価を維持：GRASS 以外なら rng.random() を呼ばない。
        - 元実装と同じ「条件 -> 上書き」の単一ステップを保つ。
    """
    if grid[y][x] != T_GRASS:
        return
    if rng.random() >= density_val:
        return
    grid[y][x] = T_TREE


def _zone_forest_density(y):
    """ゾーン別の TREE 密度を返す純粋関数。

    Args:
        y: world Y 座標。
    Returns:
        float。
    Policy:
        - 上下端は 0.0、ゾーン 0/1/2/3 で 0.08/0.18/0.30/0.05。
    """
    if _is_y_outside_forest(y):
        return 0.0
    if y < 16:
        return 0.08
    if y < 28:
        return 0.18
    if y < 38:
        return 0.30
    return 0.05


def _is_y_outside_forest(y):
    """森を生やさない上下端 y かを返す。

    Args:
        y: world Y。
    Returns:
        bool。
    Policy:
        - y < 3 または y >= 47 のとき True。
    """
    if y < 3:
        return True
    return y >= 47


def _place_decorations(grid, rng, structures):
    """ゾーン別の装飾タイルを密度ブースト付きで配置する。

    Args:
        grid: 2D タイル ID grid。
        rng: random.Random。
        structures: 拠点位置リスト。
    Policy:
        - 近傍 set 構築 -> 行ごとの装飾配置の 2 段で、乱数呼び出し順
          （行 y 内で x 昇順、density 判定 -> 当たれば choice）を維持する。
    """
    near_structure = _collect_structure_neighborhood(structures)
    near_path = _collect_path_neighborhood(grid)
    for y in range(MAP_H):
        _decorate_row(grid, y, rng, near_structure, near_path)


def _collect_structure_neighborhood(structures):
    """拠点位置から半径 3 マスの近傍 set を返す。

    Args:
        structures: (sx, sy) のイテラブル。
    Returns:
        set[tuple[int, int]]。
    Policy:
        - dx, dy in [-3, +3] の 7x7 マスを近傍として加える。
    """
    near = set()
    for sx, sy in structures:
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                near.add((sx + dx, sy + dy))
    return near


def _collect_path_neighborhood(grid):
    """PATH タイルの周囲 1 マスの近傍 set を返す。

    Args:
        grid: 2D タイル ID grid。
    Returns:
        set[tuple[int, int]]。
    Policy:
        - PATH マスごとに 3x3 の近傍を加える。
    """
    near = set()
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x] == T_PATH:
                _add_3x3_neighborhood(near, x, y)
    return near


def _add_3x3_neighborhood(near, x, y):
    """near set に (x, y) を中心とする 3x3 マスを追加する。

    Args:
        near: 追加先 set。
        x: 中心 X。
        y: 中心 Y。
    Policy:
        - dx, dy in (-1, 0, 1) の 9 マスを add する。
    """
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near.add((x + dx, y + dy))


def _decorate_row(grid, y, rng, near_structure, near_path):
    """1 行ぶんの装飾タイル配置を行う。

    Args:
        grid: 2D タイル ID grid。
        y: 行 Y。
        rng: random.Random。
        near_structure: 拠点近傍 set。
        near_path: 道沿い近傍 set。
    Policy:
        - ゾーンの装飾候補リストが空ならスキップ。
        - 各列で density 判定 -> 当たれば choice の順を維持する。
    """
    zone = get_zone(y)
    deco_list = _ZONE_DECORATIONS.get(zone, [])
    if not deco_list:
        return
    for x in range(MAP_W):
        _decorate_cell(grid, x, y, rng, deco_list, near_structure, near_path)


def _decorate_cell(grid, x, y, rng, deco_list, near_structure, near_path):
    """1 セルぶんの装飾タイル配置を行う。

    Args:
        grid: 2D タイル ID grid。
        x: 列 X。
        y: 行 Y。
        rng: random.Random。
        deco_list: ゾーン別装飾候補。
        near_structure: 拠点近傍 set。
        near_path: 道沿い近傍 set。
    Policy:
        - 装飾可能なベースタイルでなければスキップ。
        - density 判定 (rng.random()) を毎回行い、当たれば choice。
        - 元実装の乱数順を維持するため、候補不在ならランダム消費しない。
    """
    tile = grid[y][x]
    candidates = [(did, bt) for did, bt in deco_list if tile == bt]
    if not candidates:
        return
    density_val = _pick_deco_density(x, y, near_structure, near_path)
    if rng.random() < density_val:
        deco_id, _ = rng.choice(candidates)
        grid[y][x] = deco_id


def _pick_deco_density(x, y, near_structure, near_path):
    """(x, y) の装飾配置密度を返す。

    Args:
        x: 列 X。
        y: 行 Y。
        near_structure: 拠点近傍 set。
        near_path: 道沿い近傍 set。
    Returns:
        float。
    Policy:
        - 拠点近傍は 0.25、道沿いは 0.15、それ以外は 0.05。
    """
    if (x, y) in near_structure:
        return 0.25
    if (x, y) in near_path:
        return 0.15
    return 0.05


def _place_landmarks(grid):
    """2x2 マルチタイルランドマーク（世界樹・通信塔）を配置する。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - 世界樹と通信塔をそれぞれ 4 マスで敷き、周囲の障害物を除去する。
    """
    _install_bigtree(grid)
    _install_tower(grid)
    _clear_landmark_surroundings(grid)


def _install_bigtree(grid):
    """世界樹 4 マス（2x2）を配置する。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - BIGTREE_POS を左上として 2x2 マスを T_BIGTREE_* で埋める。
    """
    bx, by = BIGTREE_POS
    grid[by][bx] = T_BIGTREE_TL
    grid[by][bx + 1] = T_BIGTREE_TR
    grid[by + 1][bx] = T_BIGTREE_BL
    grid[by + 1][bx + 1] = T_BIGTREE_BR


def _install_tower(grid):
    """通信塔 4 マス（2x2）を配置する。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - TOWER_POS を左上として 2x2 マスを T_TOWER_* で埋める。
    """
    tx, ty = TOWER_POS
    grid[ty][tx] = T_TOWER_TL
    grid[ty][tx + 1] = T_TOWER_TR
    grid[ty + 1][tx] = T_TOWER_BL
    grid[ty + 1][tx + 1] = T_TOWER_BR


def _clear_landmark_surroundings(grid):
    """ランドマーク周辺の障害物を除去して通行可能化する。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - dx, dy in [-1, +2] の 4x4 範囲で TREE/MOUNTAIN を GRASS に置換。
    """
    for lx, ly in [BIGTREE_POS, TOWER_POS]:
        _clear_obstacles_around(grid, lx, ly)


def _clear_obstacles_around(grid, lx, ly):
    """1 ランドマーク周辺の 4x4 マスから障害物を除去する。

    Args:
        grid: 2D タイル ID grid。
        lx: ランドマーク左上 X。
        ly: ランドマーク左上 Y。
    Policy:
        - dx, dy in [-1, +2] の各マスで _replace_obstacle_with_grass を呼ぶ。
    """
    for dy in range(-1, 3):
        for dx in range(-1, 3):
            _replace_obstacle_with_grass(grid, lx + dx, ly + dy)


def _replace_obstacle_with_grass(grid, x, y):
    """1 マスが TREE/MOUNTAIN なら GRASS に置換する。

    Args:
        grid: 2D タイル ID grid。
        x: X 座標。
        y: Y 座標。
    Policy:
        - 範囲外と非障害物はスキップ。
    """
    if not _is_in_grid(x, y, MAP_W, MAP_H):
        return
    if grid[y][x] in {T_TREE, T_MOUNTAIN}:
        grid[y][x] = T_GRASS


_PASS_X = 22
_BRIDGE_X = 28


def _build_world_base_grid():
    """海・山・橋・砂のベース地形を敷いた world grid を返す。

    Returns:
        2D list。
    Policy:
        - _make_empty -> 周縁海 -> 山脈 -> 河川/橋 -> 南端砂 の順で生成。
    """
    grid = _make_empty(MAP_W, MAP_H, T_GRASS)
    _carve_world_water_border(grid)
    _carve_world_mountain_pass(grid)
    _carve_world_bridge_river(grid)
    _convert_south_to_sand(grid)
    return grid


def _carve_world_water_border(grid):
    """周縁 3 マスを WATER で囲う。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - y <= 2 / y >= 48 / x <= 2 / x >= 48 のいずれかなら WATER。
    """
    for y in range(MAP_H):
        for x in range(MAP_W):
            if _is_world_border(x, y):
                grid[y][x] = T_WATER


def _is_world_border(x, y):
    """(x, y) が周縁 3 マスの WATER 範囲かを返す。

    Args:
        x: X 座標。
        y: Y 座標。
    Returns:
        bool。
    Policy:
        - 上下端と左右端を Y/X 軸の述語に分けて OR を取る。
    """
    if _is_y_at_world_edge(y):
        return True
    return _is_x_at_world_edge(x)


def _is_y_at_world_edge(y):
    """Y 座標が WATER 縁（上下 3 マス）かを返す。

    Args:
        y: Y 座標。
    Returns:
        bool。
    Policy:
        - y <= 2 か y >= 48 のときだけ True。
    """
    if y <= 2:
        return True
    return y >= 48


def _is_x_at_world_edge(x):
    """X 座標が WATER 縁（左右 3 マス）かを返す。

    Args:
        x: X 座標。
    Returns:
        bool。
    Policy:
        - x <= 2 か x >= 48 のときだけ True。
    """
    if x <= 2:
        return True
    return x >= 48


def _carve_world_mountain_pass(grid):
    """中央の山脈と峠を彫る。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - 行 15..17 で _PASS_X からの距離が 1 を超えるマスを MOUNTAIN に。
    """
    for y in range(15, 18):
        for x in range(3, 48):
            if abs(x - _PASS_X) > 1:
                grid[y][x] = T_MOUNTAIN


def _carve_world_bridge_river(grid):
    """中央の河川と橋を敷く。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - 行 27..29 で _BRIDGE_X 近傍は BRIDGE、それ以外は WATER。
    """
    for y in range(27, 30):
        for x in range(3, 48):
            if abs(x - _BRIDGE_X) <= 1:
                grid[y][x] = T_BRIDGE
            else:
                grid[y][x] = T_WATER


def _convert_south_to_sand(grid):
    """南端 10 行の GRASS を SAND に置換する。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - 行 38..47 で GRASS のマスだけ SAND に置換。
    """
    for y in range(38, 48):
        for x in range(3, 48):
            if grid[y][x] == T_GRASS:
                grid[y][x] = T_SAND


def _place_world_structures(grid):
    """城・町・洞窟を grid に配置する。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - CASTLE_POS / TOWN_* / CAVE_GLITCH を該当タイル ID で敷く。
    """
    cx, cy = CASTLE_POS
    grid[cy][cx] = T_CASTLE
    for tx, ty in [TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO]:
        grid[ty][tx] = T_TOWN
    gx, gy = CAVE_GLITCH
    grid[gy][gx] = T_CAVE


def _get_world_passable_for_road():
    """road 彫りで上書き可能なタイル ID set を返す。

    Returns:
        set[int]。
    Policy:
        - GRASS / SAND / TREE と装飾タイル全部を含む。
    """
    return {T_GRASS, T_SAND, T_TREE} | DECORATION_TILES


def _carve_world_road_network(grid, rng):
    """拠点間を蛇行 PATH でつなぐ。

    Args:
        grid: 2D タイル ID grid。
        rng: random.Random。
    Policy:
        - 城 -> 町ハジメ -> 峠 -> 町ロジック -> 橋 -> 町アルゴ -> 洞窟、
          + 町ロジック支線 + 町アルゴ支線、の順序を維持する（乱数順保存）。
    """
    cx, cy = CASTLE_POS
    gx, gy = CAVE_GLITCH
    passable_all = _get_world_passable_for_road()
    _carve_winding_path(grid, cx, cy, *TOWN_HAJIME, rng, passable_all)
    _carve_winding_path(grid, *TOWN_HAJIME, _PASS_X, 16, rng, passable_all)
    _carve_winding_path(grid, _PASS_X, 18, *TOWN_LOGIC, rng, passable_all)
    _carve_winding_path(grid, *TOWN_LOGIC, _BRIDGE_X, 27, rng, passable_all)
    _carve_winding_path(grid, _BRIDGE_X, 30, *TOWN_ALGO, rng, passable_all)
    _carve_winding_path(grid, *TOWN_ALGO, gx, gy, rng, passable_all)
    _carve_winding_path(grid, *TOWN_LOGIC, 38, 24, rng, passable_all)
    _carve_winding_path(grid, *TOWN_ALGO, 10, 36, rng, passable_all)


def _get_world_structure_positions():
    """拠点位置リストを返す。

    Returns:
        list[tuple[int, int]]。
    Policy:
        - 城・町 3 種・洞窟の順で固定リストを返す。
    """
    return [CASTLE_POS, TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO, CAVE_GLITCH]


def _open_structure_walkable_ring(grid):
    """各拠点の周囲 1 マスから障害物を除去して通行可能化する。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - 拠点中心マスは触らず、周囲 8 マスの TREE/MOUNTAIN/SAND を GRASS に。
    """
    for sx, sy in _get_world_structure_positions():
        _open_one_structure_ring(grid, sx, sy)


def _open_one_structure_ring(grid, sx, sy):
    """1 拠点の周囲 8 マスから障害物を除去する。

    Args:
        grid: 2D タイル ID grid。
        sx: 拠点 X。
        sy: 拠点 Y。
    Policy:
        - 中心マス (dx, dy == 0, 0) は元タイルを保つ。
    """
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            _clear_ring_cell(grid, sx + dx, sy + dy, dx, dy)


def _clear_ring_cell(grid, nx, ny, dx, dy):
    """周辺 1 マスを条件を満たすときだけ GRASS に置換する。

    Args:
        grid: 2D タイル ID grid。
        nx: 検査 X。
        ny: 検査 Y。
        dx: 中心からのオフセット X。
        dy: 中心からのオフセット Y。
    Policy:
        - 範囲外と中心マス (dx==0 かつ dy==0) はスキップ。
        - TREE/MOUNTAIN/SAND だけを GRASS に置換する。
    """
    if not _is_in_grid(nx, ny, MAP_W, MAP_H):
        return
    if _is_center_cell(dx, dy):
        return
    if grid[ny][nx] in {T_TREE, T_MOUNTAIN, T_SAND}:
        grid[ny][nx] = T_GRASS


def _is_center_cell(dx, dy):
    """オフセットが中心 (0, 0) かを返す。

    Args:
        dx: X オフセット。
        dy: Y オフセット。
    Returns:
        bool。
    Policy:
        - and を 1 箇所に閉じ込めて CR303 を回避する。
    """
    return dx == 0 and dy == 0


def _refresh_structure_centers(grid):
    """城・町・洞窟の中心タイルを再敷設する（道カーブで上書きされた可能性に備える）。

    Args:
        grid: 2D タイル ID grid。
    Policy:
        - CASTLE_POS / TOWN_* / CAVE_GLITCH の 1 マスだけを各 ID に戻す。
    """
    cx, cy = CASTLE_POS
    grid[cy][cx] = T_CASTLE
    for tx, ty in [TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO]:
        grid[ty][tx] = T_TOWN
    gx, gy = CAVE_GLITCH
    grid[gy][gx] = T_CAVE


def _build_dungeon_rooms(grid, rng):
    """重複しない部屋を最大 6 つ生成して rooms リストを返す。

    Args:
        grid: 2D タイル ID grid。
        rng: random.Random。
    Returns:
        list[tuple[int, int, int, int]]: (rx, ry, rw, rh) のリスト。
    Policy:
        - 1 イテレーションで randint を 4 回（rw, rh, rx, ry）消費する順序を維持。
        - 重複しなければ部屋を rooms に追加し grid を FLOOR で塗る。
    """
    rooms = []
    attempts = 0
    while len(rooms) < 6 and attempts < 200:
        attempts += 1
        rw = rng.randint(3, 6)
        rh = rng.randint(3, 6)
        rx = rng.randint(1, DUNGEON_W - rw - 1)
        ry = rng.randint(1, DUNGEON_H - rh - 1)
        if _is_dungeon_room_overlapping(rooms, rx, ry, rw, rh):
            continue
        rooms.append((rx, ry, rw, rh))
        _paint_dungeon_room(grid, rx, ry, rw, rh)
    return rooms


def _is_dungeon_room_overlapping(rooms, rx, ry, rw, rh):
    """rooms と (rx, ry, rw, rh) 矩形が 1 マスでも重なるかを返す。

    Args:
        rooms: 既存部屋リスト。
        rx: 候補 X。
        ry: 候補 Y。
        rw: 候補 W。
        rh: 候補 H。
    Returns:
        bool。
    Policy:
        - 1 マスのマージンを取り、4 辺の overlap を _is_rect_overlap で判定。
    """
    for (ox, oy, ow, oh) in rooms:
        if _is_rect_overlap(rx, ry, rw, rh, ox, oy, ow, oh):
            return True
    return False


def _is_rect_overlap(rx, ry, rw, rh, ox, oy, ow, oh):
    """2 矩形が 1 マスのマージン付きで重なるかを返す。

    Args:
        rx, ry, rw, rh: 候補矩形。
        ox, oy, ow, oh: 既存矩形。
    Returns:
        bool。
    Policy:
        - 元実装の 4 辺式と同値（X / Y の両軸で交差したら overlap）。
    """
    if not _is_x_axis_overlap(rx, rw, ox, ow):
        return False
    return _is_y_axis_overlap(ry, rh, oy, oh)


def _is_x_axis_overlap(rx, rw, ox, ow):
    """X 軸で 1 マスマージン付きで重なるかを返す。

    Args:
        rx: 候補 X。
        rw: 候補 W。
        ox: 既存 X。
        ow: 既存 W。
    Returns:
        bool。
    Policy:
        - and を 1 箇所に閉じ込めて CR303 を回避する。
    """
    return rx < ox + ow + 1 and rx + rw + 1 > ox


def _is_y_axis_overlap(ry, rh, oy, oh):
    """Y 軸で 1 マスマージン付きで重なるかを返す。

    Args:
        ry: 候補 Y。
        rh: 候補 H。
        oy: 既存 Y。
        oh: 既存 H。
    Returns:
        bool。
    Policy:
        - and を 1 箇所に閉じ込めて CR303 を回避する。
    """
    return ry < oy + oh + 1 and ry + rh + 1 > oy


def _paint_dungeon_room(grid, rx, ry, rw, rh):
    """1 部屋を FLOOR で塗る。

    Args:
        grid: 2D タイル ID grid。
        rx: 左上 X。
        ry: 左上 Y。
        rw: 横幅。
        rh: 縦幅。
    Policy:
        - dy in [0, rh), dx in [0, rw) の rh*rw マスを T_FLOOR で埋める。
    """
    for dy2 in range(rh):
        for dx2 in range(rw):
            grid[ry + dy2][rx + dx2] = T_FLOOR


def _carve_dungeon_corridors(grid, rooms):
    """隣接 room 間に L 字 corridor を彫る。

    Args:
        grid: 2D タイル ID grid。
        rooms: 部屋リスト。
    Policy:
        - 隣接ペア (i, i+1) の中心を結ぶ水平 -> 垂直の 2 段で彫る。
    """
    for i in range(len(rooms) - 1):
        _carve_corridor_between(grid, rooms[i], rooms[i + 1])


def _carve_corridor_between(grid, room_a, room_b):
    """2 部屋の中心を結ぶ L 字 corridor を彫る。

    Args:
        grid: 2D タイル ID grid。
        room_a: 始点 room タプル。
        room_b: 終点 room タプル。
    Policy:
        - 始点 (ax, ay) と終点 (bx, by) を _room_center から取り、
          まず水平、次に垂直の順に FLOOR を敷く。
    """
    ax, ay = _room_center(room_a)
    bx, by = _room_center(room_b)
    _carve_horizontal_corridor(grid, ax, bx, ay)
    _carve_vertical_corridor(grid, ay, by, bx)


def _room_center(room):
    """room の中心 (cx, cy) を返す。

    Args:
        room: (rx, ry, rw, rh) タプル。
    Returns:
        tuple[int, int]。
    Policy:
        - 中心は左上 + 幅/2（整数除算、元実装と同じ）。
    """
    rx, ry, rw, rh = room
    return rx + rw // 2, ry + rh // 2


def _carve_horizontal_corridor(grid, ax, bx, ay):
    """y = ay の水平 corridor を ax -> bx に彫る。

    Args:
        grid: 2D タイル ID grid。
        ax: 始点 X。
        bx: 終点 X。
        ay: 共通 Y。
    Policy:
        - 元実装の range(ax, bx + step, step) と clamping を保持する。
    """
    step = 1 if bx >= ax else -1
    for xx in range(ax, bx + step, step):
        xx = max(1, min(DUNGEON_W - 2, xx))
        grid[ay][xx] = T_FLOOR


def _carve_vertical_corridor(grid, ay, by, bx):
    """x = bx の垂直 corridor を ay -> by に彫る。

    Args:
        grid: 2D タイル ID grid。
        ay: 始点 Y。
        by: 終点 Y。
        bx: 共通 X。
    Policy:
        - 元実装の range(ay, by + step, step) と clamping を保持する。
    """
    step = 1 if by >= ay else -1
    for yy in range(ay, by + step, step):
        yy = max(1, min(DUNGEON_H - 2, yy))
        grid[yy][bx] = T_FLOOR


def _place_dungeon_stairs_and_boss(grid, rooms):
    """階段とボストリガーを配置する。

    Args:
        grid: 2D タイル ID grid。
        rooms: 部屋リスト。
    Policy:
        - rooms が空ならスキップ。
        - 最初の部屋の入り口に階段、最後の部屋の中心にボストリガー。
        - 階段とボスが同マスなら 1 マス東に逃がす。
    """
    if not rooms:
        return
    sx = rooms[0][0] + 1
    sy = rooms[0][1] + 1
    grid[sy][sx] = T_STAIR_UP
    bx, by = _resolve_boss_position(rooms[-1], sx, sy)
    grid[by][bx] = T_GLITCH_LORD_TRIGGER


def _resolve_boss_position(last_room, sx, sy):
    """最終部屋のボス座標 (bx, by) を返す（階段と被ったら 1 マス東に逃がす）。

    Args:
        last_room: rooms[-1] のタプル。
        sx: 階段 X。
        sy: 階段 Y。
    Returns:
        tuple[int, int]。
    Policy:
        - 元実装の `min(brx + brw - 1, bx + 1)` を維持する。
    """
    brx, bry, brw, brh = last_room
    bx = brx + brw // 2
    by = bry + brh // 2
    if _is_same_cell(bx, by, sx, sy):
        bx = min(brx + brw - 1, bx + 1)
    return bx, by


def _is_same_cell(bx, by, sx, sy):
    """2 つのセル座標が一致するかを返す。

    Args:
        bx: 1 つ目 X。
        by: 1 つ目 Y。
        sx: 2 つ目 X。
        sy: 2 つ目 Y。
    Returns:
        bool。
    Policy:
        - and を 1 箇所に閉じ込めて CR303 を回避する。
    """
    return bx == sx and by == sy
