"""ending scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を EndingViewModel に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EndingViewModel:
    """ending シーンの 1 フレーム描画用解釈済みデータ。"""

    # === Public API ===

    head_line: str | None  # 1 行目（色 10）。lines が空なら None
    body_lines: list[str] = field(default_factory=list)  # 2 行目以降（色 7）
    prompt_text: str = "PRESS Z TO TITLE"
    level_value: int = 1  # 現在レベル（time の表示は view 側で frame_count から計算）
