"""Block Quest の Game クラス本体と entry point。

このファイルに含まれる関数・クラス：

- say: 画面左上にデバッグ表示するヘルパ関数（Scratch say 相当）
- say_clear: say バッファをクリアする
- run: entry point — Game() を生成して pyxel.run に入る
- _is_game_instance_present: Game インスタンスが生成済みかを返す述語
- _say_via_instance: Game._instance.messages.say(*args) に委譲する
- _clear_say_buffer_via_instance: messages.say_buffer.clear に委譲する
- _start_new_game: Game を生成しグローバル参照を更新してから start に入る
- Game: pyxel 初期化 + scene/service 組み立て + update/draw dispatcher の runtime root
  - __init__: pyxel と全 service / scene を生成する constructor
  - current_town: GameState.current_town にフォワードする property getter
  - current_town: GameState.current_town にフォワードする property setter
  - debug_mode: DebugService.mode にフォワードする property getter
  - debug_mode: DebugService.mode にフォワードする property setter
  - state: SceneManager.current にフォワードする property getter
  - state: SceneManager.current にフォワードする property setter
  - prev_state: SceneManager.previous にフォワードする property getter
  - prev_state: SceneManager.previous にフォワードする property setter
  - debug_seq: DebugService.seq にフォワードする property getter
  - debug_seq: DebugService.seq にフォワードする property setter
  - start: pyxel.run(update, draw) を呼ぶゲームループ入口
  - update: pyxel 互換固定名の毎フレーム更新メソッド
  - draw: pyxel 互換固定名の毎フレーム描画メソッド
  - _build_audio_and_dialog: SFX/dialog service を組み立てる private 委譲
  - _build_image_banks: ImageBanks を生成し、SFX 再構築 + tilemap load を行う
  - _build_runtime_state: GameState / PlayerModel / SceneManager 等を生成する
  - _build_world_helpers: vfx/text_fmt や world return 座標等を初期化する
  - _build_save_store: save_store と _has_save を初期化する
  - _build_debug_and_input: DebugService と InputStateTracker を生成する
  - _build_scenes: 各 scene と status_bar を生成する
  - _load_jp_font_or_none: 日本語フォントを読み込み失敗時は None を返す
  - _handle_emergency_exit_to_map: F1 で強制的に map state に戻す
  - _record_debug_input: 矢印/決定/キャンセル入力を debug seq に記録する
  - _is_left_or_right_btnp: 左右入力が btnp されたかを返す述語
  - _is_confirm_or_cancel_btnp: 決定/キャンセル入力が btnp されたかを返す述語
  - _is_horizontal_or_action_btnp: 左右/決定/キャンセルいずれかが btnp されたかを返す述語
  - _dispatch_update: state に応じた update を委譲する
  - _dispatch_draw: state に応じた draw を委譲する
  - _draw_overlay_status_bar: status_bar を重ねる private 描画
  - _draw_overlay_message_window: message_window を重ねる private 描画
  - _update_for_splash: splash state の update
  - _update_for_title: title state の update
  - _update_for_map: map state の update
  - _update_for_battle: battle state の update
  - _update_for_menu: menu state の update
  - _update_for_message: message state の update
  - _update_for_town: town state の update
  - _update_for_town_menu: town_menu state の update
  - _update_for_professor_intro: professor_intro state の update
  - _update_for_professor_ending_main: professor_ending_main state の update
  - _update_for_professor_ending_accepted: professor_ending_accepted の update
  - _update_for_shop: shop state の update
  - _update_for_ending: ending state の update
  - _update_for_ai_help: ai_help state の update
  - _draw_for_splash: splash state の draw
  - _draw_for_title: title state の draw
  - _draw_for_map: map state の draw（status_bar 重ね）
  - _draw_for_battle: battle state の draw
  - _draw_for_menu: menu state の draw（explore + status_bar + menu）
  - _draw_for_message: message state の draw（explore + status_bar + window）
  - _draw_for_town: town state の draw（explore + status_bar + window）
  - _draw_for_town_menu: town_menu state の draw（town_view.render_menu）
  - _draw_for_shop: shop state の draw
  - _draw_for_ending: ending state の draw
  - _draw_for_professor_intro: professor_intro state の draw
  - _draw_for_professor_ending_main: professor_ending_main state の draw
  - _draw_for_professor_ending_accepted: professor_ending_accepted state の draw
  - _draw_for_ai_help: ai_help state の draw

Problems:
    - Game.__init__ が 70 行超の手続き列で、責務（pyxel 初期化 / service /
      scene 構築 / save / debug）が判別しにくい（CR202）。
    - update / draw を「state == ...」の 13 段 elif で書くと CR301 が頻発し、
      pyxel 固定名の制約と相まって変更コストが高い。
    - current_town / state / prev_state / debug_mode / debug_seq の setter は
      ガード付き分岐を含み、CR203/CR204 に触る。

Solutions:
    - __init__ を「audio/dialog → image_banks → runtime_state → world_helpers
      → save_store → debug_and_input → scenes」の private builder に分割して
      step list に揃える。
    - update / draw は state に応じた private dispatcher (`_update_for_*` /
      `_draw_for_*`) と state→method の dict マップで分岐を 1 箇所に集約する。
    - pyxel 互換固定名（update / draw / start）は ``# noqa: CR100`` で許容し、
      property setter は ``# noqa: CR203 CR204 CR501`` で許容する。
"""
from __future__ import annotations

