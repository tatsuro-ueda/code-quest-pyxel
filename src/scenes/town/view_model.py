"""TownView が受け取る描画データ。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、描画と意思決定が混ざる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値（タイトル・ラベル・カーソル位置・所持GOLD）を TownMenuViewModel に集約する。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TownMenuViewModel:
    """TownView が受け取る描画データ（framework-rule.md M2-2）。

    View が自ら判定をせずに描けるよう、文字列・色・数値だけに解釈済み。
    """

    # === Public API ===

    title: str
    labels: tuple[str, ...]
    cursor: int
    gold: int
