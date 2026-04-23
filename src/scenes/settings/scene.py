from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.settings.model import SettingsModel
from src.scenes.settings.presenter import SettingsPresenter
from src.scenes.settings.view import SettingsView


@dataclass
class SettingsScene:
    """settings シーンの束ね役（Phase 1 スケルトン、update/draw は空）。"""

    name: str = "settings"
    model: SettingsModel = field(default_factory=SettingsModel)
    view: SettingsView = field(default_factory=SettingsView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = SettingsPresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。Phase 1 スケルトンでは何もしない。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model から描画辞書を返す。"""
        return self.view.render()
