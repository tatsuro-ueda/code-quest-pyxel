"""デバッグモード state を集約する Service（framework-rule.md M4-3）。

このファイルに含まれる関数・クラス：

- DebugService: mode と入力履歴 seq を持つデバッグ state holder クラス
  - record_up: UP 入力を seq に積み UUDD 判定をかけるメソッド
  - record_down: DOWN 入力を seq に積み UUDD 判定をかけるメソッド
  - reset_seq: seq を空配列に戻すメソッド
  - _trim_and_check: seq を 8 件以内に整え UUDD なら mode を反転するメソッド
  - _has_uudd_suffix: seq 末尾が UUDD と一致するかを返す述語メソッド

Problems:
    - デバッグモードの ON/OFF 判定や入力履歴を app.py に書くと、
      入力読み取りと state 管理が混ざってテストで Pyxel が必要になる。
    - UUDD コードの判定条件を if に直書きすると、複合条件のまま
      意味づけがされず CR303 違反が出る。

Solutions:
    - framework-rule.md M4-3 に従い、本 Service は state-only に保ち
      入力読み取り（pyxel.btnp）は app.py 側に残す。
    - UUDD 一致判定を `_has_uudd_suffix` 述語に切り出して、
      複合条件を意図ある名前で読み下せるようにする。
"""
from __future__ import annotations

from dataclasses import dataclass, field

UUDD_SEQUENCE = ["U", "U", "D", "D"]


@dataclass
class DebugService:
    """デバッグ state（mode と入力履歴）。"""

    # === Public API ===

    mode: bool = False  # noqa: CR101
    seq: list[str] = field(default_factory=list)

    def record_up(self) -> None:
        """UP 入力を seq に記録し UUDD 判定をかける。

        Policy:
            - 末尾に "U" を追加してから _trim_and_check に委譲する。
        """
        self.seq.append("U")
        self._trim_and_check()

    def record_down(self) -> None:
        """DOWN 入力を seq に記録し UUDD 判定をかける。

        Policy:
            - 末尾に "D" を追加してから _trim_and_check に委譲する。
        """
        self.seq.append("D")
        self._trim_and_check()

    def reset_seq(self) -> None:
        """seq を空配列に戻す。

        Policy:
            - mode は触らず履歴のみを初期化する。
        """
        self.seq = []

    # === Internal helpers (private) ===

    def _trim_and_check(self) -> None:
        """seq を切り詰めて UUDD ならモードを反転する。

        Policy:
            - 8 件を超えたら末尾 4 件まで縮め、UUDD なら mode を反転する。
        """
        if len(self.seq) > 8:
            self.seq = self.seq[-4:]
        if self._has_uudd_suffix():
            self.mode = not self.mode
            self.seq = []

    def _has_uudd_suffix(self) -> bool:
        """seq の末尾が UUDD と一致するかを判定する。

        Returns:
            bool: 末尾 4 件が UUDD_SEQUENCE と一致するなら True。
        Policy:
            - 末尾 4 件が ["U", "U", "D", "D"] のときに True を返す。
        """
        if len(self.seq) < 4:
            return False
        return self.seq[-4:] == UUDD_SEQUENCE
