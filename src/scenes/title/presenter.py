from __future__ import annotations

from dataclasses import dataclass

from src.scenes.title.model import TitleModel


@dataclass
class TitlePresenter:
    """タイトル画面の入力をカーソル移動に反映する presenter。"""

    model: TitleModel

    def move(self, delta: int, item_count: int) -> None:
        """カーソルを相対移動し、項目数で wrap する。"""
        self.model.cursor = (self.model.cursor + delta) % item_count
