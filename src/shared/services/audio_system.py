from __future__ import annotations

"""SFX subsystem + BGM 冪等再生ヘルパー.

2026-05-07 改訂（C+ 確定版・BGM SSoT タスク）：

BGM 関連（旧 ``AudioManager`` / ``CHIPTUNE_TRACKS`` / ``TRACK_ORDER`` /
``melody_slot`` / ``bass_slot`` / ``drum_slot`` / ``music_index`` /
``track_slot`` / ``choose_bgm_scene`` / ``sync_audio``）はすべて撤去した。

新方針：
  * BGM はそのシーンの ``view.py`` から ``pyxel.playm(N, loop=True)`` を
    直接呼ぶ。冪等性は本モジュールの ``play_bgm_track`` に集約する。
    （CJ44 確定版の追加整理：``Game.current_bgm`` のような中央集権状態は
    持たず、モジュールスコープのプライベート変数で BGM の現在値を保持する）。
  * 複数曲を持つシーン（``ExploreView`` / ``BattleView``）は
    View 内の小さな ``if`` 分岐で選曲する。
  * BGM の音符・楽器設定は ``assets/blockquest.pyxres`` が SSoT。
    Pyxel Code Maker で編集したものが起動後そのまま鳴る。
  * 演出 ON/OFF 機構（個別 / ``ぜんぶ``）は提供しない。BGM・SFX・VFX は
    常に ON。設定画面に演出切替項目は持たない（CJ44）。

本ファイルでは SFX に関する責務 + BGM 冪等再生ヘルパーを持つ：
  * ``SFX_DEFINITIONS``: pyxres 不在 / 空 slot 時の fallback 音色データ。
  * ``SfxSystem``: pyxres 尊重で SFX を ロード・再生する薄い service。
  * ``play_bgm_track``: BGM を冪等に切り替えるための 1 関数（view から呼ぶ）。
"""

import pyxel as _pyxel


SFX_CHANNEL = 3


_current_bgm_track: int | None = None
"""現在再生中の BGM (``pyxel.musics`` slot 番号)。冪等再生のためだけに使う。

CJ44 確定版：``Game`` クラスや ``AudioManager`` のような中央集権オブジェクトに
状態を持たせず、本モジュールのプライベート変数で 1 箇所だけ保持する。
"""


def play_bgm_track(target: int) -> None:
    """指定 music slot を冪等に再生する。

    既に同じ track が鳴っているなら何もしない。違う track なら ``pyxel.stop``
    したうえで ``pyxel.playm(target, loop=True)`` を呼ぶ。

    各 scene の ``view.py::play_bgm`` から呼ばれる薄いヘルパー。
    """
    global _current_bgm_track
    if _current_bgm_track == target:
        return
    _pyxel.stop()
    _pyxel.playm(target, loop=True)
    _current_bgm_track = target


def reset_bgm_state_for_tests() -> None:
    """テストから ``_current_bgm_track`` をリセットするためのフック。

    本番コードからは呼ばない。テスト間で BGM の "鳴り始め" を再現したい場合のみ。
    """
    global _current_bgm_track
    _current_bgm_track = None

# slot 33以降を使用する（旧 BGM 設計が 0-32 を消費していたため）。
# 順序が slot 割り当てを決定する（cursor=33, select=34, ... step=54）。
# 新規追加は末尾に。途中の入替は .pyxres との対応が壊れるので禁止。
SFX_BASE_SLOT = 33


