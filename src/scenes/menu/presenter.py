"""menu scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - menu の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.menu.model import MenuModel
from src.scenes.menu.view_model import MenuRow, MenuSubPanel, MenuViewModel
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)


def _build_item_use_message(game: Any, item_data: dict, result: str) -> str:
    """アイテム使用結果メッセージを組み立てる（menu 画面用）。

    Args:
        game: ``messages`` を持つ Game オブジェクト。
        item_data: 使ったアイテムのデータ。``name`` / ``value`` を参照する。
        result: ``use_item`` の戻り値（``heal`` / ``mp_heal`` /
            ``cure_poison_ok`` / ``cure_poison_none`` / ``warp``）。

    Returns:
        プレイヤー向け日本語メッセージ。未知の result なら空文字列。

    Postconditions:
        - 副作用なし。
    """
    if result == "heal":
        return game.messages.dialog_text(
            "battle.normal.item.heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if result == "mp_heal":
        return game.messages.dialog_text(
            "battle.normal.item.mp_heal",
            item=item_data["name"],
            value=item_data["value"],
        )
    if result == "cure_poison_ok":
        return f'{item_data["name"]}を使った。バグ汚染が消えた！'
    if result == "cure_poison_none":
        return f'{item_data["name"]}を使った。だが今は必要なかった。'
    if result == "warp":
        return f'{item_data["name"]}を使った。記録した場所に戻った。'
    return ""


@dataclass
class MenuPresenter:
    """menu シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    # === Public API ===

    model: MenuModel

    def build_labels(self, game: Any) -> list[str]:
        """メニュー表示ラベルの i18n 解決（has_jp_font に応じて切替）。

        2026-05-07 改訂（CJ44 確定版）：「せってい/SETTINGS」を撤去。
        演出 ON/OFF 機構ごと撤去したため、設定画面に項目が残らない。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_build_labels(game)

    def update(self, game: Any) -> None:
        """メニュー操作を処理する。sub-state に応じて分岐。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update(game)

    def build_view_model(
        self, labels: list[str], game: Any
    ) -> MenuViewModel:
        """labels と Model + PlayerModel を解釈して VM を組み立てる。

        labels は Scene が i18n 解決済みの表示文字列リスト。

        Args:
            labels: labels の値。
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_build_view_model(labels, game)

    # === Internal helpers (private) ===

    def _handle_sub_main(
        self, game: Any, model: MenuModel, menu_items: list[str]
    ) -> None:
        """メインメニュー（sub=None）の入力処理。

        Args:
            game: game の値。
            model: model の値。
            menu_items: 表示中のメニュー項目数。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.input_state.btnp(UP_BUTTONS):
            model.cursor = (model.cursor - 1) % len(menu_items)
            game.sfx.play("cursor")
        if game.input_state.btnp(DOWN_BUTTONS):
            model.cursor = (model.cursor + 1) % len(menu_items)
            game.sfx.play("cursor")
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            game.state = "map"
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            self._invoke_main_menu(game, model)

    def _handle_sub_status(
        self, game: Any, model: MenuModel, menu_items: list[str]
    ) -> None:
        """status sub の入力処理（任意キーで閉じる）。

        Args:
            game: game の値。
            model: model の値。
            menu_items: 表示中のメニュー項目数。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        is_close_pressed = (
            game.input_state.btnp(CANCEL_BUTTONS)
            or game.input_state.btnp(CONFIRM_BUTTONS)
        )
        if is_close_pressed:
            game.sfx.play("cancel")
            model.sub = None

    def _handle_sub_items(
        self, game: Any, model: MenuModel, menu_items: list[str]
    ) -> None:
        """items sub の入力処理。

        Args:
            game: game の値。
            model: model の値。
            menu_items: 表示中のメニュー項目数。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        items = game.player_model.items
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            model.sub = None
            return
        if not items:
            return
        self._move_item_cursor(game, model, items)
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            self._use_selected_item(game, model, items)

    @staticmethod
    def _move_item_cursor(game: Any, model: MenuModel, items: list) -> None:
        """items sub のカーソル移動を処理する。

        Args:
            game: game の値。
            model: model の値。
            items: 所持アイテム一覧。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.input_state.btnp(UP_BUTTONS):
            model.item_cursor = max(0, model.item_cursor - 1)
            model.message = ""
            game.sfx.play("cursor")
        if game.input_state.btnp(DOWN_BUTTONS):
            model.item_cursor = min(
                len(items) - 1, model.item_cursor + 1
            )
            model.message = ""
            game.sfx.play("cursor")

    def _use_selected_item(
        self, game: Any, model: MenuModel, items: list
    ) -> None:
        """選択中アイテムを使用する。

        Args:
            game: game の値。
            model: model の値。
            items: items の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        item = items[model.item_cursor]
        item_data = M.ITEMS[item.id]
        result = game.player_model.use_item(
            item_data,
            town_pos=(
                getattr(game, "last_town_pos", None) or (25, 6)
            ),
        )
        if not result:
            model.message = "HPがまんたんで つかえない"
            return
        self._play_item_sfx(game, result)
        _build_item_use_message(game, item_data, result)
        model.message = ""
        self._consume_item(model, items, item)

    @staticmethod
    def _play_item_sfx(game: Any, result: str) -> None:
        """アイテム使用結果に応じた SFX を再生する。

        Args:
            game: game の値。
            result: 使用結果コード。
        Policy:
            - 該当しない結果は何も鳴らさない。
        """
        if result in {"heal", "mp_heal"}:
            game.sfx.play("heal")
        elif result == "cure_poison_ok":
            game.sfx.play("cure")

    @staticmethod
    def _consume_item(model: MenuModel, items: list, item: Any) -> None:
        """アイテム残数を 1 減らし、0 なら除去する。

        Args:
            model: model の値。
            items: 所持アイテム一覧。
            item: 使用したアイテムインスタンス。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        item.qty -= 1
        if item.qty <= 0:
            items.pop(model.item_cursor)
            model.item_cursor = max(
                0, min(model.item_cursor, len(items) - 1)
            )

    def _handle_sub_equip(
        self, game: Any, model: MenuModel, menu_items: list[str]
    ) -> None:
        """equip sub の入力処理。

        Args:
            game: game の値。
            model: model の値。
            menu_items: 表示中のメニュー項目数。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            model.sub = None
            return
        if game.input_state.btnp(UP_BUTTONS):
            model.item_cursor = (model.item_cursor - 1) % 2
            game.sfx.play("cursor")
        if game.input_state.btnp(DOWN_BUTTONS):
            model.item_cursor = (model.item_cursor + 1) % 2
            game.sfx.play("cursor")

    _SUB_HANDLERS = {
        None: _handle_sub_main,
        "status": _handle_sub_status,
        "items": _handle_sub_items,
        "equip": _handle_sub_equip,
    }

    def _invoke_main_menu(self, game: Any, model: MenuModel) -> None:
        """メインメニューのカーソル位置に応じた遷移を実行する。

        Args:
            game: game の値。
            model: model の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if model.cursor == 0:
            model.sub = "status"
            return
        if model.cursor == 1:
            model.sub = "items"
            model.item_cursor = 0
            return
        if model.cursor == 2:
            model.sub = "equip"
            model.item_cursor = 0
            return
        if model.cursor == 3:
            game.ai_help_scene.enter()
            return
        if model.cursor == 4:
            game.state = "map"

    def _run_build_labels(self, game: Any) -> list[str]:
        """_run_build_labels() の実装本体。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.has_jp_font:
            return ["ステータス", "アイテム", "そうび", "AIでしゅうせい", "とじる"]
        return ["STATUS", "ITEMS", "EQUIP", "AI HELP", "CLOSE"]

    def _run_update(self, game: Any) -> None:
        """_run_update() の実装本体。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        menu_items = self.build_labels(game)
        model = self.model
        handler = self._SUB_HANDLERS.get(model.sub, self._handle_sub_main)
        handler(self, game, model, menu_items)

    def _run_build_view_model(
        self, labels: list[str], game: Any
    ) -> MenuViewModel:
        """_run_build_view_model() の実装本体。

        Args:
            labels: labels の値。
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        model = self.model
        player = game.player_model

        main_rows: list[MenuRow] = []
        for i, label in enumerate(labels):
            is_highlighted = (i == model.cursor and model.sub is None)
            color = 10 if is_highlighted else 6
            marker = ">" if is_highlighted else " "
            main_rows.append(MenuRow(text=f"{marker} {label}", color=color))

        sub_panel = self._build_sub_panel(game, model, player, M)
        return MenuViewModel(main_rows=main_rows, sub_panel=sub_panel)

    def _build_sub_panel(
        self, game: Any, model: MenuModel, player: Any, M: Any
    ) -> MenuSubPanel | None:
        """sub 値に応じた sub_panel を組み立てる。

        Args:
            game: game の値。
            model: model の値。
            player: PlayerModel。
            M: runtime データ参照。
        Returns:
            sub_panel または None。
        Policy:
            - sub が None なら何も返さない。
        """
        if model.sub == "status":
            return self._build_status_panel(player, M)
        if model.sub == "items":
            return self._build_items_panel(game, model, player, M)
        if model.sub == "equip":
            return self._build_equip_panel(game, model, player, M)
        return None

    def _build_items_panel(
        self, game: Any, model: MenuModel, player: Any, M: Any
    ) -> MenuSubPanel:
        """items sub_panel を組み立てる。

        Args:
            game: game の値。
            model: model の値。
            player: PlayerModel。
            M: runtime データ参照。
        Returns:
            描画用 MenuSubPanel。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        items = player.items
        if not items:
            return MenuSubPanel(
                height=120,
                rows=[],
                empty_message=game.text_fmt.t("アイテムがない", "No items"),
                info_message=model.message or None,
            )
        rows = self._build_item_rows(game, model, items, M)
        return MenuSubPanel(
            height=120,
            rows=rows,
            empty_message=None,
            info_message=model.message or None,
        )

    @staticmethod
    def _build_item_rows(
        game: Any, model: MenuModel, items: list, M: Any
    ) -> list[MenuRow]:
        """items panel 用の行リストを組み立てる。

        Args:
            game: game の値。
            model: model の値。
            items: 所持アイテム一覧。
            M: runtime データ参照。
        Returns:
            MenuRow のリスト。
        Policy:
            - 先頭 8 件まで表示する。
        """
        rows: list[MenuRow] = []
        for i, item in enumerate(items[:8]):
            idata = M.ITEMS[item.id]
            is_highlighted = (i == model.item_cursor)
            color = 10 if is_highlighted else 6
            marker = ">" if is_highlighted else " "
            item_name = game.text_fmt.name(idata["name"])
            rows.append(MenuRow(
                text=f"{marker} {item_name} x{item.qty}",
                color=color,
            ))
        return rows

    def _build_equip_panel(
        self, game: Any, model: MenuModel, player: Any, M: Any
    ) -> MenuSubPanel:
        """equip sub_panel を組み立てる。

        Args:
            game: game の値。
            model: model の値。
            player: PlayerModel。
            M: runtime データ参照。
        Returns:
            描画用 MenuSubPanel。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        wlbl = game.text_fmt.t("ぶき", "WPN")
        albl = game.text_fmt.t("ぼうぐ", "ARM")
        weapon = M.WEAPONS[player.weapon]
        armor = M.ARMORS[player.armor]
        weapon_name = game.text_fmt.name(weapon["name"])
        armor_name = game.text_fmt.name(armor["name"])
        equip_lines = [
            f"{wlbl}: {weapon_name} (こうげき+{weapon['atk']})",
            f"{albl}: {armor_name} (ぼうぎょ+{armor['def']})",
        ]
        rows: list[MenuRow] = []
        for i, label in enumerate(equip_lines):
            is_highlighted = (i == model.item_cursor)
            color = 10 if is_highlighted else 6
            marker = ">" if is_highlighted else " "
            rows.append(MenuRow(text=f"{marker} {label}", color=color))
        return MenuSubPanel(height=80, rows=rows)

    def _build_status_panel(
        self, player: Any, M: Any
    ) -> MenuSubPanel:
        """status sub_panel を組み立てる。

        Args:
            player: PlayerModel。
            M: runtime データ参照。
        Returns:
            描画用 MenuSubPanel。
        Policy:
            - 装備込みのこうげき/ぼうぎょ合計を表示する。
        """
        total_atk = player.atk + M.WEAPONS[player.weapon]["atk"]
        total_def = player.defense + M.ARMORS[player.armor]["def"]
        stat_lines = [
            f"レベル {player.lv}  けいけん {player.exp}",
            f"HP {player.hp}/{player.max_hp}",
            f"MP {player.mp}/{player.max_mp}",
            f"こうげき {total_atk}  ぼうぎょ {total_def}",
            f"すばやさ {player.agi}",
            f"コイン {player.gold}",
        ]
        return MenuSubPanel(
            height=120,
            rows=[MenuRow(text=line, color=7) for line in stat_lines],
        )
