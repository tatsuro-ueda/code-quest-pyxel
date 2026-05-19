"""PlayerModel: Scene 横断で使うプレイヤー状態の dataclass とルール。

このファイルに含まれる関数・クラス：

- exp_for_level: 指定レベル到達に必要な累積経験値を返す純粋関数
- stats_for_level: 指定レベルの基礎ステータス dict を返す純粋関数
- _compute_exp_for_level: exp_for_level の計算本体（レベル 2 固定値含む）
- PlayerItem: 所持アイテム 1 件（id とスタック数）の dataclass
- PlayerModel: Scene 横断で参照されるプレイヤー状態とルールの dataclass
  - new_game: ニューゲーム用の Level 1 プレイヤーを作るファクトリ
  - _build_new_game_kwargs: new_game() コンストラクタに渡す kwargs を組み立てる
  - to_snapshot: SaveStore に渡す dict スナップショットを返す
  - from_snapshot: セーブ dict から PlayerModel と town_pos を復元するファクトリ
  - apply_damage: HP を amount だけ減らす（下限 0）
  - heal: HP を amount だけ回復する（上限 max_hp）
  - restore_mp: MP を amount だけ回復する（上限 max_mp）
  - cure_poison: 毒状態を解除する（解除できたら True）
  - gain_exp: 経験値を加算してレベルアップを判定する
  - can_afford: 所持金で cost を払えるか
  - is_full_hp_mp: HP と MP がともに最大値か
  - stay_at_inn: 宿屋で全回復・毒解除する
  - buy_weapon: 武器を購入する（成功なら True）
  - buy_armor: 防具を購入する（成功なら True）
  - buy_item: 道具を購入してインベントリに追加する
  - use_item: アイテム効果を適用して result 種別を返す
  - advance_npc_talk_idx: 町ごとの NPC 会話インデックスを進めて元 index を返す
  - _build_player_payload: SAVED_FIELDS を辿って player 部の dict を作る
  - _build_snapshot_value_for: 1 フィールド分のスナップショット値を返す
  - _normalize_legacy_keys: 旧セーブ互換のキー正規化を行う
  - _migrate_boss_defeated: 旧 boss_defeated を glitch_lord_defeated に移行する
  - _drop_legacy_av_keys: 撤去済の bgm/sfx/vfx_enabled キーを捨てる
  - _build_kwargs_from_snapshot: セーブ値を PlayerModel kwargs にまとめる
  - _restore_value_for: 1 フィールド分のセーブ値を復元する
  - _has_poison: poisoned フラグの述語
  - _try_cure_poison: cure_poison() の実装本体
  - _apply_level_ups: exp 値から連続レベルアップを適用する
  - _can_level_up: 次レベルへ上がる条件を満たすかの述語
  - _apply_stats_for_current_level: 現在 lv の stats を反映する
  - _try_stay_at_inn: stay_at_inn() の実装本体
  - _apply_full_rest: 宿屋全回復の状態更新
  - _is_weapon_purchase_blocked: 武器購入を弾く述語
  - _try_buy_weapon: buy_weapon() の実装本体
  - _apply_weapon_purchase: 武器購入の状態更新
  - _is_armor_purchase_blocked: 防具購入を弾く述語
  - _try_buy_armor: buy_armor() の実装本体
  - _apply_armor_purchase: 防具購入の状態更新
  - _try_buy_item: buy_item() の実装本体
  - _apply_item_purchase: 道具購入の状態更新
  - _add_item_to_inventory: 既存スタックがあれば加算、無ければ新規追加
  - _apply_item_effect: kind に応じてアイテム効果を適用し result を返す
  - _apply_heal_item: HP 回復アイテムを適用する
  - _apply_mp_heal_item: MP 回復アイテムを適用する
  - _apply_cure_poison_item: 毒解除アイテムを適用する
  - _apply_warp_item: ワープアイテムを適用する
  - _advance_or_zero: advance_npc_talk_idx() の実装本体
  - _is_npc_talk_input_invalid: NPC 会話入力が範囲外かの述語
  - _step_npc_talk_idx: 会話インデックスを進めて元値を返す

Problems:
    - プレイヤー状態の計算と保存・復元・ショップ・アイテム使用の各ルールを
      Scene 直書きすると、同じ計算が複数 Scene に分散して仕様変更時の直し漏れが出やすい。
    - 旧セーブ互換キー（boss_defeated や bgm_enabled 等）の取り扱いを
      呼び出し側に置くと、保存形式の変更が他層へ波及する。

Solutions:
    - framework-rule.md M4-1（Model は Pyxel/Scene/副作用を知らない）と
      M4-4（PlayerModel / GameState 圧縮）に従い、ルールはここに集約する。
    - 旧 src/shared/services/player_state.py と src/shared/services/item_use.py の
      ロジックを吸収し、Scene からは PlayerModel 経由で参照する 1 本道にする。
    - 公開関数名（exp_for_level / stats_for_level / new_game / to_snapshot /
      from_snapshot 等）は外部テスト・bundle wildcard import から固定参照される
      ため CR100 は ``# noqa`` で免除する。
"""
from __future__ import annotations

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

