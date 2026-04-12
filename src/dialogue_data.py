from __future__ import annotations

"""Backward-compatible dialogue aliases.

実データは assets/dialogue.yaml -> tools/gen_data.py -> src/generated/dialogue.py
で生成される。
このモジュールは既存コード互換のための薄い公開窓口。
"""

from src.game_data import DIALOGUE_EN, DIALOGUE_JA
