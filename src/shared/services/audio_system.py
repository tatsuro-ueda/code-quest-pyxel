"""SFX subsystem + BGM 冪等再生ヘルパー.

このファイルに含まれる関数・クラス：

- play_bgm_track: 指定 music slot を冪等に再生する public ヘルパー
- reset_bgm_state_for_tests: テスト用に現在 BGM の記録をリセットする
- _is_same_track: target が現在再生中の BGM と同じ slot かを返す述語
- _switch_bgm_track_if_different: 同一なら何もせず違うときだけ切替に委譲する
- _switch_bgm_track: 違う BGM へ切り替え、内部状態を更新する private 委譲
- _clear_current_bgm_track: 現在 BGM の記録だけを初期化する private 委譲
- SfxSystem: pyxres 尊重で SFX をロード・再生する薄い service
  - __init__: Pyxel モジュールを受け取り、SFX スロットを準備する
  - play: 名前で SFX を再生する（未定義名は黙って無視）
  - _slot_has_sound: 指定 slot に既存 sound が入っているかを返す述語
  - _load: 空スロットに fallback の SFX 定義を流し込む
  - _play_named_sfx: 名前を slot に解決し、確定したときだけ再生に委譲する
  - _resolve_slot: SFX 名に対応する slot 番号を返す（未定義は None）
  - _play_slot: 確定済み slot を Pyxel に再生させる private 委譲

Problems:
    - BGM の current track を Game クラスや AudioManager に持つと、
      シーン側から「同じ曲なら鳴らし直さない」判定の入口が増える。
    - SFX 再生の入口に「未定義名なら無視」「pyxres 既存スロットを優先」
      といった分岐を直書きすると、SfxSystem.play が読み下しにくい。
    - 長大な SFX 定義 dict をモジュール docstring と分離せずに置くと、
      flake8 の行長違反と CR204 の混入が同時に走る。

Solutions:
    - BGM の current track は本モジュールのプライベート変数で 1 箇所だけ
      保持し、play_bgm_track を「述語 + 委譲 + return」のステップ列に揃える。
    - SfxSystem.play は「未定義 slot 早期 return + private 再生」のステップ列に
      整理し、slot 検査と fallback ロードは private helper に閉じ込める。
    - SFX_DEFINITIONS の長い notes/volume/effect 文字列は連結リテラルで
      分割し、1 行 79 桁以内に収める。
"""
from __future__ import annotations

import pyxel as _pyxel


SFX_CHANNEL = 3


_current_bgm_track: int | None = None
"""現在再生中の BGM (``pyxel.musics`` slot 番号)。冪等再生のためだけに使う。

CJ44 確定版：``Game`` クラスや ``AudioManager`` のような中央集権オブジェクトに
状態を持たせず、本モジュールのプライベート変数で 1 箇所だけ保持する。
"""


def play_bgm_track(target: int) -> None:
    """指定 music slot を冪等に再生する。

    Args:
        target: 再生したい ``pyxel.musics`` の slot 番号。
    Policy:
        - 「同じ track ならスキップ・違う track なら切替」の判定は
          ``_switch_bgm_track_if_different`` に閉じ込め、本体は委譲だけにする。
        - 各 scene の ``view.py::play_bgm`` から呼ばれる薄いヘルパー。
    """
    _switch_bgm_track_if_different(target)
    return


def reset_bgm_state_for_tests() -> None:
    """テストから ``_current_bgm_track`` をリセットするためのフック。

    Policy:
        - 本番コードからは呼ばない。テスト間で BGM の "鳴り始め" を再現したい
          場合のみ使う。
        - 状態初期化は ``_clear_current_bgm_track`` に委譲する。
    """
    _clear_current_bgm_track()
    return


# === Internal helpers (private) ===


def _is_same_track(target: int) -> bool:
    """target が現在再生中の BGM と同じ slot かを返す。

    Args:
        target: 再生したい music slot 番号。
    Returns:
        bool: 同一なら True（再生し直し不要）。
    Policy:
        - 比較のみで副作用を持たない。
    """
    return _current_bgm_track == target


def _switch_bgm_track_if_different(target: int) -> None:
    """target が現在 BGM と異なるときだけ切り替え再生する。

    Args:
        target: 再生したい music slot 番号。
    Policy:
        - 同一なら何もしない（_is_same_track）。
        - 異なるときは ``_switch_bgm_track`` に委譲する。
    """
    if _is_same_track(target):
        return
    _switch_bgm_track(target)


