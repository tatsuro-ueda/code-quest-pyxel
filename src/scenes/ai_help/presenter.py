"""ai_help scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - ai_help の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.ai_help.model import AiHelpModel
from src.scenes.ai_help.view_model import AiHelpViewModel
from src.shared.services.input_bindings import CANCEL_BUTTONS, CONFIRM_BUTTONS


@dataclass
class AiHelpPresenter:
    """ai_help シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1）。"""

    # === Public API ===

    model: AiHelpModel

    def update(self, game: Any) -> None:
        """AI ヘルプの入力を処理する。CONFIRM/CANCEL で menu に戻る。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update(game)

    def build_view_model(self, game: Any) -> AiHelpViewModel:
        """Model.status から AI ヘルプパネルの解釈済みデータを組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return AiHelpViewModel(
            title="AIで このゲームを しゅうせい",
            body_lines=[
                "",
                "１ Code Maker の Save をおして",
                "  main.py をダウンロード",
                "",
                "２ ブラウザで claude.ai か",
                "  chatgpt.com をひらく",
                "",
                "３ main.py をはりつけて",
                "  「ここを こう なおして」と たのむ",
                "",
                "４ かえってきた コードを",
                "  Code Maker に はりつける",
                "",
                f"  -> {self.model.status}",
            ],
        )

    # === Internal helpers (private) ===

    def _run_update(self, game: Any) -> None:
        """_run_update() の実装本体。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if (
            game.input_state.btnp(CANCEL_BUTTONS)
            or game.input_state.btnp(CONFIRM_BUTTONS)
        ):
            game.sfx.play("cancel")
            game.state = "menu"
