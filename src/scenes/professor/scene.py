from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.professor.model import ProfessorModel
from src.scenes.professor.presenter import ProfessorPresenter
from src.scenes.professor.view import ProfessorView


@dataclass
class ProfessorScene:
    """professor シーンの束ね役（Phase 1 スケルトン、update/draw は空）。"""

    name: str = "professor"
    model: ProfessorModel = field(default_factory=ProfessorModel)
    view: ProfessorView = field(default_factory=ProfessorView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = ProfessorPresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。Phase 1 スケルトンでは何もしない。"""
        return None

    def draw(self) -> dict[str, object]:
        """現在の model から描画辞書を返す。"""
        return self.view.render()
