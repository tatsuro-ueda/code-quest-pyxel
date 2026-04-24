from __future__ import annotations

"""town scene の薄い束ね（framework-rule.md M3-2）。

ルール本体は TownModel、入力/遷移/ViewModel 生成は TownPresenter、
描画は TownView が担う。本クラスは Game dispatcher の呼び出し窓口と
instance 配線だけを持つ（「Scene は入れ物」）。
"""

from dataclasses import dataclass, field
from typing import Any

from src.scenes.town.model import TownModel
from src.scenes.town.presenter import TownPresenter
from src.scenes.town.view import TownView


@dataclass
class TownScene:
    """TownModel / TownPresenter / TownView の束ね。"""

    name: str = "town"
    model: TownModel = field(default_factory=TownModel)
    game: Any = None
    view: TownView = field(init=False)
    presenter: TownPresenter = field(init=False)

    def __post_init__(self) -> None:
        self.view = TownView(game=self.game)
        self.presenter = TownPresenter(model=self.model, game=self.game)

    def update(self) -> None:
        """state == 'town'（メッセージ表示中）のフレーム処理。"""
        self.presenter.update_message()

    def update_menu(self) -> None:
        """state == 'town_menu' のフレーム処理。"""
        self.presenter.update_menu()

    def draw(self) -> None:
        """state == 'town' は draw_menu から呼ばれる場合に備えて空。"""
        return None

    def draw_menu(self) -> None:
        """state == 'town_menu' の描画。"""
        vm = self.presenter.build_menu_view_model()
        self.view.render_menu(vm)
