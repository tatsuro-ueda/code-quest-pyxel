from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.splash.model import SplashModel
from src.scenes.splash.view_model import SplashViewModel


@dataclass
class SplashPresenter:
    """splash シーンの ViewModel 組立て（M3-1 / M2-2）。"""

    model: SplashModel

    def build_view_model(self, game: Any) -> SplashViewModel:
        """Model + i18n を解釈して SplashViewModel を組み立てる。"""
        f = self.model.frame
        return SplashViewModel(
            block_color=1 if f < 15 else (5 if f < 30 else 12),
            title_color=7 if f >= 20 else 5,
            subtitle_text=(
                game.text_fmt.t("コードのたびは、ここから", "Coding journey starts here")
                if f >= 40
                else None
            ),
            presenter_text=(
                game.text_fmt.t("presented by うえだたつろう", "by Tatsuro Ueda")
                if f >= 60
                else None
            ),
            prompt_eligible=(f >= 75),
        )
