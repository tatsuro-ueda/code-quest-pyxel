"""title scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - title の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.title.model import TitleModel
from src.scenes.title.view_model import TitleMenuRow, TitleViewModel
from src.shared.services.input_bindings import (
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    TITLE_START_BUTTONS,
    UP_BUTTONS,
)
from src.shared.state.player_model import PlayerModel


LOAD_OK_MSG = "きろくをよみかえした。りかいがもどってくる。"
NO_RECORD_MSG = "まだなにもかきとめていない…"


@dataclass
class TitlePresenter:
    """title シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    # === Public API ===

    model: TitleModel

    def move(self, delta: int, item_count: int) -> None:
        """カーソルを相対移動し、項目数で wrap する。

        Args:
            delta: delta の値。
            item_count: item_count の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.model.cursor = (self.model.cursor + delta) % item_count

    def update(self, game: Any) -> None:
        """タイトル画面の入力処理と state 遷移。

        2026-05-07 改訂（CJ44 確定版）：「せってい」項目を撤去（演出 ON/OFF
        機構ごと撤去）。残るのは「はじめから」「つづきから」の 2 項目のみ。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update(game)

    def do_load(self, game: Any) -> None:
        """セーブデータを読み出して player / state を復元する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_do_load(game)

    def build_view_model(self, game: Any) -> TitleViewModel:
        """Model + i18n + has_save を解釈してタイトル画面 VM を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_build_view_model(game)

    # === Internal helpers (private) ===

    def _run_update(self, game: Any) -> None:
        """_run_update() の実装本体。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.input_state.btnp(UP_BUTTONS):
            self.move(-1, 2)
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(DOWN_BUTTONS):
            self.move(1, 2)
            game.sfx.play("cursor")
            return
        if self._is_confirm_pressed(game):
            game.sfx.play("select")
            self._confirm_title_menu(game)

    @staticmethod
    def _is_confirm_pressed(game: Any) -> bool:
        """確定入力（CONFIRM または START）かを判定する。

        Args:
            game: game の値。
        Returns:
            いずれかが押されていれば True。
        Policy:
            - タイトル画面では START も確定ボタンとして扱う。
        """
        return (
            game.input_state.btnp(CONFIRM_BUTTONS)
            or game.input_state.btnp(TITLE_START_BUTTONS)
        )

    def _confirm_title_menu(self, game: Any) -> None:
        """カーソル位置に応じて新規 / ロードを実行する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if self.model.cursor == 0:
            game.player_model = PlayerModel.new_game()
            game.state = "map"
            return
        if not game._has_save:
            return
        self.do_load(game)

    def _run_do_load(self, game: Any) -> None:
        """_run_do_load() の実装本体。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        snap = game.save_store.load()
        if snap is None:
            # 破損やバージョン未来のセーフティネット
            game._has_save = False
            game.messages.show([NO_RECORD_MSG])
            game.prev_state = "title"
            game.state = "message"
            return
        restored_player, (tx, ty) = PlayerModel.from_snapshot(snap)
        game.player_model = restored_player
        game.player_model.x = tx
        game.player_model.y = ty
        game.player_model.in_dungeon = False
        # ロード直後の暴発を防ぐため A クールダウンを立てる
        game.explore_scene.model.start_a_cooldown()
        game.messages.show([LOAD_OK_MSG])
        game.prev_state = "map"
        game.state = "message"

    def _run_build_view_model(self, game: Any) -> TitleViewModel:
        """_run_build_view_model() の実装本体。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        cursor = self.model.cursor
        rows = self._build_title_rows(game, cursor)
        no_save_msg = self._build_no_save_message(game, cursor)
        subtitle = game.text_fmt.t(
            "- コードのぼうけん -", "- A Coding Quest -"
        )
        return TitleViewModel(
            title_text="BLOCK QUEST",
            subtitle_text=subtitle,
            menu_rows=rows,
            no_save_message=no_save_msg,
        )

    @staticmethod
    def _build_title_rows(game: Any, cursor: int) -> list[TitleMenuRow]:
        """タイトルメニューの行リストを返す。

        Args:
            game: game の値。
            cursor: カーソル位置。
        Returns:
            TitleMenuRow のリスト。
        Policy:
            - CONTINUE は has_save=False のときグレーアウト。
        """
        labels = [
            game.text_fmt.t("はじめから", "NEW GAME"),
            game.text_fmt.t("つづきから", "CONTINUE"),
        ]
        rows: list[TitleMenuRow] = []
        for i, label in enumerate(labels):
            is_enabled = (i != 1) or game._has_save
            base_color = 7 if is_enabled else 5
            color = 10 if (i == cursor and is_enabled) else base_color
            marker = ">" if i == cursor else " "
            rows.append(TitleMenuRow(label=f"{marker} {label}", color=color))
        return rows

    @staticmethod
    def _build_no_save_message(game: Any, cursor: int) -> str | None:
        """CONTINUE 上で save が無いときの注意メッセージを返す。

        Args:
            game: game の値。
            cursor: カーソル位置。
        Returns:
            該当時のみメッセージ、そうでなければ None。
        Policy:
            - cursor=1（CONTINUE）かつ has_save=False のときだけ JP/EN メッセージを返す。
        """
        if cursor != 1:
            return None
        if game._has_save:
            return None
        return game.text_fmt.t("(まだなにもかきとめていない)", "(no save yet)")
