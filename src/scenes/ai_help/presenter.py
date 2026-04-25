from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.ai_help.model import AiHelpModel
from src.scenes.ai_help.view_model import AiHelpViewModel
from src.shared.services.input_bindings import CANCEL_BUTTONS, CONFIRM_BUTTONS


@dataclass
class AiHelpPresenter:
    """ai_help シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1）。"""

    model: AiHelpModel

    def update(self, game: Any) -> None:
        """AI ヘルプの入力を処理する。CONFIRM/CANCEL で menu に戻る。"""
        if game.input_state.btnp(CANCEL_BUTTONS) or game.input_state.btnp(CONFIRM_BUTTONS):
            game.sfx.play("cancel")
            game.state = "menu"

    def build_view_model(self, game: Any) -> AiHelpViewModel:
        """Model.status から AI ヘルプパネルの解釈済みデータを組み立てる。"""
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
