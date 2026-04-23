from __future__ import annotations

"""日本語名 → 英語名の変換。

BDF フォントが読み込めない環境（Pyxel Code Maker 上など）で、日本語ラベルを
英語表記に置き換えるためのマップと変換関数。
"""


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
    """日本語名を英語名に変換する。マップに無ければそのまま返す。"""
    return NAME_EN_MAP.get(name, name)


from dataclasses import dataclass
from typing import Any


@dataclass
class TextFormat:
    """日本語/英語の言語フォールバック（P1-G14 で Game から 2 メソッドを取り込み）。"""

    game: Any = None

    def t(self, jp: str, en: str) -> str:
        """言語フォールバック。BDF フォントが無いときは英語版を返す。"""
        return jp if self.game.has_jp_font else en

    def name(self, jp: str) -> str:
        """データ名（敵・アイテム・装備）の翻訳。NAME_EN_MAP を引く。"""
        return jp if self.game.has_jp_font else name_en(jp)
