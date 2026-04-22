from __future__ import annotations

from dataclasses import dataclass, field

from src.scenes.battle.model import BattleModel
from src.scenes.battle.presenter import BattlePresenter
from src.scenes.battle.view import BattleView


@dataclass
class BattleScene:
    """バトル画面の model/view/presenter を束ねる Scene 実装。"""

    name: str = "battle"
    model: BattleModel = field(default_factory=BattleModel)
    view: BattleView = field(default_factory=BattleView)

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = BattlePresenter(self.model)

    def update(self) -> None:
        """毎フレーム更新。現状は状態更新なし。"""
        return None

    def draw(self) -> dict[str, str]:
        """現在のバトルフェーズから描画辞書を返す。"""
        return self.view.render(phase=self.model.phase)
