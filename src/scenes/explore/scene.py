from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.explore.model import ExploreModel
from src.scenes.explore.presenter import ExplorePresenter
from src.scenes.explore.view import ExploreView


@dataclass
class ExploreScene:
    """フィールド探索シーン（P1-G3 で Game から update_map / draw_map 系 8 メソッドを取り込み）。

    Phase 4（M3-2）でロジックを Presenter に集約済み。Scene は配線のみ。
    """

    name: str = "explore"
    model: ExploreModel = field(default_factory=ExploreModel)
    view: ExploreView = field(default_factory=ExploreView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = ExplorePresenter(self.model)

    def _attach_image_banks(self) -> None:
        """Model に game.image_banks を注入する（DB 読み取り用、M4-1 改訂）。"""
        game = self.game
        if game is None:
            return
        ib = getattr(game, "image_banks", None)
        if ib is not None and self.model.image_banks is not ib:
            self.model.image_banks = ib

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。"""
        game = self.game
        if game is None:
            return
        self._attach_image_banks()
        self.presenter.update(game)

    def draw(self) -> dict[str, str] | None:
        """フィールド地図を Pyxel に描画する。Presenter が VM 組立て、View に委譲（M1-1 / M2-2 準拠）。

        game が未設定（単体テスト）時は既存 view.render dict を返して互換維持。
        """
        game = self.game
        if game is None:
            return self.view.render(mode=self.model.mode)
        self._attach_image_banks()
        vm = self.presenter.build_view_model(game)
        # explore view はテキストを描かないので text_writer は省略可
        text_writer = getattr(game, "messages", None)
        self.view.draw(vm, text_writer)
        return None

    # ----- 既存テスト互換のための薄いラッパ -----

    def _check_tile_events(self, tile, nx, ny):
        """既存テスト互換：Presenter._check_tile_events に委譲。"""
        game = self.game
        if game is None:
            return
        return self.presenter._check_tile_events(game, tile, nx, ny)

    def _check_landmark_events(self) -> bool:
        """既存テスト互換：Presenter._check_landmark_events に委譲。"""
        game = self.game
        if game is None:
            return False
        return self.presenter._check_landmark_events(game)

    def _resolve_landmark_scene(self, landmark):
        """既存テスト互換：Presenter._resolve_landmark_scene に委譲。"""
        game = self.game
        if game is None:
            return None
        return self.presenter._resolve_landmark_scene(game, landmark)
