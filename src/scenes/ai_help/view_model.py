from __future__ import annotations

"""ai_help シーンの ViewModel（M2-2：解釈済みの描画用データ）。"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AiHelpViewModel:
    """ai_help パネル描画用の解釈済みデータ。"""

    title: str
    body_lines: list[str] = field(default_factory=list)