def _switch_bgm_track(target: int) -> None:
    """違う BGM へ切り替え、内部状態を更新する。

    Args:
        target: 再生する music slot 番号。
    Policy:
        - 旧 BGM を ``pyxel.stop`` で止めてから ``pyxel.playm(loop=True)``
          で開始する順序を保つ（重畳再生を避ける）。
        - 内部記録 ``_current_bgm_track`` も更新する。
    """
    global _current_bgm_track
    _pyxel.stop()
    _pyxel.playm(target, loop=True)
    _current_bgm_track = target


def _clear_current_bgm_track() -> None:
    """``_current_bgm_track`` を初期化する private 委譲。

    Policy:
        - global 書き換えを本関数 1 箇所に閉じる。
    """
    global _current_bgm_track
    _current_bgm_track = None


# slot 33以降を使用する（旧 BGM 設計が 0-32 を消費していたため）。
# 順序が slot 割り当てを決定する（cursor=33, select=34, ... step=54）。
# 新規追加は末尾に。途中の入替は .pyxres との対応が壊れるので禁止。
SFX_BASE_SLOT = 33


SFX_DEFINITIONS: dict[str, dict] = {
    "cursor": {
        "tone": "t", "notes": "c3", "volume": "7",
        "effect": "f", "speed": 11,
    },
    "select": {
        "tone": "p", "notes": "g#4", "volume": "5",
        "effect": "f", "speed": 14,
    },
    "cancel": {
        "tone": "p",
        "notes": "e3e2e3e2e3e2e3e2e3e2e3e2e3e2e3e2",
        "volume": "", "effect": "f", "speed": 1,
    },
    "attack": {
        "tone": "n", "notes": "d3a2g#2c#3a3a#4",
        "volume": "765677", "effect": "nnnnnf", "speed": 2,
    },
    "hit": {
        "tone": "n",
        "notes": "f#3d4b4b3c3d2f#1f#1f#1f#1f#1f#1",
        "volume": "777777776655",
        "effect": "nnnnnnnnnnnf", "speed": 2,
    },
    "heal": {
        "tone": "sp",
        "notes": "c3c4f3f4a#3a#4a#4a#4a#4",
        "volume": "775577777",
        "effect": "nfnfnnnnf", "speed": 3,
    },
    "levelup": {
        "tone": "sp",
        "notes": "d2d3g2g3c3c4f3f4a#3a#4a#4a#4a#4",
        "volume": "7755775577777",
        "effect": "nfnfnfnfnnnnf", "speed": 3,
    },
    "victory": {
        "tone": "p", "notes": "g2c3e3g3", "volume": "6",
        "effect": "n", "speed": 10,
    },
    "save": {
        "tone": "p", "notes": "a2a3", "volume": "37",
        "effect": "nf", "speed": 5,
    },
    "encounter": {
        "tone": "p",
        "notes": (
            "g1c2e2a#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2"
            "d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2"
            "g1c2e2a#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2"
            "d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2"
        ),
        "volume": "777776544444444444444321",
        "effect": "v", "speed": 4,
    },
    "miss": {
        "tone": "n", "notes": "f#3", "volume": "7",
        "effect": "f", "speed": 4,
    },
    "dead": {
        "tone": "n",
        "notes": (
            "f2c#2a1f#1e1d#1d1d1d1d1d1d1d1d1d1d1d1d1"
            "c#1c#1c#1c#1c#1c#1c1c1a#0a0g#0g0f#0f0d#0d0c#0c0"
        ),
        "volume": "765555555555555555555443332211111111",
        "effect": "", "speed": 2,
    },
    "magic": {
        "tone": "pn",
        "notes": (
            "d2d2c#2c#2c2c2e2e2d#2d#2d2d2"
            "f#2f#2f2f2e2e2g#2g#2g2g2f#2f#2"
        ),
        "volume": "72", "effect": "", "speed": 2,
    },
    "poison": {
        "tone": "n", "notes": "f#4", "volume": "7",
        "effect": "", "speed": 20,
    },
    "cure": {
        "tone": "n",
        "notes": "a#4g4a#4g4a#4g4g4g4a#4g4a#4g4g4g4a#4g4",
        "volume": "2323233323233323",
        "effect": "nfnfnnnfnfnnnfnf", "speed": 4,
    },
    "dungeon_in": {
        "tone": "s",
        "notes": "a2a1a#2a#1b2b1c3c2a2a1a#2a#1b2b1c3c2",
        "volume": "7", "effect": "v", "speed": 5,
    },
    "boss_approach": {
        "tone": "n", "notes": "b3b2a#2g#2f2c#2d1d1d1d1d1",
        "volume": "47777776542", "effect": "n", "speed": 6,
    },
    "boss_defeat": {
        "tone": "n",
        "notes": (
            "b3c4c#4d4b3c4c#4d4b3c4c#4d4"
            "b3c4c#4d4b3c4c#4d4b3c4c#4d4"
        ),
        "volume": "777777776666666655555555",
        "effect": "nnnf", "speed": 5,
    },
    "critical": {
        "tone": "n",
        "notes": "f#3f#3a#3f#3f#3a#3f#3f#3a#3",
        "volume": "765", "effect": "ssn", "speed": 6,
    },
    "zone_change": {
        "tone": "n", "notes": "b2rc3rb2rc3",
        "volume": "7766554", "effect": "f", "speed": 13,
    },
    "poison_tick": {
        "tone": "t", "notes": "f#1", "volume": "4",
        "effect": "f", "speed": 8,
    },
    "step": {
        "tone": "s", "notes": "d#1", "volume": "3",
        "effect": "f", "speed": 6,
    },
}


