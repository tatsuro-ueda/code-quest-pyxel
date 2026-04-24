from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.town.model import TownModel
from src.scenes.town.view_model import TownMenuViewModel
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)
from src.shared.services.save_store import LocalStorageSaveStore, SaveStoreError


@dataclass
class TownPresenter:
    """town scene の入力解釈・遷移決定・ViewModel 生成（framework-rule.md M3-1）。

    描画は TownView、状態は TownModel / PlayerModel にある。
    Presenter は Service を呼び、Model を更新し、遷移を決める。
    """

    model: TownModel
    game: Any = None

    # ----- queries -----

    def current_town_index(self) -> int:
        """menu_pos から町 index を取得する。未入場時は 0。"""
        import src.runtime.main_runtime as M

        if self.model.menu_pos is None:
            return 0
        return M.TOWN_INDEX_BY_POS.get(self.model.menu_pos, 0)

    def _inn_cost(self) -> int:
        """現在の町の宿代を返す（INN_PRICES → INN_COST フォールバック）。"""
        import src.runtime.main_runtime as M

        idx = self.current_town_index()
        return M.INN_PRICES[idx] if idx < len(M.INN_PRICES) else M.INN_COST

    # ----- update entry points -----

    def update_message(self) -> None:
        """state == 'town' のフレーム処理。メッセージ送り→マップ復帰。"""
        game = self.game
        if game is None:
            return
        if game.messages.any_advance_btnp():
            game.messages.index, done = game.messages.advance_page(
                game.messages.index, game.messages.lines
            )
            if done:
                game.state = "map"

    def update_menu(self) -> None:
        """state == 'town_menu' のフレーム処理。メニュー入力を解釈する。"""
        game = self.game
        if game is None:
            return
        import src.runtime.main_runtime as M

        if game.input_state.btnp(UP_BUTTONS):
            game.sfx.play("cursor")
            self.model.move_cursor(-1, len(M.TOWN_MENU_LABELS))
            return
        if game.input_state.btnp(DOWN_BUTTONS):
            game.sfx.play("cursor")
            self.model.move_cursor(1, len(M.TOWN_MENU_LABELS))
            return
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            self._exit()
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            label = M.TOWN_MENU_LABELS[self.model.menu_cursor]
            if label == "はなす":
                self._talk()
            elif label in M.SHOP_KIND_BY_LABEL:
                game.shop_scene.enter(M.SHOP_KIND_BY_LABEL[label])
            elif label == "やどや":
                self._inn()
            elif label == "セーブ":
                self._save()
            elif label == "でる":
                self._exit()

    # ----- view model -----

    def build_menu_view_model(self) -> TownMenuViewModel:
        """メニュー描画用の ViewModel を組み立てる（framework-rule.md M2-2）。"""
        game = self.game
        import src.runtime.main_runtime as M

        labels = M.TOWN_MENU_LABELS if game.has_jp_font else M.TOWN_MENU_LABELS_EN
        title = game.text_fmt.t("まちメニュー", "TOWN MENU")
        return TownMenuViewModel(
            title=title,
            labels=tuple(labels),
            cursor=self.model.menu_cursor,
            gold=game.player_model.gold,
        )

    # ----- actions -----

    def _enter_message(self, lines, callback=None) -> None:
        """町メニュー内で通知を出す。閉じたら town_menu に戻る。"""
        game = self.game
        game.messages.lines = lines
        game.messages.index = 0
        game.messages.callback = callback
        game.prev_state = "town_menu"
        game.state = "message"

    def _talk(self) -> None:
        """町NPCとの会話。"""
        game = self.game
        import src.runtime.main_runtime as M

        scene_name = M.TOWN_DIALOG_SCENES.get(self.model.menu_pos)
        if scene_name is not None:
            lines = game.messages.dialog_lines(
                scene_name, ProfessorPhase=game.professor_scene.phase()
            )
            self._enter_message(lines)
            return
        idx = self.current_town_index()
        if idx >= len(M.TOWN_NPC_LINES):
            self._enter_message(["……ここには はなせるひとが いない。"])
            return
        npc_lines = M.TOWN_NPC_LINES[idx]
        current = game.player_model.advance_npc_talk_idx(idx, len(npc_lines))
        self._enter_message([npc_lines[current]])

    def _inn(self) -> None:
        """宿屋泊まり（PlayerModel.stay_at_inn 経由）。"""
        game = self.game
        import src.runtime.main_runtime as M

        if not game.player_model.stay_at_inn(self._inn_cost()):
            self._enter_message([M.INN_LACK_MSG])
            return
        self._enter_message([M.INN_OK_MSG])

    def _save(self) -> None:
        """セーブ実行（PlayerModel.to_snapshot 経由）。"""
        game = self.game
        import src.runtime.main_runtime as M

        snap = game.player_model.to_snapshot(town_pos=self.model.menu_pos)
        try:
            game.save_store.save(snap)
        except SaveStoreError:
            is_web = isinstance(game.save_store, LocalStorageSaveStore)
            msg = M.SAVE_FAIL_MSG_WEB if is_web else M.SAVE_FAIL_MSG_DESKTOP
            self._enter_message([msg])
            return
        game._has_save = True
        game.sfx.play("save")
        self._enter_message([M.SAVE_OK_MSG])

    def _exit(self) -> None:
        """町メニューから出る。"""
        game = self.game
        game.state = "map"
        game.explore_scene.model.a_cooldown = True
        self.model.reset()
        game.current_town = None
