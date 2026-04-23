from __future__ import annotations

from dataclasses import dataclass

from src.scenes.professor.model import ProfessorModel


@dataclass
class ProfessorPresenter:
    """professor シーンの入力／進行（Phase 1 スケルトン）。"""

    model: ProfessorModel
