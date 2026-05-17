"""professor scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を ProfessorChoiceRow に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProfessorChoiceRow:
    """選択肢 1 行（intro phase 専用）。"""

    # === Public API ===

    label: str  # marker + 表示文字列
    color: int


@dataclass(frozen=True)
class ProfessorViewModel:
    """professor 1 phase の描画用解釈済みデータ。"""

    # === Public API ===

    # 現ページの折返し済み行
    page_lines: list[str] = field(default_factory=list)
    # 1 行目の y 座標
    text_y: int = 60
    text_color: int = 7
    # 次ページプロンプト座標、None なら非表示
    prompt_xy: tuple[int, int] | None = None
    # 選択肢（intro のみ）
    choices: list[ProfessorChoiceRow] = field(default_factory=list)
