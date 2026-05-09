from __future__ import annotations

"""PlayerModel: Scene 横断で使うプレイヤー状態の dataclass とルール。

framework-rule.md M4-1（Model は Pyxel/Scene/副作用を知らない）および
M4-4（PlayerModel / GameState 圧縮、Level 2）に従う実装。
旧 src/shared/services/player_state.py と src/shared/services/item_use.py の
ロジックを吸収する。
"""

from dataclasses import dataclass, field, fields
from typing import Any


MAX_LEVEL = 100
SAVE_VERSION = 1

# セーブ対象フィールド（PlayerModel 属性名）。
# 属性名が旧セーブキー名と異なる場合は _FIELD_TO_KEY で変換する。
SAVED_FIELDS: tuple[str, ...] = (
    "x", "y",
    "hp", "max_hp", "mp", "max_mp",
    "atk", "defense", "agi",
    "lv", "exp", "gold",
    "weapon", "armor",
    "items", "spells",
    "poisoned",
    "in_dungeon",
    "glitch_lord_defeated",
    "max_zone_reached",
    "landmarkTreeSeen", "landmarkTowerSeen",
    "treeAsked", "towerNoiseCleared",
    "professor_intro_seen", "professor_defeated", "professor_ending_seen",
    "dialog_flags",
    "town_talk_idx",
)

# Python 予約語などで属性名とセーブキー名がずれる場合の対応表。
_FIELD_TO_KEY = {"defense": "def"}
_KEY_TO_FIELD = {v: k for k, v in _FIELD_TO_KEY.items()}


def exp_for_level(lv: int) -> int:
    """指定レベル到達に必要な累積経験値を返す。"""
    if lv == 2:
        return 26
    return int(10 * lv * lv + 6 * lv)


def stats_for_level(lv: int) -> dict[str, int]:
    """指定レベルでの基礎ステータスを返す。"""
    return {
        "max_hp": 30 + lv * 15,
        "max_mp": 10 + lv * 6,
        "atk": 5 + lv * 2,
        "defense": 3 + lv * 3,
        "agi": 5 + lv * 2,
    }


# Code Maker bundle 対策（shadow 耐性）：
# bundle ではこの後 player_state.py の shim ``stats_for_level`` が同じ
# 名前を上書きし、shim は ``def`` キーを返すため `PlayerModel.new_game`
# 内の ``base["defense"]`` が KeyError になる。内部参照は shadow されない
# 別名経由で行う（通常 import 環境では別 module なので影響なし）。
_stats_for_level_internal = stats_for_level


@dataclass
class PlayerItem:
    """所持アイテム一件（id とスタック数）。"""
    id: int
    qty: int