SFX_DEFINITIONS: dict[str, dict] = {
    "cursor": {
        "tone": "t", "notes": "c3", "volume": "7", "effect": "f", "speed": 11,
    },
    "select": {
        "tone": "p", "notes": "g#4", "volume": "5", "effect": "f", "speed": 14,
    },
    "cancel": {
        "tone": "p", "notes": "e3e2e3e2e3e2e3e2e3e2e3e2e3e2e3e2", "volume": "", "effect": "f", "speed": 1,
    },
    "attack": {
        "tone": "n", "notes": "d3a2g#2c#3a3a#4", "volume": "765677", "effect": "nnnnnf", "speed": 2,
    },
    "hit": {
        "tone": "n", "notes": "f#3d4b4b3c3d2f#1f#1f#1f#1f#1f#1", "volume": "777777776655", "effect": "nnnnnnnnnnnf", "speed": 2,
    },
    "heal": {
        "tone": "sp", "notes": "c3c4f3f4a#3a#4a#4a#4a#4", "volume": "775577777", "effect": "nfnfnnnnf", "speed": 3,
    },
    "levelup": {
        "tone": "sp", "notes": "d2d3g2g3c3c4f3f4a#3a#4a#4a#4a#4", "volume": "7755775577777", "effect": "nfnfnfnfnnnnf", "speed": 3,
    },
    "victory": {
        "tone": "p", "notes": "g2c3e3g3", "volume": "6", "effect": "n", "speed": 10,
    },
    "save": {
        "tone": "p", "notes": "a2a3", "volume": "37", "effect": "nf", "speed": 5,
    },
    "encounter": {
        "tone": "p", "notes": "g1c2e2a#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2g1c2e2a#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2", "volume": "777776544444444444444321", "effect": "v", "speed": 4,
    },
    "miss": {
        "tone": "n", "notes": "f#3", "volume": "7", "effect": "f", "speed": 4,
    },
    "dead": {
        "tone": "n", "notes": "f2c#2a1f#1e1d#1d1d1d1d1d1d1d1d1d1d1d1d1c#1c#1c#1c#1c#1c#1c1c1a#0a0g#0g0f#0f0d#0d0c#0c0", "volume": "765555555555555555555443332211111111", "effect": "", "speed": 2,
    },
    "magic": {
        "tone": "pn", "notes": "d2d2c#2c#2c2c2e2e2d#2d#2d2d2f#2f#2f2f2e2e2g#2g#2g2g2f#2f#2", "volume": "72", "effect": "", "speed": 2,
    },
    "poison": {
        "tone": "n", "notes": "f#4", "volume": "7", "effect": "", "speed": 20,
    },
    "cure": {
        "tone": "n", "notes": "a#4g4a#4g4a#4g4g4g4a#4g4a#4g4g4g4a#4g4", "volume": "2323233323233323", "effect": "nfnfnnnfnfnnnfnf", "speed": 4,
    },
    "dungeon_in": {
        "tone": "s", "notes": "a2a1a#2a#1b2b1c3c2a2a1a#2a#1b2b1c3c2", "volume": "7", "effect": "v", "speed": 5,
    },
    "boss_approach": {
        "tone": "n", "notes": "b3b2a#2g#2f2c#2d1d1d1d1d1", "volume": "47777776542", "effect": "n", "speed": 6,
    },
    "boss_defeat": {
        "tone": "n", "notes": "b3c4c#4d4b3c4c#4d4b3c4c#4d4b3c4c#4d4b3c4c#4d4b3c4c#4d4", "volume": "777777776666666655555555", "effect": "nnnf", "speed": 5,
    },
    "critical": {
        "tone": "n", "notes": "f#3f#3a#3f#3f#3a#3f#3f#3a#3", "volume": "765", "effect": "ssn", "speed": 6,
    },
    "zone_change": {
        "tone": "n", "notes": "b2rc3rb2rc3", "volume": "7766554", "effect": "f", "speed": 13,
    },
    "poison_tick": {
        "tone": "t", "notes": "f#1", "volume": "4", "effect": "f", "speed": 8,
    },
    "step": {
        "tone": "s", "notes": "d#1", "volume": "3", "effect": "f", "speed": 6,
    },
}


class SfxSystem:
    """SFX を初期化・再生する薄いマネージャ（pyxres 尊重）。

    `SFX_DEFINITIONS` の順序で slot 33 から割り当てる。
    `.pyxres` 側で既にサウンドが入っているスロットはそのまま使い、空スロット
    だけ fallback 値で埋める（Code Maker 編集を優先）。
    """

    def __init__(self, pyxel_module):
        """Pyxel モジュールを受け取り、SFX スロットを準備する。"""
        self.pyxel = pyxel_module
        self._slots: dict[str, int] = {}
        self._load()
        self.pyxel.channels[SFX_CHANNEL].gain = 0.5

    def _slot_has_sound(self, slot: int) -> bool:
        """Code Maker / pyxel.load() 済み slot があればそれを優先する。"""
        sound = self.pyxel.sounds[slot]
        for attr in ("notes", "tones", "volumes", "effects"):
            try:
                if len(getattr(sound, attr)) > 0:
                    return True
            except Exception:
                continue
        return False

    def _load(self):
        """空スロットに fallback の SFX 定義を流し込む。"""
        for i, (name, sd) in enumerate(SFX_DEFINITIONS.items()):
            slot = SFX_BASE_SLOT + i
            self._slots[name] = slot
            if self._slot_has_sound(slot):
                continue
            self.pyxel.sounds[slot].set(
                sd["notes"], sd["tone"], sd["volume"], sd["effect"], sd["speed"]
            )

    def play(self, name: str):
        """名前で SFX を再生する（未定義名は黙って無視）。"""
        slot = self._slots.get(name)
        if slot is None:
            return
        self.pyxel.play(SFX_CHANNEL, slot, loop=False)
