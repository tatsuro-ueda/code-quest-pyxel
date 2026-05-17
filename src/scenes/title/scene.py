"""title scene 本体（Model / View / Presenter の配線）。

Problems:
    - Scene に入力解釈と描画ロジックを直書きすると、レイヤが崩れて
      テスト時に Pyxel まで起動する必要が出る。
    - シーンごとに生成・配線手順がばらばらだと、新しいシーンを
      追加する時に何を持たせるか毎回考え直すことになる。

Solutions:
    - title の Scene は Model / View / Presenter を保持し、
      update / draw を Presenter / View へ委譲する薄い配線に保つ。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.title.model import TitleModel
from src.scenes.title.presenter import (
    LOAD_OK_MSG,
    NO_RECORD_MSG,
    TitlePresenter,
)
from src.scenes.title.view import TitleView, play_bgm as _play_title_bgm


# 既存外部参照（test 等）の互換のため module-level に再エクスポート
__all__ = ["TitleScene", "LOAD_OK_MSG", "NO_RECORD_MSG"]


@dataclass
class TitleScene:
    """タイトル画面の model/view/presenter を束ねる Scene 実装。

    P1-G1（J53）で Game.update_title / Game.draw_title / Game._do_load を
    取り込み済み。Phase 4（M3-2）でロジックは Presenter に集約済み。
    """

    # === Public API ===

    name: str = "title"
    model: TitleModel = field(default_factory=TitleModel)
    view: TitleView = field(default_factory=TitleView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.presenter = TitlePresenter(self.model)

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update()

    def draw(self) -> dict[str, object] | None:
        """タイトル画面を Pyxel に描画する。

        game が設定されていない場合（単体テスト）は view.render で snapshot を返す。
        通常実行時（game 設定済み）は View.draw に委譲（M1-1 準拠）して None を返す。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_draw()

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

    def _run_draw(self) -> dict[str, object] | None:
        """_run_draw() の実装本体。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return self.view.render(cursor=self.model.cursor)
        _play_title_bgm(game)
        vm = self.presenter.build_view_model(game)
        self.view.draw(vm, game.messages)
        return None

    def _do_load(self) -> None:
        """既存テスト互換：Presenter の do_load に委譲。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.do_load(game)
