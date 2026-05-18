"""シーン切替の state holder（framework-rule.md M4-3）。

このファイルに含まれる関数・クラス：

- SceneManager: current / previous の 2 値だけを保持する state holder クラス
  - set: previous = current → current = next の単純更新を行う切替メソッド

Problems:
    - Game クラスに state / prev_state を直接持たせると、シーン切替の責務が
      Game の他処理と混ざり、テストや差し替えが難しくなる。
    - state machine 化すると遷移表や検証ロジックが膨らみ、軽い切替に対して
      過剰な仕組みになってしまう。

Solutions:
    - state machine ではなく state holder として、current と previous の
      2 値更新だけを担う薄いクラスに切り出す。
    - 切替メソッド `set` は previous = current → current = next の単純更新だけを
      行い、遷移の妥当性検証や scene 起動コールバックは持たない。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SceneManager:
    """現在 scene と直前 scene の state holder。"""

    # === Public API ===

    current: str = "splash"
    previous: str = "map"

    def set(self, next_state: str) -> None:
        """previous = current → current = next の単純更新。

        Args:
            next_state: 次に current にしたい scene 名。
        Policy:
            - 遷移の妥当性検証は行わず、与えられた値をそのまま current に入れる。
            - 直前の current は previous に退避するだけで、履歴は保持しない。
        """
        self.previous = self.current
        self.current = next_state
