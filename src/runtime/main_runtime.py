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

from src.shared.services.world_generation import (
    get_path_variant, get_shore_variant,
    generate_world_map, generate_dungeon, get_zone,
)

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
# Game / say / say_clear は P1.5-D で src/runtime/app.py に移動
# =====================================================================
from src.runtime.app import Game, say, say_clear
from src.runtime.app import run as _run


# =====================================================================
# ENTRY POINT
# =====================================================================
# 子どもがコードを試すときは、wrapper 側から `run()` を呼ぶ。
# Code Maker 用 single-file build でも、この関数を末尾で呼び出す。
def run():
    """Block Quest の entry point。Game を生成して pyxel.run に入る。"""
    return _run()
