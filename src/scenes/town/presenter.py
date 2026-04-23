from __future__ import annotations

from dataclasses import dataclass

from src.scenes.town.model import TownModel


@dataclass
class TownPresenter:
    """town シーンの入力／進行（Phase 1 スケルトン）。"""

    model: TownModel
