"""Block Quest runtime shim（旧 import 互換用の再エクスポート窓口）。

このファイルに含まれる関数・クラス：

- run: app.run へ委譲する薄い entry point

Problems:
    - 旧 `import src.runtime.main_runtime as M` 経由で module-level 名前を
      参照する tests があり、削ると import 互換が壊れる。
Solutions:
    - 真の entry は `src/runtime/app.py::run`。本ファイルは再エクスポート専用。
"""
from __future__ import annotations
import pyxel  # noqa: F401
from src.shared.services.input_bindings import *  # noqa: F401,F403
from src.shared.services.landmark_events import *  # noqa: F401,F403
from src.shared.state.player_model import *  # noqa: F401,F403
from src.shared.services.save_store import *  # noqa: F401,F403
from src.shared.services.audio_system import *  # noqa: F401,F403
from src.shared.services.dialog_runner import *  # noqa: F401,F403
from src.game_data import *  # noqa: F401,F403
from src.shared.assets.jp_font_data import *  # noqa: F401,F403
from src.shared.constants.tile_data import *  # noqa: F401,F403
from src.shared.constants.tile_data import _PATH_VARIANTS, _SHORE_VARIANTS, _ZONE_DECORATIONS  # noqa: F401,E501
from src.shared.constants.sprite_data import *  # noqa: F401,F403
from src.shared.constants.game_config import *  # noqa: F401,F403
from src.shared.services.world_generation import *  # noqa: F401,F403
from src.shared.services.text_format import NAME_EN_MAP, name_en, TextFormat  # noqa: F401,E501
from src.shared.services.message_display import MessageDisplay  # noqa: F401
from src.shared.services.image_banks import ImageBanks  # noqa: F401
from src.shared.services.vfx import VfxSystem  # noqa: F401
from src.shared.ui.status_bar import StatusBar  # noqa: F401
from src.scenes.splash.scene import SplashScene; from src.scenes.title.scene import TitleScene  # noqa: F401,E501,E702
from src.scenes.explore.scene import ExploreScene; from src.scenes.shop.scene import ShopScene  # noqa: F401,E501,E702
from src.scenes.menu.scene import MenuScene; from src.scenes.ai_help.scene import AiHelpScene  # noqa: F401,E501,E702
from src.scenes.ending.scene import EndingScene; from src.scenes.professor.scene import ProfessorScene  # noqa: F401,E501,E702
from src.scenes.battle.scene import BattleScene  # noqa: F401
from src.runtime.app import Game, say, say_clear  # noqa: F401
from src.runtime.app import run as _run

# === Public API ===


def run():
    """app.run へ委譲する shim entry point。Returns: None / Policy: 旧 import 互換。"""
    return _run()


# === Internal helpers (private) ===