@dataclass
class PlayerModel:
    """Scene 横断で参照されるプレイヤー状態とルール。"""
    x: int = 25
    y: int = 6
    hp: int = 45
    max_hp: int = 45
    mp: int = 16
    max_mp: int = 16
    atk: int = 7
    defense: int = 6
    agi: int = 7
    lv: int = 1
    exp: int = 0
    gold: int = 50
    weapon: int = 0
    armor: int = 0
    items: list[PlayerItem] = field(default_factory=lambda: [PlayerItem(id=0, qty=3)])
    spells: list = field(default_factory=list)
    poisoned: bool = False
    in_dungeon: bool = False
    glitch_lord_defeated: bool = False
    max_zone_reached: int = 0
    landmarkTreeSeen: bool = False
    landmarkTowerSeen: bool = False
    towerEpilogueSeen: bool = False
    treeAsked: bool = False
    towerNoiseCleared: bool = False
    professor_intro_seen: bool = False
    professor_defeated: bool = False
    professor_ending_seen: bool = False
    dialog_flags: dict = field(default_factory=dict)
    town_talk_idx: list = field(default_factory=lambda: [0, 0, 0])

    @classmethod
    def new_game(cls, start_x: int = 25, start_y: int = 6) -> "PlayerModel":
        """ニューゲーム用の Level 1 プレイヤーを作る。"""
        base = _stats_for_level_internal(1)
        return cls(
            x=start_x,
            y=start_y,
            hp=base["max_hp"],
            max_hp=base["max_hp"],
            mp=base["max_mp"],
            max_mp=base["max_mp"],
            atk=base["atk"],
            defense=base["defense"],
            agi=base["agi"],
            lv=1,
            exp=0,
            gold=50,
            weapon=0,
            armor=0,
            items=[PlayerItem(id=0, qty=3)],
        )

    # ----- セーブ互換 -----

    def to_snapshot(self, town_pos: tuple[int, int]) -> dict[str, Any]:
        """SaveStore に渡す dict スナップショット（旧 dump_snapshot 互換）。"""
        saved: dict[str, Any] = {}
        for attr in SAVED_FIELDS:
            key = _FIELD_TO_KEY.get(attr, attr)
            val = getattr(self, attr)
            if attr == "items":
                val = [{"id": it.id, "qty": it.qty} for it in val]
            saved[key] = val
        return {
            "save_version": SAVE_VERSION,
            "town_pos": [int(town_pos[0]), int(town_pos[1])],
            "player": saved,
        }

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> tuple["PlayerModel", tuple[int, int]]:
        """セーブ dict から PlayerModel と town_pos を復元する（旧 restore_snapshot 互換）。"""
        raw_player = dict(snapshot["player"])
        raw_pos = snapshot["town_pos"]
        if "glitch_lord_defeated" not in raw_player and "boss_defeated" in raw_player:
            raw_player["glitch_lord_defeated"] = bool(raw_player.pop("boss_defeated"))
        # 2026-05-07 改訂（CJ44 確定版）：bgm/sfx/vfx_enabled は撤去済。
        # 古いセーブに残っていても無視（PlayerModel 属性に存在しない）。
        for legacy_av_key in ("bgm_enabled", "sfx_enabled", "vfx_enabled"):
            raw_player.pop(legacy_av_key, None)
        kwargs: dict[str, Any] = {}
        for fld in fields(cls):
            key = _FIELD_TO_KEY.get(fld.name, fld.name)
            if key in raw_player:
                val = raw_player[key]
                if fld.name == "items" and isinstance(val, list):
                    val = [PlayerItem(id=it["id"], qty=it["qty"]) for it in val]
                kwargs[fld.name] = val
        player = cls(**kwargs)
        return player, (int(raw_pos[0]), int(raw_pos[1]))

    # ----- ルール：HP / MP / 経験値 -----

    def apply_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - int(amount))

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + int(amount))

    def restore_mp(self, amount: int) -> None:
        self.mp = min(self.max_mp, self.mp + int(amount))

    def cure_poison(self) -> bool:
        if self.poisoned:
            self.poisoned = False
            return True
        return False

    def gain_exp(self, amount: int) -> bool:
        """経験値を加算。レベルアップしたら True。"""
        self.exp += int(amount)
        leveled = False
        while self.lv < MAX_LEVEL and self.exp >= exp_for_level(self.lv + 1):
            self.lv += 1
            next_stats = _stats_for_level_internal(self.lv)
            self.max_hp = next_stats["max_hp"]
            self.max_mp = next_stats["max_mp"]
            self.atk = next_stats["atk"]
            self.defense = next_stats["defense"]
            self.agi = next_stats["agi"]
            self.hp = self.max_hp
            self.mp = self.max_mp
            leveled = True
        return leveled

    # ----- ルール：宿屋・ショップ -----

    def can_afford(self, cost: int) -> bool:
        return self.gold >= int(cost)

    def stay_at_inn(self, cost: int) -> bool:
        """宿代を払って HP/MP 全回復＋毒解除。支払えないと False。"""
        if not self.can_afford(cost):
            return False
        self.gold -= int(cost)
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.poisoned = False
        return True

    def buy_weapon(self, weapon_id: int, price: int) -> bool:
        if self.weapon == weapon_id:
            return False
        if not self.can_afford(price):
            return False
        self.gold -= int(price)
        self.weapon = int(weapon_id)
        return True

    def buy_armor(self, armor_id: int, price: int) -> bool:
        if self.armor == armor_id:
            return False
        if not self.can_afford(price):
            return False
        self.gold -= int(price)
        self.armor = int(armor_id)
        return True

    def buy_item(self, item_id: int, price: int) -> bool:
        if not self.can_afford(price):
            return False
        self.gold -= int(price)
        for inv in self.items:
            if inv.id == item_id:
                inv.qty += 1
                break
        else:
            self.items.append(PlayerItem(id=int(item_id), qty=1))
        return True

    # ----- ルール：アイテム使用 -----

    def use_item(self, item_data: dict, town_pos: tuple[int, int] | None = None) -> str:
        """アイテム効果を適用し、結果種別を返す。

        戻り値:
          - 効果が発動: ``"heal"`` / ``"mp_heal"`` / ``"cure_poison_ok"`` /
            ``"cure_poison_none"`` / ``"warp"``
          - 何も起きなかった: 空文字列（例: 満タン時の heal）
        表示メッセージや音再生は呼び出し側（Presenter）で解決する。
        ``warp`` は `town_pos` が渡された場合のみ座標更新もここで行う。
        """
        kind = item_data["type"]
        if kind == "heal":
            if self.hp >= self.max_hp:
                return ""
            self.heal(item_data["value"])
            return "heal"
        if kind == "mp_heal":
            self.restore_mp(item_data["value"])
            return "mp_heal"
        if kind == "cure_poison":
            return "cure_poison_ok" if self.cure_poison() else "cure_poison_none"
        if kind == "warp":
            if town_pos is not None:
                self.x, self.y = town_pos
                self.in_dungeon = False
            return "warp"
        return ""

    # ----- ルール：NPC 会話 -----

    def advance_npc_talk_idx(self, town_index: int, line_count: int) -> int:
        """町ごとの NPC 会話インデックスを進め、進める前の index を返す。"""
        if town_index < 0 or town_index >= len(self.town_talk_idx) or line_count <= 0:
            return 0
        current = self.town_talk_idx[town_index] % line_count
        self.town_talk_idx[town_index] = (current + 1) % line_count
        return current
