from __future__ import annotations

"""title シーンの ViewModel（M2-2：解釈済みの描画用データ）。"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TitleMenuRow:
    """タイトル画面メニュー 1 行。"""

    label: str  # marker + 表示文字列
    color: int  # ハイライト色


@dataclass(frozen=True)
class TitleViewModel:
    """title シーン全体の解釈済みデータ。"""

    title_text: str
    subtitle_text: str
    menu_rows: list[TitleMenuRow] = field(default_factory=list)
    no_save_message: str | None = None  # CONTINUE 選択中＆セーブ無し時のヒント、None なら非表示
