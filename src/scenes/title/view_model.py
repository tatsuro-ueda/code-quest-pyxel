"""title scene の ViewModel（描画用解釈済みデータ）。

Problems:
    - View が Model や Presenter の内部状態を直接参照すると、
      描画と意思決定が混ざってテストしづらくなる。
    - 描画に必要なデータが暗黙に決まっていると、画面追加・文言変更時に
      View 側で都度判定が必要になる。

Solutions:
    - 描画に必要な値を TitleMenuRow に集約し、View はこの dataclass
      だけを受け取って描く。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TitleMenuRow:
    """タイトル画面メニュー 1 行。"""

    # === Public API ===

    label: str  # marker + 表示文字列
    color: int  # ハイライト色


@dataclass(frozen=True)
class TitleViewModel:
    """title シーン全体の解釈済みデータ。"""

    # === Public API ===

    title_text: str
    subtitle_text: str
    menu_rows: list[TitleMenuRow] = field(default_factory=list)
    no_save_message: str | None = None  # CONTINUE 選択中＆セーブ無し時のヒント、None なら非表示
