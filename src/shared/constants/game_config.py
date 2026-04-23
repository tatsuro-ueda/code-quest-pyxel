"""ゲーム実行時の設定定数（P1.5-E で main_runtime.py から抽出）。

- ENCOUNTER_RATES: タイルごとの遭遇率
- VFX_FLASH: 画面エフェクト設定
- BATTLE_ATTACK_SCENES / ENEMY_HIT_SCENES / VICTORY_SCENES_BY_ZONE: 戦闘 dialog scene 参照
- ZONE_NAMES / ZONE_NAMES_EN: ゾーン表示名
- TOWN_*: 町メニュー関連
- SHOP_KIND_BY_LABEL / INN_COST / TOWN_INDEX_BY_POS: 町内商店定義
- TOWN_DIALOG_SCENES / TOWN_NPC_LINES: 町会話
- *_MSG: 各種表示メッセージ
"""
from __future__ import annotations

from src.shared.constants.tile_data import (
    T_GRASS, T_SAND, T_FLOOR, T_PATH,
    T_FLOWER, T_ROCK, T_MUSHROOM, T_CACTUS, T_BUSH,
)


ENCOUNTER_RATES = {
    T_GRASS: 0.06, T_SAND: 0.08, T_FLOOR: 0.12, T_PATH: 0.03,
    T_FLOWER: 0.06, T_ROCK: 0.06, T_MUSHROOM: 0.06,
    T_CACTUS: 0.08, T_BUSH: 0.06,
}

VFX_FLASH = {
    "flash_white": {"color": 7, "duration": 2},
    "flash_red":   {"color": 8, "duration": 3},
}

BATTLE_ATTACK_SCENES = (
    "battle.normal.attack.observe",
    "battle.normal.attack.inspect",
    "battle.normal.attack.read",
    "battle.normal.attack.trace",
    "battle.normal.attack.cause",
)

ENEMY_HIT_SCENES = {
    "sequential": "battle.normal.enemy_hit.sequential",
    "loop": "battle.normal.enemy_hit.loop",
    "condition": "battle.normal.enemy_hit.condition",
    "variable": "battle.normal.enemy_hit.variable",
    "composite": "battle.normal.enemy_hit.composite",
}

VICTORY_SCENES_BY_ZONE = {
    0: "battle.normal.victory.early",
    1: "battle.normal.victory.mid",
    2: "battle.normal.victory.mid",
    3: "battle.normal.victory.late",
    4: "battle.normal.victory.late",
}

ZONE_NAMES = {0: "はじまりのそうげん", 1: "ロジックのもり", 2: "アルゴのやまみち", 3: "さばくちたい", 4: "グリッチのどうくつ"}
ZONE_NAMES_EN = {0: "Grasslands", 1: "Logic Forest", 2: "Algo Mountains", 3: "Desert", 4: "Glitch Cave"}

TOWN_MENU_LABELS = ("はなす", "ぶきや", "ぼうぐや", "どうぐや", "やどや", "セーブ", "でる")
TOWN_MENU_LABELS_EN = ("TALK", "WEAPONS", "ARMOR", "ITEMS", "INN", "SAVE", "EXIT")
SHOP_KIND_BY_LABEL = {"ぶきや": "weapons", "ぼうぐや": "armors", "どうぐや": "items"}
INN_COST = 10  # gold (フォールバック値; shops.yaml の inn_prices を優先)
TOWN_INDEX_BY_POS = {(20, 12): 0, (30, 22): 1, (18, 34): 2}

SAVE_OK_MSG = "ここまでのりかいをかきとめた。"
LOAD_OK_MSG = "きろくをよみかえした。りかいがもどってくる。"
NO_RECORD_MSG = "まだなにもかきとめていない…"
SAVE_FAIL_MSG_DESKTOP = "セーブにしっぱいしました（けんげん/ようりょうをかくにんしてください）"
SAVE_FAIL_MSG_WEB = "セーブにしっぱいしました（ブラウザのほぞんりょういきをかくにんしてください）"
INN_OK_MSG = "あんぜんなばしょでやすんだ。しこうがさえる。HPとMPが かいふくした！"
INN_LACK_MSG = "コインが たりません"
SHOP_WIP_MSG = "こうじちゅう：ほんきのうはフォローアップでじっそうよてい"

TOWN_DIALOG_SCENES = {
    (25, 6): "castle.professor.entry",
}

# 町ごとのNPCセリフ（ラウンドロビンで A→B→C→A→…）
TOWN_NPC_LINES = [
    # はじめのむら (20,12)
    [
        "ものごとには じゅんばんが あるけど\nすこしズレたって きにならないだろ？",
        "そんなに きにしてたら\nなにもできないよ。\nだいたいあってれば いいんだよ",
        "じゅんばん？\nうごけば いいんだよ、うごけば",
    ],
    # ロジックタウン (30,22)
    [
        "おなじことの くりかえし？\nそういうもんだろ、しごとって",
        "かんがえすぎだよ。\nまわってるなら それでいいじゃないか",
        "とめる？\nなんで うごいてるものを とめるんだ？",
    ],
    # アルゴリズムのまち (18,34)
    [
        "ばあいによるとか いいだすと\nはなしが すすまないんだよな",
        "かぞえなくたって\nなんとなく わかるだろ？",
        "そこまで みえなくても\nいきていけるぞ",
    ],
]
