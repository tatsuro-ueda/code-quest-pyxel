from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TownMenuViewModel:
    """TownView が受け取る描画データ（framework-rule.md M2-2）。

    View が自ら判定をせずに描けるよう、文字列・色・数値だけに解釈済み。
    """

    title: str
    labels: tuple[str, ...]
    cursor: int
    gold: int
