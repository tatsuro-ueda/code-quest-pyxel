from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MenuModel:
    """menu シーンの状態（P1-G7 で Game.menu_* を取り込み）。"""

    cursor: int = 0
    sub: str | None = None
    item_cursor: int = 0
    message: str = ""

    def clear_sub(self) -> None:
        """サブパネル選択状態をリセットする。

        メニューから設定画面に入る等、メニューを離れる遷移時に呼ぶ。
        framework-rule.md M4-1 で他 Scene の Model 内部状態への直接代入は
        禁止のため、外部 caller は本メソッド経由で sub をクリアする。
        """
        self.sub = None
