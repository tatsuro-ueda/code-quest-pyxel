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
            self._handle_empty_inventory(game)
            return
        self._handle_inventory_input(game)

    def _handle_empty_inventory(self, game: Any) -> None:
        """在庫無し時のクローズ入力を処理する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        is_close_pressed = (
            game.input_state.btnp(CANCEL_BUTTONS)
            or game.input_state.btnp(CONFIRM_BUTTONS)
        )
        if is_close_pressed:
            game.sfx.play("cancel")
            game.state = "town_menu"

    def _handle_inventory_input(self, game: Any) -> None:
        """在庫ありの場合のカーソル移動・確定・キャンセル入力を処理する。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
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
        index = self.model.inventory[self.model.cursor]
        kind = self.model.kind
        entry = self._get_entry(kind, index)
        price = entry.get("price", 0)
        pm = game.player_model
        if self._is_already_owned(kind, pm, index):
            self._set_short_message("すでに もっています")
            return
        if not pm.can_afford(price):
            self._set_short_message("コインが たりません")
            return
        self._apply_purchase(pm, kind, index, price, entry)

    @staticmethod
    def _get_entry(kind: str, index: int) -> dict:
        """kind に応じて runtime データから entry を返す。

        Args:
            kind: ショップ種別 ("weapons" / "armors" / "items")。
            index: inventory のインデックス。
        Returns:
            runtime データの entry dict。
        Policy:
            - kind が weapons / armors 以外は ITEMS を見る。
        """
        import src.runtime.main_runtime as M
        if kind == "weapons":
            return M.WEAPONS[index]
        if kind == "armors":
            return M.ARMORS[index]
        return M.ITEMS[index]

    @staticmethod
    def _is_already_owned(kind: str, pm: Any, index: int) -> bool:
        """すでに装備済みかを判定する。

        Args:
            kind: ショップ種別。
            pm: PlayerModel。
            index: 装備インデックス。
        Returns:
            装備済みなら True。
        Policy:
            - items 種別は所持量で扱うため、ここでは常に False を返す。
        """
        if kind == "weapons":
            return pm.weapon == index
        if kind == "armors":
            return pm.armor == index
        return False

    def _apply_purchase(
        self, pm: Any, kind: str, index: int, price: int, entry: dict
    ) -> None:
        """購入処理を pm に適用し、メッセージを設定する。

        Args:
            pm: PlayerModel。
            kind: ショップ種別。
            index: 購入対象インデックス。
            price: 価格。
            entry: runtime データの entry dict。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        custom_msg = entry.get("buy_msg")
        bought_text = (
            custom_msg if custom_msg else f"{entry['name']}を てにいれた！"
        )
        if kind == "weapons":
            pm.buy_weapon(index, price)
            self._set_short_message(bought_text)
            return
        if kind == "armors":
            pm.buy_armor(index, price)
            self._set_short_message(bought_text)
            return
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
        model = self.model
        title = self._resolve_shop_title(game, model.kind)
        gold_label = f"G:{game.player_model.gold}"
        empty_message: str | None = None
        rows: list[ShopRow] = []
        if not model.inventory:
            empty_message = game.text_fmt.t("(ざいこなし)", "(no stock)")
        else:
            rows = self._build_shop_rows(game)
        message = self._resolve_display_message(game)
        return ShopViewModel(
            title=title,
            gold_label=gold_label,
            rows=rows,
            empty_message=empty_message,
            message=message,
        )

    @staticmethod
    def _resolve_shop_title(game: Any, kind: str) -> str:
        """ショップ画面のタイトル文字列を返す。

        Args:
            game: game の値。
            kind: ショップ種別。
        Returns:
            JP / EN ラベル文字列。
        Policy:
            - has_jp_font の有無でラベル辞書を切り替える。
        """
        if game.has_jp_font:
            title_map = {"weapons": "ぶきや", "armors": "ぼうぐや", "items": "どうぐや"}
            return title_map.get(kind, "ショップ")
        title_map = {
            "weapons": "WEAPONS",
            "armors": "ARMOR",
            "items": "ITEMS",
        }
        return title_map.get(kind, "SHOP")

    def _build_shop_rows(self, game: Any) -> list[ShopRow]:
        """インベントリ行を組み立てる。

        Args:
            game: game の値。
        Returns:
            ShopRow のリスト。
        Policy:
            - kind に応じて行フォーマットを切り替える。
        """
        model = self.model
        rows: list[ShopRow] = []
        for i, index in enumerate(model.inventory):
            line = self._format_shop_line(game, model.kind, index)
            color = 10 if i == model.cursor else 7
            marker = ">" if i == model.cursor else " "
            rows.append(ShopRow(label=f"{marker} {line}", color=color))
        return rows

    @staticmethod
    def _format_shop_line(game: Any, kind: str, index: int) -> str:
        """1 行分のショップ表示文字列を返す。

        Args:
            game: game の値。
            kind: ショップ種別。
            index: inventory のインデックス。
        Returns:
            「名前 + 属性 + 価格」の文字列。
        Policy:
            - weapons / armors はステータス値を付け、items は価格だけにする。
        """
        import src.runtime.main_runtime as M
        if kind == "weapons":
            e = M.WEAPONS[index]
            name = game.text_fmt.name(e["name"])
            return f"{name}  こうげき+{e['atk']}  {e['price']}G"
        if kind == "armors":
            e = M.ARMORS[index]
            name = game.text_fmt.name(e["name"])
            return f"{name}  ぼうぎょ+{e['def']}  {e['price']}G"
        e = M.ITEMS[index]
        name = game.text_fmt.name(e["name"])
        return f"{name}  {e['price']}G"

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
        is_predicate_2 = model.kind == 'weapons' and pm.weapon == cursor_idx
        if is_predicate_2:
            return OWNED_MESSAGE
        is_predicate_0 = model.kind == 'armors' and pm.armor == cursor_idx
        if is_predicate_0:
            return OWNED_MESSAGE
        return None
