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

    model: ShopModel

    def update(self, game: Any) -> None:
        """ショップのカーソル操作と購入処理。短期メッセージの ttl もここで減らす。"""
        self._tick_message_ttl()
        if not self.model.inventory:
            if game.input_state.btnp(CANCEL_BUTTONS) or game.input_state.btnp(CONFIRM_BUTTONS):
                game.sfx.play("cancel")
                game.state = "town_menu"
            return
        if game.input_state.btnp(UP_BUTTONS):
            self.model.cursor = (self.model.cursor - 1) % len(self.model.inventory)
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(DOWN_BUTTONS):
            self.model.cursor = (self.model.cursor + 1) % len(self.model.inventory)
            game.sfx.play("cursor")
            return
        if game.input_state.btnp(CANCEL_BUTTONS):
            game.sfx.play("cancel")
            game.state = "town_menu"
            return
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("select")
            self.try_purchase(game)

    def try_purchase(self, game: Any) -> None:
        """購入を試みる。所持／資金不足／購入成功の各分岐で message を更新。"""
        import src.runtime.main_runtime as M
        idx = self.model.inventory[self.model.cursor]
        kind = self.model.kind
        if kind == "weapons":
            entry = M.WEAPONS[idx]
        elif kind == "armors":
            entry = M.ARMORS[idx]
        else:
            entry = M.ITEMS[idx]
        price = entry.get("price", 0)
        pm = game.player_model
        if kind == "weapons" and pm.weapon == idx:
            self._set_short_message("すでに もっています")
            return
        if kind == "armors" and pm.armor == idx:
            self._set_short_message("すでに もっています")
            return
        if not pm.can_afford(price):
            self._set_short_message("コインが たりません")
            return
        if kind == "weapons":
            pm.buy_weapon(idx, price)
            self._set_short_message(entry.get("buy_msg") or f"{entry['name']}を てにいれた！")
        elif kind == "armors":
            pm.buy_armor(idx, price)
            self._set_short_message(entry.get("buy_msg") or f"{entry['name']}を てにいれた！")
        else:
            pm.buy_item(idx, price)
            self._set_short_message(f"{entry['name']}を てにいれた！")

    def build_view_model(self, game: Any) -> ShopViewModel:
        """Model + ゲームデータを解釈してショップ画面 VM を組み立てる。

        Policy:
            - 行内に `[もっています]` は出さない（横幅が 256px を超えて切れるため）。
            - 下部メッセージは「短期 message > カーソル位置の owned 自動表示」の優先で出す。
            - owned 自動表示は weapons / armors のみ。items は装備中概念が無いため対象外。
        """
        import src.runtime.main_runtime as M
        m = self.model
        if game.has_jp_font:
            title_map = {"weapons": "ぶきや", "armors": "ぼうぐや", "items": "どうぐや"}
            title = title_map.get(m.kind, "ショップ")
        else:
            title_map = {"weapons": "WEAPONS", "armors": "ARMOR", "items": "ITEMS"}
            title = title_map.get(m.kind, "SHOP")
        gold_label = f"G:{game.player_model.gold}"
        empty_message: str | None = None
        rows: list[ShopRow] = []
        if not m.inventory:
            empty_message = game.text_fmt.t("(ざいこなし)", "(no stock)")
        else:
            for i, idx in enumerate(m.inventory):
                if m.kind == "weapons":
                    e = M.WEAPONS[idx]
                    line = f"{game.text_fmt.name(e['name'])}  こうげき+{e['atk']}  {e['price']}G"
                elif m.kind == "armors":
                    e = M.ARMORS[idx]
                    line = f"{game.text_fmt.name(e['name'])}  ぼうぎょ+{e['def']}  {e['price']}G"
                else:
                    e = M.ITEMS[idx]
                    line = f"{game.text_fmt.name(e['name'])}  {e['price']}G"
                color = 10 if i == m.cursor else 7
                marker = ">" if i == m.cursor else " "
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
        """短期メッセージの残り表示フレーム数を 1 減らし、0 以下なら message をクリアする。"""
        if self.model.message_ttl > 0:
            self.model.message_ttl -= 1
            if self.model.message_ttl <= 0:
                self.model.message = ""
                self.model.message_ttl = 0

    def _set_short_message(self, text: str) -> None:
        """短期メッセージをセットし、表示寿命を MESSAGE_TTL_FRAMES に戻す。"""
        self.model.message = text
        self.model.message_ttl = MESSAGE_TTL_FRAMES

    def _resolve_display_message(self, game: Any) -> str | None:
        """下部に表示するメッセージを決める。

        Returns:
            短期 message が残っていればそれ。
            空のときは weapons/armors のカーソル位置が装備中なら OWNED_MESSAGE。
            それ以外は None。
        """
        m = self.model
        if m.message:
            return m.message
        if not m.inventory:
            return None
        if m.kind not in ("weapons", "armors"):
            return None
        cursor_idx = m.inventory[m.cursor]
        pm = game.player_model
        if m.kind == "weapons" and pm.weapon == cursor_idx:
            return OWNED_MESSAGE
        if m.kind == "armors" and pm.armor == cursor_idx:
            return OWNED_MESSAGE
        return None
