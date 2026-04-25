from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.ending.model import EndingModel
from src.scenes.ending.view_model import EndingViewModel


@dataclass
class EndingPresenter:
    """ending シーンの ViewModel 組立て（M3-1 / M2-2）。"""

    model: EndingModel

    def build_view_model(self, game: Any) -> EndingViewModel:
        """Model + 現在の player level から EndingViewModel を組み立てる。"""
        lines = self.model.lines
        head = lines[0] if lines else None
        body = list(lines[1:]) if lines else []
        return EndingViewModel(
            head_line=head,
            body_lines=body,
            level_value=game.player_model.lv,
        )
