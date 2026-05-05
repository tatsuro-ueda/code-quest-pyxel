from __future__ import annotations

"""pyxres ロードと tile / sprite / font バンクのセットアップ（P1-G13）。

Q5A 決定：単一ファイルで 17 メソッドを保有する。
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pyxel

from src.shared.assets.jp_font_data import (
    JP_FONT_BITMAPS,
    JP_FONT_GLYPH_H,
    JP_FONT_GLYPH_W,
    JP_FONT_IMAGE_BANK,
    JP_FONT_LAYOUT,
)
from src.shared.services.world_generation import generate_world_map

DUNGEON_TM_OFFSET_Y = 110


def resolve_pyxres_path(main_runtime_file: Path | str) -> Path:
    """`my_resource.pyxres` / `assets/blockquest.pyxres` の探索先を決める。

    探索順:
      1. `main_runtime_file.parent / my_resource.pyxres`
         （Code Maker bundle: `block-quest/main.py` の隣）
      2. `main_runtime_file.parent.parent.parent / my_resource.pyxres`
         （dev project root 直下のオーバーライド）
      3. `main_runtime_file.parent.parent.parent / assets / blockquest.pyxres`
         （dev / production の正準パス、ここがフォールバックの最終）

    存在チェックはこの関数では行わず、最初に見つかったものを返す。
    全候補が存在しない場合は最後の候補（assets パス）を返す。
    """
    m_file = Path(main_runtime_file).resolve()
    project_root = m_file.parent.parent.parent
    bundle_dir = m_file.parent
    candidates = [
        bundle_dir / "my_resource.pyxres",
        project_root / "my_resource.pyxres",
        project_root / "assets" / "blockquest.pyxres",
    ]
    return next((p for p in candidates if p.exists()), candidates[-1])


@dataclass
class ImageBanks:
    """tile / sprite / font バンク管理（P1-G13 で Game から 17 メソッドを取り込み）。"""

    game: Any = None
    tile_bank: dict = field(default_factory=dict)
    tile_bank_water2: object | None = None
    sprite_bank: dict = field(default_factory=dict)
    path_variant_bank: dict = field(default_factory=dict)
    shore_variant_bank: dict = field(default_factory=dict)
    tile_id_by_pixel: dict = field(default_factory=dict)
    pyxres_loaded: bool = False
    pyxres_path: Path | None = None

    def setup_image_banks(self):
        """画像・サウンドバンクの初期化。

        重要: .pyxres は **画像バンクと音バンクの両方** を含む。
        この関数で `pyxel.load()` すると、AudioManager / SfxSystem が
        既に書き込んだ sounds 0-42 も .pyxres の内容で上書きされる。
        """
        self.layout_tile_bank()
        self.layout_sprite_bank()
        self.build_reverse_tile_map()
        self.pyxres_loaded = False
        self.pyxres_path = None

        import src.runtime.main_runtime as M
        # P3-E: browser_resource_override 削除済み。import された resource は
        # web_runtime_server が assets/blockquest.pyxres に直接書き戻す。
        # 探索ロジックは resolve_pyxres_path() に切り出し、ユニットテスト可能にした。
        pyxres_path = resolve_pyxres_path(M.__file__)
        self.pyxres_path = pyxres_path
        if pyxres_path.exists():
            try:
                pyxel.load(str(pyxres_path))
                self.pyxres_loaded = True
                return
            except Exception as exc:
                print(f"[image_bank] failed to load {pyxres_path}: {exc}; regenerating")

        self.paint_tile_bank()
        self.paint_sprite_bank()
        self.paint_jp_font_bank()

    def paint_jp_font_bank(self):
        """`JP_FONT_BITMAPS` を image bank 2 に焼き込む。"""
        bank = pyxel.images[JP_FONT_IMAGE_BANK]
        for py in range(256):
            for px in range(256):
                bank.pset(px, py, 0)
        for ch, rows in JP_FONT_BITMAPS.items():
            col, row = JP_FONT_LAYOUT[ch]
            ox = col * JP_FONT_GLYPH_W
            oy = row * JP_FONT_GLYPH_H
            for ry in range(JP_FONT_GLYPH_H):
                bits = rows[ry] if ry < len(rows) else 0
                for rx in range(JP_FONT_GLYPH_W):
                    if bits & (1 << (JP_FONT_GLYPH_W - 1 - rx)):
                        bank.pset(ox + rx, oy + ry, 7)

    def build_reverse_tile_map(self):
        """image bank pixel 座標 → 元の tile_id への逆引き辞書。"""
        import src.runtime.main_runtime as M
        self.tile_id_by_pixel = {}
        for tid, (u, v) in self.tile_bank.items():
            self.tile_id_by_pixel[(u, v)] = tid
        for (u, v) in self.path_variant_bank.values():
            self.tile_id_by_pixel[(u, v)] = M.T_PATH
        for (u, v) in self.shore_variant_bank.values():
            self.tile_id_by_pixel[(u, v)] = M.T_WATER
        if self.tile_bank_water2:
            self.tile_id_by_pixel[self.tile_bank_water2] = M.T_WATER

    def tile_bank_layout_valid(self):
        """イメージバンク 0 のピクセルが現在の TILE_DATA と一致するか検証する。"""
        import src.runtime.main_runtime as M
        bank = pyxel.images[0]
        try:
            for tid, data in M.TILE_DATA.items():
                pos = self.tile_bank.get(tid)
                if pos is None:
                    return False
                u, v = pos
                for rx, expected in enumerate(data[0]):
                    if bank.pget(u + rx, v) != expected:
                        return False
        except Exception:
            return False
        return True

    def setup_world_tilemap(self):
        """World map と dungeon を `pyxel.tilemaps[0]` と同期する。"""
        import src.runtime.main_runtime as M
        game = self.game
        try:
            pyxel.tilemaps[0].imgsrc = 0
        except Exception:
            pass

        dgrid, drooms = M.generate_dungeon(seed=99)
        game.dungeon_template = dgrid
        game.dungeon_template_rooms = drooms
        if drooms:
            game.dungeon_spawn = (drooms[0][0] + 1, drooms[0][1] + 1)
        else:
            game.dungeon_spawn = (1, 1)

        if self.pyxres_loaded:
            # pyxres の tilemap がユーザー編集も含めた source of truth。
            # 過去仕様：image bank が TILE_DATA とズレていると tilemap ごと
            # 手続き的に焼き直していたが、それだとユーザーの道路修整等の
            # tilemap 編集が無言で破棄される（CJ 破壊）。
            # 修正後：image bank 不一致のときは image bank だけ修復し、
            # tilemap には触らない。
            if not self.tile_bank_layout_valid():
                print("[tilemap] tile bank layout changed — repainting image bank only")
                self.paint_tile_bank()
                self.paint_sprite_bank()
                self.paint_jp_font_bank()
            self.derive_dungeon_from_tilemap()
            self.regenerate_world_tilemap_fallback()
            self.bake_dungeon_to_tilemap()
        else:
            self.regenerate_world_tilemap_fallback()
            self.bake_dungeon_to_tilemap()
            if self.pyxres_path is not None and sys.platform != "emscripten":
                try:
                    self.pyxres_path.parent.mkdir(parents=True, exist_ok=True)
                    pyxel.save(str(self.pyxres_path))
                    print(f"[image_bank] generated {self.pyxres_path}")
                except Exception as exc:
                    print(f"[image_bank] could not save .pyxres: {exc}")

    def bake_dungeon_to_tilemap(self):
        """共有ダンジョン (game.dungeon_template) を tilemap[0] のオフセット領域に焼き込む。"""
        import src.runtime.main_runtime as M
        game = self.game
        tilemap = pyxel.tilemaps[0]
        dg = game.dungeon_template
        oy = DUNGEON_TM_OFFSET_Y
        for y in range(len(dg)):
            for x in range(len(dg[0])):
                tile = dg[y][x]
                u, v = self.tile_bank.get(tile, self.tile_bank[M.T_GRASS])
                tu, tv = u // 8, v // 8
                tilemap.pset(2 * x,     oy + 2 * y,     (tu,     tv))
                tilemap.pset(2 * x + 1, oy + 2 * y,     (tu + 1, tv))
                tilemap.pset(2 * x,     oy + 2 * y + 1, (tu,     tv + 1))
                tilemap.pset(2 * x + 1, oy + 2 * y + 1, (tu + 1, tv + 1))

    def derive_dungeon_from_tilemap(self):
        """tilemap[0] のオフセット領域から共有ダンジョンを組み立てる。"""
        import src.runtime.main_runtime as M
        game = self.game
        tilemap = pyxel.tilemaps[0]
        dg = game.dungeon_template
        oy = DUNGEON_TM_OFFSET_Y
        derived = []
        _miss = 0
        for y in range(len(dg)):
            row = []
            for x in range(len(dg[0])):
                tu, tv = tilemap.pget(2 * x, oy + 2 * y)
                key = (tu * 8, tv * 8)
                tid = self.tile_id_by_pixel.get(key, M.T_FLOOR)
                if key not in self.tile_id_by_pixel:
                    _miss += 1
                row.append(tid)
            derived.append(row)
        if _miss:
            print(f"[tilemap] dungeon derive: {_miss} tiles fell back to T_FLOOR")
        game.dungeon_template = derived
        for y in range(len(derived)):
            for x in range(len(derived[0])):
                if derived[y][x] == M.T_STAIR_UP:
                    game.dungeon_spawn = (x, y)
                    return

    def regenerate_world_tilemap_fallback(self):
        """pyxres 不在/破損時の fallback：procedural に world を生成して tilemap[0] に焼く。

        pyxres が読み込み済みのときは tilemap が SSoT なのでスキップする
        （Code Maker で編集した道形状の保護）。pyxres 不在時 (初回起動) は
        `generate_world_map()` を直呼びし、結果を tilemap に焼いて `pyxel.save`
        で初回 pyxres を作る経路を維持する。
        """
        if self.pyxres_loaded:
            return
        import src.runtime.main_runtime as M
        tilemap = pyxel.tilemaps[0]
        wm = generate_world_map()
        for y in range(M.MAP_H):
            for x in range(M.MAP_W):
                tile = wm[y][x]
                if tile == M.T_PATH:
                    variant = M.get_path_variant(wm, x, y)
                    u, v = self.path_variant_bank.get(
                        id(variant),
                        self.tile_bank[M.T_PATH],
                    )
                elif tile == M.T_WATER:
                    variant = M.get_shore_variant(wm, x, y)
                    if variant is None:
                        u, v = self.tile_bank[M.T_WATER]
                    else:
                        u, v = self.shore_variant_bank.get(
                            id(variant),
                            self.tile_bank[M.T_WATER],
                        )
                else:
                    u, v = self.tile_bank.get(tile, self.tile_bank[M.T_GRASS])
                tu, tv = u // 8, v // 8
                tilemap.pset(2 * x,     2 * y,     (tu,     tv))
                tilemap.pset(2 * x + 1, 2 * y,     (tu + 1, tv))
                tilemap.pset(2 * x,     2 * y + 1, (tu,     tv + 1))
                tilemap.pset(2 * x + 1, 2 * y + 1, (tu + 1, tv + 1))

    def tile_iter(self):
        """タイルバンクに格納する順序を返す。"""
        import src.runtime.main_runtime as M
        for tid, tdata in M.TILE_DATA.items():
            yield ("tile", tid, tdata)
        yield ("water2", "water2", M.TILE_WATER2)
        for _name, pdata in [
            ("V", M.PATH_V), ("H", M.PATH_H), ("CROSS", M.PATH_CROSS),
            ("SE", M.PATH_SE), ("SW", M.PATH_SW), ("NE", M.PATH_NE), ("NW", M.PATH_NW),
            ("T_NES", M.PATH_T_NES), ("T_NWS", M.PATH_T_NWS),
            ("T_EWS", M.PATH_T_EWS), ("T_NEW", M.PATH_T_NEW),
        ]:
            yield ("path", id(pdata), pdata)
        for _name, sdata in [
            ("N", M.SHORE_N), ("S", M.SHORE_S), ("W", M.SHORE_W), ("E", M.SHORE_E),
            ("NE", M.SHORE_NE), ("NW", M.SHORE_NW), ("SE", M.SHORE_SE), ("SW", M.SHORE_SW),
        ]:
            yield ("shore", id(sdata), sdata)

    def layout_tile_bank(self):
        """レイアウト辞書のみ計算（pset なし）。"""
        self.tile_bank = {}
        self.path_variant_bank = {}
        self.shore_variant_bank = {}
        col = 0; row = 0
        for kind, key, _data in self.tile_iter():
            bx = col * 16; by = row * 16
            if kind == "tile":
                self.tile_bank[key] = (bx, by)
            elif kind == "water2":
                self.tile_bank_water2 = (bx, by)
            elif kind == "path":
                self.path_variant_bank[key] = (bx, by)
            elif kind == "shore":
                self.shore_variant_bank[key] = (bx, by)
            col += 1
            if col >= 16:
                col = 0; row += 1

    def paint_tile_bank(self):
        """pset でタイル絵をバンクに焼き込む。"""
        bank = pyxel.images[0]
        col = 0; row = 0
        for _kind, _key, data in self.tile_iter():
            bx = col * 16; by = row * 16
            for py in range(16):
                for px in range(16):
                    bank.pset(bx + px, by + py, data[py][px])
            col += 1
            if col >= 16:
                col = 0; row += 1

    def render_tiles_to_bank(self):
        """互換ラッパー：layout + paint を順に呼ぶ。"""
        self.layout_tile_bank()
        self.paint_tile_bank()

    def sprite_iter(self):
        import src.runtime.main_runtime as M
        sprites_to_render = {
            "hero_down": M.HERO_DOWN, "hero_walk": M.HERO_DOWN_WALK,
        }
        sprites_to_render.update(M.ENEMY_SPRITES)
        for name, sdata in sprites_to_render.items():
            yield (name, sdata)

    def layout_sprite_bank(self):
        self.sprite_bank = {}
        col = 0; row = 0
        for name, _data in self.sprite_iter():
            bx = col * 16; by = row * 16
            self.sprite_bank[name] = (bx, by)
            col += 1
            if col >= 16:
                col = 0; row += 1

    def paint_sprite_bank(self):
        bank = pyxel.images[1]
        col = 0; row = 0
        for _name, sdata in self.sprite_iter():
            bx = col * 16; by = row * 16
            for py in range(16):
                for px in range(16):
                    bank.pset(bx + px, by + py, sdata[py][px])
            col += 1
            if col >= 16:
                col = 0; row += 1

    def render_sprites_to_bank(self):
        """互換ラッパー：layout + paint を順に呼ぶ。"""
        self.layout_sprite_bank()
        self.paint_sprite_bank()
