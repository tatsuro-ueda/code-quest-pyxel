from __future__ import annotations

from dataclasses import dataclass

from src.scenes.ai_help.model import AiHelpModel


@dataclass
class AiHelpPresenter:
    """ai_help シーンの入力／進行（Phase 1 スケルトン）。"""

    model: AiHelpModel
