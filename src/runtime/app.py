"""Block Quest の Game クラス本体と entry point（Phase 1.5-D で main_runtime.py から抽出）。

`src/app.py::BlockQuestApp` は scene_manager + GameState の薄い shell として残し、
pyxel 初期化 + scene/service instance の組み立て + update/draw dispatcher の
重量級 runtime は本ファイルに Game クラスとして置く。
"""
from __future__ import annotations
import pyxel
from pathlib import Path

from src.shared.assets.jp_font_data import JP_FONT_LAYOUT
from src.shared.services.audio_system import AudioManager, SfxSystem
from src.shared.services.audio_system import sync_audio as _sync_audio_fn
from src.shared.services.dialog_runner import StructuredDialogRunner
from src.shared.services.image_banks import ImageBanks
from src.shared.services.input_bindings import (
    UP_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
    InputStateTracker,
)
from src.shared.services.message_display import MessageDisplay
from src.shared.services.player_state import create_initial_player
from src.shared.services.save_store import make_save_store
from src.shared.services.text_format import TextFormat
from src.shared.services.vfx import VfxSystem
from src.shared.services.world_generation import generate_world_map
from src.shared.ui.status_bar import StatusBar

from src.game_data import DIALOGUE_JA, DIALOGUE_EN

from src.scenes.ai_help.scene import AiHelpScene
from src.scenes.battle.scene import BattleScene
from src.scenes.ending.scene import EndingScene
from src.scenes.explore.scene import ExploreScene
from src.scenes.menu.scene import MenuScene
from src.scenes.professor.scene import ProfessorScene
from src.scenes.settings.scene import SettingsScene
from src.scenes.shop.scene import ShopScene
from src.scenes.splash.scene import SplashScene
from src.scenes.title.scene import TitleScene
from src.scenes.town.scene import TownScene


class Game:
    _instance: "Game | None" = None  # disp() のグローバル参照用

    def __init__(self):
        Game._instance = self
        self.messages = MessageDisplay(game=self)
        pyxel.init(256, 256, title="Block Quest", fps=30)
        # 日本語フォントの読み込み。Code Maker 等で BDF が読めない環境では
        # None になり、各 UI ラベルとダイアログは英語フォールバックに切り替わる。
        try:
            self.font = pyxel.Font("assets/umplus_j10r.bdf")
        except Exception:
            self.font = None
        self.has_jp_font = bool(JP_FONT_LAYOUT)
        self.audio = AudioManager(pyxel)
        self.sfx = SfxSystem(pyxel)
        dialogue_data = DIALOGUE_JA if self.has_jp_font else DIALOGUE_EN
        self.dialog = StructuredDialogRunner(dialogue_data)

        self.image_banks = ImageBanks(game=self)
        self.image_banks.setup_image_banks()
        # slot 番号の対応は維持しつつ、import 済み SFX は上書きしない
        self.sfx = SfxSystem(pyxel)
        self.audio = AudioManager(pyxel)

        self.world_map = generate_world_map()
        self.image_banks.setup_world_tilemap()

        self.dungeon_map = None
        self.dungeon_rooms = None

        self.player = create_initial_player()

        self.state = "splash"
        self.prev_state = "map"

        self.vfx = VfxSystem(game=self)
        self.text_fmt = TextFormat(game=self)

        self.last_town_pos: tuple[int, int] | None = None

        # Save store (D1/D12/D17)
        save_path = Path(__file__).resolve().parent / "save.json"
        self.save_store = make_save_store(save_path)
        self._has_save = self.save_store.exists()

        self.debug_mode = False
        self.debug_seq = []
        self.input_state = InputStateTracker()

        self.cam_x = 0
        self.cam_y = 0

        self.world_return_x = 0
        self.world_return_y = 0

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

        self.settings_scene.apply_av()

        _sync_audio_fn(self)

    def start(self):
        """ゲームループに入る。`Game()` 後の `disp()` 呼び出しを有効にするため
        `__init__` から `pyxel.run` を分離してある。"""
        pyxel.run(self.update, self.draw)

    def update(self):
        self.input_state.update(pyxel)

        # 緊急脱出: F1 で強制的にフィールド (map) へ戻す
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


def say(*args):
    """画面左上にデバッグ表示するヘルパ関数（Scratch の「say」ブロック相当）。"""
    if Game._instance is not None:
        Game._instance.messages.say(*args)


def say_clear():
    """say バッファをクリアする。"""
    if Game._instance is not None:
        Game._instance.messages.say_buffer.clear()


def run():
    """entry point: Game を生成して pyxel.run に入る。"""
    global game
    game = Game()
    game.start()
    return game


# グローバル 'game' 変数は run() の最初で上書きされる。
game: "Game | None" = None
