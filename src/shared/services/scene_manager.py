from __future__ import annotations

"""シーン切替の state holder（framework-rule.md M4-3）。

Game クラスから state / prev_state field を移送する最小実装。
state machine ではなく state holder：current と previous の 2 値だけを保持し、
切替メソッド (`set`) は previous = current → current = next の更新のみ行う。
遷移の妥当性検証や scene 起動コールバックは持たない。
"""

from dataclasses import dataclass


@dataclass
class SceneManager:
    """現在 scene と直前 scene の state holder。"""

    current: str = "splash"
    previous: str = "map"

    def set(self, next_state: str) -> None:
        """previous = current → current = next の単純更新。"""
        self.previous = self.current
        self.current = next_state
