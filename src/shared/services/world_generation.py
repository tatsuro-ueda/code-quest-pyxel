from __future__ import annotations

"""World map / dungeon 生成ロジック（Phase 1.5 実装）。

以下を保有する:
- get_path_variant / get_shore_variant (auto-tile variant 選択)
- _make_empty / _carve_winding_path (primitive builders)
- _place_forests / _place_decorations / _place_landmarks (生成段階)
- generate_world_map / generate_dungeon (world/dungeon 生成 entrypoint)
- get_zone (Y 座標からゾーン ID)

Phase 1.5-A でタイル定数を `src/shared/constants/tile_data.py` に移したため、
循環 import なしでここに関数群を移せるようになった。
"""

import random

from src.shared.constants.tile_data import (
    # タイル ID
    T_GRASS, T_WATER, T_TREE, T_SAND, T_FLOOR, T_WALL, T_CASTLE, T_TOWN,
    T_CAVE, T_MOUNTAIN, T_BRIDGE, T_PATH, T_STAIR_UP,
    T_FLOWER, T_ROCK, T_MUSHROOM, T_CACTUS, T_BUSH,
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
    # decoration / landmark
    DECORATION_TILES, LANDMARK_TILES, IMPASSABLE,
)
from src.shared.constants.tile_data import (
    _PATH_VARIANTS, _SHORE_VARIANTS, _ZONE_DECORATIONS,
)


def get_path_variant(world_map, mx, my):
    h = len(world_map)
    w = len(world_map[0]) if h > 0 else 0
    def is_path(x, y):
        if 0 <= x < w and 0 <= y < h:
            return world_map[y][x] == T_PATH
        return False
    n = is_path(mx, my - 1); e = is_path(mx + 1, my)
    s = is_path(mx, my + 1); w_ = is_path(mx - 1, my)
    key = (n, e, s, w_)
    variant = _PATH_VARIANTS.get(key)
    if variant: return variant
    if n or s: return PATH_V
    if e or w_: return PATH_H
    return PATH_V

def get_shore_variant(world_map, mx, my):
    h = len(world_map)
    w = len(world_map[0]) if h > 0 else 0
    def is_land(x, y):
        if 0 <= x < w and 0 <= y < h:
            return world_map[y][x] != T_WATER
        return False
    n = is_land(mx, my - 1); e = is_land(mx + 1, my)
    s = is_land(mx, my + 1); w_ = is_land(mx - 1, my)
    if not (n or e or s or w_): return None
    key = (n, e, s, w_)
    variant = _SHORE_VARIANTS.get(key)
    if variant: return variant
    if n: return SHORE_N
    if s: return SHORE_S
    if w_: return SHORE_W
    if e: return SHORE_E
    return None

from src.shared.constants.sprite_data import *  # HERO_DOWN, HERO_DOWN_WALK, ENEMY_SPRITES 等を一括 import
def _make_empty(w, h, fill):
    return [[fill] * w for _ in range(h)]

def _carve_winding_path(grid, x1, y1, x2, y2, rng, passable=None):
    if passable is None:
        passable = {T_GRASS, T_SAND}
    cx, cy = x1, y1
    max_iter = (abs(x2 - x1) + abs(y2 - y1)) * 4 + 50
    for _ in range(max_iter):
        if cx == x2 and cy == y2: break
        if rng.random() < 0.3 and cx != x2 and cy != y2:
            if rng.random() < 0.5: cx += 1 if x2 > cx else -1
            else: cy += 1 if y2 > cy else -1
        else:
            if abs(x2 - cx) > abs(y2 - cy): cx += 1 if x2 > cx else -1
            else: cy += 1 if y2 > cy else -1
        cx = max(1, min(MAP_W - 2, cx))
        cy = max(1, min(MAP_H - 2, cy))
        if grid[cy][cx] in passable:
            grid[cy][cx] = T_PATH

