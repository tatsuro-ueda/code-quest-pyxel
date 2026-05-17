"""splash scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - splash の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.splash.model import SplashModel
from src.scenes.splash.view_model import SplashViewModel
from src.shared.services.input_bindings import CANCEL_BUTTONS, CONFIRM_BUTTONS


@dataclass
class SplashPresenter:
    """splash シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1）。"""

    # === Public API ===

    model: SplashModel

    def update(self, game: Any) -> None:
        """フレームを進めて自動遷移するか、任意キーでスキップする。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.model.frame += 1
        if (
            self.model.frame >= 90
            or game.input_state.btnp(CONFIRM_BUTTONS)
            or game.input_state.btnp(CANCEL_BUTTONS)
        ):
            game.state = "title"

    def build_view_model(self, game: Any) -> SplashViewModel:
        """Model + i18n を解釈して SplashViewModel を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
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
            is_prompt_eligible=(f >= 75),
        )
