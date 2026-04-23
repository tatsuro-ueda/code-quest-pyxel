from __future__ import annotations

from dataclasses import dataclass

from src.scenes.splash.model import SplashModel


@dataclass
class SplashPresenter:
    """splash シーンの入力／進行（Phase 1 スケルトン）。"""

    model: SplashModel