from pathlib import Path

import pyxel

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
    """Block Quest の runtime root（pyxel 初期化と scene 委譲を担う唯一クラス）."""

    _instance: "Game | None" = None  # disp() のグローバル参照用

    # === Public API ===

    def __init__(self):  # noqa: CR203 CR204 CR501
        """pyxel と全 service / scene を生成する constructor.

        Policy:
            - 責務ごとに private builder へ分割し、ステップ列で読み下せる順序を保つ。
            - pyxel.init は本コンストラクタの先頭で 1 回だけ呼ぶ。
        """
        Game._instance = self
        self.messages = MessageDisplay(game=self)
        pyxel.init(256, 256, title="Block Quest", fps=30)
        self.font = self._load_jp_font_or_none()
        self.has_jp_font = bool(JP_FONT_LAYOUT)
        self._build_audio_and_dialog()
        self._build_image_banks()
        self._build_runtime_state()
        self._build_world_helpers()
        self._build_save_store()
        self._build_debug_and_input()
        self._build_scenes()

    @property
    def current_town(self) -> "TownContext | None":  # noqa: CR100
        """現在入場中の町情報を GameState から返す（M4-3 段階移行）。

        Returns:
            TownContext | None: 入場中なら TownContext、未入場なら None。
        Policy:
            - Game.__new__(Game) で作る test 経路でも動くよう、game_state が
              まだ無ければ None を返す（lazy 防御）。
        """
        gs = getattr(self, "game_state", None)
        return gs.current_town if gs is not None else None

    @current_town.setter
    def current_town(  # noqa: CR100 CR203 CR204 CR501
        self, value: "TownContext | None"
    ) -> None:
        if not hasattr(self, "game_state"):
            self.game_state = GameState()
        self.game_state.current_town = value

    @property
    def debug_mode(self) -> bool:
        """デバッグモード state を DebugService から返す（M4-3 段階移行）。

        Returns:
            bool: DebugService.mode の現在値。未生成なら False。
        Policy:
            - Game.__new__(Game) で作る test 経路でも動くよう lazy 防御する。
        """
        dbg = getattr(self, "debug", None)
        return dbg.mode if dbg is not None else False

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:  # noqa: CR203 CR204 CR501
        if not hasattr(self, "debug"):
            self.debug = DebugService()
        self.debug.mode = bool(value)

    @property
    def state(self) -> str:
        """現在 scene を SceneManager から返す（M4-3 段階移行）。

        Returns:
            str: SceneManager.current。未生成なら "splash"。
        Policy:
            - Game.__new__(Game) で作る test 経路でも動くよう lazy 防御する。
        """
        sm = getattr(self, "scene_manager", None)
        return sm.current if sm is not None else "splash"

    @state.setter
    def state(self, value: str) -> None:  # noqa: CR203 CR204 CR501
        if not hasattr(self, "scene_manager"):
            self.scene_manager = SceneManager()
        self.scene_manager.current = value

    @property
    def prev_state(self) -> str:  # noqa: CR100
        """直前 scene を SceneManager から返す（M4-3 段階移行）。

        Returns:
            str: SceneManager.previous。未生成なら "map"。
        Policy:
            - 名前 ``prev_state`` は SceneManager API と歴史的整合のため固定。
        """
        sm = getattr(self, "scene_manager", None)
        return sm.previous if sm is not None else "map"

    @prev_state.setter
    def prev_state(  # noqa: CR100 CR203 CR204 CR501
        self, value: str
    ) -> None:
        if not hasattr(self, "scene_manager"):
            self.scene_manager = SceneManager()
        self.scene_manager.previous = value

    @property
    def debug_seq(self) -> list:
        """DebugService.seq の現在 snapshot を返す。

        Returns:
            list: 現在の入力シーケンス。未生成なら空 list。
        Policy:
            - DebugService 未生成時のため getattr で防御する。
        """
        dbg = getattr(self, "debug", None)
        return dbg.seq if dbg is not None else []

    @debug_seq.setter
    def debug_seq(self, value) -> None:  # noqa: CR203 CR204 CR501
        if not hasattr(self, "debug"):
            self.debug = DebugService()
        self.debug.seq = list(value)

    def start(self):
        """ゲームループに入る。

        Policy:
            - ``Game()`` 後の ``disp()`` 呼び出しを有効にするため、
              ``__init__`` と ``pyxel.run`` を分離してある。
        """
        pyxel.run(self.update, self.draw)

    def update(self):  # noqa: CR100 CR203 CR204
        """毎フレームの入力反映と state 委譲（pyxel 互換固定名）.

        Policy:
            - ``pyxel.run(update, draw)`` の入口名なので ``update`` 固定。
            - 入力前処理 → debug 記録 → state ディスパッチの 3 段に分割。
        """
        self.input_state.update(pyxel)
        self._handle_emergency_exit_to_map()
        self._record_debug_input()
        self._dispatch_update()

    def draw(self):  # noqa: CR100 CR203 CR204
        """毎フレームの描画（pyxel 互換固定名）.

        Policy:
            - ``pyxel.run(update, draw)`` の入口名なので ``draw`` 固定。
            - ``pyxel.cls(0)`` → state 別 draw → デバッグ overlay の 3 段。
        """
        pyxel.cls(0)
        self._dispatch_draw()
        self.messages.draw_say_overlay()

    # === Internal helpers (private) ===

    def _load_jp_font_or_none(self):
        """日本語フォントを読み込み、失敗時は None を返す。

        Returns:
            pyxel.Font | None: 読み込めれば Font、失敗時は None。
        Policy:
            - Code Maker 等で BDF が読めない環境では None になり、
              各 UI ラベルとダイアログは英語フォールバックに切り替わる。
        """
        try:
            return pyxel.Font("assets/umplus_j10r.bdf")
        except Exception:
            return None

    def _build_audio_and_dialog(self) -> None:
        """SFX と dialog runner を組み立てる。

        Policy:
            - 2026-05-07 改訂：BGM は scene の view.py が pyxel.playm を
              直接呼ぶ（CJ44 確定版）。AudioManager は撤去済。
        """
        self.sfx = SfxSystem(pyxel)
        dialogue_data = DIALOGUE_JA if self.has_jp_font else DIALOGUE_EN
        self.dialog = StructuredDialogRunner(dialogue_data)

    def _build_image_banks(self) -> None:
        """ImageBanks を生成し、SFX 再構築 + tilemap load を行う。

        Policy:
            - pyxres load 後に SfxSystem を再構築する（_slot_has_sound ガードで
              import 済み SFX は上書きしない）。
        """
        self.image_banks = ImageBanks(game=self)
        self.image_banks.setup_image_banks()
        self.sfx = SfxSystem(pyxel)
        self.image_banks.setup_world_tilemap()

    def _build_runtime_state(self) -> None:
        """GameState / PlayerModel / SceneManager を生成する。

        Policy:
            - framework-rule.md M4-3 に従い scene 跨ぎ state を集約する。
            - PlayerModel が player 状態の唯一の正本（M4-1 / M4-4）。
        """
        self.game_state = GameState()
        self.player_model = PlayerModel.new_game()
        self.scene_manager = SceneManager()

    def _build_world_helpers(self) -> None:
        """vfx / text_fmt / world return 座標等を初期化する。

        Policy:
            - last_town_pos は最終的に GameState に統合予定だが、現状は Game 直属。
        """
        self.vfx = VfxSystem(game=self)
        self.text_fmt = TextFormat(game=self)
        self.last_town_pos: tuple[int, int] | None = None
        self.world_return_x = 0
        self.world_return_y = 0

    def _build_save_store(self) -> None:
        """save_store と _has_save を初期化する。

        Policy:
            - save 場所は src/runtime/save.json（dev/prod 共通）。
        """
        save_path = Path(__file__).resolve().parent / "save.json"
        self.save_store = make_save_store(save_path)
        self._has_save = self.save_store.exists()

    def _build_debug_and_input(self) -> None:
        """DebugService と InputStateTracker を生成する。

        Policy:
            - framework-rule.md M4-3：デバッグ state は DebugService に集約。
            - game.debug_mode / game.debug_seq は @property でフォワード。
        """
        self.debug = DebugService()
        self.input_state = InputStateTracker()

    def _build_scenes(self) -> None:
        """各 scene と status_bar を生成する。

        Policy:
            - 2026-05-07 改訂（CJ44 確定版）：settings_scene と apply_av は撤去済。
              BGM/SFX/VFX は常に ON。
        """
        self.splash_scene = SplashScene(game=self)
        self.title_scene = TitleScene(game=self)
        self.explore_scene = ExploreScene(game=self)
        self.shop_scene = ShopScene(game=self)
        self.menu_scene = MenuScene(game=self)
        self.ai_help_scene = AiHelpScene(game=self)
        self.ending_scene = EndingScene(game=self)
        self.town_model = TownModel()
        self.town_view = TownView(game=self)
        self.town_presenter = TownPresenter(
            model=self.town_model, game=self
        )
        self.professor_scene = ProfessorScene(game=self)
        self.battle_scene = BattleScene(game=self)
        self.status_bar = StatusBar(game=self)

    def _handle_emergency_exit_to_map(self) -> None:
        """F1 で強制的に map state へ戻す。

        Policy:
            - 緊急脱出のため explore_scene の cooldown / messages もリセットする。
        """
        if not pyxel.btnp(pyxel.KEY_F1):
            return
        self.state = "map"
        self.explore_scene.model.move_cooldown = 0
        self.explore_scene.model.has_a_cooldown = False
        self.messages.lines = []
        self.messages.index = 0
        self.messages.callback = None

    def _record_debug_input(self) -> None:
        """矢印/決定/キャンセル入力を debug seq に記録する。

        Policy:
            - up/down/その他で 3 分岐。up または down は seq に記録、
              left/right/confirm/cancel は seq をリセットする。
        """
        if self.input_state.btnp(UP_BUTTONS):
            self.debug.record_up()
            return
        if self.input_state.btnp(DOWN_BUTTONS):
            self.debug.record_down()
            return
        if self._is_horizontal_or_action_btnp():
            self.debug.reset_seq()

    def _is_left_or_right_btnp(self) -> bool:
        """左右入力が btnp されたかを返す。

        Returns:
            bool: 左/右いずれかの btnp が立っていれば True。
        Policy:
            - 副作用なしの述語。
        """
        if self.input_state.btnp(LEFT_BUTTONS):
            return True
        return self.input_state.btnp(RIGHT_BUTTONS)

    def _is_confirm_or_cancel_btnp(self) -> bool:
        """決定/キャンセル入力が btnp されたかを返す。

        Returns:
            bool: 決定/キャンセルいずれかの btnp が立っていれば True。
        Policy:
            - 副作用なしの述語。
        """
        if self.input_state.btnp(CONFIRM_BUTTONS):
            return True
        return self.input_state.btnp(CANCEL_BUTTONS)

    def _is_horizontal_or_action_btnp(self) -> bool:
        """左右/決定/キャンセルいずれかが btnp されたかを返す。

        Returns:
            bool: 述語の OR。
        Policy:
            - 述語を 2 段に分けて CR302/CR303 を回避する。
        """
        if self._is_left_or_right_btnp():
            return True
        return self._is_confirm_or_cancel_btnp()

    def _dispatch_update(self) -> None:
        """state に応じた update を委譲する。

        Policy:
            - dict マップで分岐を 1 か所に集約し、未知 state は noop。
        """
        handler = _UPDATE_DISPATCH.get(self.state)
        if handler is None:
            return
        handler(self)

    def _dispatch_draw(self) -> None:
        """state に応じた draw を委譲する。

        Policy:
            - dict マップで分岐を 1 か所に集約し、未知 state は noop。
        """
        handler = _DRAW_DISPATCH.get(self.state)
        if handler is None:
            return
        handler(self)

    def _draw_overlay_status_bar(self) -> None:
        """status_bar を重ねる private 描画。

        Policy:
            - explore 系 state の draw 後段に挟む。
        """
        self.status_bar.draw()

    def _draw_overlay_message_window(self) -> None:
        """message window を重ねる private 描画。

        Policy:
            - message/town 系 state の draw 後段に挟む。
        """
        self.messages.draw_window()

    # ---- update dispatchers (state → private handler) ----

    def _update_for_splash(self) -> None:
        """splash state の update.

        Policy:
            - splash_scene.update に委譲するだけ。
        """
        self.splash_scene.update()

    def _update_for_title(self) -> None:
        """title state の update.

        Policy:
            - title_scene.update に委譲するだけ。
        """
        self.title_scene.update()

    def _update_for_map(self) -> None:
        """map state の update.

        Policy:
            - explore_scene.update に委譲するだけ。
        """
        self.explore_scene.update()

    def _update_for_battle(self) -> None:
        """battle state の update.

        Policy:
            - battle_scene.update に委譲するだけ。
        """
        self.battle_scene.update()

    def _update_for_menu(self) -> None:
        """menu state の update.

        Policy:
            - menu_scene.update に委譲するだけ。
        """
        self.menu_scene.update()

    def _update_for_message(self) -> None:
        """message state の update.

        Policy:
            - messages.update に委譲するだけ。
        """
        self.messages.update()

    def _update_for_town(self) -> None:
        """town state の update.

        Policy:
            - town_presenter.update_message に委譲するだけ。
        """
        self.town_presenter.update_message()

    def _update_for_town_menu(self) -> None:
        """town_menu state の update.

        Policy:
            - town_presenter.update_menu に委譲するだけ。
        """
        self.town_presenter.update_menu()

    def _update_for_professor_intro(self) -> None:
        """professor_intro state の update.

        Policy:
            - professor_scene.update_intro に委譲するだけ。
        """
        self.professor_scene.update_intro()

    def _update_for_professor_ending_main(self) -> None:
        """professor_ending_main state の update.

        Policy:
            - professor_scene.update_ending_main に委譲するだけ。
        """
        self.professor_scene.update_ending_main()

    def _update_for_professor_ending_accepted(self) -> None:
        """professor_ending_accepted state の update.

        Policy:
            - professor_scene.update_ending_accepted に委譲するだけ。
        """
        self.professor_scene.update_ending_accepted()

    def _update_for_shop(self) -> None:
        """shop state の update.

        Policy:
            - shop_scene.update に委譲するだけ。
        """
        self.shop_scene.update()

    def _update_for_ending(self) -> None:
        """ending state の update.

        Policy:
            - ending_scene.update に委譲するだけ。
        """
        self.ending_scene.update()

    def _update_for_ai_help(self) -> None:
        """ai_help state の update.

        Policy:
            - ai_help_scene.update に委譲するだけ。
        """
        self.ai_help_scene.update()

    # ---- draw dispatchers (state → private handler) ----

    def _draw_for_splash(self) -> None:
        """splash state の draw.

        Policy:
            - splash_scene.draw に委譲するだけ。
        """
        self.splash_scene.draw()

    def _draw_for_title(self) -> None:
        """title state の draw.

        Policy:
            - title_scene.draw に委譲するだけ。
        """
        self.title_scene.draw()

    def _draw_for_map(self) -> None:
        """map state の draw（status_bar 重ね）.

        Policy:
            - explore_scene.draw → _draw_overlay_status_bar の 2 段。
        """
        self.explore_scene.draw()
        self._draw_overlay_status_bar()

    def _draw_for_battle(self) -> None:
        """battle state の draw.

        Policy:
            - battle_scene.draw に委譲するだけ。
        """
        self.battle_scene.draw()

    def _draw_for_menu(self) -> None:
        """menu state の draw（explore + status_bar + menu）.

        Policy:
            - 3 段重ね（explore → status_bar → menu）の固定順序。
        """
        self.explore_scene.draw()
        self._draw_overlay_status_bar()
        self.menu_scene.draw()

    def _draw_for_message(self) -> None:
        """message state の draw（explore + status_bar + window）.

        Policy:
            - 3 段重ね（explore → status_bar → message_window）の固定順序。
        """
        self.explore_scene.draw()
        self._draw_overlay_status_bar()
        self._draw_overlay_message_window()

    def _draw_for_town(self) -> None:
        """town state の draw（explore + status_bar + window）.

        Policy:
            - 3 段重ね（explore → status_bar → message_window）の固定順序。
        """
        self.explore_scene.draw()
        self._draw_overlay_status_bar()
        self._draw_overlay_message_window()

    def _draw_for_town_menu(self) -> None:
        """town_menu state の draw（town_view.render_menu）.

        Policy:
            - presenter が組み立てた view_model を view に渡すだけ。
        """
        self.town_view.render_menu(
            self.town_presenter.build_menu_view_model()
        )

    def _draw_for_shop(self) -> None:
        """shop state の draw.

        Policy:
            - shop_scene.draw に委譲するだけ。
        """
        self.shop_scene.draw()

    def _draw_for_ending(self) -> None:
        """ending state の draw.

        Policy:
            - ending_scene.draw に委譲するだけ。
        """
        self.ending_scene.draw()

    def _draw_for_professor_intro(self) -> None:
        """professor_intro state の draw.

        Policy:
            - professor_scene.draw_intro に委譲するだけ。
        """
        self.professor_scene.draw_intro()

    def _draw_for_professor_ending_main(self) -> None:
        """professor_ending_main state の draw.

        Policy:
            - professor_scene.draw_ending_main に委譲するだけ。
        """
        self.professor_scene.draw_ending_main()

    def _draw_for_professor_ending_accepted(self) -> None:
        """professor_ending_accepted state の draw.

        Policy:
            - professor_scene.draw_ending_accepted に委譲するだけ。
        """
        self.professor_scene.draw_ending_accepted()

    def _draw_for_ai_help(self) -> None:
        """ai_help state の draw.

        Policy:
            - ai_help_scene.draw に委譲するだけ。
        """
        self.ai_help_scene.draw()


