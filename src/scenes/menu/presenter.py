from __future__ import annotations

from dataclasses import dataclass

from src.scenes.menu.model import MenuModel


@dataclass
class MenuPresenter:
    """menu シーンの入力／進行（Phase 1 スケルトン）。"""

    model: MenuModel
