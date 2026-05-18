"""会話ウィンドウ（画面下部の台詞枠）レイアウト設定の不変レコード。

このファイルに含まれる関数・クラス：

- DialogWindow: 会話ウィンドウの配置寸法を保持する不変レコード
  - rect: 描画用に (x, y, width, height) のタプルを返す

Problems:
    - 各 scene の描画コードに会話枠の magic number を直接書くと、
      レイアウト変更のたびに複数箇所を編集することになる。
    - 寸法を可変フィールドとして持つと、描画中に書き換わって
      フレーム間で表示位置がぶれるリスクがある。

Solutions:
    - DialogWindow を frozen dataclass にして、生成後は値が変わらない
      レイアウト記述子として scene 間で共有する。
    - 寸法取得は rect() に集約し、scene 側は (x, y, w, h) の組だけを
      受け取って描画位置とサイズを決める。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DialogWindow:
    """会話ウィンドウの配置寸法（画面下部の台詞枠）を表す不変レコード。"""

    # === Public API ===

    x: int = 8
    y: int = 208
    width: int = 240
    height: int = 44

    def rect(self) -> tuple[int, int, int, int]:  # noqa: CR100
        """描画用に (x, y, width, height) のタプルを返す。

        Returns:
            (x, y, width, height) 形式の矩形寸法。
        Policy:
            - フィールドの単純な並び替えに留め、座標変換や副作用は行わない。
            - メソッド名 rect は他の UI レイアウトと統一されているため固定。
        """
        return (self.x, self.y, self.width, self.height)
