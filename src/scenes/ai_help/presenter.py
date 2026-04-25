from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.ai_help.model import AiHelpModel
from src.scenes.ai_help.view_model import AiHelpViewModel


@dataclass
class AiHelpPresenter:
    """ai_help シーンの ViewModel 組立て（M3-1 / M2-2）。"""

    model: AiHelpModel

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
