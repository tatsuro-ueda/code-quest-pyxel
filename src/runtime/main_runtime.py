"""Block Quest — Single-file build for Pyxel Code Maker.

GENERATED FILE — do not edit by hand.
Source of truth: main.py + src/*.py
Regenerate via: python tools/build_codemaker.py

Known limitations on Code Maker:
- Japanese text falls back to English (BDF font cannot be loaded)
- save.json file I/O may not work; use the localStorage path
"""
from __future__ import annotations
import sys


# audio_system 一式は下で import（CHIPTUNE_TRACKS 含む）

from src.shared.services.input_bindings import (
    UP_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
    TITLE_START_BUTTONS,
    BUTTON_GROUPS,
    any_btn,
    any_btnp,
    InputStateTracker,
)

from src.shared.services.landmark_events import (
    LandmarkEvent,
    LANDMARK_EVENTS,
    find_landmark_event,
    find_landmark_at,
    resolve_scene,
)

from src.shared.services.player_state import (
    MAX_LEVEL,
    SAVE_VERSION,
    SAVED_PLAYER_KEYS,
    exp_for_level,
    stats_for_level,
    create_initial_player,
    dump_snapshot,
    restore_snapshot,
)

from src.shared.services.save_store import (
    SaveStoreError,
    SaveStore,
    SUPPORTED_SAVE_VERSIONS,
    InMemorySaveStore,
    FileSaveStore,
    LocalStorageSaveStore,
    make_save_store,
)

from src.shared.services.browser_resource_override import (
    BROWSER_IMPORT_ZIP_KEY,
    BROWSER_IMPORT_META_KEY,
    stage_browser_imported_resource,
)

from src.shared.services.audio_system import (
    SFX_CHANNEL,
    SFX_BASE_SLOT,
    SFX_DEFINITIONS,
    SfxSystem,
)

from src.shared.services.dialog_runner import (
    DialogChoice,
    DialogStep,
    DialogValidationError,
    StructuredDialogRunner,
)

from src.shared.services.audio_system import (
    CHIPTUNE_TRACKS,
    TRACK_ORDER,
    MELODY_CHANNEL,
    BASS_CHANNEL,
    DRUM_CHANNEL,
    BGM_CHANNEL,
    melody_slot,
    bass_slot,
    drum_slot,
    music_index,
    track_slot,
    choose_bgm_scene,
    AudioManager,
)

from src.game_data import (
    ASSETS_DIR,
    load_yaml,
    ENEMIES,
    ITEMS,
    WEAPONS,
    ARMORS,
    SPELLS,
    SHOPS,
    DIALOGUE_JA,
    DIALOGUE_EN,
    ZONE_ENEMIES,
    GLITCH_LORD_DATA,
    PROFESSOR_DATA,
    GLITCH_CLONE_DATA,
    NOISE_GUARDIAN_DATA,
    SPELL_BY_NAME,
    INN_PRICES,
    SHOP_LIST,
    GLITCH_LORD_PHASE_MESSAGES,
    glitch_lord_phase,
    load_enemies,
    load_items,
    load_weapons,
    load_armors,
    load_spells,
    load_shops,
    load_dialogue,
)
# _build_zone_enemies は 2 定義あった：(a) game_data.py のゾーン索引化
# (b) world 生成内の別用途。ここでは (a) を使うので game_data からは import せず、
# world 側の (b) は残しておく（P1-D1 で world_generation.py に分離時に確定）。

from typing import Any

from src.shared.assets.jp_font_data import (
    JP_FONT_GLYPH_W,
    JP_FONT_GLYPH_H,
    JP_FONT_COLS,
    JP_FONT_ROWS,
    JP_FONT_IMAGE_BANK,
    JP_FONT_LAYOUT,
    JP_FONT_BITMAPS,
)


# === inline adapter: alias for stripped imports ===
_SHOP_BUNDLE = SHOPS


# === main.py body ===
"""Block Quest - Pyxel RPG (single-file for app2html export)"""
import pyxel
import random
from pathlib import Path


