from __future__ import annotations

"""professor シーンの ViewModel（M2-2：解釈済みの描画用データ）。

3 つの phase (intro / ending_main / ending_accepted) を 1 つの VM 形式に
統一し、view 側を単一描画メソッドに縮退する。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProfessorChoiceRow:
    """選択肢 1 行（intro phase 専用）。"""

    label: str  # marker + 表示文字列
    color: int


@dataclass(frozen=True)
class ProfessorViewModel:
    """professor 1 phase の描画用解釈済みデータ。"""

    page_lines: list[str] = field(default_factory=list)  # 現ページの折返し済み行
    text_y: int = 60  # 1 行目の y 座標
    text_color: int = 7
    prompt_xy: tuple[int, int] | None = None  # 次ページプロンプト座標、None なら非表示
    choices: list[ProfessorChoiceRow] = field(default_factory=list)  # 選択肢（intro のみ）
