"""splash scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を SplashViewModel に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SplashViewModel:
    """splash シーンの 1 フレーム描画用解釈済みデータ。"""

    # === Public API ===

    block_color: int
    title_color: int
    subtitle_text: str | None
    presenter_text: str | None
    # 表示候補時間帯かどうか。実際の点滅判定は View が pyxel.frame_count で行う
    is_prompt_eligible: bool
