from __future__ import annotations

"""settings シーンの ViewModel（M2-2：解釈済みの描画用データ）。"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SettingsRow:
    """設定行 1 行の解釈済みデータ。"""

    label: str  # 表示文字列（marker + key + value 込み）
    color: int  # ハイライト色


@dataclass(frozen=True)
class SettingsViewModel:
    """settings シーン全体の解釈済みデータ。"""

    title: str
    footer: str
    rows: list[SettingsRow] = field(default_factory=list)
