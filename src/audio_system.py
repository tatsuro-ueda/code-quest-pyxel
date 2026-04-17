from __future__ import annotations
from src.chiptune_tracks import CHIPTUNE_TRACKS

"""BGMサブシステム.

シーン名 → Pyxel music スロットのマッピング。
ノートデータは src/chiptune_tracks.py に分離。

設計方針:
- 各シーンは Pyxel `musics[N]` に格納される（N = TRACK_ORDER 内の index）
- 音は3チャンネル（melody/bass/drums）が `pyxel.sounds` に書き込まれ、
  music が ch0/ch1/ch2 から再生する。ch3 は SFX 用に空けてある
- `pyxel.playm(N, loop=True)` 1回呼ぶだけで3チャンネル同時に再生される

注意: ここで `pyxel.sounds[N].set()` / `pyxel.musics[N].set()` で書き込むのは
**起動時のフォールバック値**。main.py の `_setup_image_banks` が `.pyxres` を
load するとこのスロットも上書きされるため、Code Maker / `pyxel edit` で
編集した BGM が優先される。コード側の編集を反映させたい場合は
`assets/blockquest.pyxres` を削除する。
"""




TRACK_ORDER = tuple(CHIPTUNE_TRACKS.keys())

MELODY_CHANNEL = 0
BASS_CHANNEL = 1
DRUM_CHANNEL = 2

# 旧コードとの互換用 (BGMの代表チャンネル)
BGM_CHANNEL = MELODY_CHANNEL


def melody_slot(scene_name: str) -> int:
    return TRACK_ORDER.index(scene_name) * 3


def bass_slot(scene_name: str) -> int:
    return TRACK_ORDER.index(scene_name) * 3 + 1


def drum_slot(scene_name: str) -> int:
    return TRACK_ORDER.index(scene_name) * 3 + 2


def music_index(scene_name: str) -> int:
    """シーン名から music スロット index (0-7) を返す。"""
    return TRACK_ORDER.index(scene_name)


def track_slot(scene_name: str) -> int:
    """旧API互換: シーンの代表スロット (= melody) を返す."""
    return melody_slot(scene_name)


def choose_bgm_scene(
    *,
    state: str,
    in_dungeon: bool,
    zone: int,
    battle_is_glitch_lord: bool = False,
    battle_enemy_hp: int = 0,
    battle_enemy_max_hp: int = 0,
    battle_phase: str = "menu",
) -> str:
    """state/zone/battle 状態から再生すべき BGM シーン名を返す。

    8トラック構成（title/town/overworld/dungeon/battle/boss/victory/ending）に
    マップする。旧 zone1/2/3 → overworld、旧 boss1/2 → boss に統合済み。
    """
    if state == "title":
        return "title"
    if state == "ending":
        return "ending"
    if state == "battle":
        if battle_phase == "result" and battle_enemy_hp <= 0:
            return "victory"
        if battle_is_glitch_lord:
            return "boss"
        return "battle"
    if state == "town":
        return "town"
    if in_dungeon:
        return "dungeon"
    if zone >= 1:
        return "overworld"
    return "town"


class AudioManager:
    def __init__(self, pyxel_module):
        self.pyxel = pyxel_module
        self.current_scene: str | None = None
        self._load_tracks()

    def _load_tracks(self):
        """sounds[0..23] に各トラックの melody/bass/drum を書き込み、
        musics[0..7] にその3スロットを束ねる。
        """
        for scene_name in TRACK_ORDER:
            data = CHIPTUNE_TRACKS[scene_name]
            speed = data["speed"]
            mslot = melody_slot(scene_name)
            bslot = bass_slot(scene_name)
            dslot = drum_slot(scene_name)
            self.pyxel.sounds[mslot].set(data["melody"], "p", "6", "n", speed)
            self.pyxel.sounds[bslot].set(data["bass"], "t", "5", "n", speed)
            self.pyxel.sounds[dslot].set(data["drums"], "n", "4", "f", speed)
            # music スロットに 3チャンネル分を設定（ch3 は空＝SFX用に確保）
            self.pyxel.musics[music_index(scene_name)].set(
                [mslot], [bslot], [dslot], []
            )
        # 初期チャンネルゲイン (タイトルBGM相当)
        title_gain = CHIPTUNE_TRACKS["title"]["gain"]
        self.pyxel.channels[MELODY_CHANNEL].gain = title_gain
        self.pyxel.channels[BASS_CHANNEL].gain = title_gain * 0.7
        self.pyxel.channels[DRUM_CHANNEL].gain = title_gain * 0.5

    def play_scene(self, scene_name: str):
        if self.current_scene == scene_name:
            return
        self.current_scene = scene_name
        gain = CHIPTUNE_TRACKS[scene_name]["gain"]
        self.pyxel.channels[MELODY_CHANNEL].gain = gain
        self.pyxel.channels[BASS_CHANNEL].gain = gain * 0.7
        self.pyxel.channels[DRUM_CHANNEL].gain = gain * 0.5
        # 1回の playm で3チャンネル同時再生
        self.pyxel.playm(music_index(scene_name), loop=True)
