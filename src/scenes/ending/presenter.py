"""ending scene の入力解釈・遷移決定・ViewModel 組立て。

Problems:
    - シーン固有の入力解釈・遷移決定・ViewModel 組立てが Scene に直書き
      されると、責務が混ざってテストしづらい。
    - 同じ入力でも phase によって意味が変わるロジックが分散すると、
      仕様変更時に直し漏れが起きやすい。

Solutions:
    - ending の Presenter に入力解釈と遷移決定を集約し、Scene は
      生成と配線だけを担う。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.ending.model import EndingModel
from src.scenes.ending.view_model import EndingViewModel
from src.shared.services.input_bindings import CONFIRM_BUTTONS


@dataclass
class EndingPresenter:
    """ending シーンの入力解釈・遷移決定・ViewModel 組立て（M3-1）。"""

    # === Public API ===

    model: EndingModel

    def update(self, game: Any) -> None:
        """エンディング入力を処理する。CONFIRM で map に戻る（ダンジョン解除）。

        Args:
            game: game の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        if game.input_state.btnp(CONFIRM_BUTTONS):
            game.player_model.in_dungeon = False
            game.explore_scene.model.start_a_cooldown()
            game.state = "map"

    def build_view_model(self, game: Any) -> EndingViewModel:
        """Model + 現在の player level から EndingViewModel を組み立てる。

        Args:
            game: game の値。
        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        lines = self.model.lines
        head = lines[0] if lines else None
        body = list(lines[1:]) if lines else []
        return EndingViewModel(
            head_line=head,
            body_lines=body,
            level_value=game.player_model.lv,
        )
