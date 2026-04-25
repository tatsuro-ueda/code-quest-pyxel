from __future__ import annotations

"""ending シーンの ViewModel（M2-2：解釈済みの描画用データ）。

現在経過時間は pyxel.frame_count に依存するため VM には乗せず、view 側で
計算する（presenter で pyxel API を読むと M1-1 違反）。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EndingViewModel:
    """ending シーンの 1 フレーム描画用解釈済みデータ。"""

    head_line: str | None  # 1 行目（色 10）。lines が空なら None
    body_lines: list[str] = field(default_factory=list)  # 2 行目以降（色 7）
    prompt_text: str = "PRESS Z TO TITLE"
    level_value: int = 1  # 現在レベル（time の表示は view 側で frame_count から計算）
