from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.title.model import TitleModel
from src.scenes.title.presenter import LOAD_OK_MSG, NO_RECORD_MSG, TitlePresenter
from src.scenes.title.view import TitleView


# 既存外部参照（test 等）の互換のため module-level に再エクスポート
__all__ = ["TitleScene", "LOAD_OK_MSG", "NO_RECORD_MSG"]


@dataclass
class TitleScene:
    """タイトル画面の model/view/presenter を束ねる Scene 実装。

    P1-G1（J53）で Game.update_title / Game.draw_title / Game._do_load を
    取り込み済み。Phase 4（M3-2）でロジックは Presenter に集約済み。
    """

    name: str = "title"
    model: TitleModel = field(default_factory=TitleModel)
    view: TitleView = field(default_factory=TitleView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = TitlePresenter(self.model)

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。"""
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def draw(self) -> dict[str, object] | None:
        """タイトル画面を Pyxel に描画する。

        game が設定されていない場合（単体テスト）は view.render で snapshot を返す。
        通常実行時（game 設定済み）は View.draw に委譲（M1-1 準拠）して None を返す。
        """
        game = self.game
        if game is None:
            return self.view.render(
                cursor=self.model.cursor,
                settings_open=self.model.settings_open,
            )
        vm = self.presenter.build_view_model(game)
        self.view.draw(vm, game.messages)
        return None

    def _do_load(self) -> None:
        """既存テスト互換：Presenter の do_load に委譲。"""
        game = self.game
        if game is None:
            return
        self.presenter.do_load(game)