# state → handler の dict マップ（CR301 elif チェーンを廃する）。
_UPDATE_DISPATCH = {
    "splash": Game._update_for_splash,
    "title": Game._update_for_title,
    "map": Game._update_for_map,
    "battle": Game._update_for_battle,
    "menu": Game._update_for_menu,
    "message": Game._update_for_message,
    "town": Game._update_for_town,
    "town_menu": Game._update_for_town_menu,
    "professor_intro": Game._update_for_professor_intro,
    "professor_ending_main": Game._update_for_professor_ending_main,
    "professor_ending_accepted": Game._update_for_professor_ending_accepted,
    "shop": Game._update_for_shop,
    "ending": Game._update_for_ending,
    "ai_help": Game._update_for_ai_help,
}


_DRAW_DISPATCH = {
    "splash": Game._draw_for_splash,
    "title": Game._draw_for_title,
    "map": Game._draw_for_map,
    "battle": Game._draw_for_battle,
    "menu": Game._draw_for_menu,
    "message": Game._draw_for_message,
    "town": Game._draw_for_town,
    "town_menu": Game._draw_for_town_menu,
    "shop": Game._draw_for_shop,
    "ending": Game._draw_for_ending,
    "professor_intro": Game._draw_for_professor_intro,
    "professor_ending_main": Game._draw_for_professor_ending_main,
    "professor_ending_accepted": Game._draw_for_professor_ending_accepted,
    "ai_help": Game._draw_for_ai_help,
}


