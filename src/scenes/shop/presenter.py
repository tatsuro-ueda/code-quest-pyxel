"""shop scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - shop の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.shop.model import ShopModel
from src.scenes.shop.view_model import ShopRow, ShopViewModel
from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    UP_BUTTONS,
)

# 短期メッセージ（買った/コイン不足/すでにもっている）の表示寿命。
# 30fps 想定で約 2 秒。0 になったらカーソル位置の装備判定にフォールバックする。
MESSAGE_TTL_FRAMES = 60

OWNED_MESSAGE = "すでに もっている。"


@dataclass
class ShopPresenter:
    """shop シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1 / M2-2）。"""

    # === Public API ===

    model: ShopModel

    def update(self, game: Any) -> None:
        """ショップのカーソル操作と購入処理。短期メッセージの ttl もここで減らす。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update(game)

    def try_purchase(self, game: Any) -> None:
        """購入を試みる。所持／資金不足／購入成功の各分岐で message を更新。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_try_purchase(game)

    def build_view_model(self, game: Any) -> ShopViewModel:
        """Model + ゲームデータを解釈してショップ画面 VM を組み立てる。

        Policy:
            - 行内に `[もっています]` は出さない（横幅が 256px を超えて切れるため）。
            - 下部メッセージは「短期 message > カーソル位置の owned 自動表示」の優先で出す。
            - owned 自動表示は weapons / armors のみ。items は装備中概念が無いため対象外。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
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
        self._tick_message_ttl()
        if not self.model.inventory:
            if (
                game.input_state.btnp(CANCEL_BUTTONS)
                or game.input_state.btnp(CONFIRM_BUTTONS)
            ):
                game.sfx.play("cancel")
                game.state = "town_menu"
            return
        inventory_size = len(self.model.inventory)
        if game.input_state.btnp(UP_BUTTONS):
            self.model.cursor = (self.model.cursor - 1) % inventory_size
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(DOWN_BUTTONS):
            self.model.cursor = (self.model.cursor + 1) % inventory_size
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            game.state = "town_menu"
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            self.try_purchase(game)

    def _run_try_purchase(self, game: Any) -> None:
        """_run_try_purchase() の実装本体。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        index = self.model.inventory[self.model.cursor]
        kind = self.model.kind
        if kind == "weapons":
            entry = M.WEAPONS[index]
        elif kind == "armors":
            entry = M.ARMORS[index]
        else:
            entry = M.ITEMS[index]
        price = entry.get("price", 0)
        pm = game.player_model
        if kind == "weapons" and pm.weapon == index:
            self._set_short_message("すでに もっています")
            return
        if kind == "armors" and pm.armor == index:
            self._set_short_message("すでに もっています")
            return
        if not pm.can_afford(price):
            self._set_short_message("コインが たりません")
            return
        custom_msg = entry.get("buy_msg")
        bought_text = (
            custom_msg if custom_msg else f"{entry['name']}を てにいれた！"
        )
        if kind == "weapons":
            pm.buy_weapon(index, price)
            self._set_short_message(bought_text)
        elif kind == "armors":
            pm.buy_armor(index, price)
            self._set_short_message(bought_text)
        else:
            pm.buy_item(index, price)
            self._set_short_message(f"{entry['name']}を てにいれた！")

    def _run_build_view_model(self, game: Any) -> ShopViewModel:
        """_run_build_view_model() の実装本体。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        import src.runtime.main_runtime as M
        model = self.model
        if game.has_jp_font:
            title_map = {"weapons": "ぶきや", "armors": "ぼうぐや", "items": "どうぐや"}
            title = title_map.get(model.kind, "ショップ")
        else:
            title_map = {
                "weapons": "WEAPONS",
                "armors": "ARMOR",
                "items": "ITEMS",
            }
            title = title_map.get(model.kind, "SHOP")
        gold_label = f"G:{game.player_model.gold}"
        empty_message: str | None = None
        rows: list[ShopRow] = []
        if not model.inventory:
            empty_message = game.text_fmt.t("(ざいこなし)", "(no stock)")
        else:
            for i, index in enumerate(model.inventory):
                if model.kind == "weapons":
                    e = M.WEAPONS[index]
                    name = game.text_fmt.name(e["name"])
                    line = f"{name}  こうげき+{e['atk']}  {e['price']}G"
                elif model.kind == "armors":
                    e = M.ARMORS[index]
                    name = game.text_fmt.name(e["name"])
                    line = f"{name}  ぼうぎょ+{e['def']}  {e['price']}G"
                else:
                    e = M.ITEMS[index]
                    name = game.text_fmt.name(e["name"])
                    line = f"{name}  {e['price']}G"
                color = 10 if i == model.cursor else 7
                marker = ">" if i == model.cursor else " "
                rows.append(ShopRow(label=f"{marker} {line}", color=color))
        message = self._resolve_display_message(game)
        return ShopViewModel(
            title=title,
            gold_label=gold_label,
            rows=rows,
            empty_message=empty_message,
            message=message,
        )

    def _tick_message_ttl(self) -> None:
        """短期メッセージの残り表示フレーム数を 1 減らし、0 以下なら message をクリアする。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if self.model.message_ttl > 0:
            self.model.message_ttl -= 1
            if self.model.message_ttl <= 0:
                self.model.message = ""
                self.model.message_ttl = 0

    def _set_short_message(self, text: str) -> None:
        """短期メッセージをセットし、表示寿命を MESSAGE_TTL_FRAMES に戻す。

        Args:
            text: text の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.model.message = text
        self.model.message_ttl = MESSAGE_TTL_FRAMES

    def _resolve_display_message(self, game: Any) -> str | None:
        """下部に表示するメッセージを決める。

        Returns:
            短期 message が残っていればそれ。
            空のときは weapons/armors のカーソル位置が装備中なら OWNED_MESSAGE。
            それ以外は None。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        model = self.model
        if model.message:
            return model.message
        if not model.inventory:
            return None
        if model.kind not in ("weapons", "armors"):
            return None
        cursor_idx = model.inventory[model.cursor]
        pm = game.player_model
        if model.kind == "weapons" and pm.weapon == cursor_idx:
            return OWNED_MESSAGE
        if model.kind == "armors" and pm.armor == cursor_idx:
            return OWNED_MESSAGE
        return None