from src.shared.constants.tile_data import *  # TILE_*, T_*, PATH_*, SHORE_*, MAP_W/H, CASTLE_POS 等を一括 import
from src.shared.constants.tile_data import (
    _PATH_VARIANTS,
    _SHORE_VARIANTS,
    _ZONE_DECORATIONS,
)  # `import *` は _ 始まりを除外するため個別 import

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

# =====================================================================
# SPRITE DATA
# =====================================================================
HERO_DOWN = [
    [ 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15, 8, 0, 8,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,14,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0,12,12,12,12,12,12,12,12,12, 0, 0, 0, 0],
    [ 0, 0,15,12,12,12,12,12,12,12,12,12,15, 0, 0, 0],
    [ 0, 0,15,12, 1,12,12,12,12,12, 1,12,15, 0, 0, 0],
    [ 0, 0, 0,12,12,12,12,12,12,12,12,12, 0, 0, 0, 0],
    [ 0, 0, 0,12,12,12, 1,12, 1,12,12,12, 0, 0, 0, 0],
    [ 0, 0, 0, 0,12,12, 1,12, 1,12,12, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0,15,15, 0, 0, 0, 0,15,15, 0, 0, 0, 0],
    [ 0, 0, 0, 0,15,15, 0, 0, 0, 0,15,15, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
HERO_DOWN_WALK = [
    [ 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15, 8, 0, 8,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,14,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0,12,12,12,12,12,12,12,12,12, 0, 0, 0, 0],
    [ 0, 0,15,12,12,12,12,12,12,12,12,12,15, 0, 0, 0],
    [ 0, 0,15,12, 1,12,12,12,12,12, 1,12,15, 0, 0, 0],
    [ 0, 0, 0,12,12,12,12,12,12,12,12,12, 0, 0, 0, 0],
    [ 0, 0, 0,12,12,12, 1,12, 1,12,12,12, 0, 0, 0, 0],
    [ 0, 0, 0, 0,12,12, 1,12, 1,12,12, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0,15, 0, 0, 0, 0,15, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0,15, 0, 0, 0,15, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 4, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
SLIME_10HO = [
    [ 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 3,11,11,11,11, 3, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 3,11,11,11,11,11,11, 3, 0, 0, 0, 0, 0],
    [ 0, 0, 3,11,11, 7,11,11, 7,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 3,11,11,11,11,11,11,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 3,11,11,11, 8,11, 8,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 3,11,11,11,11,11,11,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 3,11,11,11,11, 8,11,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 0, 3,11,11,11,11,11,11, 3, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 3, 3,11,11,11, 3, 3, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
    [ 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0],
    [ 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
GOBLIN_KAITEN = [
    [ 0, 0, 0, 0, 0, 0, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 9,15,15,15, 9, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 9,15,15, 8,15,15, 9, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 9,15, 8,15,15,15, 8,15, 9, 0, 0, 0, 0],
    [ 0, 0, 0, 9,15,15,15,15,15,15,15, 9, 0, 0, 0, 0],
    [ 0, 0, 0, 9, 8,15,11, 8,11,15, 8, 9, 0, 0, 0, 0],
    [ 0, 0, 0, 9,15,15,15,14,15,15,15, 9, 0, 0, 0, 0],
    [ 0, 0, 9, 9, 8, 8, 9, 9, 9, 8, 8, 9, 9, 0, 0, 0],
    [ 0, 9, 8, 8,15,15, 9, 9, 9,15,15, 8, 8, 9, 0, 0],
    [ 9, 8,15,15,15,15, 8, 9, 8,15,15,15,15, 8, 9, 0],
    [ 0, 9, 8, 8, 8, 8, 9, 0, 9, 8, 8, 8, 8, 9, 0, 0],
    [ 0, 0, 0, 9, 9, 9, 0, 0, 0, 9, 9, 9, 0, 0, 0, 0],
    [ 0, 0, 9, 8,15, 8, 9, 0, 9, 8,15, 8, 9, 0, 0, 0],
    [ 0, 0, 9, 8, 8, 9, 0, 0, 0, 9, 8, 8, 9, 0, 0, 0],
    [ 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
GHOST_LOOP = [
    [ 0, 0, 0, 0, 0,13,13,13,13,13, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0,13, 7, 7, 7, 7, 7,13, 0, 0, 0, 0, 0],
    [ 0, 0, 0,13, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0, 0],
    [ 0, 0,13, 7, 7, 6, 7, 7, 7, 6, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 1, 7, 7, 7, 1, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 8, 7, 8, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13,13, 7, 7, 7, 7, 7, 7, 7,13,13, 0, 0, 0],
    [ 0, 0,13, 0,13, 7, 7, 7, 7, 7,13, 0,13, 0, 0, 0],
    [ 0, 0,13, 0, 0,13,13, 7,13,13, 0, 0,13, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0,13, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0,13, 0,13, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
KNIGHT_10KAI = [
    [ 0, 0, 0, 0, 5, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 7, 6, 7, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 5, 5, 6, 6, 6, 6, 6, 6, 6, 5, 5, 0, 0, 0],
    [ 0, 5,12,12, 6, 6, 6, 6, 6, 6, 6,12,12, 5, 0, 0],
    [ 0, 5,12,12, 6, 6, 6, 1, 6, 6, 6,12,12, 5, 0, 0],
    [ 0, 5,12,12, 6, 6, 6, 6, 6, 6, 6,12,12, 5, 0, 0],
    [ 0, 0, 5, 5, 5, 6, 6, 6, 6, 6, 5, 5, 5, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 5, 6, 5, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 5, 5, 6, 5, 5, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 5, 5, 0, 5, 0, 5, 5, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
GUARD_MOSHI = [
    [ 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5,15,15,15,15,15, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5,15,15,15,15,15, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5,15, 0,15, 0,15, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5,15,15,14,15,15, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 6, 5, 5, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 6, 6, 6, 5, 6, 6, 6, 6, 6, 5, 6, 0, 0, 0, 0],
    [ 0, 6, 6, 6, 5, 6, 6, 8, 6, 6, 5, 6, 0, 0, 0, 0],
    [ 0, 6, 6, 6, 5, 6, 6, 6, 6, 6, 5, 6, 0, 0, 0, 0],
    [ 0, 0, 6, 5, 5, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 5, 6, 6, 6, 5, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 5, 5, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
SLIME_DENAKEREBA = [
    [ 0, 0, 0, 0, 0, 2,14, 2, 2, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 2,14,14,14,14, 2, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 2,14,14,14,14,14,14, 2, 0, 0, 0, 0, 0],
    [ 0, 0, 2,14,14, 7,14,14, 7,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14,14,14,14,14,14,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14,14,14, 2,14, 2,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14,14,14,14,14,14,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14,14,14,14, 8,14,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 0, 2,14,14,14,14,14,14, 2, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 2, 2,14,14,14, 2, 2, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14, 2, 0, 0, 0, 0, 0, 2,14, 2, 0, 0, 0],
    [ 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
COUNTER_HP = [
    [ 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [ 0, 1,12,12,12,12,12,12,12,12,12,12,12, 1, 0, 0],
    [ 1,12, 7, 7, 7,12,12,12,12, 7, 7, 7,12,12, 1, 0],
    [ 1,12, 7,10, 7,12,10,12,10, 7,10, 7,12,12, 1, 0],
    [ 1,12, 7, 7, 7,12,10,12,10, 7, 7, 7,12,12, 1, 0],
    [ 1,12,12,12,12,12,10,12,10,12,12,12,12,12, 1, 0],
    [ 1,12, 8, 8, 8,12,12,12,12,12, 8, 8,12,12, 1, 0],
    [ 1,12, 8, 8, 8,12,12,12,12,12, 8, 8,12,12, 1, 0],
    [ 1,12,12,12,12,12,12,12,12,12,12,12,12,12, 1, 0],
    [ 1,12,12, 1, 1,12,12,12,12, 1, 1,12,12,12, 1, 0],
    [ 1,12, 1, 0, 0, 1,12,12, 1, 0, 0, 1,12,12, 1, 0],
    [ 1,12, 1, 0, 0, 1,12,12, 1, 0, 0, 1,12,12, 1, 0],
    [ 1,12,12, 1, 1,12,12,12,12, 1, 1,12,12,12, 1, 0],
    [ 1,12,12,12,12,12,12,12,12,12,12,12,12,12, 1, 0],
    [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
NINJA_CLONE = [
    [ 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 8, 5, 8, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0, 0],
    [ 0, 1, 1, 1, 5, 5, 1, 5, 1, 5, 5, 1, 1, 1, 0, 0],
    [ 1, 5, 5, 5, 5, 5, 1, 5, 1, 5, 5, 5, 5, 5, 1, 0],
    [ 1, 5, 0, 0, 5, 5, 1, 5, 1, 5, 5, 0, 0, 5, 1, 0],
    [ 1, 5, 5, 5, 5, 5, 1, 5, 1, 5, 5, 5, 5, 5, 1, 0],
    [ 0, 1, 1, 1, 5, 5, 1, 5, 1, 5, 5, 1, 1, 1, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 1, 5, 1, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 1, 5, 1, 5, 1, 5, 1, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
BUG_MUGEN = [
    [ 0, 8, 0,10, 0, 8, 0,10, 0, 8, 0,10, 0, 8, 0, 0],
    [ 8, 0,11, 0, 8, 0,11, 0, 8, 0,11, 0, 8, 0, 0, 0],
    [ 0, 8, 2, 8, 0, 8, 2, 8, 0, 8, 2, 8, 0, 8, 0, 0],
    [ 2,11, 0, 2,11, 0, 2,11, 0, 2,11, 0, 2,11, 0, 0],
    [ 0, 2, 8, 0, 2, 8, 7, 2, 8, 0, 2, 8, 0, 2, 0, 0],
    [ 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 0, 0],
    [ 0,11, 0, 0,11, 0, 0,11, 0, 0,11, 0, 0,11, 0, 0],
    [ 2, 0, 8, 2, 0, 8, 2, 0, 8, 2, 0, 8, 2, 0, 0, 0],
    [ 0, 8, 2, 0, 8, 2, 0, 8, 2, 0, 8, 2, 0, 8, 0, 0],
    [11, 2, 0,11, 2, 0,11, 2, 0,11, 2, 0,11, 2, 0, 0],
    [ 0,11, 8, 0,11, 8, 0,11, 8, 0,11, 8, 0,11, 0, 0],
    [ 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 0, 0],
    [ 2, 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 0],
    [ 0, 2,11, 0, 2,11, 0, 2,11, 0, 2,11, 0, 2, 0, 0],
    [11, 0, 8,11, 0, 8,11, 0, 8,11, 0, 8,11, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
BOSS_GLITCH = [
    [ 0, 0, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 0, 0, 0],
    [ 0, 2, 8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 2, 0, 0],
    [ 2, 8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 2, 0],
    [ 8, 2, 2, 8, 2, 8, 2, 2, 2, 8, 2, 8, 2, 2, 8, 0],
    [ 2, 2, 2, 2, 8, 2, 2, 2, 2, 2, 8, 2, 2, 2, 2, 0],
    [ 2, 2, 2, 2, 2, 2, 8, 2, 8, 2, 2, 2, 2, 2, 2, 0],
    [ 2, 2, 2, 2, 2, 2, 2, 8, 2, 2, 2, 2, 2, 2, 2, 0],
    [ 0, 2, 8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 2, 0, 0],
    [ 0, 8, 2, 8, 2, 2, 2, 2, 2, 2, 2, 8, 2, 8, 0, 0],
    [ 0, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 0, 0],
    [ 0, 0, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 0, 0, 0],
    [ 0, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 0, 0],
    [ 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 0],
    [ 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 0],
    [ 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

ENEMY_SPRITES = {
    "slime": SLIME_10HO, "goblin": GOBLIN_KAITEN,
    "ghost": GHOST_LOOP, "knight": KNIGHT_10KAI,
    "guard": GUARD_MOSHI, "else_slime": SLIME_DENAKEREBA,
    "counter": COUNTER_HP, "ninja": NINJA_CLONE,
    "inf_bug": BUG_MUGEN, "glitch_lord": BOSS_GLITCH,
}
# fmt: on

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

# =====================================================================
# ENEMY DATA — ZONE_ENEMIES / GLITCH_LORD_DATA 等は game_data.py から
# import 済み（P1-C10）。ここで重複定義していた _build_zone_enemies と
# re-assignment を削除（P1-D1）。
# =====================================================================

ENCOUNTER_RATES = {
    T_GRASS: 0.06, T_SAND: 0.08, T_FLOOR: 0.12, T_PATH: 0.03,
    T_FLOWER: 0.06, T_ROCK: 0.06, T_MUSHROOM: 0.06,
    T_CACTUS: 0.08, T_BUSH: 0.06,
}

VFX_FLASH = {
    "flash_white": {"color": 7, "duration": 2},
    "flash_red":   {"color": 8, "duration": 3},
}

BATTLE_ATTACK_SCENES = (
    "battle.normal.attack.observe",
    "battle.normal.attack.inspect",
    "battle.normal.attack.read",
    "battle.normal.attack.trace",
    "battle.normal.attack.cause",
)

ENEMY_HIT_SCENES = {
    "sequential": "battle.normal.enemy_hit.sequential",
    "loop": "battle.normal.enemy_hit.loop",
    "condition": "battle.normal.enemy_hit.condition",
    "variable": "battle.normal.enemy_hit.variable",
    "composite": "battle.normal.enemy_hit.composite",
}

VICTORY_SCENES_BY_ZONE = {
    0: "battle.normal.victory.early",
    1: "battle.normal.victory.mid",
    2: "battle.normal.victory.mid",
    3: "battle.normal.victory.late",
    4: "battle.normal.victory.late",
}

ZONE_NAMES = {0: "はじまりのそうげん", 1: "ロジックのもり", 2: "アルゴのやまみち", 3: "さばくちたい", 4: "グリッチのどうくつ"}
ZONE_NAMES_EN = {0: "Grasslands", 1: "Logic Forest", 2: "Algo Mountains", 3: "Desert", 4: "Glitch Cave"}

from src.shared.services.text_format import NAME_EN_MAP, name_en
from src.scenes.splash.scene import SplashScene
from src.scenes.title.scene import TitleScene
from src.scenes.explore.scene import ExploreScene
from src.scenes.shop.scene import ShopScene
from src.scenes.menu.scene import MenuScene
from src.scenes.ai_help.scene import AiHelpScene
from src.scenes.ending.scene import EndingScene
from src.scenes.settings.scene import SettingsScene
from src.scenes.town.scene import TownScene
from src.scenes.professor.scene import ProfessorScene
from src.scenes.battle.scene import BattleScene
from src.shared.services.message_display import MessageDisplay
from src.shared.services.image_banks import ImageBanks
from src.shared.services.vfx import VfxSystem
from src.shared.services.text_format import TextFormat
from src.shared.services.item_use import use_item as _item_use_fn
from src.shared.ui.status_bar import StatusBar
from src.shared.services.audio_system import sync_audio as _sync_audio_fn

TOWN_MENU_LABELS = ("はなす", "ぶきや", "ぼうぐや", "どうぐや", "やどや", "セーブ", "でる")
TOWN_MENU_LABELS_EN = ("TALK", "WEAPONS", "ARMOR", "ITEMS", "INN", "SAVE", "EXIT")
SHOP_KIND_BY_LABEL = {"ぶきや": "weapons", "ぼうぐや": "armors", "どうぐや": "items"}
INN_COST = 10  # gold (フォールバック値; shops.yaml の inn_prices を優先)
SHOPS = _SHOP_BUNDLE["shops"]
INN_PRICES = _SHOP_BUNDLE["inn_prices"]
TOWN_INDEX_BY_POS = {(20, 12): 0, (30, 22): 1, (18, 34): 2}
SPELL_BY_NAME = {s["name"]: s for s in SPELLS}
SAVE_OK_MSG = "ここまでのりかいをかきとめた。"
LOAD_OK_MSG = "きろくをよみかえした。りかいがもどってくる。"
NO_RECORD_MSG = "まだなにもかきとめていない…"
SAVE_FAIL_MSG_DESKTOP = "セーブにしっぱいしました（けんげん/ようりょうをかくにんしてください）"
SAVE_FAIL_MSG_WEB = "セーブにしっぱいしました（ブラウザのほぞんりょういきをかくにんしてください）"
INN_OK_MSG = "あんぜんなばしょでやすんだ。しこうがさえる。HPとMPが かいふくした！"
INN_LACK_MSG = "コインが たりません"
SHOP_WIP_MSG = "こうじちゅう：ほんきのうはフォローアップでじっそうよてい"

TOWN_DIALOG_SCENES = {
    (25, 6): "castle.professor.entry",
}

# 町ごとのNPCセリフ（ラウンドロビンで A→B→C→A→…）
TOWN_NPC_LINES = [
    # はじめのむら (20,12)
    [
        "ものごとには じゅんばんが あるけど\nすこしズレたって きにならないだろ？",
        "そんなに きにしてたら\nなにもできないよ。\nだいたいあってれば いいんだよ",
        "じゅんばん？\nうごけば いいんだよ、うごけば",
    ],
    # ロジックタウン (30,22)
    [
        "おなじことの くりかえし？\nそういうもんだろ、しごとって",
        "かんがえすぎだよ。\nまわってるなら それでいいじゃないか",
        "とめる？\nなんで うごいてるものを とめるんだ？",
    ],
    # アルゴリズムのまち (18,34)
    [
        "ばあいによるとか いいだすと\nはなしが すすまないんだよな",
        "かぞえなくたって\nなんとなく わかるだろ？",
        "そこまで みえなくても\nいきていけるぞ",
    ],
]


# =====================================================================
# GAME CLASS
# =====================================================================
class Game:
    _instance: "Game | None" = None  # disp() のグローバル参照用

    def __init__(self):
        Game._instance = self
        self.messages = MessageDisplay(game=self)
        # デバッグオーバーレイ用のリングバッファ
        # _say_buffer は MessageDisplay.say_buffer に移動（P1-G12）
        pyxel.init(256, 256, title="Block Quest", fps=30)
        # 日本語フォントの読み込み。Code Maker 等で BDF が読めない環境では
        # None になり、各 UI ラベルとダイアログは英語フォールバックに切り替わる。
        # 日本語フォントは image bank 2 に焼き込んで使う（self.text 経由）。
        # BDF はレガシー互換のため一応試みる（読めなくても問題ない）。
        # has_jp_font は JP_FONT_LAYOUT が登録されている限り常に True。
        try:
            self.font = pyxel.Font("assets/umplus_j10r.bdf")
        except Exception:
            self.font = None
        self.has_jp_font = bool(JP_FONT_LAYOUT)
        self.audio = AudioManager(pyxel)
        self.sfx = SfxSystem(pyxel)
        # has_jp_font に応じて日本語/英語ダイアログを選択（src/generated/dialogue.py 由来）
        dialogue_data = DIALOGUE_JA if self.has_jp_font else DIALOGUE_EN
        self.dialog = StructuredDialogRunner(dialogue_data)

        # Tile/sprite bank は ImageBanks に移動（P1-G13）
        self.image_banks = ImageBanks(game=self)

        # Image bank: .pyxres があればロード、無ければプログラム描画
        self.image_banks.setup_image_banks()
        # slot 番号の対応は維持しつつ、import 済み SFX は上書きしない
        self.sfx = SfxSystem(pyxel)
        self.audio = AudioManager(pyxel)

        self.world_map = generate_world_map()
        # Tilemap[0] に world_map をベイク or .pyxres から派生
        self.image_banks.setup_world_tilemap()

        self.dungeon_map = None
        self.dungeon_rooms = None

        self.player = create_initial_player()
        # 注意：settings_scene はこの __init__ の末尾で生成されるので、
        # 起動時の apply_av は scene 生成後に呼ぶ（末尾で実行）。

        self.state = "splash"
        # splash_frame は SplashModel.frame に移動（P1-G2）
        self.prev_state = "map"
        # walk_frame / walk_timer / move_cooldown は ExploreModel に移動（P1-G3）

        # Battle state は BattleModel に移動（P1-G6）
        # vfx state は VfxSystem に移動（P1-G14）
        self.vfx = VfxSystem(game=self)
        self.text_fmt = TextFormat(game=self)

        # professor state は ProfessorModel に移動（P1-G10）
        # town_menu state は TownModel に移動（P1-G4）
        self.last_town_pos: tuple[int, int] | None = None

        # a_cooldown は ExploreModel.a_cooldown に移動（P1-G3）

        # Title cursor は TitleModel.cursor に移動（P1-G1）
        # settings_cursor / settings_origin は SettingsModel に移動（P1-G8）

        # Save store (D1/D12/D17)
        save_path = Path(__file__).resolve().parent / "save.json"
        self.save_store = make_save_store(save_path)
        self._has_save = self.save_store.exists()

        # Message state は MessageDisplay に移動（P1-G12）

        # Debug mode
        self.debug_mode = False
        self.debug_seq = []
        self.input_state = InputStateTracker()

        # Camera
        self.cam_x = 0
        self.cam_y = 0

        # Dungeon return position
        self.world_return_x = 0
        self.world_return_y = 0

        # Scene instances（P1-G で Game メソッドを取り込んだ scene を保有する）
        self.splash_scene = SplashScene(game=self)
        self.title_scene = TitleScene(game=self)
        self.explore_scene = ExploreScene(game=self)
        self.shop_scene = ShopScene(game=self)
        self.menu_scene = MenuScene(game=self)
        self.ai_help_scene = AiHelpScene(game=self)
        self.ending_scene = EndingScene(game=self)
        self.settings_scene = SettingsScene(game=self)
        self.town_scene = TownScene(game=self)
        self.professor_scene = ProfessorScene(game=self)
        self.battle_scene = BattleScene(game=self)
        self.status_bar = StatusBar(game=self)

        # 起動時の AV 設定適用（settings_scene 生成後に呼ぶ）
        self.settings_scene.apply_av()

        _sync_audio_fn(self)

    def start(self):
        """ゲームループに入る。`Game()` 後の `disp()` 呼び出しを有効にするため
        `__init__` から `pyxel.run` を分離してある。"""
        pyxel.run(self.update, self.draw)



    # ----- World tilemap setup (.pyxres tilemap[0] support) -----
    # Code Maker / pyxel edit は tilemap[N] のデフォルト imgsrc を N と仮定して
    # 表示するため、tilemap[1] を使うとイメージバンク 1（敵スプライト）が表示されて
    # しまう。これを避けるため、ワールドマップとダンジョンを **同じ tilemap[0]** に
    # 配置して、画像バンク 0 だけを参照させる。


    # ----- Image bank: layout (positions) と paint (pset) を分離 -----
    # 通常起動時は .pyxres から load してレイアウト辞書だけ計算する。
    # .pyxres が無ければ paint してから save する（初回のみ）。


    # -----------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------


    def update(self):
        self.input_state.update(pyxel)

        # 緊急脱出: F1 で強制的にフィールド (map) へ戻す
        # 「入力が効かない」と感じたときの最終手段
        if pyxel.btnp(pyxel.KEY_F1):
            self.state = "map"
            self.explore_scene.model.move_cooldown = 0
            self.explore_scene.model.a_cooldown = False
            self.messages.lines = []
            self.messages.index = 0
            self.messages.callback = None

        # Debug code: up up down down
        if self.input_state.btnp(UP_BUTTONS):
            self.debug_seq.append("U")
        elif self.input_state.btnp(DOWN_BUTTONS):
            self.debug_seq.append("D")
        else:
            if (
                self.input_state.btnp(LEFT_BUTTONS)
                or self.input_state.btnp(RIGHT_BUTTONS)
                or self.input_state.btnp(CONFIRM_BUTTONS)
                or self.input_state.btnp(CANCEL_BUTTONS)
            ):
                self.debug_seq = []

        # 無限に伸びるのを防ぐ
        if len(self.debug_seq) > 8:
            self.debug_seq = self.debug_seq[-4:]

        if len(self.debug_seq) >= 4:
            if self.debug_seq[-4:] == ["U", "U", "D", "D"]:
                self.debug_mode = not self.debug_mode
                self.debug_seq = []

        if self.state == "splash":
            self.splash_scene.update()
        elif self.state == "title":
            self.title_scene.update()
        elif self.state == "map":
            self.explore_scene.update()
        elif self.state == "battle":
            self.battle_scene.update()
        elif self.state == "menu":
            self.menu_scene.update()
        elif self.state == "settings":
            self.settings_scene.update()
        elif self.state == "message":
            self.messages.update()
        elif self.state == "town":
            self.town_scene.update()
        elif self.state == "town_menu":
            self.town_scene.update_menu()
        elif self.state == "professor_intro":
            self.professor_scene.update_intro()
        elif self.state == "professor_ending_main":
            self.professor_scene.update_ending_main()
        elif self.state == "professor_ending_accepted":
            self.professor_scene.update_ending_accepted()
        elif self.state == "shop":
            self.shop_scene.update()
        elif self.state == "ending":
            self.ending_scene.update()
        elif self.state == "ai_help":
            self.ai_help_scene.update()

        _sync_audio_fn(self)

    # update_splash は SplashScene に移動（P1-G2）
    # update_title / _do_load は TitleScene に移動（P1-G1）


    # ----- AI でしゅうせい (Code Maker と外部 AI の橋渡し) -----

    # -----------------------------------------------------------------
    # DRAW
    # -----------------------------------------------------------------
    def draw(self):
        pyxel.cls(0)
        if self.state == "splash":
            self.splash_scene.draw()
        elif self.state == "title":
            self.title_scene.draw()
        elif self.state == "map":
            self.explore_scene.draw()
            self.status_bar.draw()
        elif self.state == "battle":
            self.battle_scene.draw()
        elif self.state == "menu":
            self.explore_scene.draw()
            self.status_bar.draw()
            self.menu_scene.draw()
        elif self.state == "settings":
            if self.settings_scene.model.origin == "menu":
                self.explore_scene.draw()
                self.status_bar.draw()
            else:
                self.title_scene.draw()
            self.settings_scene.draw()
        elif self.state == "message":
            self.explore_scene.draw()
            self.status_bar.draw()
            self.messages.draw_window()
        elif self.state == "town":
            self.explore_scene.draw()
            self.status_bar.draw()
            self.messages.draw_window()
        elif self.state == "town_menu":
            self.town_scene.draw_menu()
        elif self.state == "shop":
            self.shop_scene.draw()
        elif self.state == "ending":
            self.ending_scene.draw()
        elif self.state == "professor_intro":
            self.professor_scene.draw_intro()
        elif self.state == "professor_ending_main":
            self.professor_scene.draw_ending_main()
        elif self.state == "professor_ending_accepted":
            self.professor_scene.draw_ending_accepted()
        elif self.state == "ai_help":
            self.ai_help_scene.draw()

        # デバッグオーバーレイ（最後に重ねる）
        self.messages.draw_say_overlay()


# =====================================================================
# DEBUG: グローバル say() 関数 — Scratch の「say」ブロックと同じ感覚
# =====================================================================
def say(*args):
    """画面左上にデバッグ表示するヘルパ関数。

    使い方:
        say("こんにちは")             # → 画面左上に「こんにちは」が出る
        say("hp =", player["hp"])     # → 「hp = 45」のように出る

    最新 12 行までが画面左上にオーバーレイ表示される。
    print() より便利な点:
      - ゲーム画面に出るのでブラウザでも見える（Code Maker 環境向け）
      - 日本語が表示できる（仮名のみ）
    """
    if Game._instance is not None:
        Game._instance.messages.say(*args)


def say_clear():
    """say バッファをクリアする。"""
    if Game._instance is not None:
        Game._instance.messages.say_buffer.clear()


# =====================================================================
# ENTRY POINT
# =====================================================================
# 子どもがコードを試すときは、wrapper 側から `run()` を呼ぶ。
# Code Maker 用 single-file build でも、この関数を末尾で呼び出す。
def run():
    global game
    game = Game()
    game.start()
    return game
