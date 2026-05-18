"""メニューウィンドウの配置寸法（コマンドメニュー枠）を表す不変レコード。

このファイルに含まれる関数・クラス：

- MenuWindow: メニューウィンドウの矩形（x / y / width / height）を保持する不変レコード
  - rect: 描画用に (x, y, width, height) のタプルを返す

Problems:
    - 各 scene の描画コードにメニュー枠の magic number を直接書くと、
      レイアウト変更のたびに複数箇所を編集することになる。
    - 矩形を可変フィールドとして持つと、描画中に書き換わって
      フレーム間でメニュー位置がぶれるリスクがある。

Solutions:
    - MenuWindow を frozen dataclass にして、生成後は値が変わらない
      レイアウト記述子として scene 間で共有する。
    - 矩形取得は rect() に集約し、scene 側は (x, y, w, h) の組だけを
      受け取って描画範囲を決める。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MenuWindow:
    """メニューウィンドウの配置寸法を表す不変レコード。"""

    # === Public API ===

    x: int = 20
    y: int = 40
    width: int = 216
    height: int = 170

    def rect(self) -> tuple[int, int, int, int]:  # noqa: CR100
        """描画用に (x, y, width, height) のタプルを返す。

        Returns:
            (x, y, width, height) 形式の矩形タプル。
        Policy:
            - フィールドの単純な並び替えに留め、座標変換や副作用は行わない。
            - メソッド名 rect は外部テストで参照されているため固定。
        """
        return (self.x, self.y, self.width, self.height)
