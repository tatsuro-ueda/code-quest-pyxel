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
        if game.has_jp_font:
            return ["ステータス", "アイテム", "そうび", "AIでしゅうせい", "とじる"]
        return ["STATUS", "ITEMS", "EQUIP", "AI HELP", "CLOSE"]

    def update(self, game: Any) -> None:
        """メニュー操作を処理する。sub-state に応じて分岐。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        menu_items = self.build_labels(game)
        model = self.model
        if model.sub is None:
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
                if model.cursor == 0:
                    model.sub = "status"
                elif model.cursor == 1:
                    model.sub = "items"
                    model.item_cursor = 0
                elif model.cursor == 2:
                    model.sub = "equip"
                    model.item_cursor = 0
                elif model.cursor == 3:
                    game.ai_help_scene.enter()
                elif model.cursor == 4:
                    game.state = "map"
        elif model.sub == "status":
            if (
                game.input_state.btnp(CANCEL_BUTTONS)
                or game.input_state.btnp(CONFIRM_BUTTONS)
            ):
                game.sfx.play("cancel")
                model.sub = None
        elif model.sub == "items":
            items = game.player_model.items
            if game.input_state.btnp(CANCEL_BUTTONS):
                game.sfx.play("cancel")
                model.sub = None
                return
            if items:
                if game.input_state.btnp(UP_BUTTONS):
                    model.item_cursor = max(0, model.item_cursor - 1)
                    model.message = ""
                    game.sfx.play("cursor")
                if game.input_state.btnp(DOWN_BUTTONS):
                    model.item_cursor = min(len(items) - 1, model.item_cursor + 1)
                    model.message = ""
                    game.sfx.play("cursor")
                if game.input_state.btnp(CONFIRM_BUTTONS):
                    game.sfx.play("select")
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
                    else:
                        if result in {"heal", "mp_heal"}:
                            game.sfx.play("heal")
                        elif result == "cure_poison_ok":
                            game.sfx.play("cure")
                        _build_item_use_message(game, item_data, result)
                        model.message = ""
                        item.qty -= 1
                        if item.qty <= 0:
                            items.pop(model.item_cursor)
                            model.item_cursor = max(
                                0, min(model.item_cursor, len(items) - 1)
                            )
        elif model.sub == "equip":
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
        import src.runtime.main_runtime as M
        model = self.model
        player = game.player_model

        main_rows: list[MenuRow] = []
        for i, label in enumerate(labels):
            is_highlighted = (i == model.cursor and model.sub is None)
            color = 10 if is_highlighted else 6
            marker = ">" if is_highlighted else " "
            main_rows.append(MenuRow(text=f"{marker} {label}", color=color))

        sub_panel: MenuSubPanel | None = None
        if model.sub == "status":
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
            sub_panel = MenuSubPanel(
                height=120,
                rows=[MenuRow(text=line, color=7) for line in stat_lines],
            )
        elif model.sub == "items":
            items = player.items
            rows: list[MenuRow] = []
            empty_message: str | None = None
            if not items:
                empty_message = game.text_fmt.t("アイテムがない", "No items")
            else:
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
            sub_panel = MenuSubPanel(
                height=120,
                rows=rows,
                empty_message=empty_message,
                info_message=model.message or None,
            )
        elif model.sub == "equip":
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
            rows = []
            for i, label in enumerate(equip_lines):
                is_highlighted = (i == model.item_cursor)
                color = 10 if is_highlighted else 6
                marker = ">" if is_highlighted else " "
                rows.append(MenuRow(text=f"{marker} {label}", color=color))
            sub_panel = MenuSubPanel(height=80, rows=rows)

        return MenuViewModel(main_rows=main_rows, sub_panel=sub_panel)
