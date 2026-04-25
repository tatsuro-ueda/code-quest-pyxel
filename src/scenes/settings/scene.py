from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.settings.model import SettingsModel
from src.scenes.settings.presenter import SettingsPresenter
from src.scenes.settings.view import SettingsView


@dataclass
class SettingsScene:
    """設定画面（P1-G8 で Game から 7 メソッドを取り込み）。"""

    name: str = "settings"
    model: SettingsModel = field(default_factory=SettingsModel)
    view: SettingsView = field(default_factory=SettingsView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = SettingsPresenter(self.model)

    def open(self, origin: str) -> None:
        """設定画面に入る。origin は 'menu' か 'title'。"""
        game = self.game
        self.model.origin = origin
        self.model.cursor = 0
        game.menu_scene.model.sub = None
        game.state = "settings"

    def apply_av(self) -> None:
        """player の AV 設定を audio / sfx に反映する（外部 API 互換）。"""
        game = self.game
        if game is None:
            return
        self.presenter.apply_av(game)

    def _toggle(self, key: str) -> None:
        """既存テスト互換：トグル処理を Presenter に委譲。"""
        game = self.game
        if game is None:
            return
        self.presenter._toggle(game, key)

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。"""
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def draw(self) -> None:
        """設定画面を描画する。Presenter が VM 組立て、View に委譲（M1-1 / M2-2 準拠）。"""
        game = self.game
        if game is None:
            return
        vm = self.presenter.build_view_model(game)
        self.view.render(vm, game.messages)
