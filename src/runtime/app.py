"""Block Quest の Game クラス本体と entry point。

pyxel 初期化 + scene/service instance の組み立て + update/draw dispatcher を
まとめた唯一の runtime root を本ファイルに置く。
"""
from __future__ import annotations
import pyxel
from pathlib import Path

from src.shared.assets.jp_font_data import JP_FONT_LAYOUT
from src.shared.services.audio_system import SfxSystem
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
from src.shared.services.debug_service import DebugService
from src.shared.services.message_display import MessageDisplay
from src.shared.services.game_state import GameState, TownContext
from src.shared.services.scene_manager import SceneManager
from src.shared.services.save_store import make_save_store
from src.shared.state.player_model import PlayerModel
from src.shared.services.text_format import TextFormat
from src.shared.services.vfx import VfxSystem
from src.shared.ui.status_bar import StatusBar

from src.game_data import DIALOGUE_JA, DIALOGUE_EN

from src.scenes.ai_help.scene import AiHelpScene
from src.scenes.battle.scene import BattleScene
from src.scenes.ending.scene import EndingScene
from src.scenes.explore.scene import ExploreScene
from src.scenes.menu.scene import MenuScene
from src.scenes.professor.scene import ProfessorScene
from src.scenes.shop.scene import ShopScene
from src.scenes.splash.scene import SplashScene
from src.scenes.title.scene import TitleScene
from src.scenes.town.model import TownModel
from src.scenes.town.presenter import TownPresenter
from src.scenes.town.view import TownView


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
        # 2026-05-07 改訂：BGM は scene の view.py が pyxel.playm を直接呼ぶ
        # （CJ44 確定版）。AudioManager は撤去済。BGM の冪等性は
        # audio_system.play_bgm_track 内のモジュールスコープ変数で保持し、
        # Game クラス自身は BGM 状態を持たない。
        self.sfx = SfxSystem(pyxel)
        dialogue_data = DIALOGUE_JA if self.has_jp_font else DIALOGUE_EN
        self.dialog = StructuredDialogRunner(dialogue_data)

        self.image_banks = ImageBanks(game=self)
        self.image_banks.setup_image_banks()
        # pyxres ロード後に SfxSystem を再構築：import 済み SFX は上書きしない
        # (_slot_has_sound ガード)。
        self.sfx = SfxSystem(pyxel)

        self.image_banks.setup_world_tilemap()

        # framework-rule.md M4-3: scene 跨ぎ共有 state は GameState に持つ。
        # 段階移行中につき player_model 等の field は Game にも残るが、
        # current_town は本オブジェクト経由でアクセスする。
        self.game_state = GameState()

        # PlayerModel が player 状態の唯一の正本（framework-rule.md M4-1 / M4-4）。
        self.player_model = PlayerModel.new_game()

        # framework-rule.md M4-3: scene 切替メタは SceneManager に集約。
        # game.state / game.prev_state は @property でフォワードする。
        self.scene_manager = SceneManager()

        self.vfx = VfxSystem(game=self)
        self.text_fmt = TextFormat(game=self)

        self.last_town_pos: tuple[int, int] | None = None
        # current_town は GameState に統合済み。Game クラス本体の @property
        # (current_town) で self.game_state.current_town にフォワードする。

        # Save store (D1/D12/D17)
        save_path = Path(__file__).resolve().parent / "save.json"
        self.save_store = make_save_store(save_path)
        self._has_save = self.save_store.exists()

        # framework-rule.md M4-3: デバッグ state は DebugService に集約。
        # game.debug_mode / game.debug_seq は @property でフォワードする。
        self.debug = DebugService()
        self.input_state = InputStateTracker()

        self.world_return_x = 0
        self.world_return_y = 0

        self.splash_scene = SplashScene(game=self)
        self.title_scene = TitleScene(game=self)
        self.explore_scene = ExploreScene(game=self)
        self.shop_scene = ShopScene(game=self)
        self.menu_scene = MenuScene(game=self)
        self.ai_help_scene = AiHelpScene(game=self)
        self.ending_scene = EndingScene(game=self)
        self.town_model = TownModel()
        self.town_view = TownView(game=self)
        self.town_presenter = TownPresenter(model=self.town_model, game=self)
        self.professor_scene = ProfessorScene(game=self)
        self.battle_scene = BattleScene(game=self)
        self.status_bar = StatusBar(game=self)
        # 2026-05-07 改訂（CJ44 確定版）：settings_scene と apply_av は撤去済。
        # BGM/SFX/VFX は常に ON。設定画面は存在しない。

    @property
    def current_town(self) -> "TownContext | None":
        """現在入場中の町情報を GameState から返す（M4-3 段階移行）。

        Game.__new__(Game) で作る test 経路でも動くよう、game_state が
        まだ無ければ None を返す（lazy 防御）。
        """
        gs = getattr(self, "game_state", None)
        return gs.current_town if gs is not None else None

    @current_town.setter
    def current_town(self, value: "TownContext | None") -> None:
        if not hasattr(self, "game_state"):
            self.game_state = GameState()
        self.game_state.current_town = value

    @property
    def debug_mode(self) -> bool:
        """デバッグモード state を DebugService から返す（M4-3 段階移行）。"""
        dbg = getattr(self, "debug", None)
        return dbg.mode if dbg is not None else False

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        if not hasattr(self, "debug"):
            self.debug = DebugService()
        self.debug.mode = bool(value)

    @property
    def state(self) -> str:
        """現在 scene を SceneManager から返す（M4-3 段階移行）。"""
        sm = getattr(self, "scene_manager", None)
        return sm.current if sm is not None else "splash"

    @state.setter
    def state(self, value: str) -> None:
        if not hasattr(self, "scene_manager"):
            self.scene_manager = SceneManager()
        self.scene_manager.current = value

    @property
    def prev_state(self) -> str:
        """直前 scene を SceneManager から返す（M4-3 段階移行）。"""
        sm = getattr(self, "scene_manager", None)
        return sm.previous if sm is not None else "map"

    @prev_state.setter
    def prev_state(self, value: str) -> None:
        if not hasattr(self, "scene_manager"):
            self.scene_manager = SceneManager()
        self.scene_manager.previous = value

    @property
    def debug_seq(self) -> list:
        dbg = getattr(self, "debug", None)
        return dbg.seq if dbg is not None else []

    @debug_seq.setter
    def debug_seq(self, value) -> None:
        if not hasattr(self, "debug"):
            self.debug = DebugService()
        self.debug.seq = list(value)

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

        # Debug code: up up down down → DebugService に状態集約済み
        if self.input_state.btnp(UP_BUTTONS):
            self.debug.record_up()
        elif self.input_state.btnp(DOWN_BUTTONS):
            self.debug.record_down()
        elif (
            self.input_state.btnp(LEFT_BUTTONS)
            or self.input_state.btnp(RIGHT_BUTTONS)
            or self.input_state.btnp(CONFIRM_BUTTONS)
            or self.input_state.btnp(CANCEL_BUTTONS)
        ):
            self.debug.reset_seq()

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
        elif self.state == "message":
            self.messages.update()
        elif self.state == "town":
            self.town_presenter.update_message()
        elif self.state == "town_menu":
            self.town_presenter.update_menu()
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

        # 2026-05-07 改訂：BGM 同期は各 scene の view.draw 冒頭で行うため、
        # ここでの sync_audio 呼び出しは撤去（CJ44 確定版）。

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
        elif self.state == "message":
            self.explore_scene.draw()
            self.status_bar.draw()
            self.messages.draw_window()
        elif self.state == "town":
            self.explore_scene.draw()
            self.status_bar.draw()
            self.messages.draw_window()
        elif self.state == "town_menu":
            self.town_view.render_menu(self.town_presenter.build_menu_view_model())
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