class SfxSystem:
    """SFX を初期化・再生する薄いマネージャ（pyxres 尊重）。

    `SFX_DEFINITIONS` の順序で slot 33 から割り当てる。
    `.pyxres` 側で既にサウンドが入っているスロットはそのまま使い、空スロット
    だけ fallback 値で埋める（Code Maker 編集を優先）。
    """

    # === Public API ===

    def __init__(self, pyxel_module):
        """Pyxel モジュールを受け取り、SFX スロットを準備する。

        Args:
            pyxel_module: pyxel 本体、または同じ I/F を持つテスト用フェイク。
        Policy:
            - インスタンス生成時に空スロットへ fallback 定義をロードする。
            - SFX チャンネルの gain は固定値 0.5（CJ44 確定版：個別調整なし）。
        """
        self.pyxel = pyxel_module
        self._slots: dict[str, int] = {}
        self._load()
        self.pyxel.channels[SFX_CHANNEL].gain = 0.5

    def play(self, name: str):  # noqa: CR100
        """名前で SFX を再生する（未定義名は黙って無視）。

        Args:
            name: SFX_DEFINITIONS のキー文字列。
        Policy:
            - 公開 API 名 ``play`` は pyxel 慣用（pyxel.play）に合わせて固定。
            - 名前→slot 解決と「未定義なら無視」の判定は private 側に閉じ込め、
              本体は ``_play_named_sfx`` への委譲のみのステップ列に揃える。
        """
        self._play_named_sfx(name)
        return

    # === Internal helpers (private) ===

    def _slot_has_sound(self, slot: int) -> bool:
        """Code Maker / pyxel.load() 済み slot があればそれを優先する。

        Args:
            slot: ``pyxel.sounds`` のインデックス。
        Returns:
            bool: notes / tones / volumes / effects のいずれかに既存値があれば True。
        Policy:
            - .pyxres を優先するため、内容がある slot は fallback ロードを skip する。
        """
        sound = self.pyxel.sounds[slot]
        for attr in ("notes", "tones", "volumes", "effects"):
            try:
                if len(getattr(sound, attr)) > 0:
                    return True
            except Exception:
                continue
        return False

    def _load(self):
        """空スロットに fallback の SFX 定義を流し込む。

        Policy:
            - SFX_DEFINITIONS の順序通り SFX_BASE_SLOT から割り当てる。
            - 既存内容のあるスロットは上書きせず、空のときだけ set する。
        """
        for i, (name, sd) in enumerate(SFX_DEFINITIONS.items()):
            slot = SFX_BASE_SLOT + i
            self._slots[name] = slot
            if self._slot_has_sound(slot):
                continue
            self.pyxel.sounds[slot].set(
                sd["notes"],
                sd["tone"],
                sd["volume"],
                sd["effect"],
                sd["speed"])

    def _play_named_sfx(self, name: str) -> None:
        """名前を slot に解決して、確定したときだけ Pyxel に再生させる。

        Args:
            name: SFX_DEFINITIONS のキー文字列。
        Policy:
            - 未定義名は黙って無視（早期 return）。
            - 確定した slot は ``_play_slot`` に委譲する。
        """
        slot = self._resolve_slot(name)
        if slot is None:
            return
        self._play_slot(slot)

    def _resolve_slot(self, name: str) -> int | None:
        """SFX 名に対応する slot 番号を返す（未定義は None）。

        Args:
            name: SFX_DEFINITIONS のキー文字列。
        Returns:
            int | None: 登録済みなら slot 番号、未定義なら None。
        Policy:
            - 未定義名でも例外を投げず、呼び出し側に None で知らせる。
        """
        return self._slots.get(name)

    def _play_slot(self, slot: int) -> None:
        """確定済み slot を Pyxel に再生させる。

        Args:
            slot: ``pyxel.sounds`` のインデックス。
        Policy:
            - 必ず SFX_CHANNEL で loop=False。BGM チャンネルは触らない。
        """
        self.pyxel.play(SFX_CHANNEL, slot, loop=False)
