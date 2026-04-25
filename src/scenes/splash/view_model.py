from __future__ import annotations

"""splash シーンの ViewModel（M2-2：解釈済みの描画用データ）。

View には Model や Game を直接渡さず、本 ViewModel に「解釈済み」の値
（色・表示文字列・可視フラグ等）だけを乗せて渡す。フレーム数や i18n の
分岐判断は Presenter / Scene 側で済ませる。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SplashViewModel:
    """splash シーンの 1 フレーム描画用解釈済みデータ。"""

    block_color: int
    title_color: int
    subtitle_text: str | None
    presenter_text: str | None
    prompt_eligible: bool  # 表示候補時間帯かどうか。実際の点滅判定は View が pyxel.frame_count で行う
