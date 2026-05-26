"""page_dialog scene の描画用 ViewModel。

Problems:
    - View が Scene や Model を直接見ると、描画と state 管理が混ざる。
    - full-screen 会話の色や text_y の違いを View が都度判定すると、
      scene ごとの見た目差分が増えたときに条件分岐が広がる。

Solutions:
    - 描画に必要な値を PageDialogViewModel にまとめ、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PageDialogViewModel:
    """full-screen page dialog の描画用解釈済みデータ。"""

    # === Public API ===

    page_lines: list[str] = field(default_factory=list)
    text_y: int = 60
    text_color: int = 7
    prompt_xy: tuple[int, int] | None = None
