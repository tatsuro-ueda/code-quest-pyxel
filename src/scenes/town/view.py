from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TownView:
    """town シーンの描画情報（Phase 1 スケルトン）。"""

    def render(self) -> dict[str, object]:
        """描画に必要な辞書を返す。Phase 1 スケルトンでは空 dict のみ。"""
        return {}
