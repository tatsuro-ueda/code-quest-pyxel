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


# ======================================================================
# SFX: 効果音
# ======================================================================

SFX_CHANNEL = 3

# slot 33以降を使用する（BGMが0-32を消費）。
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
        "tone": "p", "notes": "g1c2e2a#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2g1c2e2a#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2", "volume": "777776544444444444444321", "effect": "v", "speed": 4,
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
    """SFX を初期化・再生する小さなマネージャ。

    `SFX_DEFINITIONS` の順序で slot 33 から割り当てる。
    `.pyxres` 側で既にサウンドが入っているスロットはそのまま使い、空スロットだけ
    fallback 値で埋める（Code Maker 編集を優先）。
    """

    def __init__(self, pyxel_module):
        """Pyxel モジュールを受け取り、SFX スロットを準備する。"""
        self.pyxel = pyxel_module
        self._slots: dict[str, int] = {}
        self.enabled = True
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
        """名前で SFX を再生する（未定義名は黙って無視、ON/OFF も尊重）。"""
        if not self.enabled:
            return
        slot = self._slots.get(name)
        if slot is None:
            return
        self.pyxel.play(SFX_CHANNEL, slot, loop=False)

    def set_enabled(self, enabled: bool):
        """SFX の ON/OFF を切り替える。OFF にした瞬間に再生中 SE を止める。"""
        self.enabled = bool(enabled)
        if not self.enabled:
            self.pyxel.stop(SFX_CHANNEL)


def sync_audio(game):
    """game.audio に BGM scene と enabled を反映する（P1-G15 で Game から移動）。"""
    import src.runtime.main_runtime as M
    bm = game.battle_scene.model
    battle_enemy_max_hp = bm.enemy["hp"] if bm.enemy else 0
    state_for_audio = game.state
    if game.state == "settings" and game.settings_scene.model.origin == "title":
        state_for_audio = "title"
    scene_name = choose_bgm_scene(
        state=state_for_audio,
        in_dungeon=game.player["in_dungeon"],
        zone=M.get_zone(game.player["y"], game.player["in_dungeon"]),
        battle_is_glitch_lord=bm.is_glitch_lord,
        battle_enemy_hp=bm.enemy_hp,
        battle_enemy_max_hp=battle_enemy_max_hp,
        battle_phase=bm.phase,
    )
    game.audio.set_enabled(game.player.get("bgm_enabled", True))
    game.audio.play_scene(scene_name)

