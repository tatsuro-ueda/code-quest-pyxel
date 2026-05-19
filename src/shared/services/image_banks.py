"""pyxres ロードと tile / sprite / font バンクのセットアップ（P1-G13）。

このファイルに含まれる関数・クラス：

- resolve_pyxres_path: pyxres 候補から最初に存在するパスを返す
- ImageBanks: tile / sprite / font バンク管理 dataclass
  - pyxres_loaded: 旧名後方互換 property getter
  - pyxres_loaded: 旧名後方互換 property setter
  - load_image_banks: 画像・サウンドバンク全体を初期化する public 入口
  - paint_jp_font_bank: `JP_FONT_BITMAPS` を image bank 2 に焼き込む
  - build_reverse_tile_map: image bank pixel 座標 → tile_id の逆引き辞書を組む
  - is_tile_bank_layout_valid: image bank 0 が TILE_DATA と一致するかを返す述語
  - load_world_tilemap: world map と dungeon を `pyxel.tilemaps[0]` と同期する
  - regenerate_dungeon_tilemap_fallback: pyxres 不在時の fallback で dungeon を焼く
  - derive_dungeon_from_tilemap: tilemap のオフセット領域から共有 dungeon を組み立てる
  - regenerate_world_tilemap_fallback: pyxres 不在時の fallback で world を焼く
  - iter_tiles: タイルバンクに格納する順序を返す generator
  - layout_tile_bank: タイルレイアウト辞書のみ計算（pset なし）
  - paint_tile_bank: pset でタイル絵を image bank 0 に焼き込む
  - render_tiles_to_bank: 互換ラッパー（layout + paint）
  - iter_sprites: スプライト名と pixel data を順に返す generator
  - layout_sprite_bank: スプライトレイアウト辞書のみ計算（pset なし）
  - paint_sprite_bank: pset でスプライト絵を image bank 1 に焼き込む
  - render_sprites_to_bank: 互換ラッパー（layout + paint）
  - setup_image_banks: load_image_banks への後方互換 alias
  - setup_world_tilemap: world と dungeon を tilemap[0] に同期する旧名入口
  - tile_bank_layout_valid: is_tile_bank_layout_valid への後方互換 alias
  - tile_iter: iter_tiles への後方互換 alias
  - sprite_iter: iter_sprites への後方互換 alias
  - _reset_layout_state: layout 系と pyxres state を初期化する
  - _load_pyxres_or_repaint: pyxres ロード or 手続き再描画を切り替える
  - _try_load_pyxres: 指定 pyxres を読めたかを返す述語
  - _do_pyxres_load: 例外を握って pyxel.load を試行する private 委譲
  - _paint_all_banks_from_data: tile/sprite/jp_font をまとめて焼く private 委譲
  - _paint_jp_font_into: jp_font bank をクリアしてからグリフを焼く
  - _clear_jp_font_bank: jp_font bank を全画素 0 で埋める
  - _paint_jp_font_glyphs: JP_FONT_BITMAPS のグリフを bank に焼く
  - _paint_one_glyph: 1 グリフ分のビット列を bank に pset する
  - _reset_reverse_tile_map: 逆引き辞書を空にする
  - _fill_reverse_tile_map: tile/path/shore を逆引き辞書に転写する
  - _record_reverse_tile_entries: tile_bank を逆引き辞書に転写する
  - _record_reverse_path_entries: path_variant_bank を T_PATH に対応付ける
  - _record_reverse_shore_entries: shore_variant_bank を T_WATER に対応付ける
  - _all_tiles_match_or_false: 例外を False に変換しつつ層比較を行う
  - _all_tiles_match: 全 tile_id について 1 行目が一致するかを返す
  - _row_matches: bank の (u, v) 行が expected_row と一致するかを返す
  - _ensure_imgsrc_zero: tilemap[0].imgsrc=0 を best-effort で適用する
  - _build_dungeon_template: dungeon grid と spawn 座標を game に書く
  - _compute_initial_spawn: 最初の room から初期 spawn 座標を返す
  - _repaint_image_bank_if_layout_changed: layout 不一致なら image bank を焼き直す
  - _save_pyxres_if_possible: pyxres を best-effort で書き出す
  - _save_pyxres_now: 実際に pyxel.save を呼ぶ
  - _paint_dungeon_tilemap_from_template: dungeon grid を tilemap dungeon 領域に焼く
  - _iter_dungeon_cells: dungeon grid を (x, y, tile) で順に返す
  - _paint_dungeon_cell: 4 マス分の tilemap pset を 1 タイル分まとめて行う
  - _assign_derived_dungeon_to_game: 派生 dungeon を game に書き spawn を確定する
  - _build_derived_dungeon_grid: tilemap から dungeon grid を派生する
  - _log_dungeon_miss_count: 逆引きミス件数をログする
  - _derive_dungeon_row: 1 行分の dungeon を tilemap から派生する
  - _derive_dungeon_cell_id: tilemap から 1 マス分の tile_id を推定する
  - _find_dungeon_spawn: derived grid から STAIR_UP の座標を spawn として採用する
  - _paint_world_tilemap_procedural: generate_world_map の結果を tilemap[0] に焼く
  - _resolve_world_tile_pixel: world map 1 マス分の (u, v) を返す
  - _resolve_path_pixel: T_PATH 用の variant pixel を返す
  - _resolve_water_pixel: T_WATER 用の shore variant pixel を返す
  - _paint_world_cell: 4 マス分の tilemap pset を 1 タイル分まとめて行う
  - _iter_tile_entries: tile/path/shore を kind タグ付きで順に yield する
  - _yield_tile_entries: tile_data を kind="tile" で順に yield する
  - _yield_path_variants: path 系 variant を kind="path" で順に yield する
  - _yield_shore_variants: shore 系 variant を kind="shore" で順に yield する
  - _reset_layout_dicts: タイルレイアウト辞書を空に戻す
  - _fill_layout_dicts: iter_tiles 全件を 16 桁グリッドに割り付ける
  - _layout_one_tile: 1 タイル分のレイアウトを記録しカーソルを進める
  - _paint_tiles_into: iter_tiles 全件を 16 桁グリッドで bank に焼く
  - _paint_one_tile: 1 タイル分の絵を bank に焼きカーソルを進める
  - _reset_sprite_layout: sprite_bank を空に戻す
  - _fill_sprite_layout: iter_sprites 全件を 16 桁グリッドに割り付ける
  - _layout_one_sprite: 1 sprite 分のレイアウトを記録しカーソルを進める
  - _iter_sprite_entries: hero と enemy_sprites を 1 dict にまとめて yield する
  - _paint_sprites_into: iter_sprites 全件を 16 桁グリッドで bank に焼く
  - _paint_one_sprite: 1 sprite 分の絵を bank に焼きカーソルを進める
  - _record_layout_entry: tile/path/shore を bx/by に書き分ける private 委譲
  - _paint_16x16_cell: bank の (col*16, row*16) 起点に 16x16 を pset する
  - _advance_grid_cursor_in_place: col/row を自身の dict に保持し進める
- _advance_grid_cursor: col/row を 16 折返しで進める純粋関数

Problems:
    - pyxres の有無で tile/sprite/font バンクと tilemap の初期化経路が
      大きく分岐するため、public メソッドに制御フローを直書きすると
      CR203/CR204 違反が一気に増える。
    - 16 桁折返しの (col, row) 進行を毎所で持つと CR202 を超え、変更点も分散する。
    - layout 系 / paint 系の generator 走査を public で書くと CR203/CR204 に触る。

Solutions:
    - public メソッドは「private 委譲 + return」のステップ列だけにし、
      ループ・分岐・early return は ``_…`` private helper に閉じ込める。
    - 16 桁折返しの進行は ``_advance_grid_cursor`` 純粋関数 1 箇所に集める。
    - 命名規約 CR100/CR101 のため `setup_…` / `pyxres_loaded` /
      `tile_iter` 等は public な動詞接頭辞に改名しつつ、後方互換 alias を残す。
"""
from __future__ import annotations

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

    Args:
        main_runtime_file: ``main_runtime.py`` の絶対/相対パス。
    Returns:
        Path: 最初に見つかった候補。すべて不在のときは最後の候補。
    Policy:
        - 探索順は 1) bundle 隣、2) project root 直下、
          3) assets/blockquest.pyxres。
        - 存在チェックはここで行い、最初に True になった候補を返す。
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
    """tile / sprite / font バンク管理（P1-G13 で Game から 17 メソッド取込み）."""

    game: Any = None
    tile_bank: dict = field(default_factory=dict)
    sprite_bank: dict = field(default_factory=dict)
    path_variant_bank: dict = field(default_factory=dict)
    shore_variant_bank: dict = field(default_factory=dict)
    tile_id_by_pixel: dict = field(default_factory=dict)
    is_pyxres_loaded: bool = False
    pyxres_path: Path | None = None

    # === Public API ===

    @property
    def pyxres_loaded(self) -> bool:  # noqa: CR100 CR101
        """旧名 ``pyxres_loaded`` を保持する後方互換 alias。

        Returns:
            bool: ``is_pyxres_loaded`` と同じ値。
        Policy:
            - 命名規約 CR101 のため内部は ``is_pyxres_loaded`` に統一しつつ、
              既存呼び出し側との互換のために property で公開する。
        """
        return self.is_pyxres_loaded

    @pyxres_loaded.setter
    def pyxres_loaded(self, value: bool) -> None:  # noqa: CR100 CR501
        self.is_pyxres_loaded = bool(value)

    def load_image_banks(self) -> None:
        """画像・サウンドバンクを初期化する（pyxres ロードを含む）。

        Policy:
            - 重要: .pyxres は画像バンクと音バンクの両方を含むため、
              本メソッドが SfxSystem の slot を上書きし得る。
            - layout 計算 → pyxres 試行 → 失敗時に手続き描画、を private に委譲。
        """
        self._reset_layout_state()
        self._load_pyxres_or_repaint()

    def paint_jp_font_bank(self) -> None:
        """`JP_FONT_BITMAPS` を image bank 2 に焼き込む。

        Policy:
            - 全画面クリア後、レイアウト座標に従って 1 グリフずつ pset。
        """
        self._paint_jp_font_into(pyxel.images[JP_FONT_IMAGE_BANK])

    def build_reverse_tile_map(self) -> None:
        """image bank pixel 座標 → tile_id の逆引き辞書を組む。

        Policy:
            - tile_bank / path_variant_bank / shore_variant_bank を統合する。
        """
        self._reset_reverse_tile_map()
        self._fill_reverse_tile_map()

    def is_tile_bank_layout_valid(self) -> bool:
        """image bank 0 が現在の TILE_DATA と一致するかを返す。

        Returns:
            bool: 全 tile_id の 1 行目が一致すれば True。
        Policy:
            - pget 失敗等は False 扱い（呼び出し側は repaint に進む）。
        """
        return self._all_tiles_match_or_false()

    def load_world_tilemap(self) -> None:
        """World map と dungeon を `pyxel.tilemaps[0]` と同期する（新名）。

        Policy:
            - 旧名 ``setup_world_tilemap`` に委譲する（実体はそちら）。
        """
        self.setup_world_tilemap()

    def regenerate_dungeon_tilemap_fallback(self) -> None:  # noqa: CR203 CR204
        """pyxres 不在/破損時の fallback：dungeon を tilemap[0] dungeon 領域に焼く.

        Policy:
            - pyxres 読み込み済みのときは tilemap が SSoT なのでスキップ
              （Code Maker で編集した dungeon タイルの保護）。
            - 対称性のため冒頭に ``if self.pyxres_loaded: return`` を直書きする。
        """
        if self.pyxres_loaded:
            return
        self._paint_dungeon_tilemap_from_template()

    def derive_dungeon_from_tilemap(self) -> None:
        """tilemap[0] のオフセット領域から共有 dungeon を組み立てる。

        Policy:
            - 派生 grid を `game.dungeon_template` に書き戻し、最初の
              STAIR_UP を spawn 座標として採用する。
        """
        self._assign_derived_dungeon_to_game()

    def regenerate_world_tilemap_fallback(self) -> None:  # noqa: CR203 CR204
        """pyxres 不在/破損時の fallback：procedural に world を焼く.

        Policy:
            - pyxres 読み込み済みのときは tilemap が SSoT なのでスキップ
              （Code Maker で編集した道形状の保護）。
            - pyxres 不在時は ``generate_world_map()`` を直呼びする。
            - test_setup_world_tilemap_preserves_user_edits が AST で
              「冒頭が ``if self.pyxres_loaded: return``」を検証するため、
              本関数の冒頭はその形を直に書く。
        """
        if self.pyxres_loaded:
            return
        self._paint_world_tilemap_procedural()

    def iter_tiles(self):
        """タイルバンクに格納する順序を返す generator.

        Returns:
            Iterator: (kind, key, data) の三つ組を順に返す iterator。
        Policy:
            - tile → path → shore の順で yield する。kind は文字列。
        """
        return self._iter_tile_entries()

    def layout_tile_bank(self) -> None:  # noqa: CR100
        """レイアウト辞書のみ計算（pset なし）。

        Policy:
            - ``iter_tiles()`` の順を 16 桁折返しのグリッドに割り付ける。
            - 互換のため動詞接頭辞は付けず ``layout_*`` を維持する。
        """
        self._reset_layout_dicts()
        self._fill_layout_dicts()

    def paint_tile_bank(self) -> None:
        """pset でタイル絵を image bank 0 に焼き込む。

        Policy:
            - ``iter_tiles()`` の順を 16 桁折返しでグリッドに描画する。
        """
        self._paint_tiles_into(pyxel.images[0])

    def render_tiles_to_bank(self) -> None:
        """互換ラッパー：layout + paint を順に呼ぶ.

        Policy:
            - 旧 API 維持のためだけに残す。
        """
        self.layout_tile_bank()
        self.paint_tile_bank()

    def iter_sprites(self):
        """スプライト名と pixel data を順に返す generator.

        Returns:
            Iterator: (name, sdata) の二つ組を順に返す iterator。
        Policy:
            - hero と enemy_sprites を 1 dict にまとめて順序を確定する。
        """
        return self._iter_sprite_entries()

    def layout_sprite_bank(self) -> None:  # noqa: CR100
        """スプライトのレイアウト辞書のみ計算（pset なし）。

        Policy:
            - ``iter_sprites()`` の順を 16 桁折返しのグリッドに割り付ける。
        """
        self._reset_sprite_layout()
        self._fill_sprite_layout()

    def paint_sprite_bank(self) -> None:
        """pset でスプライト絵を image bank 1 に焼き込む。

        Policy:
            - ``iter_sprites()`` の順を 16 桁折返しでグリッドに描画する。
        """
        self._paint_sprites_into(pyxel.images[1])

    def render_sprites_to_bank(self) -> None:
        """互換ラッパー：layout + paint を順に呼ぶ.

        Policy:
            - 旧 API 維持のためだけに残す。
        """
        self.layout_sprite_bank()
        self.paint_sprite_bank()

    # ---- 後方互換 alias（旧名で呼ばれる API を維持） ----

    def setup_image_banks(self) -> None:  # noqa: CR100
        """旧名 ``setup_image_banks`` を維持する後方互換 alias。

        Policy:
            - 既存呼び出し（Game.__init__ 等）が動く間は残す。
        """
        self.load_image_banks()

    def setup_world_tilemap(self) -> None:  # noqa: CR100 CR203 CR204
        """World map と dungeon を `pyxel.tilemaps[0]` と同期する。

        Policy:
            - pyxres が SSoT のときは tilemap には触らず image bank のみ修復。
            - pyxres 不在時は手続き生成で tilemap を焼き、可能なら保存する。
            - test_setup_world_tilemap_preserves_user_edits が AST で
              ``if self.pyxres_loaded:`` 分岐から
              ``self.regenerate_world_tilemap_fallback`` 呼び出しを期待するため、
              関数本体に明示的な分岐を直書きする。
        """
        self._ensure_imgsrc_zero()
        self._build_dungeon_template()
        if self.pyxres_loaded:
            self._repaint_image_bank_if_layout_changed()
            self.derive_dungeon_from_tilemap()
            self.regenerate_world_tilemap_fallback()
            self.regenerate_dungeon_tilemap_fallback()
            return
        self.regenerate_world_tilemap_fallback()
        self.regenerate_dungeon_tilemap_fallback()
        self._save_pyxres_if_possible()

    def tile_bank_layout_valid(self) -> bool:
        """旧名 ``tile_bank_layout_valid`` を維持する後方互換 alias。

        Returns:
            bool: ``is_tile_bank_layout_valid`` と同じ値。
        Policy:
            - 既存テストや呼び出しを壊さないために残す。
        """
        return self.is_tile_bank_layout_valid()

    def tile_iter(self):
        """旧名 ``tile_iter`` を維持する後方互換 alias。

        Returns:
            Iterator: ``iter_tiles()`` と同じ iterator。
        Policy:
            - 既存テストや呼び出しを壊さないために残す。
        """
        return self.iter_tiles()

    def sprite_iter(self):  # noqa: CR100
        """旧名 ``sprite_iter`` を維持する後方互換 alias。

        Returns:
            Iterator: ``iter_sprites()`` と同じ iterator。
        Policy:
            - 既存テストや呼び出しを壊さないために残す。
        """
        return self.iter_sprites()

    # === Internal helpers (private) ===

    def _reset_layout_state(self) -> None:
        """レイアウトと pyxres state を初期化する。

        Policy:
            - layout 系を呼び直し、pyxres フラグもリセットする。
        """
        self.layout_tile_bank()
        self.layout_sprite_bank()
        self.build_reverse_tile_map()
        self.is_pyxres_loaded = False
        self.pyxres_path = None

    def _load_pyxres_or_repaint(self) -> None:
        """pyxres をロードできれば終わり、ダメなら手続き再描画する。

        Policy:
            - 早期 return で 2 経路を直列に並べる。
        """
        import src.runtime.main_runtime as M
        pyxres_path = resolve_pyxres_path(M.__file__)
        self.pyxres_path = pyxres_path
        if self._try_load_pyxres(pyxres_path):
            return
        self._paint_all_banks_from_data()

    def _try_load_pyxres(self, pyxres_path: Path) -> bool:
        """指定 pyxres を読み込めたかを返す述語。

        Args:
            pyxres_path: ロードを試みる .pyxres のパス。
        Returns:
            bool: pyxel.load に成功すれば True、それ以外は False。
        Policy:
            - 存在しない／load 失敗時は False を返し、ログだけ残す。
        """
        if not pyxres_path.exists():
            return False
        return self._do_pyxres_load(pyxres_path)

    def _do_pyxres_load(self, pyxres_path: Path) -> bool:
        """例外を握って pyxel.load を試行する private 委譲。

        Args:
            pyxres_path: ロード対象パス（exists 前提）。
        Returns:
            bool: 成功なら True、例外なら False。
        Policy:
            - 副作用は pyxel.load と print のみ。
        """
        try:
            pyxel.load(str(pyxres_path))
            self.is_pyxres_loaded = True
            return True
        except Exception as exc:
            print(
                f"[image_bank] failed to load {pyxres_path}: "
                f"{exc}; regenerating"
            )
            return False

    def _paint_all_banks_from_data(self) -> None:
        """tile/sprite/jp_font の三バンクをまとめて焼く private 委譲。

        Policy:
            - pyxres 不在時の手続き再生成 1 か所に閉じ込める。
        """
        self.paint_tile_bank()
        self.paint_sprite_bank()
        self.paint_jp_font_bank()

    def _paint_jp_font_into(self, bank) -> None:
        """jp_font bank をクリアしてからグリフを焼く。

        Args:
            bank: 焼き先となる pyxel image bank。
        Policy:
            - clear → glyph paint の 2 段に分割して責務を分ける。
        """
        self._clear_jp_font_bank(bank)
        self._paint_jp_font_glyphs(bank)

    def _clear_jp_font_bank(self, bank) -> None:
        """jp_font bank を全画素 0 で埋める。

        Args:
            bank: クリア対象の pyxel image bank。
        Policy:
            - 256x256 の総走査で副作用のみ。
        """
        for py in range(256):
            for px in range(256):
                bank.pset(px, py, 0)

    def _paint_jp_font_glyphs(self, bank) -> None:
        """`JP_FONT_BITMAPS` の各グリフを bank に焼く。

        Args:
            bank: 焼き先となる pyxel image bank。
        Policy:
            - レイアウトに従って 1 グリフずつ ``_paint_one_glyph`` に委譲する。
        """
        for ch, rows in JP_FONT_BITMAPS.items():
            col, row = JP_FONT_LAYOUT[ch]
            ox = col * JP_FONT_GLYPH_W
            oy = row * JP_FONT_GLYPH_H
            self._paint_one_glyph(bank, ox, oy, rows)

    def _paint_one_glyph(self, bank, ox: int, oy: int, rows) -> None:
        """1 グリフ分のビット列を bank に pset する。

        Args:
            bank: 焼き先 image bank。
            ox: グリフの左上 X 座標。
            oy: グリフの左上 Y 座標。
            rows: グリフ行ビット列（整数列）。
        Policy:
            - 最上位ビット側を左ピクセルとして展開する。
        """
        for ry in range(JP_FONT_GLYPH_H):
            bits = rows[ry] if ry < len(rows) else 0
            for rx in range(JP_FONT_GLYPH_W):
                if bits & (1 << (JP_FONT_GLYPH_W - 1 - rx)):
                    bank.pset(ox + rx, oy + ry, 7)

    def _reset_reverse_tile_map(self) -> None:
        """逆引き辞書を空 dict にリセットする。

        Policy:
            - 副作用 1 行のみ。
        """
        self.tile_id_by_pixel = {}

    def _fill_reverse_tile_map(self) -> None:
        """tile / path / shore の全 bank を逆引き辞書に転写する。

        Policy:
            - path/shore は元の tile_id が同じなので main_runtime の定数を使う。
        """
        import src.runtime.main_runtime as M
        self._record_reverse_tile_entries()
        self._record_reverse_path_entries(M.T_PATH)
        self._record_reverse_shore_entries(M.T_WATER)

    def _record_reverse_tile_entries(self) -> None:
        """tile_bank → tile_id_by_pixel に転写する。

        Policy:
            - 1:1 マッピングなのでループのみ。
        """
        for tid, (u, v) in self.tile_bank.items():
            self.tile_id_by_pixel[(u, v)] = tid

    def _record_reverse_path_entries(self, t_path: int) -> None:
        """path_variant_bank のピクセル座標を T_PATH に対応付ける。

        Args:
            t_path: main_runtime.T_PATH の整数値。
        Policy:
            - 全 variant が同じ tile_id に潰れる仕様。
        """
        for (u, v) in self.path_variant_bank.values():
            self.tile_id_by_pixel[(u, v)] = t_path

    def _record_reverse_shore_entries(self, t_water: int) -> None:
        """shore_variant_bank のピクセル座標を T_WATER に対応付ける。

        Args:
            t_water: main_runtime.T_WATER の整数値。
        Policy:
            - 全 variant が同じ tile_id に潰れる仕様。
        """
        for (u, v) in self.shore_variant_bank.values():
            self.tile_id_by_pixel[(u, v)] = t_water

    def _all_tiles_match_or_false(self) -> bool:  # noqa: CR100
        """例外を False に変換しつつ全タイル一致判定を行う。

        Returns:
            bool: 全 tile_id について 1 行目が一致すれば True、例外時は False。
        Policy:
            - pget 失敗等を握り潰して fallback 経路に進める。
        """
        import src.runtime.main_runtime as M
        bank = pyxel.images[0]
        try:
            return self._all_tiles_match(bank, M.TILE_DATA)
        except Exception:
            return False

    def _all_tiles_match(self, bank, tile_data) -> bool:  # noqa: CR100
        """全 tile_id について 1 行目が一致するかを返す。

        Args:
            bank: 検査対象 image bank。
            tile_data: main_runtime.TILE_DATA。
        Returns:
            bool: 全一致なら True、欠落や不一致が 1 件でもあれば False。
        Policy:
            - pos 未登録は False、行不一致も即 False。
        """
        for tid, data in tile_data.items():
            pos = self.tile_bank.get(tid)
            if pos is None:
                return False
            u, v = pos
            if not self._row_matches(bank, u, v, data[0]):
                return False
        return True

    def _row_matches(self, bank, u: int, v: int, expected_row) -> bool:
        """bank の (u, v) 行が expected_row と一致するかを返す。

        Args:
            bank: 検査対象 image bank。
            u: 開始 X 座標。
            v: Y 座標。
            expected_row: 期待するピクセル列。
        Returns:
            bool: 全ピクセル一致なら True。
        Policy:
            - 1 ピクセルでも不一致なら False を早期 return。
        """
        for rx, expected in enumerate(expected_row):
            if bank.pget(u + rx, v) != expected:
                return False
        return True

    def _ensure_imgsrc_zero(self) -> None:
        """tilemap[0].imgsrc=0 を best-effort で適用する。

        Policy:
            - 例外は握り潰す（古い pyxel API でも動かしたいため）。
        """
        try:
            pyxel.tilemaps[0].imgsrc = 0
        except Exception:
            pass

    def _build_dungeon_template(self) -> None:
        """dungeon grid と spawn 座標を game に書き込む。

        Policy:
            - 固定 seed=99 で生成。room 配列の先頭から spawn を割り当てる。
        """
        import src.runtime.main_runtime as M
        game = self.game
        dgrid, drooms = M.generate_dungeon(seed=99)
        game.dungeon_template = dgrid
        game.dungeon_template_rooms = drooms
        game.dungeon_spawn = self._compute_initial_spawn(drooms)

    def _compute_initial_spawn(self, drooms) -> tuple[int, int]:
        """最初の room から初期 spawn 座標を返す。

        Args:
            drooms: ``generate_dungeon`` が返す room 配列。
        Returns:
            tuple[int, int]: spawn の (x, y)。room 不在時は (1, 1)。
        Policy:
            - 先頭 room の左上 +1 をデフォルト spawn とする。
        """
        if drooms:
            return (drooms[0][0] + 1, drooms[0][1] + 1)
        return (1, 1)

    def _repaint_image_bank_if_layout_changed(self) -> None:
        """layout 不一致のときだけ image bank の三バンクを焼き直す。

        Policy:
            - tilemap には触らず image bank のみ更新する（ユーザー編集保護）。
        """
        if self.is_tile_bank_layout_valid():
            return
        print(
            "[tilemap] tile bank layout changed — "
            "repainting image bank only"
        )
        self._paint_all_banks_from_data()

    def _save_pyxres_if_possible(self) -> None:
        """pyxres を best-effort で書き出す。

        Policy:
            - emscripten 環境では書き込まない。失敗時もログだけで継続。
        """
        if self.pyxres_path is None:
            return
        if sys.platform == "emscripten":
            return
        self._save_pyxres_now()

    def _save_pyxres_now(self) -> None:
        """pyxel.save を実行する private 委譲。

        Policy:
            - 親フォルダを作ってから save。例外はログだけで握り潰す。
        """
        try:
            self.pyxres_path.parent.mkdir(parents=True, exist_ok=True)
            pyxel.save(str(self.pyxres_path))
            print(f"[image_bank] generated {self.pyxres_path}")
        except Exception as exc:
            print(f"[image_bank] could not save .pyxres: {exc}")

    def _paint_dungeon_tilemap_from_template(self) -> None:
        """dungeon grid を tilemap の dungeon 領域に書く。

        Policy:
            - 1 マスあたり 4 ピクセル分の pset を ``_paint_dungeon_cell`` に委譲。
        """
        import src.runtime.main_runtime as M
        game = self.game
        tilemap = pyxel.tilemaps[0]
        dg = game.dungeon_template
        oy = DUNGEON_TM_OFFSET_Y
        for x, y, tile in self._iter_dungeon_cells(dg):
            u, v = self.tile_bank.get(tile, self.tile_bank[M.T_GRASS])
            self._paint_dungeon_cell(tilemap, x, y, oy, u, v)

    def _iter_dungeon_cells(self, dg):
        """dungeon grid を (x, y, tile) で順に返す。

        Args:
            dg: 2 次元 dungeon grid（dg[y][x] = tile_id）。
        Returns:
            Iterator: (x, y, tile_id) を yield する iterator。
        Policy:
            - 行優先で順序を固定する。
        """
        for y in range(len(dg)):
            for x in range(len(dg[0])):
                yield (x, y, dg[y][x])

    def _paint_dungeon_cell(
        self, tilemap, x: int, y: int, oy: int, u: int, v: int
    ) -> None:
        """4 マス分の tilemap pset を 1 タイル分まとめて行う。

        Args:
            tilemap: pyxel.tilemaps[0]。
            x: グリッド列。
            y: グリッド行。
            oy: tilemap 内の Y オフセット（DUNGEON_TM_OFFSET_Y）。
            u: image bank の X ピクセル。
            v: image bank の Y ピクセル。
        Policy:
            - 8x8 タイル単位に変換して 4 マスに展開する。
        """
        tu, tv = u // 8, v // 8
        tilemap.pset(2 * x, oy + 2 * y, (tu, tv))
        tilemap.pset(2 * x + 1, oy + 2 * y, (tu + 1, tv))
        tilemap.pset(2 * x, oy + 2 * y + 1, (tu, tv + 1))
        tilemap.pset(2 * x + 1, oy + 2 * y + 1, (tu + 1, tv + 1))

    def _assign_derived_dungeon_to_game(self) -> None:
        """tilemap から派生した dungeon を game に書き spawn を確定する。

        Policy:
            - derived → game.dungeon_template → spawn の 3 ステップに分解。
        """
        derived = self._build_derived_dungeon_grid()
        self.game.dungeon_template = derived
        self._find_dungeon_spawn(derived)

    def _build_derived_dungeon_grid(self) -> list:
        """tilemap から dungeon grid を派生する。

        Returns:
            list: 派生した 2 次元 grid。
        Policy:
            - 逆引きに乗らないマスは T_FLOOR に潰し、件数をログする。
        """
        import src.runtime.main_runtime as M
        game = self.game
        tilemap = pyxel.tilemaps[0]
        dg = game.dungeon_template
        derived = []
        miss_count = 0
        for y in range(len(dg)):
            row, row_miss = self._derive_dungeon_row(
                tilemap, len(dg[0]), y, M.T_FLOOR
            )
            derived.append(row)
            miss_count += row_miss
        self._log_dungeon_miss_count(miss_count)
        return derived

    def _log_dungeon_miss_count(self, miss_count: int) -> None:
        """逆引きミス件数をログする。

        Args:
            miss_count: T_FLOOR に潰されたタイル数。
        Policy:
            - 0 件のときは無音、それ以外だけ print。
        """
        if not miss_count:
            return
        print(
            f"[tilemap] dungeon derive: "
            f"{miss_count} tiles fell back to T_FLOOR"
        )

    def _derive_dungeon_row(
        self, tilemap, width: int, y: int, t_floor: int
    ) -> tuple[list, int]:
        """1 行分の dungeon を tilemap から派生する。

        Args:
            tilemap: pyxel.tilemaps[0]。
            width: 派生する列数。
            y: 行 index（dungeon 内座標）。
            t_floor: 逆引きミス時の fallback tile_id。
        Returns:
            tuple[list, int]: (1 行分の tile_id 列, ミス件数)。
        Policy:
            - ミスは miss カウンタで計上するだけで行自体は埋める。
        """
        row: list = []
        miss = 0
        oy = DUNGEON_TM_OFFSET_Y
        for x in range(width):
            tid, hit = self._derive_dungeon_cell_id(
                tilemap, x, y, oy, t_floor
            )
            row.append(tid)
            if not hit:
                miss += 1
        return row, miss

    def _derive_dungeon_cell_id(
        self, tilemap, x: int, y: int, oy: int, t_floor: int
    ) -> tuple[int, bool]:
        """tilemap から 1 マス分の tile_id と「逆引きヒットしたか」を返す。

        Args:
            tilemap: pyxel.tilemaps[0]。
            x: 列。
            y: 行。
            oy: dungeon 領域の Y オフセット。
            t_floor: 逆引きミス時の fallback tile_id。
        Returns:
            tuple[int, bool]: (tile_id, hit)。
        Policy:
            - key 不在のときは (t_floor, False)。
        """
        tu, tv = tilemap.pget(2 * x, oy + 2 * y)
        key = (tu * 8, tv * 8)
        if key in self.tile_id_by_pixel:
            return self.tile_id_by_pixel[key], True
        return t_floor, False

    def _find_dungeon_spawn(self, derived) -> None:
        """derived grid から STAIR_UP の座標を spawn として採用する。

        Args:
            derived: 派生した dungeon grid。
        Policy:
            - 最初に見つかった 1 箇所だけ使う。
        """
        import src.runtime.main_runtime as M
        game = self.game
        for y in range(len(derived)):
            for x in range(len(derived[0])):
                if derived[y][x] == M.T_STAIR_UP:
                    game.dungeon_spawn = (x, y)
                    return

    def _paint_world_tilemap_procedural(self) -> None:
        """generate_world_map() の結果を tilemap[0] に焼く。

        Policy:
            - tile 種別の解決は ``_resolve_world_tile_pixel`` に委譲。
        """
        import src.runtime.main_runtime as M
        tilemap = pyxel.tilemaps[0]
        wm = generate_world_map()
        for y in range(M.MAP_H):
            for x in range(M.MAP_W):
                u, v = self._resolve_world_tile_pixel(M, wm, x, y)
                self._paint_world_cell(tilemap, x, y, u, v)

    def _resolve_world_tile_pixel(self, M, wm, x: int, y: int):
        """world map 1 マス分の (u, v) を返す。

        Args:
            M: main_runtime モジュール。
            wm: world map grid。
            x: 列。
            y: 行。
        Returns:
            tuple[int, int]: image bank 上の (u, v)。
        Policy:
            - T_PATH / T_WATER は variant 解決、それ以外は tile_bank 直引き。
        """
        tile = wm[y][x]
        if tile == M.T_PATH:
            return self._resolve_path_pixel(M, wm, x, y)
        if tile == M.T_WATER:
            return self._resolve_water_pixel(M, wm, x, y)
        return self.tile_bank.get(tile, self.tile_bank[M.T_GRASS])

    def _resolve_path_pixel(self, M, wm, x: int, y: int):
        """T_PATH 用の variant pixel を返す。

        Args:
            M: main_runtime モジュール。
            wm: world map grid。
            x: 列。
            y: 行。
        Returns:
            tuple[int, int]: variant に対応する (u, v)。
        Policy:
            - variant 不在時は T_PATH の代表座標にフォールバック。
        """
        variant = M.get_path_variant(wm, x, y)
        return self.path_variant_bank.get(
            id(variant),
            self.tile_bank[M.T_PATH],
        )

    def _resolve_water_pixel(self, M, wm, x: int, y: int):
        """T_WATER 用の shore variant pixel を返す。

        Args:
            M: main_runtime モジュール。
            wm: world map grid。
            x: 列。
            y: 行。
        Returns:
            tuple[int, int]: shore variant に対応する (u, v)。
        Policy:
            - variant=None / 不在時は T_WATER の代表座標にフォールバック。
        """
        variant = M.get_shore_variant(wm, x, y)
        if variant is None:
            return self.tile_bank[M.T_WATER]
        return self.shore_variant_bank.get(
            id(variant),
            self.tile_bank[M.T_WATER],
        )

    def _paint_world_cell(
        self, tilemap, x: int, y: int, u: int, v: int
    ) -> None:
        """4 マス分の tilemap pset を 1 タイル分まとめて行う。

        Args:
            tilemap: pyxel.tilemaps[0]。
            x: 列。
            y: 行。
            u: image bank の X ピクセル。
            v: image bank の Y ピクセル。
        Policy:
            - 8x8 タイル単位に変換して 4 マスに展開する。
        """
        tu, tv = u // 8, v // 8
        tilemap.pset(2 * x, 2 * y, (tu, tv))
        tilemap.pset(2 * x + 1, 2 * y, (tu + 1, tv))
        tilemap.pset(2 * x, 2 * y + 1, (tu, tv + 1))
        tilemap.pset(2 * x + 1, 2 * y + 1, (tu + 1, tv + 1))

    def _iter_tile_entries(self):
        """tile/path/shore を kind タグ付きで順に yield する。

        Policy:
            - public ``iter_tiles()`` の本体を担う private 委譲。
        """
        import src.runtime.main_runtime as M
        yield from self._yield_tile_entries(M.TILE_DATA)
        yield from self._yield_path_variants(M)
        yield from self._yield_shore_variants(M)

    def _yield_tile_entries(self, tile_data):
        """tile_data を kind="tile" で順に yield する。

        Args:
            tile_data: main_runtime.TILE_DATA。
        Policy:
            - dict のキー順を保ったまま yield する。
        """
        for tid, tdata in tile_data.items():
            yield ("tile", tid, tdata)

    def _yield_path_variants(self, M):
        """path 系 variant を kind="path" で順に yield する。

        Args:
            M: main_runtime モジュール。
        Policy:
            - 順序は描画レイアウトと逆引きで安定させる。
        """
        entries = [
            M.PATH_V, M.PATH_H, M.PATH_CROSS,
            M.PATH_SE, M.PATH_SW, M.PATH_NE, M.PATH_NW,
            M.PATH_T_NES, M.PATH_T_NWS,
            M.PATH_T_EWS, M.PATH_T_NEW,
        ]
        for pdata in entries:
            yield ("path", id(pdata), pdata)

    def _yield_shore_variants(self, M):
        """shore 系 variant を kind="shore" で順に yield する。

        Args:
            M: main_runtime モジュール。
        Policy:
            - 順序は描画レイアウトと逆引きで安定させる。
        """
        entries = [
            M.SHORE_N, M.SHORE_S, M.SHORE_W, M.SHORE_E,
            M.SHORE_NE, M.SHORE_NW, M.SHORE_SE, M.SHORE_SW,
        ]
        for sdata in entries:
            yield ("shore", id(sdata), sdata)

    def _reset_layout_dicts(self) -> None:
        """tile / path / shore のレイアウト辞書を空に戻す。

        Policy:
            - dict を新規割り当てで初期化する。
        """
        self.tile_bank = {}
        self.path_variant_bank = {}
        self.shore_variant_bank = {}

    def _fill_layout_dicts(self) -> None:
        """``iter_tiles()`` 全件を 16 桁グリッドに割り付ける。

        Policy:
            - 1 件あたり ``_layout_one_tile`` に委譲する。
        """
        cursor = {"col": 0, "row": 0}
        for kind, key, _data in self.iter_tiles():
            self._layout_one_tile(cursor, kind, key)

    def _layout_one_tile(  # noqa: CR100
        self, cursor: dict, kind: str, key
    ) -> None:
        """1 タイル分のレイアウトを記録しカーソルを進める。

        Args:
            cursor: {"col": int, "row": int} を保持する dict。
            kind: "tile"/"path"/"shore" のいずれか。
            key: 各辞書のキー。
        Policy:
            - cursor は in-place 更新する（呼び出し側のループに整合）。
        """
        bx = cursor["col"] * 16
        by = cursor["row"] * 16
        self._record_layout_entry(kind, key, bx, by)
        self._advance_grid_cursor_in_place(cursor)

    def _paint_tiles_into(self, bank) -> None:
        """``iter_tiles()`` 全件を 16 桁グリッドで bank に焼く。

        Args:
            bank: 焼き先 image bank。
        Policy:
            - 1 件あたり ``_paint_one_tile`` に委譲する。
        """
        cursor = {"col": 0, "row": 0}
        for _kind, _key, data in self.iter_tiles():
            self._paint_one_tile(cursor, bank, data)

    def _paint_one_tile(self, cursor: dict, bank, data) -> None:
        """1 タイル分の絵を bank に焼きカーソルを進める。

        Args:
            cursor: {"col": int, "row": int} を保持する dict。
            bank: 焼き先 image bank。
            data: 16x16 ピクセル配列。
        Policy:
            - cursor は in-place 更新する。
        """
        self._paint_16x16_cell(bank, cursor["col"], cursor["row"], data)
        self._advance_grid_cursor_in_place(cursor)

    def _reset_sprite_layout(self) -> None:
        """sprite_bank を空に戻す。

        Policy:
            - dict を新規割り当てで初期化する。
        """
        self.sprite_bank = {}

    def _fill_sprite_layout(self) -> None:
        """``iter_sprites()`` 全件を 16 桁グリッドに割り付ける。

        Policy:
            - 1 件あたり ``_layout_one_sprite`` に委譲する。
        """
        cursor = {"col": 0, "row": 0}
        for name, _data in self.iter_sprites():
            self._layout_one_sprite(cursor, name)

    def _layout_one_sprite(  # noqa: CR100
        self, cursor: dict, name: str
    ) -> None:
        """1 sprite 分のレイアウトを記録しカーソルを進める。

        Args:
            cursor: {"col": int, "row": int} を保持する dict。
            name: sprite_bank に登録するキー名。
        Policy:
            - cursor は in-place 更新する。
        """
        self.sprite_bank[name] = (cursor["col"] * 16, cursor["row"] * 16)
        self._advance_grid_cursor_in_place(cursor)

    def _iter_sprite_entries(self):
        """hero と enemy_sprites を 1 dict にまとめて yield する。

        Policy:
            - public ``iter_sprites()`` の本体を担う private 委譲。
        """
        import src.runtime.main_runtime as M
        sprites_to_render = {
            "hero_down": M.HERO_DOWN, "hero_walk": M.HERO_DOWN_WALK,
        }
        sprites_to_render.update(M.ENEMY_SPRITES)
        for name, sdata in sprites_to_render.items():
            yield (name, sdata)

    def _paint_sprites_into(self, bank) -> None:
        """``iter_sprites()`` 全件を 16 桁グリッドで bank に焼く。

        Args:
            bank: 焼き先 image bank。
        Policy:
            - 1 件あたり ``_paint_one_sprite`` に委譲する。
        """
        cursor = {"col": 0, "row": 0}
        for _name, sdata in self.iter_sprites():
            self._paint_one_sprite(cursor, bank, sdata)

    def _paint_one_sprite(self, cursor: dict, bank, sdata) -> None:
        """1 sprite 分の絵を bank に焼きカーソルを進める。

        Args:
            cursor: {"col": int, "row": int} を保持する dict。
            bank: 焼き先 image bank。
            sdata: 16x16 ピクセル配列。
        Policy:
            - cursor は in-place 更新する。
        """
        self._paint_16x16_cell(bank, cursor["col"], cursor["row"], sdata)
        self._advance_grid_cursor_in_place(cursor)

    def _record_layout_entry(
        self, kind: str, key, bx: int, by: int
    ) -> None:
        """tile/path/shore を bx/by に書き分ける private 委譲。

        Args:
            kind: "tile"/"path"/"shore"。
            key: 各辞書のキー。
            bx: image bank 上の X ピクセル。
            by: image bank 上の Y ピクセル。
        Policy:
            - 不明な kind は記録しない（早期 return）。
        """
        if kind == "tile":
            self.tile_bank[key] = (bx, by)
            return
        if kind == "path":
            self.path_variant_bank[key] = (bx, by)
            return
        if kind == "shore":
            self.shore_variant_bank[key] = (bx, by)

    def _paint_16x16_cell(
        self, bank, col: int, row: int, data
    ) -> None:
        """bank の (col*16, row*16) 起点に 16x16 を pset する。

        Args:
            bank: 焼き先 image bank。
            col: グリッド列。
            row: グリッド行。
            data: 16x16 ピクセル配列。
        Policy:
            - data[py][px] をそのまま pset する。
        """
        bx = col * 16
        by = row * 16
        for py in range(16):
            for px in range(16):
                bank.pset(bx + px, by + py, data[py][px])

    def _advance_grid_cursor_in_place(self, cursor: dict) -> None:
        """cursor (dict) の col/row を 16 折返しで進める。

        Args:
            cursor: {"col": int, "row": int}。
        Policy:
            - 純粋関数 ``_advance_grid_cursor`` の結果を dict に書き戻す。
        """
        col, row = _advance_grid_cursor(cursor["col"], cursor["row"])
        cursor["col"] = col
        cursor["row"] = row


def _advance_grid_cursor(col: int, row: int) -> tuple[int, int]:
    """16 桁折返しで 1 マス進めた (col, row) を返す純粋関数。

    Args:
        col: 現在の列。
        row: 現在の行。
    Returns:
        tuple[int, int]: 1 マス進めた (col, row)。
    Policy:
        - col が 16 以上になったら row を 1 つ進め col=0 に戻す。
    """
    col += 1
    if col >= 16:
        return 0, row + 1
    return col, row
