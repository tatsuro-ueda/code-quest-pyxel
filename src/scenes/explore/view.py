from __future__ import annotations


class ExploreView:
    """探索シーンの描画用ビューモデルを組み立てる。"""

    def render(self, *, mode: str) -> dict[str, str]:
        """現在の探索モードを描画に必要な辞書として返す。"""
        return {"mode": mode}
