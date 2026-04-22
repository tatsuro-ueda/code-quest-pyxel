from __future__ import annotations

from dataclasses import dataclass

from src.scenes.battle.model import BattleModel


@dataclass
class BattlePresenter:
    """バトル画面のフェーズ遷移を model に反映する presenter。"""

    model: BattleModel

    def change_phase(self, phase: str) -> None:
        """バトルの現在フェーズを指定値に差し替える。"""
        self.model.phase = phase
