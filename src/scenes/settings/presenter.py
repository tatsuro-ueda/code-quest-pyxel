from __future__ import annotations

from dataclasses import dataclass

from src.scenes.settings.model import SettingsModel


@dataclass
class SettingsPresenter:
    """settings シーンの入力／進行（Phase 1 スケルトン）。"""

    model: SettingsModel
