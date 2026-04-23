from __future__ import annotations

"""pyxres ロードと tile / sprite / font バンクのセットアップ（Phase 1 スケルトン）。

Q5A 決定：単一ファイルで 19 メソッドを保有する。P1-G13 で Game クラスから
以下を取り込む：
- _setup_image_banks / _paint_jp_font_bank / _build_reverse_tile_map
- _tile_bank_layout_valid / _setup_world_tilemap
- _bake_dungeon_to_tilemap / _derive_dungeon_from_tilemap
- _bake_world_to_tilemap / _derive_world_from_tilemap
- _tile_iter / _layout_tile_bank / _paint_tile_bank / _render_tiles_to_bank
- _sprite_iter / _layout_sprite_bank / _paint_sprite_bank / _render_sprites_to_bank

保有 state（P1-B inventory 由来）:
- font, has_jp_font, tile_bank, tile_bank_water2, sprite_bank,
  path_variant_bank, shore_variant_bank, tile_id_by_pixel,
  _pyxres_loaded, _pyxres_path
"""

from dataclasses import dataclass, field


@dataclass
class ImageBanks:
    """tile / sprite / font バンクの受け皿（P1-G13 で中身を埋める）。"""

    font: object | None = None
    has_jp_font: bool = False
    tile_bank: dict = field(default_factory=dict)
    tile_bank_water2: object | None = None
    sprite_bank: dict = field(default_factory=dict)
    path_variant_bank: dict = field(default_factory=dict)
    shore_variant_bank: dict = field(default_factory=dict)
    tile_id_by_pixel: dict = field(default_factory=dict)
    pyxres_loaded: bool = False
    pyxres_path: str | None = None
