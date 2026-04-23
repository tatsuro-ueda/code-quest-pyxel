from __future__ import annotations

from dataclasses import dataclass

from src.scenes.shop.model import ShopModel


@dataclass
class ShopPresenter:
    """shop シーンの入力／進行（Phase 1 スケルトン）。"""

    model: ShopModel
