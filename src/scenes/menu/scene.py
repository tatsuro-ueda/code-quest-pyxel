"""menu scene 本体（Model / View / Presenter の配線）。

Problems:
    - Scene に入力解釈と描画ロジックを直書きすると、レイヤが崩れて
      テスト時に Pyxel まで起動する必要が出る。
    - シーンごとに生成・配線手順がばらばらだと、新しいシーンを
      追加する時に何を持たせるか毎回考え直すことになる。

Solutions:
    - menu の Scene は Model / View / Presenter を保持し、
      update / draw を Presenter / View へ委譲する薄い配線に保つ。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.menu.model import MenuModel
from src.scenes.menu.presenter import MenuPresenter
from src.scenes.menu.view import MenuView


@dataclass
class MenuScene:
    """menu シーン（P1-G7 で Game から 3 メソッドを取り込み）。"""

    # === Public API ===

    name: str = "menu"
    model: MenuModel = field(default_factory=MenuModel)
    view: MenuView = field(default_factory=MenuView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.presenter = MenuPresenter(self.model)

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def draw(self) -> None:
        """メニュー画面を描画する。描画本体は View に委譲（M1-1 準拠）。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return self.view.render()
        vm = self.presenter.build_view_model(
            self.presenter.build_labels(game), game
        )
        self.view.draw(vm, game.messages)

    # === Internal helpers (private) ===

    def _get_labels(self) -> list[str]:
        """既存テスト互換：Presenter.build_labels に委譲。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self.presenter.build_labels(self.game)
