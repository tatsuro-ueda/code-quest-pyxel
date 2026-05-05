from __future__ import annotations

"""デバッグモード state を集約する Service（framework-rule.md M4-3）。

入力読み取り（pyxel.btnp）は app.py に残し、本 Service は state-only。
UUDD コードでデバッグモードのトグルが起きる。
"""

from dataclasses import dataclass, field


@dataclass
class DebugService:
    """デバッグ state（mode と入力履歴）。"""

    mode: bool = False
    seq: list[str] = field(default_factory=list)

    def record_up(self) -> None:
        self.seq.append("U")
        self._trim_and_check()

    def record_down(self) -> None:
        self.seq.append("D")
        self._trim_and_check()

    def reset_seq(self) -> None:
        self.seq = []

    def _trim_and_check(self) -> None:
        if len(self.seq) > 8:
            self.seq = self.seq[-4:]
        if len(self.seq) >= 4 and self.seq[-4:] == ["U", "U", "D", "D"]:
            self.mode = not self.mode
            self.seq = []