# 旧セーブから引き継ぐが現在は撤去されたキー（CJ44 確定版で削除済）。
_LEGACY_DROPPED_KEYS: tuple[str, ...] = (
    "bgm_enabled", "sfx_enabled", "vfx_enabled",
)


# === Public API ===


def exp_for_level(lv: int) -> int:  # noqa: CR100
    """指定レベル到達に必要な累積経験値を返す。

    Args:
        lv: 対象レベル（2 以上で意味を持つ）。
    Returns:
        そのレベルに到達するために必要な累積 EXP。
    Policy:
        - 関数名 exp_for_level は battle/scene と test 群が固定参照しているため
          動詞接頭辞ルール（CR100）を ``# noqa`` で免除する。
        - 計算本体は _compute_exp_for_level に委譲する。
    """
    return _compute_exp_for_level(lv)


def stats_for_level(lv: int) -> dict[str, int]:  # noqa: CR100
    """指定レベルでの基礎ステータスを返す。

    Args:
        lv: 対象レベル。
    Returns:
        max_hp / max_mp / atk / defense / agi をキーに持つ dict。
    Policy:
        - 関数名 stats_for_level は test 群と bundle wildcard import で固定参照
          されるため CR100 を ``# noqa`` で免除する。
        - キー "defense" を使う（player_state.py の shim が "def" に詰め直す）。
    """
    return {
        "max_hp": 30 + lv * 15,
        "max_mp": 10 + lv * 6,
        "atk": 5 + lv * 2,
        "defense": 3 + lv * 3,
        "agi": 5 + lv * 2,
    }


def _compute_exp_for_level(lv: int) -> int:
    """exp_for_level の計算本体（レベル 2 は固定値、それ以外は二次式）。

    Args:
        lv: 対象レベル。
    Returns:
        必要な累積 EXP。
    Policy:
        - 制御フローを public 側から引き取るための実装本体。
    """
    if lv == 2:
        return 26
    return int(10 * lv * lv + 6 * lv)


# Code Maker bundle 対策（shadow 耐性）：
# bundle ではこの後 player_state.py の shim ``stats_for_level`` が同じ
# 名前を上書きし、shim は ``def`` キーを返すため `PlayerModel.new_game`
# 内の ``base["defense"]`` が KeyError になる。内部参照は shadow されない
# 別名経由で行う（通常 import 環境では別 module なので影響なし）。
_stats_for_level_internal = stats_for_level


@dataclass
class PlayerItem:
    """所持アイテム 1 件（id とスタック数）。"""

    # === Public API ===

    id: int  # noqa: CR100
    qty: int


