from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExploreModel:
    """フィールド探索時のモード（map / menu 等）を保持する。"""

    mode: str = "map"
