"""Block Quest runtime shim (P1.5-E で <50 行に圧縮)。

真の entry point は `src/runtime/app.py::run`。tests / Code Maker bundler /
旧 `import src.runtime.main_runtime as M` の互換のため、module-level 名前を
ここで再エクスポートする。
"""
from __future__ import annotations
import pyxel  # tests が M.pyxel 経由で参照する
from src.shared.services.input_bindings import *
from src.shared.services.landmark_events import *
from src.shared.state.player_model import *
from src.shared.services.save_store import *
from src.shared.services.audio_system import *
from src.shared.services.dialog_runner import *
from src.game_data import *
from src.shared.assets.jp_font_data import *
from src.shared.constants.tile_data import *
from src.shared.constants.tile_data import _PATH_VARIANTS, _SHORE_VARIANTS, _ZONE_DECORATIONS
from src.shared.constants.sprite_data import *
from src.shared.constants.game_config import *
from src.shared.services.world_generation import *
from src.shared.services.text_format import NAME_EN_MAP, name_en, TextFormat
from src.shared.services.message_display import MessageDisplay
from src.shared.services.image_banks import ImageBanks
from src.shared.services.vfx import VfxSystem
from src.shared.ui.status_bar import StatusBar
# 2026-05-07: sync_audio は撤去済（BGM は各 scene の view.draw 冒頭で発火）。
from src.scenes.splash.scene import SplashScene
from src.scenes.title.scene import TitleScene
from src.scenes.explore.scene import ExploreScene
from src.scenes.shop.scene import ShopScene
from src.scenes.menu.scene import MenuScene
from src.scenes.ai_help.scene import AiHelpScene
from src.scenes.ending.scene import EndingScene
from src.scenes.professor.scene import ProfessorScene
from src.scenes.battle.scene import BattleScene
from src.runtime.app import Game, say, say_clear
from src.runtime.app import run as _run

# =====================================================================
# ENTRY POINT
# =====================================================================
def run():
    """Block Quest の entry point。Game を生成して pyxel.run に入る。"""
    return _run()
