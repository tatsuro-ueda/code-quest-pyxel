from __future__ import annotations

from dataclasses import dataclass

from src.scenes.explore.model import ExploreModel


@dataclass
class ExplorePresenter:
    """探索シーンのモード切替を model に反映する presenter。"""

    model: ExploreModel

    def change_mode(self, mode: str) -> None:
        """探索モードを指定値（map / menu など）に差し替える。"""
        self.model.mode = mode
