from __future__ import annotations


class BattleView:
    """バトル画面の描画用ビューモデルを組み立てる。"""

    def render(self, *, phase: str) -> dict[str, str]:
        """現在のバトルフェーズを描画に必要な辞書として返す。"""
        return {"phase": phase}