def _place_forests(grid, rng):
    def density(y):
        if y < 3 or y >= 47: return 0.0
        if y < 16: return 0.08
        if y < 28: return 0.18
        if y < 38: return 0.30
        return 0.05
    for y in range(MAP_H):
        d = density(y)
        for x in range(MAP_W):
            if grid[y][x] == T_GRASS and rng.random() < d:
                grid[y][x] = T_TREE


def _place_decorations(grid, rng, structures):
    """ゾーン別の装飾タイルを配置する。密度は拠点/道沿い/一般で変える。"""
    # 拠点周辺マスのセット（密度ブースト用）
    near_structure = set()
    for sx, sy in structures:
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                near_structure.add((sx + dx, sy + dy))
    # 道沿いマスのセット
    near_path = set()
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x] == T_PATH:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        near_path.add((x + dx, y + dy))

    for y in range(MAP_H):
        zone = get_zone(y)
        deco_list = _ZONE_DECORATIONS.get(zone, [])
        if not deco_list:
            continue
        for x in range(MAP_W):
            tile = grid[y][x]
            # 装飾可能なベースタイルか？
            candidates = [(did, bt) for did, bt in deco_list if tile == bt]
            if not candidates:
                continue
            # 密度を決定
            if (x, y) in near_structure:
                density = 0.25
            elif (x, y) in near_path:
                density = 0.15
            else:
                density = 0.05
            if rng.random() < density:
                deco_id, _ = rng.choice(candidates)
                grid[y][x] = deco_id


def _place_landmarks(grid):
    """2x2 マルチタイルランドマークを配置する。"""
    # 世界樹
    bx, by = BIGTREE_POS
    grid[by][bx] = T_BIGTREE_TL; grid[by][bx + 1] = T_BIGTREE_TR
    grid[by + 1][bx] = T_BIGTREE_BL; grid[by + 1][bx + 1] = T_BIGTREE_BR
    # 通信塔
    tx, ty = TOWER_POS
    grid[ty][tx] = T_TOWER_TL; grid[ty][tx + 1] = T_TOWER_TR
    grid[ty + 1][tx] = T_TOWER_BL; grid[ty + 1][tx + 1] = T_TOWER_BR
    # 周囲を通行可能に（障害物を除去）
    for lx, ly in [BIGTREE_POS, TOWER_POS]:
        for dy in range(-1, 3):
            for dx in range(-1, 3):
                ny, nx = ly + dy, lx + dx
                if 0 <= ny < MAP_H and 0 <= nx < MAP_W:
                    if grid[ny][nx] in {T_TREE, T_MOUNTAIN}:
                        grid[ny][nx] = T_GRASS


