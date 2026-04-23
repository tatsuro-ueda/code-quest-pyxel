from __future__ import annotations

from dataclasses import dataclass

from src.scenes.ending.model import EndingModel


@dataclass
class EndingPresenter:
    """ending シーンの入力／進行（Phase 1 スケルトン）。"""

    model: EndingModel
