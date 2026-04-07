"""BGMサブシステム.

シーン名 → Pyxel内蔵チップチューン (3チャンネル: melody/bass/drums) のマッピング。
ノートデータは src/chiptune_tracks.py に分離。
"""

from __future__ import annotations

from src.chiptune_tracks import CHIPTUNE_TRACKS


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


def track_slot(scene_name: str) -> int:
    """旧API互換: シーンの代表スロット (= melody) を返す."""
    return melody_slot(scene_name)


def choose_bgm_scene(
    *,
    state: str,
    in_dungeon: bool,
    zone: int,
    battle_is_boss: bool = False,
    battle_enemy_hp: int = 0,
    battle_enemy_max_hp: int = 0,
    battle_phase: str = "menu",
) -> str:
    if state == "title":
        return "title"
    if state == "ending":
        return "ending"
    if state == "battle":
        if battle_phase == "result" and battle_enemy_hp <= 0:
            return "victory"
        if battle_is_boss:
            hp_ratio = battle_enemy_hp / max(1, battle_enemy_max_hp)
            return "boss2" if hp_ratio <= 0.4 else "boss1"
        return "battle"
    if state == "town":
        return "town"
    if in_dungeon:
        return "dungeon"
    if zone >= 3:
        return "zone3"
    if zone == 2:
        return "zone2"
    if zone == 1:
        return "zone1"
    return "town"


class AudioManager:
    def __init__(self, pyxel_module):
        self.pyxel = pyxel_module
        self.current_scene: str | None = None
        self._load_tracks()

    def _load_tracks(self):
        for scene_name in TRACK_ORDER:
            data = CHIPTUNE_TRACKS[scene_name]
            speed = data["speed"]
            self.pyxel.sounds[melody_slot(scene_name)].set(
                data["melody"], "p", "6", "n", speed
            )
            self.pyxel.sounds[bass_slot(scene_name)].set(
                data["bass"], "t", "5", "n", speed
            )
            self.pyxel.sounds[drum_slot(scene_name)].set(
                data["drums"], "n", "4", "f", speed
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
        self.pyxel.play(MELODY_CHANNEL, melody_slot(scene_name), loop=True)
        self.pyxel.play(BASS_CHANNEL, bass_slot(scene_name), loop=True)
        self.pyxel.play(DRUM_CHANNEL, drum_slot(scene_name), loop=True)