def generate_world_map(seed=42):
    rng = random.Random(seed)
    grid = _make_empty(MAP_W, MAP_H, T_GRASS)
    for y in range(MAP_H):
        for x in range(MAP_W):
            if y <= 2 or y >= 48 or x <= 2 or x >= 48:
                grid[y][x] = T_WATER
    PASS_X = 22
    for y in range(15, 18):
        for x in range(3, 48):
            if abs(x - PASS_X) > 1: grid[y][x] = T_MOUNTAIN
    BRIDGE_X = 28
    for y in range(27, 30):
        for x in range(3, 48):
            if abs(x - BRIDGE_X) <= 1: grid[y][x] = T_BRIDGE
            else: grid[y][x] = T_WATER
    for y in range(38, 48):
        for x in range(3, 48):
            if grid[y][x] == T_GRASS: grid[y][x] = T_SAND
    _place_forests(grid, rng)
    cx, cy = CASTLE_POS; grid[cy][cx] = T_CASTLE
    for tx, ty in [TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO]:
        grid[ty][tx] = T_TOWN
    gx, gy = CAVE_GLITCH; grid[gy][gx] = T_CAVE
    passable_all = {T_GRASS, T_SAND, T_TREE} | DECORATION_TILES
    _carve_winding_path(grid, cx, cy, *TOWN_HAJIME, rng, passable_all)
    _carve_winding_path(grid, *TOWN_HAJIME, PASS_X, 16, rng, passable_all)
    _carve_winding_path(grid, PASS_X, 18, *TOWN_LOGIC, rng, passable_all)
    _carve_winding_path(grid, *TOWN_LOGIC, BRIDGE_X, 27, rng, passable_all)
    _carve_winding_path(grid, BRIDGE_X, 30, *TOWN_ALGO, rng, passable_all)
    _carve_winding_path(grid, *TOWN_ALGO, gx, gy, rng, passable_all)
    _carve_winding_path(grid, *TOWN_LOGIC, 38, 24, rng, passable_all)
    _carve_winding_path(grid, *TOWN_ALGO, 10, 36, rng, passable_all)
    structures = [CASTLE_POS, TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO, CAVE_GLITCH]
    for sx, sy in structures:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = sy + dy, sx + dx
                if 0 <= ny < MAP_H and 0 <= nx < MAP_W:
                    if grid[ny][nx] in {T_TREE, T_MOUNTAIN, T_SAND} and (dx != 0 or dy != 0):
                        grid[ny][nx] = T_GRASS
    grid[cy][cx] = T_CASTLE
    for tx, ty in [TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO]:
        grid[ty][tx] = T_TOWN
    grid[gy][gx] = T_CAVE
    # 装飾とランドマークの配置（道カーブ後に行う）
    _place_decorations(grid, rng, structures)
    _place_landmarks(grid)
    return grid

def generate_dungeon(seed=99):
    rng = random.Random(seed)
    grid = _make_empty(DUNGEON_W, DUNGEON_H, T_WALL)
    rooms = []
    attempts = 0
    while len(rooms) < 6 and attempts < 200:
        attempts += 1
        rw = rng.randint(3, 6); rh = rng.randint(3, 6)
        rx = rng.randint(1, DUNGEON_W - rw - 1)
        ry = rng.randint(1, DUNGEON_H - rh - 1)
        overlap = False
        for (ox, oy, ow, oh) in rooms:
            if rx < ox + ow + 1 and rx + rw + 1 > ox and ry < oy + oh + 1 and ry + rh + 1 > oy:
                overlap = True; break
        if not overlap:
            rooms.append((rx, ry, rw, rh))
            for dy2 in range(rh):
                for dx2 in range(rw):
                    grid[ry + dy2][rx + dx2] = T_FLOOR
    for i in range(len(rooms) - 1):
        ax = rooms[i][0] + rooms[i][2] // 2
        ay = rooms[i][1] + rooms[i][3] // 2
        bx = rooms[i+1][0] + rooms[i+1][2] // 2
        by = rooms[i+1][1] + rooms[i+1][3] // 2
        step = 1 if bx >= ax else -1
        for xx in range(ax, bx + step, step):
            xx = max(1, min(DUNGEON_W - 2, xx))
            grid[ay][xx] = T_FLOOR
        step = 1 if by >= ay else -1
        for yy in range(ay, by + step, step):
            yy = max(1, min(DUNGEON_H - 2, yy))
            grid[yy][bx] = T_FLOOR
    if rooms:
        # 最初の部屋の入り口を確保し、その位置に上り階段を置く
        sx = rooms[0][0] + 1
        sy = rooms[0][1] + 1
        grid[sy][sx] = T_STAIR_UP
        # 最後の部屋を終点として、ボストリガーを1マスだけ置く
        brx, bry, brw, brh = rooms[-1]
        bx = brx + brw // 2
        by = bry + brh // 2
        if (bx, by) == (sx, sy):
            bx = min(brx + brw - 1, bx + 1)
        grid[by][bx] = T_GLITCH_LORD_TRIGGER
    return grid, rooms

def get_zone(tile_y, in_dungeon=False):
    if in_dungeon: return 4
    if tile_y < 16: return 0
    if tile_y < 28: return 1
    if tile_y < 38: return 2
    return 3

