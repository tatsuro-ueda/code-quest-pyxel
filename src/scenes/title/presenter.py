from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.scenes.title.model import TitleModel
from src.scenes.title.view_model import TitleMenuRow, TitleViewModel


@dataclass
class TitlePresenter:
    """title シーンの入力解釈・カーソル移動・ViewModel 組立て（M3-1 / M2-2）。"""

    model: TitleModel

    def move(self, delta: int, item_count: int) -> None:
        """カーソルを相対移動し、項目数で wrap する。"""
        self.model.cursor = (self.model.cursor + delta) % item_count

    def build_view_model(self, game: Any) -> TitleViewModel:
        """Model + i18n + has_save を解釈してタイトル画面 VM を組み立てる。"""
        cursor = self.model.cursor
        labels = [
            game.text_fmt.t("はじめから", "NEW GAME"),
            game.text_fmt.t("つづきから", "CONTINUE"),
            game.text_fmt.t("せってい", "SETTINGS"),
        ]
        rows: list[TitleMenuRow] = []
        for i, label in enumerate(labels):
            enabled = (i != 1) or game._has_save
            base_color = 7 if enabled else 5
            color = 10 if (i == cursor and enabled) else base_color
            marker = ">" if i == cursor else " "
            rows.append(TitleMenuRow(label=f"{marker} {label}", color=color))
        no_save_msg: str | None = None
        if cursor == 1 and not game._has_save:
            no_save_msg = game.text_fmt.t("(まだなにもかきとめていない)", "(no save yet)")
        return TitleViewModel(
            title_text="BLOCK QUEST",
            subtitle_text=game.text_fmt.t("- コードのぼうけん -", "- A Coding Quest -"),
            menu_rows=rows,
            no_save_message=no_save_msg,
        )
