from __future__ import annotations

"""BGM subsystem and track catalog."""


CHIPTUNE_TRACKS: dict[str, dict] = {
    "title": {
        "melody": "e2g2a2b2 e3d3b2a2 g2a2b2c3 d3e3rr",
        "bass": "e1e1e1e1 c1c1c1c1 d1d1d1d1 e1e1e1e1",
        "drums": "f0ra4r f0ra4r f0ra4r f0f0a4r",
        "speed": 22,
        "gain": 0.30,
    },
    "town": {
        "melody": "c2e2g2c3 a2g2e2g2 f2a2c3a2 g2e2c2r",
        "bass": "c1c1c1c1 f1f1f1f1 g1g1g1g1 c1c1c1c1",
        "drums": "f0rrr a4rrr f0rrr a4rrr",
        "speed": 25,
        "gain": 0.28,
    },
    "overworld": {
        "melody": "g2b2d3g3 d3b2g2d2 e2g2b2d3 b2g2d2g2",
        "bass": "g1g1g1g1 d1d1d1d1 c1c1c1c1 g1g1g1g1",
        "drums": "f0rrr a4rrr f0rrr a4rrr",
        "speed": 23,
        "gain": 0.30,
    },
    "dungeon": {
        "melody": "e2rg2r b2re3r d3rb2r g2re2r",
        "bass": "e1e1e1e1 e1e1e1e1 c1c1c1c1 d1d1d1d1",
        "drums": "f0rrr rrrr f0rrr rrrr",
        "speed": 30,
        "gain": 0.32,
    },
    "battle": {
        "melody": "a2c3a2e2 c3e3c3a2 g2b2g2d2 b2d3b2g2",
        "bass": "a1a1e1e1 a1a1e1e1 g1g1d1d1 g1g1d1d1",
        "drums": "f0ra4r f0f0a4r f0ra4r f0f0a4r",
        "speed": 16,
        "gain": 0.34,
    },
    "boss": {
        "melody": "f#2a2c#3f#3 c#3a2f#2c#2 e2g2b2e3 b2g2e2b1",
        "bass": "f#1f#1c#1c#1 f#1f#1c#1c#1 e1e1b0b0 e1e1b0b0",
        "drums": "f0f0a4r f0f0a4r f0f0a4r f0a4a4r",
        "speed": 17,
        "gain": 0.36,
    },
    "victory": {
        "melody": "c3e3g3c4 g3c4rr e3g3c4e4 c4rrr",
        "bass": "c2c2c2c2 c2c2rr f1g1c2c2 c2rrr",
        "drums": "f0f0a4r f0f0a4r f0f0a4a4 f0rrr",
        "speed": 18,
        "gain": 0.34,
    },
    "ending": {
        "melody": "d3f#3a3d4 a3f#3d3a2 g2b2d3g3 f#3d3a2d2",
        "bass": "d1d1d1d1 g1g1g1g1 a1a1a1a1 d1d1d1d1",
        "drums": "f0rrr rrrr f0rrr rrrr",
        "speed": 32,
        "gain": 0.30,
    },
}


TRACK_ORDER = tuple(CHIPTUNE_TRACKS.keys())
MELODY_CHANNEL = 0
BASS_CHANNEL = 1
DRUM_CHANNEL = 2
BGM_CHANNEL = MELODY_CHANNEL


def melody_slot(scene_name: str) -> int:
    """シーンに割り当てられたメロディ用 Pyxel サウンドスロット番号を返す。"""
    return TRACK_ORDER.index(scene_name) * 3


def bass_slot(scene_name: str) -> int:
    """シーンに割り当てられたベース用 Pyxel サウンドスロット番号を返す。"""
    return TRACK_ORDER.index(scene_name) * 3 + 1


def drum_slot(scene_name: str) -> int:
    """シーンに割り当てられたドラム用 Pyxel サウンドスロット番号を返す。"""
    return TRACK_ORDER.index(scene_name) * 3 + 2


def music_index(scene_name: str) -> int:
    """シーンに対応する Pyxel ミュージック番号を返す。"""
    return TRACK_ORDER.index(scene_name)


def track_slot(scene_name: str) -> int:
    """シーンの代表サウンドスロット（melody と同一）を返す互換API。"""
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
    """ゲーム状態から再生すべき BGM シーン名を決定する純粋関数。"""
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
    """Pyxel 音声 API をラップし、シーンごとの BGM 再生と ON/OFF を管理する。"""

    def __init__(self, pyxel_module):
        """Pyxel モジュールを受け取り、全トラックを事前ロードする。"""
        self.pyxel = pyxel_module
        self.current_scene: str | None = None
        self.enabled = True
        self._load_tracks()

    def _load_tracks(self):
        """CHIPTUNE_TRACKS を Pyxel の sounds / musics スロットに流し込む。"""
        for scene_name in TRACK_ORDER:
            data = CHIPTUNE_TRACKS[scene_name]
            speed = data["speed"]
            mslot = melody_slot(scene_name)
            bslot = bass_slot(scene_name)
            dslot = drum_slot(scene_name)
            self.pyxel.sounds[mslot].set(data["melody"], "p", "6", "n", speed)
            self.pyxel.sounds[bslot].set(data["bass"], "t", "5", "n", speed)
            self.pyxel.sounds[dslot].set(data["drums"], "n", "4", "f", speed)
            self.pyxel.musics[music_index(scene_name)].set([mslot], [bslot], [dslot], [])
        title_gain = CHIPTUNE_TRACKS["title"]["gain"]
        self.pyxel.channels[MELODY_CHANNEL].gain = title_gain
        self.pyxel.channels[BASS_CHANNEL].gain = title_gain * 0.7
        self.pyxel.channels[DRUM_CHANNEL].gain = title_gain * 0.5

    def play_scene(self, scene_name: str):
        """指定シーンの BGM に切り替える（同じシーンなら何もしない）。"""
        if self.current_scene == scene_name:
            return
        self.current_scene = scene_name
        if not self.enabled:
            return
        gain = CHIPTUNE_TRACKS[scene_name]["gain"]
        self.pyxel.channels[MELODY_CHANNEL].gain = gain
        self.pyxel.channels[BASS_CHANNEL].gain = gain * 0.7
        self.pyxel.channels[DRUM_CHANNEL].gain = gain * 0.5
        self.pyxel.playm(music_index(scene_name), loop=True)

    def set_enabled(self, enabled: bool):
        """BGM の ON/OFF を切り替える。OFF時は停止、ON復帰時は現在シーンを再開する。"""
        enabled = bool(enabled)
        if self.enabled == enabled:
            return
        self.enabled = enabled
        if not enabled:
            self.pyxel.stop(MELODY_CHANNEL)
            self.pyxel.stop(BASS_CHANNEL)
            self.pyxel.stop(DRUM_CHANNEL)
            return
        if self.current_scene is None:
            return
        gain = CHIPTUNE_TRACKS[self.current_scene]["gain"]
        self.pyxel.channels[MELODY_CHANNEL].gain = gain
        self.pyxel.channels[BASS_CHANNEL].gain = gain * 0.7
        self.pyxel.channels[DRUM_CHANNEL].gain = gain * 0.5
        self.pyxel.playm(music_index(self.current_scene), loop=True)
