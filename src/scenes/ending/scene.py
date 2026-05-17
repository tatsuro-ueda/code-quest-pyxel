"""ending scene 本体（Model / View / Presenter の配線）。

Problems:
    - Scene に入力解釈と描画ロジックを直書きすると、レイヤが崩れて
      テスト時に Pyxel まで起動する必要が出る。
    - シーンごとに生成・配線手順がばらばらだと、新しいシーンを
      追加する時に何を持たせるか毎回考え直すことになる。

Solutions:
    - ending の Scene は Model / View / Presenter を保持し、
      update / draw を Presenter / View へ委譲する薄い配線に保つ。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.ending.model import EndingModel
from src.scenes.ending.presenter import EndingPresenter
from src.scenes.ending.view import EndingView, play_bgm as _play_ending_bgm


@dataclass
class EndingScene:
    """エンディング画面（P1-G11 で Game から 3 メソッドを取り込み）。"""

    # === Public API ===

    name: str = "ending"
    model: EndingModel = field(default_factory=EndingModel)
    view: EndingView = field(default_factory=EndingView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.presenter = EndingPresenter(self.model)

    def enter(self) -> None:
        """エンディングに入る。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        self.model.lines = game.messages.dialog_lines("ending.main.line01")
        game.state = "ending"

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update()

    def draw(self) -> None:
        """エンディング画面を描画する。Presenter が VM 組立て、View に委譲（M1-1 / M2-2 準拠）。

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
        if not self.model.lines:
            self.model.lines = game.messages.dialog_lines("ending.main.line01")
        _play_ending_bgm(game)
        vm = self.presenter.build_view_model(game)
        self.view.render(vm, game.messages)
