from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TownModel:
    """town scene の local state（framework-rule.md M4-1）。"""

    menu_cursor: int = 0
    menu_pos: tuple[int, int] | None = None

    def move_cursor(self, delta: int, label_count: int) -> None:
        """メニューカーソルを delta 分動かす（循環）。"""
        if label_count <= 0:
            return
        self.menu_cursor = (self.menu_cursor + delta) % label_count

    def reset(self) -> None:
        """町を出るときに呼ぶ。menu_pos を None に戻す。"""
        self.menu_pos = None
        self.menu_cursor = 0
