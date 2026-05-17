"""town scene の local state。

Problems:
    - 町メニューのカーソル位置や入場マスを画面側に持たせると、シーン遷移で状態が散らばる。
    - メニュー項目数が変わったときにカーソル循環ロジックが各所で重複しがちで、UI 操作の挙動がぶれる。

Solutions:
    - TownModel に menu_cursor / menu_pos を集約し、循環カーソル更新を model 内に閉じる。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TownModel:
    """town scene の local state（framework-rule.md M4-1）。"""

    # === Public API ===

    menu_cursor: int = 0
    menu_pos: tuple[int, int] | None = None

    def move_cursor(self, delta: int, label_count: int) -> None:
        """メニューカーソルを delta 分動かす（循環）。

        Args:
            delta: カーソル移動量（正で次へ、負で前へ）。
            label_count: メニュー項目数。

        Boundary:
            - label_count <= 0 なら何もしない。
        """
        self._update_cursor(delta, label_count)

    def reset(self) -> None:
        """町を出るときに呼ぶ。menu_pos を None に戻す。

        Postconditions:
            - menu_pos が None、menu_cursor が 0 に戻る。
        """
        self.menu_pos = None
        self.menu_cursor = 0

    # === Internal helpers (private) ===

    def _update_cursor(self, delta: int, label_count: int) -> None:
        """label_count を法とした循環カーソル更新。

        Args:
            delta: カーソル移動量。
            label_count: メニュー項目数。

        Boundary:
            - label_count <= 0 なら何もしない。
        """
        if label_count <= 0:
            return
        self.menu_cursor = (self.menu_cursor + delta) % label_count
