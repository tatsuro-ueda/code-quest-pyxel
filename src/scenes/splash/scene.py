"""splash scene 本体（Model / View / Presenter の配線）。

Problems:
    - Scene に入力解釈と描画ロジックを直書きすると、レイヤが崩れて
      テスト時に Pyxel まで起動する必要が出る。
    - シーンごとに生成・配線手順がばらばらだと、新しいシーンを
      追加する時に何を持たせるか毎回考え直すことになる。

Solutions:
    - splash の Scene は Model / View / Presenter を保持し、
      update / draw を Presenter / View へ委譲する薄い配線に保つ。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.splash.model import SplashModel
from src.scenes.splash.presenter import SplashPresenter
from src.scenes.splash.view import SplashView


@dataclass
class SplashScene:
    """起動直後のスプラッシュ画面（P1-G2 で update_splash / draw_splash を取り込み）。"""

    # === Public API ===

    name: str = "splash"
    model: SplashModel = field(default_factory=SplashModel)
    view: SplashView = field(default_factory=SplashView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.presenter = SplashPresenter(self.model)

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update()

    def draw(self) -> None:
        """スプラッシュ画面を描画する。

        Presenter が ViewModel を組み立て、View に委譲（M1-1 / M2-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_draw()

    # === Internal helpers (private) ===

    def _run_update(self) -> None:
        """_run_update() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def _run_draw(self) -> None:
        """_run_draw() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        vm = self.presenter.build_view_model(game)
        self.view.render(vm, game.messages)