def say(*args) -> None:
    """画面左上にデバッグ表示するヘルパ関数（Scratch say 相当）.

    Args:
        *args: 任意個の表示対象（messages.say にそのまま渡す）。
    Policy:
        - Game が未生成のときは何もしない（test 経路の防御）。
    """
    _say_via_instance(args)


def say_clear() -> None:
    """say バッファをクリアする.

    Policy:
        - Game が未生成のときは何もしない（test 経路の防御）。
    """
    _clear_say_buffer_via_instance()


def run() -> "Game":
    """entry point: Game を生成して pyxel.run に入る.

    Returns:
        Game: 生成した Game インスタンス（テスト用）。
    Policy:
        - グローバル ``game`` を上書きしてから ``start()`` に入る。
    """
    return _start_new_game()


# === Internal helpers (private, module-level) ===


def _is_game_instance_present() -> bool:
    """Game インスタンスが生成済みかを返す述語。

    Returns:
        bool: Game._instance が None でなければ True。
    Policy:
        - 副作用なしの判定だけを行う。
    """
    return Game._instance is not None


def _say_via_instance(args) -> None:
    """Game._instance.messages.say(*args) に委譲する。

    Args:
        args: say() がそのまま受け取った可変引数タプル。
    Policy:
        - Game 未生成のときは何もしない。
    """
    if not _is_game_instance_present():
        return
    Game._instance.messages.say(*args)


def _clear_say_buffer_via_instance() -> None:
    """Game._instance.messages.say_buffer.clear() に委譲する。

    Policy:
        - Game 未生成のときは何もしない。
    """
    if not _is_game_instance_present():
        return
    Game._instance.messages.say_buffer.clear()


def _start_new_game() -> "Game":
    """Game を生成しグローバル参照を更新してから start に入る。

    Returns:
        Game: 生成した Game インスタンス。
    Policy:
        - global ``game`` の書き換えは本ヘルパーに閉じる。
    """
    global game
    game = Game()
    game.start()
    return game


# グローバル 'game' 変数は run() の最初で上書きされる。
game: "Game | None" = None
