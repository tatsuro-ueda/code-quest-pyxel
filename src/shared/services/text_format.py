"""日本語名 → 英語名の変換マップと言語フォールバック。

このファイルに含まれる関数・クラス：

- name_en: 日本語名を NAME_EN_MAP で英語名に変換する純粋関数
- TextFormat: game.has_jp_font に応じて jp/en を切り替える言語フォールバック
  - t: jp/en の 2 引数から、フォント有無に応じてどちらかを返す
  - name: データ名（敵・装備など）の翻訳。フォントが無いとき name_en を引く

Problems:
    - BDF フォント未読込環境（Pyxel Code Maker など）では日本語が描画できず、
      日本語ラベルをそのまま渡すと表示が崩れる。
    - 呼び出し側で毎回 if has_jp_font を書くと、表示分岐が散らばってしまう。

Solutions:
    - 名前変換は NAME_EN_MAP の 1 箇所に集約し、未登録時は原文を返す純粋関数で包む。
    - 言語フォールバックは TextFormat に集約し、game.has_jp_font の参照を 1 箇所にする。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


NAME_EN_MAP = {
    # enemies
    "10ほスライム": "10-step Slime",
    "かいてんゴブリン": "Loop Goblin",
    "ループゴースト": "Loop Ghost",
    "10かいナイト": "10-times Knight",
    "もしガード": "If Guard",
    "でなければスライム": "Else Slime",
    "HPカウンター": "HP Counter",
    "クローンにんじゃ": "Clone Ninja",
    "むげんバグ": "Infinity Bug",
    "まおうグリッチのクローン": "Glitch Lord Clone",
    "まおうグリッチ": "Glitch Lord",
    "プロフェッサー": "The Professor",
    # items
    "バグレポート": "Bug Report",
    "エナジードリンク": "Energy Drink",
    "アンチウイルス": "Antivirus",
    "セーブポイント": "Save Point",
    # weapons
    "すで": "Bare Hands",
    "マウス": "Mouse",
    "キーボード": "Keyboard",
    "テキストエディタ": "Text Editor",
    "コードエディタ": "Code Editor",
    "デバッガー": "Debugger",
    "コンパイラ": "Compiler",
    "アーキテクト": "Architect",
    # armors
    "ふだんぎ": "Casual Wear",
    "きほんのちしき": "Basic Knowledge",
    "じゅんじしょりのりかい": "Sequential Logic",
    "ループのりかい": "Loop Mastery",
    "じょうけんのりかい": "Conditional Logic",
    "へんすうのりかい": "Variable Mastery",
    "せっけいりょく": "Design Skill",
    "さいてきかのしこう": "Optimization Mind",
    # spells
    "デバッグ": "Debug",
    "プリント": "Print",
    "ループブレイク": "Loop Break",
    "リファクタリング": "Refactor",
    "コンパイル": "Compile",
    # misc UI strings used inside game logic
    "プログラマー": "Programmer",
}


def name_en(name: str) -> str:
    """日本語名を英語名に変換する。マップに無ければそのまま返す。

    Args:
        name: 変換したい日本語名。
    Returns:
        NAME_EN_MAP に登録があれば英語名、無ければ name をそのまま返す。
    Policy:
        - 未登録名は失敗せずに原文をそのまま通す（フォールバック責務）。
    """
    return NAME_EN_MAP.get(name, name)


@dataclass
class TextFormat:
    """日本語/英語の言語フォールバック（P1-G14 で Game から 2 メソッドを取り込み）。"""

    # === Public API ===

    game: Any = None

    def t(self, jp: str, en: str) -> str:
        """言語フォールバック。BDF フォントが無いときは英語版を返す。

        Args:
            jp: 日本語表記。
            en: 英語表記（フォント未読込時のフォールバック）。
        Returns:
            game.has_jp_font が真なら jp、偽なら en。
        Policy:
            - has_jp_font の判定だけに依存し、文字列の中身は検査しない。
        """
        return jp if self.game.has_jp_font else en

    def name(self, jp: str) -> str:
        """データ名（敵・アイテム・装備）の翻訳。NAME_EN_MAP を引く。

        Args:
            jp: データ上の日本語名。
        Returns:
            game.has_jp_font が真なら jp、偽なら name_en(jp) の結果。
        Policy:
            - 任意文字列ではなくデータ名を想定し、未登録時は name_en の原文返しに従う。
        """
        return jp if self.game.has_jp_font else name_en(jp)