@dataclass
class PlayerModel:
    """Scene 横断で参照されるプレイヤー状態とルール。"""

    # === Public API ===

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
    items: list[PlayerItem] = field(
        default_factory=lambda: [
            PlayerItem(
                id=0, qty=3)])
    spells: list = field(default_factory=list)
    poisoned: bool = False  # noqa: CR101
    in_dungeon: bool = False  # noqa: CR101
    glitch_lord_defeated: bool = False  # noqa: CR101
    max_zone_reached: int = 0
    landmarkTreeSeen: bool = False  # noqa: CR101
    landmarkTowerSeen: bool = False  # noqa: CR101
    towerEpilogueSeen: bool = False  # noqa: CR101
    treeAsked: bool = False  # noqa: CR101
    towerNoiseCleared: bool = False  # noqa: CR101
    professor_intro_seen: bool = False  # noqa: CR101
    professor_defeated: bool = False  # noqa: CR101
    professor_ending_seen: bool = False  # noqa: CR101
    dialog_flags: dict = field(default_factory=dict)
    town_talk_idx: list = field(default_factory=lambda: [0, 0, 0])

    @classmethod
    def new_game(  # noqa: CR100
        cls, start_x: int = 25, start_y: int = 6
    ) -> "PlayerModel":
        """ニューゲーム用の Level 1 プレイヤーを作る。

        Args:
            start_x: 初期 x 座標。
            start_y: 初期 y 座標。
        Returns:
            stats_for_level(1) を埋め込んだ PlayerModel インスタンス。
        Policy:
            - factory 名 new_game は title presenter と test 群が固定参照する
              ため CR100 を ``# noqa`` で免除する。
            - kwargs 組み立ては _build_new_game_kwargs に委譲する。
        """
        return cls(**cls._build_new_game_kwargs(start_x, start_y))

    # ----- セーブ互換 -----

    def to_snapshot(  # noqa: CR100
        self, town_pos: tuple[int, int]
    ) -> dict[str, Any]:
        """SaveStore に渡す dict スナップショット（旧 dump_snapshot 互換）。

        Args:
            town_pos: 直近の町座標（タイル単位）。
        Returns:
            "save_version" / "town_pos" / "player" をキーに持つ dict。
        Policy:
            - 関数名 to_snapshot は SaveStore 経由で固定参照されるため
              CR100 を ``# noqa`` で免除する。
            - 中身の組み立ては _build_player_payload に委譲する。
        """
        return {
            "save_version": SAVE_VERSION,
            "town_pos": [int(town_pos[0]), int(town_pos[1])],
            "player": self._build_player_payload(),
        }

    @classmethod
    def from_snapshot(  # noqa: CR100
        cls, snapshot: dict[str, Any]
    ) -> tuple["PlayerModel", tuple[int, int]]:
        """セーブ dict から PlayerModel と town_pos を復元する。

        Args:
            snapshot: SaveStore から読んだ dict（"player" と "town_pos" を持つ）。
        Returns:
            復元した (PlayerModel, town_pos) のタプル。
        Policy:
            - 関数名 from_snapshot は title presenter と test 群が固定参照する
              ため CR100 を ``# noqa`` で免除する。
            - 旧キー（boss_defeated / bgm_enabled 等）の正規化は
              _normalize_legacy_keys に委譲する。
        """
        raw_player = dict(snapshot["player"])
        raw_pos = snapshot["town_pos"]
        cls._normalize_legacy_keys(raw_player)
        kwargs = cls._build_kwargs_from_snapshot(raw_player)
        player = cls(**kwargs)
        return player, (int(raw_pos[0]), int(raw_pos[1]))

    # ----- ルール：HP / MP / 経験値 -----

    def apply_damage(self, amount: int) -> None:
        """HP を amount だけ減らす（下限 0）。

        Args:
            amount: 減らす量（負値も int() を経由するため許容）。
        Policy:
            - hp は 0 未満にならない。
        """
        self.hp = max(0, self.hp - int(amount))

    def heal(self, amount: int) -> None:
        """HP を amount だけ回復する（上限 max_hp）。

        Args:
            amount: 回復量。
        Policy:
            - hp は max_hp を超えない。
        """
        self.hp = min(self.max_hp, self.hp + int(amount))

    def restore_mp(self, amount: int) -> None:
        """MP を amount だけ回復する（上限 max_mp）。

        Args:
            amount: 回復量。
        Policy:
            - mp は max_mp を超えない。
        """
        self.mp = min(self.max_mp, self.mp + int(amount))

    def cure_poison(self) -> bool:
        """毒状態を解除する。

        Returns:
            元から毒状態で解除できたら True、無毒なら False。
        Policy:
            - 状態判定は _has_poison に切り出し、ステップ列を保つ。
        """
        return self._try_cure_poison()

    def gain_exp(self, amount: int) -> bool:
        """経験値を加算してレベルアップ判定する。

        Args:
            amount: 加算する経験値。
        Returns:
            1 回でもレベルアップしたなら True。
        Policy:
            - 加算は単純代入、レベルアップループは _apply_level_ups に委譲する。
        """
        self.exp += int(amount)
        return self._apply_level_ups()

    # ----- ルール：宿屋・ショップ -----

    def can_afford(self, cost: int) -> bool:
        """所持金で cost を払えるか。

        Args:
            cost: 必要金額。
        Returns:
            gold >= cost なら True。
        Policy:
            - 判定のみで副作用は持たない。
        """
        return self.gold >= int(cost)

    def is_full_hp_mp(self) -> bool:
        """HP と MP がともに最大値か。毒状態は判定に含めない。

        Returns:
            hp == max_hp かつ mp == max_mp なら True。
        Policy:
            - 毒（poisoned）は別判定。
        """
        return self.hp >= self.max_hp and self.mp >= self.max_mp

    def stay_at_inn(self, cost: int) -> bool:
        """宿代を払って HP/MP 全回復＋毒解除する。

        Args:
            cost: 宿代。
        Returns:
            支払えて全回復したら True、支払えなければ False。
        Policy:
            - 述語＋実装本体を private に委譲する。
        """
        return self._try_stay_at_inn(cost)

    def buy_weapon(self, weapon_id: int, price: int) -> bool:
        """武器を購入する。

        Args:
            weapon_id: 購入する武器 id。
            price: 価格。
        Returns:
            購入できたら True。既に装備中・支払い不可なら False。
        Policy:
            - 試行は _try_buy_weapon に委譲する。
        """
        return self._try_buy_weapon(weapon_id, price)

    def buy_armor(self, armor_id: int, price: int) -> bool:
        """防具を購入する。

        Args:
            armor_id: 購入する防具 id。
            price: 価格。
        Returns:
            購入できたら True。既に装備中・支払い不可なら False。
        Policy:
            - 試行は _try_buy_armor に委譲する。
        """
        return self._try_buy_armor(armor_id, price)

    def buy_item(self, item_id: int, price: int) -> bool:
        """道具を購入してインベントリに追加する。

        Args:
            item_id: 購入する道具 id。
            price: 価格。
        Returns:
            購入できたら True。支払えなければ False。
        Policy:
            - 試行は _try_buy_item に委譲する。
        """
        return self._try_buy_item(item_id, price)

    # ----- ルール：アイテム使用 -----

    def use_item(
        self,
        item_data: dict,
        town_pos: tuple[int, int] | None = None,
    ) -> str:
        """アイテム効果を適用し、結果種別を返す。

        Args:
            item_data: SSoT の ITEMS 1 件（少なくとも "type"、必要に応じて "value"）。
            town_pos: ワープ系で使う町座標（タイル単位）。
        Returns:
            結果種別の文字列。

            - 効果が発動: ``"heal"`` / ``"mp_heal"`` / ``"cure_poison_ok"`` /
              ``"cure_poison_none"`` / ``"warp"``
            - 何も起きなかった: 空文字列（例: 満タン時の heal）

            表示メッセージや音再生は呼び出し側（Presenter）で解決する。
            ``warp`` は ``town_pos`` が渡された場合のみ座標更新もここで行う。
        Policy:
            - kind ごとの分岐は _apply_item_effect に委譲し、public 側は委譲＋return に揃える。
        """
        return self._apply_item_effect(item_data, town_pos)

    # ----- ルール：NPC 会話 -----

    def advance_npc_talk_idx(self, town_index: int, line_count: int) -> int:
        """町ごとの NPC 会話インデックスを進め、進める前の index を返す。

        Args:
            town_index: 対象の町インデックス。
            line_count: その町の台詞行数。
        Returns:
            進める前の index（範囲外なら 0）。
        Policy:
            - 試行本体は _advance_or_zero に委譲する。
        """
        return self._advance_or_zero(town_index, line_count)

    # === Internal helpers (private) ===

    @staticmethod
    def _build_new_game_kwargs(start_x: int, start_y: int) -> dict[str, Any]:
        """new_game() コンストラクタ呼び出しに渡す kwargs を組み立てる。

        Args:
            start_x: 初期 x 座標。
            start_y: 初期 y 座標。
        Returns:
            Level 1 プレイヤーの初期状態 kwargs。
        Policy:
            - shadow 耐性のため _stats_for_level_internal 経由で stats を取る。
        """
        base = _stats_for_level_internal(1)
        return {
            "x": start_x,
            "y": start_y,
            "hp": base["max_hp"],
            "max_hp": base["max_hp"],
            "mp": base["max_mp"],
            "max_mp": base["max_mp"],
            "atk": base["atk"],
            "defense": base["defense"],
            "agi": base["agi"],
            "lv": 1,
            "exp": 0,
            "gold": 50,
            "weapon": 0,
            "armor": 0,
            "items": [PlayerItem(id=0, qty=3)],
        }

    def _build_player_payload(self) -> dict[str, Any]:
        """SAVED_FIELDS を辿って player 部の dict を作る。

        Returns:
            セーブキー名をキーとする dict。
        Policy:
            - items は dict 化、それ以外はそのまま値を写す。
        """
        saved: dict[str, Any] = {}
        for attr in SAVED_FIELDS:
            key = _FIELD_TO_KEY.get(attr, attr)
            saved[key] = self._build_snapshot_value_for(attr)
        return saved

    def _build_snapshot_value_for(self, attr: str) -> Any:
        """1 フィールド分のスナップショット値を返す。

        Args:
            attr: PlayerModel の属性名。
        Returns:
            セーブ用に変換された値。
        Policy:
            - items は dict のリストへ展開する。
        """
        value = getattr(self, attr)
        if attr == "items":
            return [{"id": item.id, "qty": item.qty} for item in value]
        return value

    @classmethod
    def _normalize_legacy_keys(cls, raw_player: dict[str, Any]) -> None:
        """旧セーブ互換のキー正規化を行う（副作用：raw_player を書き換える）。

        Args:
            raw_player: セーブの "player" 部 dict。
        Policy:
            - boss_defeated → glitch_lord_defeated に統合する。
            - bgm/sfx/vfx_enabled は CJ44 確定版で撤去済のため捨てる。
        """
        cls._migrate_boss_defeated(raw_player)
        cls._drop_legacy_av_keys(raw_player)

    @staticmethod
    def _migrate_boss_defeated(raw_player: dict[str, Any]) -> None:
        """旧 boss_defeated を glitch_lord_defeated に移行する。

        Args:
            raw_player: セーブの "player" 部 dict。
        Policy:
            - glitch_lord_defeated が既にあれば何もしない。
        """
        if "glitch_lord_defeated" in raw_player:
            return
        if "boss_defeated" not in raw_player:
            return
        raw_player["glitch_lord_defeated"] = bool(
            raw_player.pop("boss_defeated"))

    @staticmethod
    def _drop_legacy_av_keys(raw_player: dict[str, Any]) -> None:
        """撤去済の bgm/sfx/vfx_enabled を捨てる。

        Args:
            raw_player: セーブの "player" 部 dict。
        Policy:
            - 2026-05-07 改訂（CJ44 確定版）で撤去済のため値があっても無視する。
        """
        for legacy_av_key in _LEGACY_DROPPED_KEYS:
            raw_player.pop(legacy_av_key, None)

    @classmethod
    def _build_kwargs_from_snapshot(
        cls, raw_player: dict[str, Any]
    ) -> dict[str, Any]:
        """PlayerModel の各フィールドに対応するセーブ値を kwargs にまとめる。

        Args:
            raw_player: セーブの "player" 部 dict（旧キーは正規化済の想定）。
        Returns:
            PlayerModel コンストラクタに渡す kwargs。
        Policy:
            - キーが無いフィールドは default に任せる。
        """
        kwargs: dict[str, Any] = {}
        for fld in fields(cls):
            key = _FIELD_TO_KEY.get(fld.name, fld.name)
            if key not in raw_player:
                continue
            kwargs[fld.name] = cls._restore_value_for(
                fld.name, raw_player[key])
        return kwargs

    @staticmethod
    def _restore_value_for(field_name: str, value: Any) -> Any:
        """1 フィールド分のセーブ値を PlayerModel 用に復元する。

        Args:
            field_name: PlayerModel の属性名。
            value: セーブから読んだ生値。
        Returns:
            復元後の値。
        Policy:
            - items は PlayerItem のリストへ詰め直す。
        """
        if field_name != "items":
            return value
        if not isinstance(value, list):
            return value
        return [
            PlayerItem(id=row["id"], qty=row["qty"]) for row in value
        ]

    def _has_poison(self) -> bool:
        """毒状態か。

        Returns:
            poisoned フラグが True なら True。
        Policy:
            - public 側の制御フロー回避のため述語化したのみ。
        """
        return bool(self.poisoned)

    def _try_cure_poison(self) -> bool:
        """毒状態なら解除して True、もともと無毒なら False。

        Returns:
            解除できたら True。
        Policy:
            - 制御フローを public 側から引き取るための実装本体。
        """
        if not self._has_poison():
            return False
        self.poisoned = False
        return True

    def _apply_level_ups(self) -> bool:
        """exp の値からレベルアップを連続適用する。

        Returns:
            1 回でもレベルアップしたなら True。
        Policy:
            - while ループは private に閉じ込め、stats 反映は
              _apply_stats_for_current_level に切り出す。
        """
        is_leveled = False
        while self._can_level_up():
            self.lv += 1
            self._apply_stats_for_current_level()
            is_leveled = True
        return is_leveled

    def _can_level_up(self) -> bool:
        """次のレベルへ上がる条件を満たすか。

        Returns:
            lv < MAX_LEVEL かつ exp が次レベル必要量以上なら True。
        Policy:
            - while の条件式を述語化することで CR302/CR303 を避ける。
        """
        if self.lv >= MAX_LEVEL:
            return False
        return self.exp >= exp_for_level(self.lv + 1)

    def _apply_stats_for_current_level(self) -> None:
        """現在 lv の stats を反映し、HP/MP を全回復する。

        Policy:
            - shadow 耐性のため _stats_for_level_internal 経由で取得する。
        """
        next_stats = _stats_for_level_internal(self.lv)
        self.max_hp = next_stats["max_hp"]
        self.max_mp = next_stats["max_mp"]
        self.atk = next_stats["atk"]
        self.defense = next_stats["defense"]
        self.agi = next_stats["agi"]
        self.hp = self.max_hp
        self.mp = self.max_mp

    def _try_stay_at_inn(self, cost: int) -> bool:
        """宿屋利用の試行。支払えれば全回復を適用して True を返す。

        Args:
            cost: 宿代。
        Returns:
            支払えれば True、支払えなければ False。
        Policy:
            - 支払い可否は can_afford、回復処理は _apply_full_rest に委譲する。
        """
        if not self.can_afford(cost):
            return False
        self._apply_full_rest(cost)
        return True

    def _apply_full_rest(self, cost: int) -> None:
        """宿屋の全回復処理（金支払い・HP/MP 満タン・毒解除）を適用する。

        Args:
            cost: 宿代。
        Policy:
            - 述語ガードは呼び出し側で済んでいる前提。
        """
        self.gold -= int(cost)
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.poisoned = False

    def _is_weapon_purchase_blocked(self, weapon_id: int, price: int) -> bool:
        """武器購入を弾く条件か（同一装備または支払い不可）。

        Args:
            weapon_id: 候補の武器 id。
            price: 価格。
        Returns:
            購入を拒否するなら True。
        Policy:
            - public 側の制御フロー回避のため述語化したのみ。
        """
        if self.weapon == weapon_id:
            return True
        return not self.can_afford(price)

    def _try_buy_weapon(self, weapon_id: int, price: int) -> bool:
        """武器購入の試行。条件を満たせば購入を適用して True を返す。

        Args:
            weapon_id: 候補の武器 id。
            price: 価格。
        Returns:
            購入できたら True、できなければ False。
        Policy:
            - 弾く条件は _is_weapon_purchase_blocked、適用は _apply_weapon_purchase。
        """
        if self._is_weapon_purchase_blocked(weapon_id, price):
            return False
        self._apply_weapon_purchase(weapon_id, price)
        return True

    def _apply_weapon_purchase(self, weapon_id: int, price: int) -> None:
        """武器購入の状態更新（支払い・装備変更）を適用する。

        Args:
            weapon_id: 装備する武器 id。
            price: 支払う金額。
        Policy:
            - 述語ガードは呼び出し側で済んでいる前提。
        """
        self.gold -= int(price)
        self.weapon = int(weapon_id)

    def _is_armor_purchase_blocked(self, armor_id: int, price: int) -> bool:
        """防具購入を弾く条件か（同一装備または支払い不可）。

        Args:
            armor_id: 候補の防具 id。
            price: 価格。
        Returns:
            購入を拒否するなら True。
        Policy:
            - public 側の制御フロー回避のため述語化したのみ。
        """
        if self.armor == armor_id:
            return True
        return not self.can_afford(price)

    def _try_buy_armor(self, armor_id: int, price: int) -> bool:
        """防具購入の試行。条件を満たせば購入を適用して True を返す。

        Args:
            armor_id: 候補の防具 id。
            price: 価格。
        Returns:
            購入できたら True、できなければ False。
        Policy:
            - 弾く条件は _is_armor_purchase_blocked、適用は _apply_armor_purchase。
        """
        if self._is_armor_purchase_blocked(armor_id, price):
            return False
        self._apply_armor_purchase(armor_id, price)
        return True

    def _apply_armor_purchase(self, armor_id: int, price: int) -> None:
        """防具購入の状態更新（支払い・装備変更）を適用する。

        Args:
            armor_id: 装備する防具 id。
            price: 支払う金額。
        Policy:
            - 述語ガードは呼び出し側で済んでいる前提。
        """
        self.gold -= int(price)
        self.armor = int(armor_id)

    def _try_buy_item(self, item_id: int, price: int) -> bool:
        """道具購入の試行。支払えれば購入を適用して True を返す。

        Args:
            item_id: 候補の道具 id。
            price: 価格。
        Returns:
            購入できたら True、できなければ False。
        Policy:
            - 支払い可否は can_afford、適用は _apply_item_purchase。
        """
        if not self.can_afford(price):
            return False
        self._apply_item_purchase(item_id, price)
        return True

    def _apply_item_purchase(self, item_id: int, price: int) -> None:
        """道具購入の状態更新（支払い・インベントリ追加）を適用する。

        Args:
            item_id: 購入する道具 id。
            price: 支払う金額。
        Policy:
            - 既存スタックがあれば qty を 1 加算、無ければ新規追加する。
        """
        self.gold -= int(price)
        self._add_item_to_inventory(item_id)

    def _add_item_to_inventory(self, item_id: int) -> None:
        """既存スタックがあれば qty を 1 加算、無ければ新規追加する。

        Args:
            item_id: 追加する道具 id。
        Policy:
            - 制御フローを private に閉じ込めるためのヘルパ。
        """
        for inv in self.items:
            if inv.id == item_id:
                inv.qty += 1
                return
        self.items.append(PlayerItem(id=int(item_id), qty=1))

    def _apply_item_effect(
        self,
        item_data: dict,
        town_pos: tuple[int, int] | None,
    ) -> str:
        """item_data["type"] に応じてアイテム効果を適用し、結果種別を返す。

        Args:
            item_data: SSoT の ITEMS 1 件。
            town_pos: ワープ系で使う町座標。
        Returns:
            "heal" / "mp_heal" / "cure_poison_ok" / "cure_poison_none" /
            "warp" / 空文字列のいずれか。
        Policy:
            - kind ごとに専用 helper へ分岐させ、未知 kind は空文字列を返す。
        """
        kind = item_data["type"]
        if kind == "heal":
            return self._apply_heal_item(item_data)
        if kind == "mp_heal":
            return self._apply_mp_heal_item(item_data)
        if kind == "cure_poison":
            return self._apply_cure_poison_item()
        if kind == "warp":
            return self._apply_warp_item(town_pos)
        return ""

    def _apply_heal_item(self, item_data: dict) -> str:
        """HP 回復アイテムを適用する。

        Args:
            item_data: "value" に回復量を持つ dict。
        Returns:
            効果が出たら "heal"、満タンで効果なしなら空文字列。
        Policy:
            - 満タン判定は public 側で済まないため、ここで行う。
        """
        if self.hp >= self.max_hp:
            return ""
        self.heal(item_data["value"])
        return "heal"

    def _apply_mp_heal_item(self, item_data: dict) -> str:
        """MP 回復アイテムを適用する。

        Args:
            item_data: "value" に回復量を持つ dict。
        Returns:
            "mp_heal"。
        Policy:
            - MP は上限超過分が捨てられるだけなので必ず "mp_heal" を返す。
        """
        self.restore_mp(item_data["value"])
        return "mp_heal"

    def _apply_cure_poison_item(self) -> str:
        """毒解除アイテムを適用する。

        Returns:
            解除に成功したら "cure_poison_ok"、無毒なら "cure_poison_none"。
        Policy:
            - cure_poison() の戻り値を結果文字列にマップする。
        """
        if self.cure_poison():
            return "cure_poison_ok"
        return "cure_poison_none"

    def _apply_warp_item(self, town_pos: tuple[int, int] | None) -> str:
        """ワープアイテムを適用する。

        Args:
            town_pos: 戻る町座標（None なら座標は変えない）。
        Returns:
            "warp"。
        Policy:
            - town_pos が指定された時のみ自分の x/y を上書きし、in_dungeon を解除する。
        """
        if town_pos is not None:
            self.x, self.y = town_pos
            self.in_dungeon = False
        return "warp"

    def _advance_or_zero(self, town_index: int, line_count: int) -> int:
        """advance_npc_talk_idx の実装本体（範囲外なら 0、それ以外は元 index）。

        Args:
            town_index: 対象の町インデックス。
            line_count: 台詞行数。
        Returns:
            進める前の index 値。
        Policy:
            - 入力妥当性は _is_npc_talk_input_invalid、ステップは _step_npc_talk_idx。
        """
        if self._is_npc_talk_input_invalid(town_index, line_count):
            return 0
        return self._step_npc_talk_idx(town_index, line_count)

    def _is_npc_talk_input_invalid(
        self, town_index: int, line_count: int
    ) -> bool:
        """advance_npc_talk_idx の入力が範囲外か。

        Args:
            town_index: 対象の町インデックス。
            line_count: 台詞行数。
        Returns:
            範囲外（town_index 負・上限超え、line_count <= 0）なら True。
        Policy:
            - public 側の複合条件（CR302/CR303）を回避するための述語化。
        """
        if town_index < 0:
            return True
        if town_index >= len(self.town_talk_idx):
            return True
        return line_count <= 0

    def _step_npc_talk_idx(self, town_index: int, line_count: int) -> int:
        """会話インデックスを進めて元の値を返す。

        Args:
            town_index: 対象の町インデックス。
            line_count: 台詞行数。
        Returns:
            進める前の index 値。
        Policy:
            - 入力妥当性は呼び出し側で検証済みの前提。
        """
        current = self.town_talk_idx[town_index] % line_count
        self.town_talk_idx[town_index] = (current + 1) % line_count
        return current
