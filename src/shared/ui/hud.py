"""HUD（ステータス表示）レイアウト設定の不変レコード。

このファイルに含まれる関数・クラス：

- HudLayout: HUD の余白（top_margin / left_margin）を保持する不変レコード
  - origin: HUD の描画原点 (x, y) を返す

Problems:
    - 各 scene の描画コードに余白の magic number を直接書くと、
      レイアウト変更のたびに複数箇所を編集することになる。
    - 余白を可変フィールドとして持つと、描画中に書き換わって
      フレーム間で表示位置がぶれるリスクがある。

Solutions:
    - HudLayout を frozen dataclass にして、生成後は値が変わらない
      レイアウト記述子として scene 間で共有する。
    - 原点取得は origin() に集約し、scene 側は (x, y) の組だけを
      受け取って描画位置を決める。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HudLayout:
    """HUD（ステータス表示）の余白設定を表す不変レコード。"""

    # === Public API ===

    top_margin: int = 0
    left_margin: int = 0

    def origin(self) -> tuple[int, int]:  # noqa: CR100
        """HUD の描画原点 (x, y) を返す。

        Returns:
            (x, y) 形式の描画原点。x = left_margin、y = top_margin。
        Policy:
            - フィールドの単純な並び替えに留め、座標変換や副作用は行わない。
            - メソッド名 origin は外部テストで参照されているため固定。
        """
        return (self.left_margin, self.top_margin)
