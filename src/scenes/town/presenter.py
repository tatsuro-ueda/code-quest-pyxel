"""town scene の入力解釈・遷移決定・ViewModel 生成。

Problems:
    - 町メニューの入力解釈・遷移・描画用データ生成が散らばると、ボタン仕様変更や町追加で複数箇所を直すことになる。
    - shop/inn/save/exit など町固有アクションが update_menu に直書きされると、責務が混ざってテストしづらい。

Solutions:
    - TownPresenter に town scene 用入力解釈と遷移決定を集約し、各アクションを private helper に分離する。
"""

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

    # === Public API ===

    model: TownModel
    game: Any = None

    def update_message(self) -> None:
        """state == 'town' のフレーム処理。メッセージ送り→マップ復帰。

        Policy:
            - メッセージ送りが完了したら state を 'map' に戻す。
        """
        self._tick_message()

    def update_menu(self) -> None:
        """state == 'town_menu' のフレーム処理。メニュー入力を解釈する。

        Policy:
            - 上下入力でカーソル移動、確定キーで選択中ラベルのアクションを実行する。
        """
        self._tick_menu()

    def build_menu_view_model(self) -> TownMenuViewModel:
        """メニュー描画用の ViewModel を組み立てる（framework-rule.md M2-2）。

        Returns:
            TownMenuViewModel: 描画用データ。日本語フォントの有無でラベルを切り替え済み。

        Policy:
            - 表示と判定を分離するため、ここで言語切替済みの label を埋め込む。
        """
        return self._build_menu_vm()

    # === Internal helpers (private) ===

    def _get_town_index(self) -> int:
        """menu_pos から町 index を取得する。未入場時は 0。

        Returns:
            int: TOWN_INDEX_BY_POS から引いた町 index。

        Policy:
            - menu_pos が None（未入場）なら 0 を返す。
        """
        import src.runtime.main_runtime as M

        if self.model.menu_pos is None:
            return 0
        return M.TOWN_INDEX_BY_POS.get(self.model.menu_pos, 0)

    def _get_inn_cost(self) -> int:
        """現在の町の宿代を返す。

        Returns:
            int: 宿代（INN_PRICES → INN_COST フォールバック）。

        Policy:
            - 町 index が INN_PRICES の範囲外なら INN_COST を使う。
        """
        import src.runtime.main_runtime as M

        index = self._get_town_index()
        return M.INN_PRICES[index] if index < len(M.INN_PRICES) else M.INN_COST

    def _tick_message(self) -> None:
        """update_message の本体。メッセージ送り→マップ復帰。

        Policy:
            - game が未設定なら何もしない。送り完了で state を 'map' に戻す。
        """
        game = self.game
        if game is None:
            return
        if not game.messages.any_advance_btnp():
            return
        game.messages.index, done = game.messages.advance_page(
            game.messages.index, game.messages.lines
        )
        if done:
            game.state = "map"

    def _tick_menu(self) -> None:
        """update_menu の本体。入力分岐をアーリーリターンで連結する。

        Policy:
            - カーソル入力 → キャンセル入力 → 確定入力の順に処理する。
        """
        game = self.game
        if game is None:
            return
        if self._handle_cursor_input():
            return
        if self._handle_cancel_input():
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            self._dispatch_confirm()

    def _handle_cursor_input(self) -> bool:
        """上下入力でカーソル移動。

        Returns:
            bool: 上下入力でカーソルを動かしたら True、それ以外は False。

        Policy:
            - 移動時には cursor SE を再生する。
        """
        game = self.game
        import src.runtime.main_runtime as M

        if game.input_state.btnp(UP_BUTTONS):
            game.sfx.play("cursor")
            self.model.move_cursor(-1, len(M.TOWN_MENU_LABELS))
            return True
        if game.input_state.btnp(DOWN_BUTTONS):
            game.sfx.play("cursor")
            self.model.move_cursor(1, len(M.TOWN_MENU_LABELS))
            return True
        return False

    def _handle_cancel_input(self) -> bool:
        """キャンセル入力で町を出る。

        Returns:
            bool: キャンセル入力で町を出たら True、それ以外は False。

        Policy:
            - 出るときに cancel SE を再生する。
        """
        game = self.game
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            self._exit()
            return True
        return False

    def _dispatch_confirm(self) -> None:
        """確定キーで選択中ラベルのアクションを実行する。

        Policy:
            - はなす / shop / やどや / セーブ / でる の各ラベルを private helper に振り分ける。
        """
        import src.runtime.main_runtime as M

        label = M.TOWN_MENU_LABELS[self.model.menu_cursor]
        if label == "はなす":
            self._talk()
            return
        if label in M.SHOP_KIND_BY_LABEL:
            self.game.shop_scene.enter(M.SHOP_KIND_BY_LABEL[label])
            return
        if label == "やどや":
            self._stay_at_inn()
            return
        if label == "セーブ":
            self._save()
            return
        if label == "でる":
            self._exit()

    def _build_menu_vm(self) -> TownMenuViewModel:
        """build_menu_view_model の本体。

        Returns:
            TownMenuViewModel: 描画用データ。

        Policy:
            - 日本語フォントの有無で TOWN_MENU_LABELS / TOWN_MENU_LABELS_EN を切り替える。
            - 「やどや」/「INN」ラベルだけ宿代を併記し、子どもが選ぶ前に費用が分かるようにする。
        """
        game = self.game
        import src.runtime.main_runtime as M

        base_labels = M.TOWN_MENU_LABELS if game.has_jp_font else M.TOWN_MENU_LABELS_EN
        inn_cost = self._get_inn_cost()
        labels = tuple(self._format_inn_label(label, inn_cost) for label in base_labels)
        title = game.text_fmt.t("まちメニュー", "TOWN MENU")
        return TownMenuViewModel(
            title=title,
            labels=labels,
            cursor=self.model.menu_cursor,
            gold=game.player_model.gold,
        )

    def _format_inn_label(self, label: str, inn_cost: int) -> str:
        """「やどや」/「INN」ラベルだけ宿代を併記する。

        Args:
            label: 元のメニューラベル文字列。
            inn_cost: 現在の町の宿代。

        Returns:
            str: 「やどや」なら「やどや（{inn_cost}G）」、「INN」なら「INN ({inn_cost}G)」、
                 それ以外は label をそのまま返す。

        Policy:
            - 日本語は全角括弧、英語は半角括弧で統一する。
            - ぶきや等の他ラベルは複数アイテムで価格が一意でないため、ここでは整形しない。
        """
        if label == "やどや":
            return f"やどや（{inn_cost}G）"
        if label == "INN":
            return f"INN ({inn_cost}G)"
        return label

    def _enter_message(self, lines, callback=None) -> None:
        """町メニュー内で通知を出す。閉じたら town_menu に戻る。

        Args:
            lines: 表示するメッセージ行のリスト。
            callback: メッセージ閉じ時に呼ぶコールバック。

        Postconditions:
            - state == 'message'、prev_state == 'town_menu' になる。
        """
        game = self.game
        game.messages.lines = lines
        game.messages.index = 0
        game.messages.callback = callback
        game.prev_state = "town_menu"
        game.state = "message"

    def _talk(self) -> None:
        """町NPCとの会話。

        Policy:
            - 専用ダイアログ scene があればそれを優先、なければ NPC ラインを順送りする。
        """
        game = self.game
        import src.runtime.main_runtime as M

        scene_name = M.TOWN_DIALOG_SCENES.get(self.model.menu_pos)
        if scene_name is not None:
            lines = game.messages.dialog_lines(
                scene_name, ProfessorPhase=game.professor_scene.phase()
            )
            self._enter_message(lines)
            return
        index = self._get_town_index()
        if index >= len(M.TOWN_NPC_LINES):
            self._enter_message(["……ここには はなせるひとが いない。"])
            return
        npc_lines = M.TOWN_NPC_LINES[index]
        current = game.player_model.advance_npc_talk_idx(index, len(npc_lines))
        self._enter_message([npc_lines[current]])

    def _stay_at_inn(self) -> None:
        """宿屋泊まり（PlayerModel.stay_at_inn 経由）。

        Policy:
            - 所持金が宿代に満たなければ INN_LACK_MSG、足りれば INN_OK_MSG を出す。
        """
        game = self.game
        import src.runtime.main_runtime as M

        if not game.player_model.stay_at_inn(self._get_inn_cost()):
            self._enter_message([M.INN_LACK_MSG])
            return
        self._enter_message([M.INN_OK_MSG])

    def _save(self) -> None:
        """セーブ実行（PlayerModel.to_snapshot 経由）。

        Policy:
            - SaveStoreError 時は Web / Desktop で失敗文言を切り替える。
        """
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
        """町メニューから出る。

        Postconditions:
            - state == 'map'、TownModel が reset、current_town が None。
        """
        game = self.game
        game.state = "map"
        game.explore_scene.model.start_a_cooldown()
        self.model.reset()
        game.current_town = None
