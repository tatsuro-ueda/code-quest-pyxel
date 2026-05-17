"""ai_help scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を AiHelpViewModel に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AiHelpViewModel:
    """ai_help パネル描画用の解釈済みデータ。"""

    # === Public API ===

    title: str
    body_lines: list[str] = field(default_factory=list)
