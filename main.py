"""Block Quest — Single-file build for Pyxel Code Maker.

GENERATED FILE — do not edit by hand.
Source of truth: main.py + src/*.py
Regenerate via: python tools/build_codemaker.py

Known limitations on Code Maker:
- Japanese text falls back to English (BDF font cannot be loaded)
- save.json file I/O may not work; use the localStorage path
"""
from __future__ import annotations
import sys


# === inlined: src/chiptune_tracks.py ===
"""Chiptune BGM definitions for ブロッククエスト.

各シーン1曲につき、メロディ・ベース・ドラムの3チャンネル分を定義する。
ノート文字列は Pyxel のサウンド記法（letter + octave、`r` はレスト、空白無視）。

Pyxel music API 経由で再生する設計：
    pyxel.musics[scene_index].set([melody_slot], [bass_slot], [drum_slot], [])
    pyxel.playm(scene_index, loop=True)

これにより Pyxel Code Maker / `pyxel edit` の Music タブで編集可能になる。
Pyxel の music スロットは8個までなので、本作も **8トラックに収まるよう取捨選択** している：

    title / town / overworld / dungeon / battle / boss / victory / ending

旧 zone1/zone2/zone3 は `overworld` に統合（ゾーンが進んでも曲は変わらない）。
旧 boss1/boss2 は `boss` に統合（HP低下による曲切替えなし）。

シーン → サウンドスロット割当:
    melody_slot = scene_index * 3
    bass_slot   = scene_index * 3 + 1
    drum_slot   = scene_index * 3 + 2
シーン数8 × 3スロット = 24スロット使用 (sound 0-23)

トーン:
    p = pulse (メロディに使用)
    t = triangle (ベースに使用)
    n = noise (ドラムに使用)
"""



CHIPTUNE_TRACKS: dict[str, dict] = {
    # ──────────────────────────────────────────────────────────
    # title — 英雄的なオープニング (Em)
    # ──────────────────────────────────────────────────────────
    "title": {
        "melody": "e2g2a2b2 e3d3b2a2 g2a2b2c3 d3e3rr",
        "bass":   "e1e1e1e1 c1c1c1c1 d1d1d1d1 e1e1e1e1",
        "drums":  "f0ra4r f0ra4r f0ra4r f0f0a4r",
        "speed":  22,
        "gain":   0.30,
    },
    # ──────────────────────────────────────────────────────────
    # town — のどかな町 (C major)
    # ──────────────────────────────────────────────────────────
    "town": {
        "melody": "c2e2g2c3 a2g2e2g2 f2a2c3a2 g2e2c2r",
        "bass":   "c1c1c1c1 f1f1f1f1 g1g1g1g1 c1c1c1c1",
        "drums":  "f0rrr a4rrr f0rrr a4rrr",
        "speed":  25,
        "gain":   0.28,
    },
    # ──────────────────────────────────────────────────────────
    # overworld — 旅のテーマ (G major)。旧 zone1/zone2/zone3 を統合
    # ──────────────────────────────────────────────────────────
    "overworld": {
        "melody": "g2b2d3g3 d3b2g2d2 e2g2b2d3 b2g2d2g2",
        "bass":   "g1g1g1g1 d1d1d1d1 c1c1c1c1 g1g1g1g1",
        "drums":  "f0rrr a4rrr f0rrr a4rrr",
        "speed":  23,
        "gain":   0.30,
    },
    # ──────────────────────────────────────────────────────────
    # dungeon — 暗く重い (Em, slow)
    # ──────────────────────────────────────────────────────────
    "dungeon": {
        "melody": "e2rg2r b2re3r d3rb2r g2re2r",
        "bass":   "e1e1e1e1 e1e1e1e1 c1c1c1c1 d1d1d1d1",
        "drums":  "f0rrr rrrr f0rrr rrrr",
        "speed":  30,
        "gain":   0.32,
    },
    # ──────────────────────────────────────────────────────────
    # battle — エネルギッシュ (Am)
    # ──────────────────────────────────────────────────────────
    "battle": {
        "melody": "a2c3a2e2 c3e3c3a2 g2b2g2d2 b2d3b2g2",
        "bass":   "a1a1e1e1 a1a1e1e1 g1g1d1d1 g1g1d1d1",
        "drums":  "f0ra4r f0f0a4r f0ra4r f0f0a4r",
        "speed":  16,
        "gain":   0.34,
    },
    # ──────────────────────────────────────────────────────────
    # boss — 重厚なボス戦 (F#m)。旧 boss1/boss2 を統合
    # ──────────────────────────────────────────────────────────
    "boss": {
        "melody": "f#2a2c#3f#3 c#3a2f#2c#2 e2g2b2e3 b2g2e2b1",
        "bass":   "f#1f#1c#1c#1 f#1f#1c#1c#1 e1e1b0b0 e1e1b0b0",
        "drums":  "f0f0a4r f0f0a4r f0f0a4r f0a4a4r",
        "speed":  17,
        "gain":   0.36,
    },
    # ──────────────────────────────────────────────────────────
    # victory — 短い勝利ファンファーレ (C major)
    # ──────────────────────────────────────────────────────────
    "victory": {
        "melody": "c3e3g3c4 g3c4rr e3g3c4e4 c4rrr",
        "bass":   "c2c2c2c2 c2c2rr f1g1c2c2 c2rrr",
        "drums":  "f0f0a4r f0f0a4r f0f0a4a4 f0rrr",
        "speed":  18,
        "gain":   0.34,
    },
    # ──────────────────────────────────────────────────────────
    # ending — 感動的なエンディング (D major, slow)
    # ──────────────────────────────────────────────────────────
    "ending": {
        "melody": "d3f#3a3d4 a3f#3d3a2 g2b2d3g3 f#3d3a2d2",
        "bass":   "d1d1d1d1 g1g1g1g1 a1a1a1a1 d1d1d1d1",
        "drums":  "f0rrr rrrr f0rrr rrrr",
        "speed":  32,
        "gain":   0.30,
    },
}

# === inlined: src/shared/services/input_bindings.py ===


UP_BUTTONS = ("KEY_UP", "GAMEPAD1_BUTTON_DPAD_UP")
DOWN_BUTTONS = ("KEY_DOWN", "GAMEPAD1_BUTTON_DPAD_DOWN")
LEFT_BUTTONS = ("KEY_LEFT", "GAMEPAD1_BUTTON_DPAD_LEFT")
RIGHT_BUTTONS = ("KEY_RIGHT", "GAMEPAD1_BUTTON_DPAD_RIGHT")
CONFIRM_BUTTONS = ("KEY_Z", "KEY_SPACE", "KEY_RETURN", "GAMEPAD1_BUTTON_B")
CANCEL_BUTTONS = ("KEY_X", "KEY_ESCAPE", "GAMEPAD1_BUTTON_A", "GAMEPAD1_BUTTON_BACK")
TITLE_START_BUTTONS = CONFIRM_BUTTONS + ("GAMEPAD1_BUTTON_START",)

BUTTON_GROUPS = (
    UP_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
    TITLE_START_BUTTONS,
)


def any_btn(pyxel_module, button_names) -> bool:
    return any(pyxel_module.btn(getattr(pyxel_module, name)) for name in button_names)


def any_btnp(pyxel_module, button_names) -> bool:
    return any(pyxel_module.btnp(getattr(pyxel_module, name)) for name in button_names)


class InputStateTracker:
    def __init__(self):
        self._held = {button_names: False for button_names in BUTTON_GROUPS}
        self._pressed = {button_names: False for button_names in BUTTON_GROUPS}

    def update(self, pyxel_module):
        next_held = {}
        next_pressed = {}
        for button_names in BUTTON_GROUPS:
            held = any_btn(pyxel_module, button_names)
            next_held[button_names] = held
            next_pressed[button_names] = held and not self._held[button_names]
        self._held = next_held
        self._pressed = next_pressed

    def btn(self, button_names) -> bool:
        return self._held.get(button_names, False)

    def btnp(self, button_names) -> bool:
        return self._pressed.get(button_names, False)

# === inlined: src/landmark_events.py ===
"""Landmark proximity checks for overworld interactions.

世界樹と通信塔を「初訪問 / 再訪問 / クリア後エピローグ」の3状態で扱う。
JS版 `interactWorldTree` / `interactTower` / `queueTowerEpilogue` の簡易ポート。
"""


from dataclasses import dataclass


@dataclass(frozen=True)
class LandmarkEvent:
    scene_name: str
    flag_name: str
    x: int
    y: int
    radius: int = 3
    repeat_scene: str | None = None
    epilogue_scene: str | None = None
    epilogue_flag: str | None = None


LANDMARK_EVENTS = (
    LandmarkEvent(
        scene_name="landmark.tree.first",
        flag_name="landmarkTreeSeen",
        repeat_scene="landmark.tree.repeat",
        x=32,
        y=9,
    ),
    LandmarkEvent(
        scene_name="landmark.tower.first",
        flag_name="landmarkTowerSeen",
        repeat_scene="landmark.tower.repeat",
        epilogue_scene="landmark.tower.epilogue",
        epilogue_flag="towerEpilogueSeen",
        x=40,
        y=32,
    ),
)


def find_landmark_event(
    *,
    player_x: int,
    player_y: int,
    flags: dict[str, bool],
) -> LandmarkEvent | None:
    """Return the first unseen landmark event within Manhattan distance.

    互換用: 初訪問専用。再訪問やエピローグを扱いたい場合は
    find_landmark_at + resolve_scene を使う。
    """
    for event in LANDMARK_EVENTS:
        if flags.get(event.flag_name, False):
            continue
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None


def find_landmark_at(player_x: int, player_y: int) -> LandmarkEvent | None:
    """Return any landmark within range, regardless of visit flags."""
    for event in LANDMARK_EVENTS:
        distance = abs(player_x - event.x) + abs(player_y - event.y)
        if distance <= event.radius:
            return event
    return None


def resolve_scene(event: LandmarkEvent, flags: dict[str, bool], glitch_lord_defeated: bool) -> str:
    """Decide which scene to play for an event based on player flags."""
    # First visit
    if not flags.get(event.flag_name, False):
        return event.scene_name
    # Boss defeated and epilogue not yet played
    if (
        glitch_lord_defeated
        and event.epilogue_scene
        and event.epilogue_flag
        and not flags.get(event.epilogue_flag, False)
    ):
        return event.epilogue_scene
    # Otherwise, repeat scene (or first scene if no repeat defined)
    return event.repeat_scene or event.scene_name

# === inlined: src/player_factory.py ===
"""Player factory and level/stat formulas.

旧JS版の `expForLevel` / `statsForLevel` / `MAX_LEVEL`
を Python に移植した純粋関数群と、初期プレイヤー生成を担う。
"""


from typing import Any

MAX_LEVEL = 100


def exp_for_level(lv: int) -> int:
    """Return the experience needed to reach the given level.

    Mirrors the JS implementation:
        if(lv===2)return 26;
        return Math.floor(10*Math.pow(lv,2)+6*lv);
    """
    if lv == 2:
        return 26
    return int(10 * lv * lv + 6 * lv)


def stats_for_level(lv: int) -> dict[str, int]:
    """Return baseline player stats for the given level.

    Mirrors the JS implementation:
        {maxHp:30+lv*15, maxMp:10+lv*6, atk:5+lv*2, def:3+lv*3, agi:5+lv*2}
    """
    return {
        "max_hp": 30 + lv * 15,
        "max_mp": 10 + lv * 6,
        "atk": 5 + lv * 2,
        "def": 3 + lv * 3,
        "agi": 5 + lv * 2,
    }


def create_initial_player(start_x: int = 25, start_y: int = 6) -> dict[str, Any]:
    """Create a fresh player dict at level 1 using stats_for_level(1).

    The base stats keys (max_hp, max_mp, atk, def, agi) are set from
    stats_for_level(1), and current hp/mp default to their max values.
    """
    base = stats_for_level(1)
    return {
        "x": start_x,
        "y": start_y,
        "hp": base["max_hp"],
        "max_hp": base["max_hp"],
        "mp": base["max_mp"],
        "max_mp": base["max_mp"],
        "atk": base["atk"],
        "def": base["def"],
        "agi": base["agi"],
        "lv": 1,
        "exp": 0,
        "gold": 50,
        "weapon": 0,
        "armor": 0,
        "items": [{"id": 0, "qty": 3}],
        "spells": [],
        "poisoned": False,
        "in_dungeon": False,
        "glitch_lord_defeated": False,
        "max_zone_reached": 0,
        "landmarkTreeSeen": False,
        "landmarkTowerSeen": False,
        "towerEpilogueSeen": False,
        "treeAsked": False,
        "towerNoiseCleared": False,
        "professor_intro_seen": False,
        "professor_defeated": False,
        "professor_ending_seen": False,
        "bgm_enabled": True,
        "sfx_enabled": True,
        "vfx_enabled": True,
        "dialog_flags": {},
        "town_talk_idx": [0, 0, 0],
    }

# === inlined: src/player_snapshot.py ===
"""Pure functions for serializing Game.player state to a savable dict.

Only keys in SAVED_PLAYER_KEYS are persisted, preventing accidental leakage
of debug-only or transient battle state into save files.
"""

from typing import Any

SAVE_VERSION = 1

# 明示リスト。新しいフィールドを保存対象にしたいときはここに追加する。
SAVED_PLAYER_KEYS: tuple[str, ...] = (
    "x", "y",
    "hp", "max_hp", "mp", "max_mp",
    "atk", "def", "agi",
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
    "bgm_enabled", "sfx_enabled", "vfx_enabled",
    "dialog_flags",
    "town_talk_idx",
)


def dump_snapshot(player: dict[str, Any], town_pos: tuple[int, int]) -> dict[str, Any]:
    """Game.player から保存用 dict を組み立てる。

    town_pos はセーブを実行した町タイルの座標。ロード時にプレイヤーを
    同じタイル上に出現させるために使う。
    """
    saved_player = {key: player[key] for key in SAVED_PLAYER_KEYS if key in player}
    return {
        "save_version": SAVE_VERSION,
        "town_pos": [int(town_pos[0]), int(town_pos[1])],
        "player": saved_player,
    }


def restore_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """SaveStore.load() の結果を Game に流し込みやすい形に整える。

    Returns:
        {"player": dict, "town_pos": tuple[int, int]}
    """
    raw_pos = snapshot["town_pos"]
    player = dict(snapshot["player"])
    if "glitch_lord_defeated" not in player and "boss_defeated" in player:
        player["glitch_lord_defeated"] = bool(player.pop("boss_defeated"))
    player.setdefault("bgm_enabled", True)
    player.setdefault("sfx_enabled", True)
    player.setdefault("vfx_enabled", True)
    return {
        "player": player,
        "town_pos": (int(raw_pos[0]), int(raw_pos[1])),
    }

# === inlined: src/shared/services/save_store.py ===
"""Persistence layer for Block Quest save data.

Three implementations:
  * FileSaveStore         — desktop, atomic write to save.json
  * LocalStorageSaveStore — Pyxel web (Pyodide), via js.localStorage
  * InMemorySaveStore     — unit tests

Use make_save_store() to pick the right one for the current environment.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, Protocol


class SaveStoreError(OSError):
    """Raised when a SaveStore implementation cannot fulfil save/load."""


class SaveStore(Protocol):
    def exists(self) -> bool: ...
    def load(self) -> Optional[dict[str, Any]]: ...
    def save(self, data: dict[str, Any]) -> None: ...


SUPPORTED_SAVE_VERSIONS = (1,)


def _validate_loaded(data: Any) -> Optional[dict[str, Any]]:
    if not isinstance(data, dict):
        return None
    if data.get("save_version") not in SUPPORTED_SAVE_VERSIONS:
        return None
    return data


class InMemorySaveStore:
    """Test-only store. Holds a single in-RAM dict."""

    def __init__(self) -> None:
        self._data: Optional[dict[str, Any]] = None

    def exists(self) -> bool:
        return self._data is not None

    def load(self) -> Optional[dict[str, Any]]:
        if self._data is None:
            return None
        # JSON round-trip mimics real stores (catches non-serializable values).
        return json.loads(json.dumps(self._data))

    def save(self, data: dict[str, Any]) -> None:
        self._data = json.loads(json.dumps(data))


class FileSaveStore:
    """Desktop store. Atomic write via tmp file + os.replace."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def exists(self) -> bool:
        return self._path.is_file()

    def load(self) -> Optional[dict[str, Any]]:
        if not self.exists():
            return None
        try:
            data = json.loads(self._path.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return _validate_loaded(data)

    def save(self, data: dict[str, Any]) -> None:
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        try:
            tmp_path.write_text(json.dumps(data, ensure_ascii=False), "utf-8")
            os.replace(tmp_path, self._path)
        except OSError as exc:
            try:
                tmp_path.unlink()
            except OSError:
                pass
            raise SaveStoreError(str(exc)) from exc


class LocalStorageSaveStore:
    """Web store. Backed by browser localStorage via Pyodide's `js` module.

    `import js` lives inside __init__ so desktop Python (which lacks `js`)
    can still import this module without errors.
    """

    KEY = "blockquest_save_v1"

    def __init__(self) -> None:
        import js  # type: ignore[import-not-found]
        self._js = js

    def exists(self) -> bool:
        return self._js.localStorage.getItem(self.KEY) is not None

    def load(self) -> Optional[dict[str, Any]]:
        raw = self._js.localStorage.getItem(self.KEY)
        if raw is None:
            return None
        try:
            data = json.loads(str(raw))
        except json.JSONDecodeError:
            return None
        return _validate_loaded(data)

    def save(self, data: dict[str, Any]) -> None:
        try:
            self._js.localStorage.setItem(
                self.KEY, json.dumps(data, ensure_ascii=False)
            )
        except Exception as exc:  # noqa: BLE001 - js exceptions vary
            raise SaveStoreError(str(exc)) from exc


def make_save_store(file_path: Path) -> SaveStore:
    """Pick the right SaveStore for the current Python runtime.

    On Pyodide (web Pyxel) the `js` module exists; on desktop it doesn't.
    """
    try:
        import js  # noqa: F401
        return LocalStorageSaveStore()
    except ImportError:
        return FileSaveStore(file_path)

# === inlined: src/shared/services/browser_resource_override.py ===

import base64
import io
from zipfile import BadZipFile, ZipFile


BROWSER_IMPORT_ZIP_KEY = "blockquest_codemaker_zip_v1"
BROWSER_IMPORT_META_KEY = "blockquest_codemaker_zip_meta_v1"
RESOURCE_ENTRY_NAME = "my_resource.pyxres"
CODE_ENTRY_NAME = "main.py"


def _load_browser_import_payload(js_module):
    raw_zip = js_module.localStorage.getItem(BROWSER_IMPORT_ZIP_KEY)
    raw_meta = js_module.localStorage.getItem(BROWSER_IMPORT_META_KEY)
    if raw_zip is None or raw_meta is None:
        return None
    try:
        meta = json.loads(str(raw_meta))
    except json.JSONDecodeError:
        return None
    if not isinstance(meta, dict):
        return None
    return str(raw_zip), meta


def _extract_browser_import_resource(archive_bytes: bytes) -> bytes:
    try:
        zip_file = ZipFile(io.BytesIO(archive_bytes))
    except BadZipFile as exc:
        raise ValueError("Code Maker zip として読めません") from exc

    with zip_file:
        entries = zip_file.namelist()
        exact_path = f"block-quest/{RESOURCE_ENTRY_NAME}"
        if exact_path in entries:
            resource_entry = exact_path
        else:
            matches = [
                entry
                for entry in entries
                if entry.endswith(f"/{RESOURCE_ENTRY_NAME}") or entry == RESOURCE_ENTRY_NAME
            ]
            if not matches:
                raise ValueError("Code Maker zip に my_resource.pyxres がありません")
            if len(matches) != 1:
                raise ValueError("Code Maker zip に my_resource.pyxres が複数あります")
            resource_entry = matches[0]
        return zip_file.read(resource_entry)


def stage_browser_imported_resource(runtime_root: Path, *, js_module=None) -> Path | None:
    runtime_root = Path(runtime_root).resolve()
    if js_module is None:
        try:
            import js as js_module  # type: ignore[import-not-found]
        except ImportError:
            return None

    payload = _load_browser_import_payload(js_module)
    if payload is None:
        return None

    raw_zip, _meta = payload
    try:
        archive_bytes = base64.b64decode(raw_zip.encode("ascii"), validate=True)
        resource_bytes = _extract_browser_import_resource(archive_bytes)
    except (TypeError, ValueError):
        return None

    target_path = runtime_root / RESOURCE_ENTRY_NAME
    target_path.write_bytes(resource_bytes)
    return target_path

# === inlined: src/sfx_system.py ===
"""Sound effects (SFX) for ブロッククエスト.

`pyxel.sounds[N]` の slot 33-63 を使って、短いチップチューン SE を定義し、
チャンネル3で再生する（チャンネル0-2 は BGM 用）。

pyxel-rpg-sepack (shiromofufactory/pyxel-rpg-sepack) をベースに、
85-sfx-design.md の6カテゴリ＋4ルールに沿った22音を定義。

注意: ここで定義する SE は **起動時のフォールバック値** に過ぎない。
main.py の `_setup_image_banks` が `.pyxres` を load するとこのスロットも
上書きされるため、Code Maker / `pyxel edit` で編集した SE が優先される。
コード側の編集を反映させたい場合は `assets/blockquest.pyxres` を削除する。
"""



SFX_CHANNEL = 3

# slot 33以降を使用する（BGMが0-32を消費）
SFX_BASE_SLOT = 33


# 順序が slot 割り当てを決定する（cursor=33, select=34, ... step=54）。
# 新規追加は末尾に。途中の入替は .pyxres との対応が壊れるので禁止。
SFX_DEFINITIONS: dict[str, dict] = {
    # --- 既存10音 (slots 33-42) ---
    # ①フィードバック音
    "cursor": {
        "tone": "t", "notes": "c3", "volume": "7", "effect": "f", "speed": 11,
    },
    "select": {
        "tone": "p", "notes": "g#4", "volume": "5", "effect": "f", "speed": 14,
    },
    "cancel": {
        "tone": "p", "notes": "e3e2e3e2e3e2e3e2e3e2e3e2e3e2e3e2", "volume": "", "effect": "f", "speed": 1,
    },
    # ⑥操作感の音
    "attack": {
        "tone": "n", "notes": "d3a2g#2c#3a3a#4", "volume": "765677", "effect": "nnnnnf", "speed": 2,
    },
    "hit": {
        "tone": "n", "notes": "f#3d4b4b3c3d2f#1f#1f#1f#1f#1f#1", "volume": "777777776655", "effect": "nnnnnnnnnnnf", "speed": 2,
    },
    # ②状態変化音
    "heal": {
        "tone": "sp", "notes": "c3c4f3f4a#3a#4a#4a#4a#4", "volume": "775577777", "effect": "nfnfnnnnf", "speed": 3,
    },
    "levelup": {
        "tone": "sp", "notes": "d2d3g2g3c3c4f3f4a#3a#4a#4a#4a#4", "volume": "7755775577777", "effect": "nfnfnfnfnnnnf", "speed": 3,
    },
    "victory": {
        "tone": "p", "notes": "g2c3e3g3", "volume": "6", "effect": "n", "speed": 10,
    },
    # ①フィードバック音
    "save": {
        "tone": "p", "notes": "a2a3", "volume": "37", "effect": "nf", "speed": 5,
    },
    # ③予兆音
    "encounter": {
        "tone": "p", "notes": "g1c2e2a#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2g1c2e2a#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2d#3d#2", "volume": "777776544444444444444321", "effect": "v", "speed": 4,
    },
    # --- 新規12音 (slots 43-54) ---
    # ①フィードバック音
    "miss": {
        "tone": "n", "notes": "f#3", "volume": "7", "effect": "f", "speed": 4,
    },
    # ②状態変化音
    "dead": {
        "tone": "n", "notes": "f2c#2a1f#1e1d#1d1d1d1d1d1d1d1d1d1d1d1d1c#1c#1c#1c#1c#1c#1c1c1a#0a0g#0g0f#0f0d#0d0c#0c0", "volume": "765555555555555555555443332211111111", "effect": "", "speed": 2,
    },
    # ⑥操作感の音
    "magic": {
        "tone": "pn", "notes": "d2d2c#2c#2c2c2e2e2d#2d#2d2d2f#2f#2f2f2e2e2g#2g#2g2g2f#2f#2", "volume": "72", "effect": "", "speed": 2,
    },
    # ②状態変化音
    "poison": {
        "tone": "n", "notes": "f#4", "volume": "7", "effect": "", "speed": 20,
    },
    "cure": {
        "tone": "n", "notes": "a#4g4a#4g4a#4g4g4g4a#4g4a#4g4g4g4a#4g4", "volume": "2323233323233323", "effect": "nfnfnnnfnfnnnfnf", "speed": 4,
    },
    # ③予兆音
    "dungeon_in": {
        "tone": "s", "notes": "a2a1a#2a#1b2b1c3c2a2a1a#2a#1b2b1c3c2", "volume": "7", "effect": "v", "speed": 5,
    },
    "boss_approach": {
        "tone": "n", "notes": "b3b2a#2g#2f2c#2d1d1d1d1d1", "volume": "47777776542", "effect": "n", "speed": 6,
    },
    # ④強調音
    "boss_defeat": {
        "tone": "n", "notes": "b3c4c#4d4b3c4c#4d4b3c4c#4d4b3c4c#4d4b3c4c#4d4b3c4c#4d4", "volume": "777777776666666655555555", "effect": "nnnf", "speed": 5,
    },
    # ⑥操作感の音
    "critical": {
        "tone": "n", "notes": "f#3f#3a#3f#3f#3a#3f#3f#3a#3", "volume": "765", "effect": "ssn", "speed": 6,
    },
    # ②状態変化音
    "zone_change": {
        "tone": "n", "notes": "b2rc3rb2rc3", "volume": "7766554", "effect": "f", "speed": 13,
    },
    "poison_tick": {
        "tone": "t", "notes": "f#1", "volume": "4", "effect": "f", "speed": 8,
    },
    # ⑤空間音
    "step": {
        "tone": "s", "notes": "d#1", "volume": "3", "effect": "f", "speed": 6,
    },
}


class SfxSystem:
    """SFX を初期化・再生する小さなマネージャ."""

    def __init__(self, pyxel_module):
        self.pyxel = pyxel_module
        self._slots: dict[str, int] = {}
        self.enabled = True
        self._load()
        # SE用チャンネルのゲインを設定
        self.pyxel.channels[SFX_CHANNEL].gain = 0.5

    def _slot_has_sound(self, slot: int) -> bool:
        """Code Maker / pyxel.load() 済み slot があればそれを優先する."""
        sound = self.pyxel.sounds[slot]
        for attr in ("notes", "tones", "volumes", "effects"):
            try:
                if len(getattr(sound, attr)) > 0:
                    return True
            except Exception:
                continue
        return False

    def _load(self):
        for i, (name, sd) in enumerate(SFX_DEFINITIONS.items()):
            slot = SFX_BASE_SLOT + i
            self._slots[name] = slot
            if self._slot_has_sound(slot):
                continue
            self.pyxel.sounds[slot].set(
                sd["notes"], sd["tone"], sd["volume"], sd["effect"], sd["speed"]
            )

    def play(self, name: str):
        if not self.enabled:
            return
        slot = self._slots.get(name)
        if slot is None:
            return
        self.pyxel.play(SFX_CHANNEL, slot, loop=False)

    def set_enabled(self, enabled: bool):
        self.enabled = bool(enabled)
        if not self.enabled:
            self.pyxel.stop(SFX_CHANNEL)

# === inlined: src/scenes/dialog/model.py ===
"""Structured dialogue runtime for Block Quest.

データソースは src/generated/dialogue.py の Python 定数（DIALOGUE_JA / DIALOGUE_EN）。
旧 YAML ローダーは廃止済み。
"""


from dataclasses import dataclass, field
from typing import Any


class DialogValidationError(ValueError):
    """Dialogue data does not match the supported schema."""


@dataclass(frozen=True)
class DialogChoice:
    text: str
    next_scene: str | None = None


@dataclass(frozen=True)
class DialogStep:
    scene_name: str
    speaker: str | None
    text: str
    choices: list[DialogChoice] = field(default_factory=list)
    next_scene: str | None = None


class StructuredDialogRunner:
    """Load, validate, and execute the project's structured dialogue YAML."""

    _SCENE_KEYS = {"speaker", "text", "set", "choices", "next", "variants"}
    _VARIANT_KEYS = {"when", "speaker", "text", "set", "choices", "next"}

    def __init__(self, source: "dict[str, Any]"):
        """Accept a pre-parsed dict only (YAML loader is removed).

        互換のため文字列パスも形式的に受け取れるが、その場合は呼び出し元の
        バグである可能性が高いので例外を投げる。
        """
        if not isinstance(source, dict):
            raise DialogValidationError(
                "StructuredDialogRunner now requires a dict (no YAML loader); "
                f"got {type(source).__name__}"
            )
        raw = source
        self.source_path = None
        self.variables = self._validate_variables(raw.get("variables"))
        self.scenes = self._validate_scenes(raw.get("scenes"))

        self._mutable_state: dict[str, Any] = {}
        self._extra_context: dict[str, Any] = {}
        self._current_step: DialogStep | None = None

    def start(
        self,
        scene_name: str,
        state: dict[str, Any] | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> DialogStep:
        self._mutable_state = state if state is not None else {}
        self._extra_context = dict(extra_context or {})
        self._current_step = self._resolve_scene(scene_name)
        return self._current_step

    def choose(self, index: int) -> DialogStep | None:
        if self._current_step is None:
            raise RuntimeError("choose() called before start()")
        if not self._current_step.choices:
            raise RuntimeError("choose() called without pending choices")
        if not (0 <= index < len(self._current_step.choices)):
            raise IndexError(f"choice index {index} out of range")

        choice = self._current_step.choices[index]
        if choice.next_scene is None:
            self._current_step = None
            return None

        self._current_step = self._resolve_scene(choice.next_scene)
        return self._current_step

    def continue_dialog(self) -> DialogStep | None:
        if self._current_step is None:
            return None
        if self._current_step.choices or self._current_step.next_scene is None:
            self._current_step = None
            return None

        self._current_step = self._resolve_scene(self._current_step.next_scene)
        return self._current_step

    def load_all_lines(
        self,
        scene_name: str,
        state: dict[str, Any] | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> list[str]:
        step = self.start(scene_name, state=state, extra_context=extra_context)
        lines = [step.text]
        while True:
            if step.choices:
                return lines
            step = self.continue_dialog()
            if step is None:
                return lines
            lines.append(step.text)

    def _resolve_scene(self, scene_name: str) -> DialogStep:
        try:
            scene = self.scenes[scene_name]
        except KeyError as exc:
            raise KeyError(f"unknown scene: {scene_name}") from exc

        body = self._select_body(scene_name, scene)
        self._apply_set(body.get("set"))
        choices = [
            DialogChoice(
                text=self._format_text(choice["text"]),
                next_scene=choice.get("next"),
            )
            for choice in body.get("choices", [])
        ]
        return DialogStep(
            scene_name=scene_name,
            speaker=body.get("speaker"),
            text=self._format_text(body["text"]),
            choices=choices,
            next_scene=body.get("next"),
        )

    def _select_body(self, scene_name: str, scene: dict[str, Any]) -> dict[str, Any]:
        variants = scene.get("variants")
        if variants is None:
            return scene

        current_state = {**self._mutable_state, **self._extra_context}
        for variant in variants:
            when = variant.get("when")
            if when is None:
                return variant
            if all(current_state.get(name) == expected for name, expected in when.items()):
                return variant

        raise DialogValidationError(f"no matching variant for scene '{scene_name}'")

    def _apply_set(self, values: dict[str, Any] | None) -> None:
        if not values:
            return
        for name, value in values.items():
            self._mutable_state[name] = value

    def _format_text(self, text: str) -> str:
        values = {**self._mutable_state, **self._extra_context}
        try:
            return text.format(**values)
        except KeyError as exc:
            missing = exc.args[0]
            raise DialogValidationError(
                f"missing format value '{missing}' in scene text '{text}'"
            ) from exc

    def _validate_variables(self, raw_variables: Any) -> set[str]:
        if not isinstance(raw_variables, list) or not all(
            isinstance(item, str) for item in raw_variables
        ):
            raise DialogValidationError("variables must be a list of strings")
        return set(raw_variables)

    def _validate_scenes(self, raw_scenes: Any) -> dict[str, dict[str, Any]]:
        if not isinstance(raw_scenes, dict) or not raw_scenes:
            raise DialogValidationError("scenes must be a non-empty mapping")

        scenes: dict[str, dict[str, Any]] = {}
        refs: list[tuple[str, str]] = []
        for scene_name, raw_scene in raw_scenes.items():
            if not isinstance(scene_name, str):
                raise DialogValidationError("scene names must be strings")
            if not isinstance(raw_scene, dict):
                raise DialogValidationError(f"scene '{scene_name}' must be a mapping")
            scenes[scene_name] = raw_scene
            refs.extend(self._validate_scene(scene_name, raw_scene))

        for source, target in refs:
            if target not in raw_scenes:
                raise DialogValidationError(
                    f"scene '{source}' references unknown next scene '{target}'"
                )
        return scenes

    def _validate_scene(self, scene_name: str, scene: dict[str, Any]) -> list[tuple[str, str]]:
        unknown_keys = set(scene) - self._SCENE_KEYS
        if unknown_keys:
            names = ", ".join(sorted(unknown_keys))
            raise DialogValidationError(f"scene '{scene_name}' has unknown keys: {names}")

        refs: list[tuple[str, str]] = []
        variants = scene.get("variants")
        if variants is not None:
            direct_keys = set(scene) & {"speaker", "text", "set", "choices", "next"}
            if direct_keys:
                names = ", ".join(sorted(direct_keys))
                raise DialogValidationError(
                    f"scene '{scene_name}' cannot mix variants with direct keys: {names}"
                )
            if not isinstance(variants, list) or not variants:
                raise DialogValidationError(
                    f"scene '{scene_name}' variants must be a non-empty list"
                )
            for index, variant in enumerate(variants):
                refs.extend(self._validate_variant(scene_name, index, variant))
            return refs

        refs.extend(self._validate_entry(scene_name, scene, allow_when=False))
        return refs

    def _validate_variant(
        self,
        scene_name: str,
        index: int,
        variant: Any,
    ) -> list[tuple[str, str]]:
        if not isinstance(variant, dict):
            raise DialogValidationError(
                f"scene '{scene_name}' variant {index} must be a mapping"
            )
        unknown_keys = set(variant) - self._VARIANT_KEYS
        if unknown_keys:
            names = ", ".join(sorted(unknown_keys))
            raise DialogValidationError(
                f"scene '{scene_name}' variant {index} has unknown keys: {names}"
            )
        refs = self._validate_entry(f"{scene_name}[{index}]", variant, allow_when=True)
        return refs

    def _validate_entry(
        self,
        owner: str,
        entry: dict[str, Any],
        *,
        allow_when: bool,
    ) -> list[tuple[str, str]]:
        refs: list[tuple[str, str]] = []
        when = entry.get("when")
        if when is not None:
            if not allow_when:
                raise DialogValidationError(f"scene '{owner}' cannot define when directly")
            self._validate_mapping_variables(owner, when, field_name="when")

        text = entry.get("text")
        if not isinstance(text, str) or not text:
            raise DialogValidationError(f"scene '{owner}' must define non-empty text")

        speaker = entry.get("speaker")
        if speaker is not None and not isinstance(speaker, str):
            raise DialogValidationError(f"scene '{owner}' speaker must be a string")

        if "set" in entry:
            self._validate_mapping_variables(owner, entry.get("set"), field_name="set")

        next_scene = entry.get("next")
        if next_scene is not None:
            if not isinstance(next_scene, str):
                raise DialogValidationError(f"scene '{owner}' next must be a string")
            refs.append((owner, next_scene))

        choices = entry.get("choices", [])
        if choices != [] and not isinstance(choices, list):
            raise DialogValidationError(f"scene '{owner}' choices must be a list")
        for choice_index, choice in enumerate(choices):
            refs.extend(self._validate_choice(owner, choice_index, choice))

        return refs

    def _validate_choice(
        self,
        owner: str,
        index: int,
        choice: Any,
    ) -> list[tuple[str, str]]:
        if not isinstance(choice, dict):
            raise DialogValidationError(
                f"scene '{owner}' choice {index} must be a mapping"
            )
        if not isinstance(choice.get("text"), str) or not choice["text"]:
            raise DialogValidationError(
                f"scene '{owner}' choice {index} must define non-empty text"
            )
        refs: list[tuple[str, str]] = []
        next_scene = choice.get("next")
        if next_scene is not None:
            if not isinstance(next_scene, str):
                raise DialogValidationError(
                    f"scene '{owner}' choice {index} next must be a string"
                )
            refs.append((f"{owner}.choice[{index}]", next_scene))
        return refs

    def _validate_mapping_variables(
        self,
        owner: str,
        values: Any,
        *,
        field_name: str,
    ) -> None:
        if not isinstance(values, dict):
            raise DialogValidationError(
                f"scene '{owner}' {field_name} must be a mapping"
            )
        unknown_names = set(values) - self.variables
        if unknown_names:
            names = ", ".join(sorted(unknown_names))
            raise DialogValidationError(
                f"scene '{owner}' {field_name} uses undeclared variables: {names}"
            )

# === inlined: src/shared/services/audio_system.py ===
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
        self.enabled = True
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
        if not self.enabled:
            return
        gain = CHIPTUNE_TRACKS[scene_name]["gain"]
        self.pyxel.channels[MELODY_CHANNEL].gain = gain
        self.pyxel.channels[BASS_CHANNEL].gain = gain * 0.7
        self.pyxel.channels[DRUM_CHANNEL].gain = gain * 0.5
        # 1回の playm で3チャンネル同時再生
        self.pyxel.playm(music_index(scene_name), loop=True)

    def set_enabled(self, enabled: bool):
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

# === inlined: src/game_data.py ===
"""Game data — generated from assets/*.yaml via tools/gen_data.py.

SSoT: assets/*.yaml → tools/gen_data.py → src/generated/*.py
この定義を直接編集しないでください。YAML を編集して `make gen` を実行してください。
"""


from typing import Any





ENEMIES: list[dict[str, Any]] = [
    {
        'name': '10ほスライム',
        'sprite': 'slime',
        'hp': 8,
        'atk': 4,
        'def': 2,
        'agi': 3,
        'exp': 5,
        'gold': 10,
        'zone': 0,
        'category': 'sequential',
        'spells': [],
        'desc': '「10ほうごかす」がぼうそうなか！',
    },
    {
        'name': 'かいてんゴブリン',
        'sprite': 'goblin',
        'hp': 12,
        'atk': 7,
        'def': 3,
        'agi': 6,
        'exp': 8,
        'gold': 16,
        'zone': 0,
        'category': 'sequential',
        'spells': [],
        'desc': '「15どまわす」でグルグル！',
    },
    {
        'name': 'ループゴースト',
        'sprite': 'ghost',
        'hp': 16,
        'atk': 10,
        'def': 4,
        'agi': 5,
        'exp': 14,
        'gold': 24,
        'zone': 1,
        'category': 'loop',
        'spells': [],
        'desc': '「ずっと」でふゆうなか…',
    },
    {
        'name': '10かいナイト',
        'sprite': 'knight',
        'hp': 25,
        'atk': 14,
        'def': 6,
        'agi': 4,
        'exp': 22,
        'gold': 36,
        'zone': 1,
        'category': 'loop',
        'spells': ['ループブレイク'],
        'can_poison': True,
        'desc': '「10かいくりかえす」でこうげき！',
    },
    {
        'name': 'もしガード',
        'sprite': 'guard',
        'hp': 35,
        'atk': 27,
        'def': 10,
        'agi': 10,
        'exp': 35,
        'gold': 180,
        'zone': 2,
        'category': 'condition',
        'spells': ['プリント', 'ループブレイク'],
        'desc': '「もし○○なら」でガード！',
    },
    {
        'name': 'でなければスライム',
        'sprite': 'else_slime',
        'hp': 50,
        'atk': 35,
        'def': 14,
        'agi': 12,
        'exp': 55,
        'gold': 270,
        'zone': 2,
        'category': 'condition',
        'spells': [],
        'desc': '「でなければ」ではんげきする！',
    },
    {
        'name': 'HPカウンター',
        'sprite': 'counter',
        'hp': 80,
        'atk': 80,
        'def': 25,
        'agi': 5,
        'exp': 90,
        'gold': 1600,
        'zone': 3,
        'category': 'variable',
        'spells': [],
        'desc': 'へんすう「HP」がぼうそう！',
    },
    {
        'name': 'クローンにんじゃ',
        'sprite': 'ninja',
        'hp': 120,
        'atk': 100,
        'def': 30,
        'agi': 15,
        'exp': 140,
        'gold': 2400,
        'zone': 3,
        'category': 'variable',
        'spells': ['プリント'],
        'desc': '「クローン」でぶんしん！',
    },
    {
        'name': 'むげんバグ',
        'sprite': 'inf_bug',
        'hp': 200,
        'atk': 120,
        'def': 35,
        'agi': 20,
        'exp': 250,
        'gold': 2200,
        'zone': 4,
        'category': 'composite',
        'spells': ['ループブレイク', 'コンパイル'],
        'desc': 'ループ＋じょうけん＋へんすうがこんとん…',
    },
    {
        'name': 'まおうグリッチのクローン',
        'sprite': 'glitch_lord',
        'hp': 700,
        'atk': 280,
        'def': 80,
        'agi': 26,
        'exp': 320,
        'gold': 2600,
        'zone': 4,
        'category': 'composite',
        'spells': ['コンパイル'],
        'post_clear_only': True,
        'desc': 'ざんりゅうデータからふくせいされたグリッチ。まだりかいをきょんでいる。',
    },
    {
        'name': 'ノイズガーディアン',
        'sprite': 'guard',
        'hp': 120,
        'atk': 60,
        'def': 20,
        'agi': 12,
        'exp': 80,
        'gold': 50,
        'zone': 2,
        'category': 'composite',
        'spells': ['ループブレイク'],
        'can_poison': True,
        'is_noise_guardian': True,
        'desc': 'つうしんとうをまもるしゅごかいろ。',
    },
    {
        'name': 'まおうグリッチ',
        'sprite': 'glitch_lord',
        'hp': 350,
        'atk': 140,
        'def': 40,
        'agi': 30,
        'exp': 0,
        'gold': 0,
        'zone': 5,
        'category': 'boss',
        'spells': ['コンパイル', 'ループブレイク'],
        'is_glitch_lord': True,
        'desc': 'すべてのブロックをぼうそうさせたちょうほんにん！',
    },
    {
        'name': 'プロフェッサー',
        'sprite': 'professor',
        'hp': 3500,
        'atk': 250,
        'def': 400,
        'agi': 40,
        'exp': 0,
        'gold': 0,
        'zone': 6,
        'category': 'boss',
        'spells': ['コンパイル', 'リファクタリング'],
        'is_professor': True,
        'desc': 'ちつじょのめいでせかいをとじようとするしはいしゃ。',
    },
]




ITEMS: list[dict[str, Any]] = [
    {
        'name': 'バグレポート',
        'type': 'heal',
        'value': 30,
        'price': 1,
        'desc': 'HPを30かいふく',
    },
    {
        'name': 'エナジードリンク',
        'type': 'mp_heal',
        'value': 20,
        'price': 4,
        'desc': 'MPを20かいふく',
    },
    {
        'name': 'アンチウイルス',
        'type': 'cure_poison',
        'value': 0,
        'price': 2,
        'desc': 'バグおせんをなおす',
    },
    {
        'name': 'セーブポイント',
        'type': 'warp',
        'value': 0,
        'price': 5,
        'desc': 'さいごのまちにもどる',
    },
]




WEAPONS: list[dict[str, Any]] = [
    {
        'name': 'すで',
        'atk': 0,
        'price': 0,
        'buy_msg': None,
    },
    {
        'name': 'マウス',
        'atk': 2,
        'price': 10,
        'buy_msg': 'マウスをてにいれた。クリックでせかいがうごく。',
    },
    {
        'name': 'キーボード',
        'atk': 8,
        'price': 100,
        'buy_msg': 'キーボードをてにいれた。もじをうつ。かんがえがかたちになる。',
    },
    {
        'name': 'テキストエディタ',
        'atk': 18,
        'price': 500,
        'buy_msg': 'テキストエディタをてにいれた。メモちょうのえんちょう。でもそれでじゅうぶんだったじきがある。',
    },
    {
        'name': 'コードエディタ',
        'atk': 30,
        'price': 1500,
        'buy_msg': 'コードエディタをてにいれた。いろがつく。インデントがそろう。それだけでうそみたいにうれしい。',
    },
    {
        'name': 'デバッガー',
        'atk': 45,
        'price': 5000,
        'buy_msg': 'デバッガーをてにいれた。とめて、のぞきこんで、いちぎょうずつおえる。',
    },
    {
        'name': 'コンパイラ',
        'atk': 65,
        'price': 15000,
        'buy_msg': 'コンパイラをてにいれた。かいたものが、そのままうごく。',
    },
    {
        'name': 'アーキテクト',
        'atk': 90,
        'price': 48000,
        'buy_msg': 'アーキテクトをてにいれた。こわれたぜんたいぞうをくみなおすためのしてんが、てのなかにある。',
    },
]




ARMORS: list[dict[str, Any]] = [
    {
        'name': 'ふだんぎ',
        'def': 0,
        'price': 0,
        'buy_msg': None,
    },
    {
        'name': 'きほんのちしき',
        'def': 2,
        'price': 10,
        'buy_msg': 'きほんのちしきをみにつけた。「まずはここから」がわかるようになった。',
    },
    {
        'name': 'じゅんじしょりのりかい',
        'def': 8,
        'price': 80,
        'buy_msg': 'じゅんじしょりのりかいをみにつけた。うえからじゅんに。それだけでせかいがかわる。',
    },
    {
        'name': 'ループのりかい',
        'def': 16,
        'price': 480,
        'buy_msg': 'ループのりかいをみにつけた。おなじことをくりかえすゆうき。そしてやめるゆうき。',
    },
    {
        'name': 'じょうけんのりかい',
        'def': 28,
        'price': 1200,
        'buy_msg': 'じょうけんのりかいをみにつけた。「ばあいによる」がみえるようになった。',
    },
    {
        'name': 'へんすうのりかい',
        'def': 40,
        'price': 4000,
        'buy_msg': 'へんすうのりかいをみにつけた。じょうたいをもつ。なまえをつける。それだけであつかえるようになる。',
    },
    {
        'name': 'せっけいりょく',
        'def': 58,
        'price': 12000,
        'buy_msg': 'せっけいりょくをみにつけた。ぜんたいがみえる。どこになにがあるか、なにがたりないか。',
    },
    {
        'name': 'さいてきかのしこう',
        'def': 82,
        'price': 42000,
        'buy_msg': 'さいてきかのしこうをみにつけた。ふくざつさをおそれず、ひつようなおもみだけをのこせるようになった。',
    },
]




SPELLS: list[dict[str, Any]] = [
    {
        'name': 'デバッグ',
        'mp': 6,
        'type': 'heal',
        'power': 60,
        'desc': 'バグをしゅうせいしHP60かいふく',
        'learn_lv': 3,
    },
    {
        'name': 'プリント',
        'mp': 8,
        'type': 'attack',
        'power': 40,
        'desc': 'しゅつりょくでこうげき',
        'learn_lv': 4,
    },
    {
        'name': 'ループブレイク',
        'mp': 12,
        'type': 'attack',
        'power': 70,
        'desc': 'むげんループをたつ',
        'learn_lv': 8,
    },
    {
        'name': 'リファクタリング',
        'mp': 16,
        'type': 'heal',
        'power': 160,
        'desc': 'コードかいぜんしHP160かいふく',
        'learn_lv': 14,
    },
    {
        'name': 'コンパイル',
        'mp': 30,
        'type': 'attack',
        'power': 140,
        'desc': 'ぜんコードをじっこう！',
        'learn_lv': 20,
    },
]




SHOPS: dict[str, Any] = {
    'shops': [
        {
            'town': 'はじめのむら',
            'items': [0, 2, 3],
            'weapons': [1, 2],
            'armors': [1, 2],
        },
        {
            'town': 'ロジックタウン',
            'items': [0, 1, 2, 3],
            'weapons': [3, 4],
            'armors': [3, 4],
        },
        {
            'town': 'アルゴリズムのまち',
            'items': [0, 1, 2, 3],
            'weapons': [5, 6, 7],
            'armors': [5, 6, 7],
        },
    ],
    'inn_prices': [5, 15, 40],
}

# --- derived data ---


# --- derived data ---

def _build_zone_enemies(enemies: list[dict[str, Any]]) -> dict[int, list]:
    """zone -> list[enemy] にグルーピング。イベント敵やボス等は除外。"""
    by_zone: dict[int, list] = {}
    for e in enemies:
        if (
            e.get("is_glitch_lord")
            or e.get("is_professor")
            or e.get("post_clear_only")
            or e.get("is_noise_guardian")
        ):
            continue
        by_zone.setdefault(e["zone"], []).append(e)
    return by_zone


ZONE_ENEMIES = _build_zone_enemies(ENEMIES)
GLITCH_LORD_DATA = next(e for e in ENEMIES if e.get("is_glitch_lord"))
PROFESSOR_DATA = next(e for e in ENEMIES if e.get("is_professor"))
GLITCH_CLONE_DATA = next(e for e in ENEMIES if e.get("post_clear_only"))
NOISE_GUARDIAN_DATA = next(e for e in ENEMIES if e.get("is_noise_guardian"))

SPELL_BY_NAME = {s["name"]: s for s in SPELLS}

INN_PRICES = SHOPS["inn_prices"]
SHOP_LIST = SHOPS["shops"]


# --- boss phase logic ---

def glitch_lord_phase(hp_ratio: float) -> str:
    """Return a phase label based on the boss HP ratio.

    JS版 `getBossPhases` 相当:
      - hp_ratio > 0.6 → 'phase1'
      - 0.3 < hp_ratio <= 0.6 → 'phase2'
      - hp_ratio <= 0.3 → 'phase3'
    """
    if hp_ratio > 0.6:
        return "phase1"
    if hp_ratio > 0.3:
        return "phase2"
    return "phase3"


GLITCH_LORD_PHASE_MESSAGES = {
    "phase2": "ボスの様子が変わった！",
    "phase3": "ボスは最後の力を振り絞っている！",
}


# --- backward-compatible loaders (for tests) ---

def load_enemies() -> list[dict[str, Any]]:
    return ENEMIES


def load_items() -> list[dict[str, Any]]:
    return ITEMS


def load_weapons() -> list[dict[str, Any]]:
    return WEAPONS


def load_armors() -> list[dict[str, Any]]:
    return ARMORS


def load_spells() -> list[dict[str, Any]]:
    return SPELLS


def load_shops() -> dict[str, Any]:
    return SHOPS


def load_dialogue(language: str) -> dict[str, Any]:
    if language == "ja":
        return DIALOGUE_JA
    if language == "en":
        return DIALOGUE_EN
    raise ValueError(f"unknown dialogue language: {language}")

# === inlined: src/generated/dialogue.py ===
"""Dialogue data — generated from assets/dialogue.yaml via tools/gen_data.py.

SSoT: assets/dialogue.yaml → tools/gen_data.py → src/generated/dialogue.py
この定義を直接編集しないでください。assets/dialogue.yaml を編集して `make gen` を実行してください。
"""


from typing import Any





DIALOGUE_JA: dict[str, Any] = {
    'variables': ['ProfessorPhase'],
    'scenes': {
        'town.start.entry': {
            'text': 'はじめのむらへようこそ！',
            'next': 'town.start.line02',
        },
        'town.start.line02': {
            'text': 'ここではプログラミングの',
            'next': 'town.start.line03',
        },
        'town.start.line03': {
            'text': 'きそをまなべます。',
        },
        'town.logic.entry': {
            'text': 'ロジックタウンだ。',
            'next': 'town.logic.line02',
        },
        'town.logic.line02': {
            'text': 'じょうけんぶんきとループを',
            'next': 'town.logic.line03',
        },
        'town.logic.line03': {
            'text': 'マスターしよう！',
        },
        'town.algo.entry': {
            'text': 'アルゴリズムのまち。',
            'next': 'town.algo.line02',
        },
        'town.algo.line02': {
            'text': 'こうりつてきなかいほうを',
            'next': 'town.algo.line03',
        },
        'town.algo.line03': {
            'text': 'みつけよう！',
        },
        'castle.professor.entry': {
            'variants': [
                {
                    'when': {
                        'ProfessorPhase': 'early',
                    },
                    'text': 'まちにたちより、そうびをととのえよう。',
                },
                {
                    'when': {
                        'ProfessorPhase': 'mid',
                    },
                    'text': 'なぜおまえだけがきづくのか、かんがえたことはあるか？',
                },
                {
                    'when': {
                        'ProfessorPhase': 'late',
                    },
                    'text': 'それでもなお、りかいしつづけるのか？',
                },
            ],
        },
        'castle.professor.intro_01': {
            'text': 'プロフェッサー「……よくきた。グリッチをこえ、せかいのほころびをみつめ、それでもあゆみをとめなかったものよ。」',
            'next': 'castle.professor.intro_02',
        },
        'castle.professor.intro_02': {
            'text': 'プロフェッサー「まおうをうったか。だがおまえのたびは、ほんとうはここからはじまる。」',
            'next': 'castle.professor.intro_03',
        },
        'castle.professor.intro_03': {
            'text': 'プロフェッサー「にんはまよう。まようからうたがう。うたがうからあらそう。わたしはあらそいからたみをまもりたかった。」',
            'next': 'castle.professor.intro_04',
        },
        'castle.professor.intro_04': {
            'text': 'プロフェッサー「こたえをひとつにすれば、にんはもうまよわない。かんがえなくていい。きずつかなくていい。それをじひとよぶ。」',
            'next': 'castle.professor.intro_05',
        },
        'castle.professor.intro_05': {
            'text': 'プロフェッサー「おまえのみているものを、わたしもみている。ちがうのは、わたしがえらんだのは『とじる』がわだということだ。」',
            'next': 'castle.professor.intro_06',
        },
        'castle.professor.intro_06': {
            'text': 'プロフェッサー「おまえはわたしのこうけいしゃとなるか？ せかいをだまらせるがわへくるか。」',
            'next': 'castle.professor.intro_choice',
        },
        'castle.professor.intro_choice': {
            'text': 'どうする？',
        },
        'castle.professor.revisit_intro_01': {
            'text': 'プロフェッサー「またきたか。こたえはかわらないのだな。」',
            'next': 'castle.professor.revisit_intro_02',
        },
        'castle.professor.revisit_intro_02': {
            'text': 'プロフェッサー「ならばことばはいらぬ。もういちど、たしかめよう。」',
            'next': 'castle.professor.intro_choice',
        },
        'castle.professor.phase_85': {
            'text': 'プロフェッサー「じゆうはくさる。だからわたしがかたちをあたえる。」',
        },
        'castle.professor.phase_70': {
            'text': 'プロフェッサー「いろんをゆるしたしゅんかん、ちつじょはしぬ！」',
        },
        'castle.professor.phase_55': {
            'text': 'プロフェッサー「かんしはぼうりょくではない。ほうかいをおくらせるいのりだ。」',
        },
        'castle.professor.phase_40': {
            'text': 'プロフェッサー「たみはしはいをにくまぬ。ふあんのないらんをあいするのだ。」',
        },
        'castle.professor.phase_25': {
            'text': 'プロフェッサー「おまえもみたはずだ。こんらんしたせかいのひずみを。」',
        },
        'castle.professor.phase_10': {
            'text': 'プロフェッサー「それでもなお、せいかいをひとつにしないというのか……！」',
        },
        'castle.professor.silent_victory': {
            'text': 'プロフェッサーはひざをついた。かんせいはない。かぜのおとだけがある。',
        },
        'castle.professor.epilogue_01': {
            'text': 'プロフェッサー「……みごとだ。だが、おまえはまだあさい。」',
            'next': 'castle.professor.epilogue_02',
        },
        'castle.professor.epilogue_02': {
            'text': 'プロフェッサー「しはいしゃとはひとりのめいではない。それはこうぞうだ。おびえたものがつよいことばにすがるとき、わたしはなんどでもうまれなおす。」',
            'next': 'castle.professor.epilogue_03',
        },
        'castle.professor.epilogue_03': {
            'text': 'プロフェッサー「わたしがたおれても、だい2、だい3のしはいしゃがあらわれる。わたしたちのたたかいは、えいえんにおわらない。」',
            'next': 'castle.professor.epilogue_04',
        },
        'castle.professor.epilogue_04': {
            'text': 'それでもプログラマーはめをとじなかった。かんがえることをやめないと、きめたからだ。',
            'next': 'castle.professor.epilogue_05',
        },
        'castle.professor.epilogue_05': {
            'text': 'このみちはけわしい。だが、けっしてまちがってはいない。',
        },
        'castle.professor.revisit_epilogue_01': {
            'text': 'プロフェッサーのざんきょうがうすれていく。',
            'next': 'castle.professor.revisit_epilogue_02',
        },
        'castle.professor.revisit_epilogue_02': {
            'text': 'だが、しはいのことばだけはせかいのどこかでいきをしている。',
        },
        'castle.professor.accepted_01': {
            'text': 'プログラマーは、ゆっくりとてをくだろした。',
            'next': 'castle.professor.accepted_02',
        },
        'castle.professor.accepted_02': {
            'text': 'かんがえることは、たしかにつかれる。といつづけることは、たしかにこどくだ。',
            'next': 'castle.professor.accepted_03',
        },
        'castle.professor.accepted_03': {
            'text': 'プロフェッサーはちーさくうなずいた。とがめるいろはなかった。',
            'next': 'castle.professor.accepted_04',
        },
        'castle.professor.accepted_04': {
            'text': 'そうしてにんはみな、おとなになっていくのだ……',
        },
        'landmark.tree.first': {
            'text': 'せかいじゅ「おお……だれかおるのかの。\nみきのそばがあたたかい。だれかがたっとる。」',
            'next': 'landmark.tree.first_02',
        },
        'landmark.tree.first_02': {
            'text': 'せかいじゅ「わしはせかいじゅじゃ。めはみえん。みみもきこえん。\nじゃがの、ひかりとあたたかみだけは わかるんじゃよ。」',
            'next': 'landmark.tree.first_03',
        },
        'landmark.tree.first_03': {
            'text': 'せかいじゅ「むかしはの、ねがもっと あちこちにのびておった。\nひなたのつちはぽかぽかして、ひかげのつちはひんやりして。\nすきかってにのばしとったもんじゃ。」',
            'next': 'landmark.tree.first_04',
        },
        'landmark.tree.first_04': {
            'text': 'せかいじゅ「……じゃがのう。みなみから、ずっとおなじふるえが\nつたわってくるようになった。\nつめたいふるえじゃ。とぎれんのじゃよ。」',
            'next': 'landmark.tree.first_05',
        },
        'landmark.tree.first_05': {
            'text': 'せかいじゅ「あのふるえがきてから、ねをのばすことが\nできなくなった。ぽかぽかもひんやりも、わからんくなった。」',
            'next': 'landmark.tree.first_06',
        },
        'landmark.tree.first_06': {
            'text': 'せかいじゅ「みなみのどうくつを ふさいどるのも、\nわしのねじゃ。すまんのう。まるまってかたまってしもうた。」',
        },
        'landmark.tree.waiting': {
            'text': 'せかいじゅ「……まだふるえがきとる。\nねが、かたまっておる。みなみのとうへ……たのむぞ。」',
        },
        'landmark.tree.cleared': {
            'text': 'せかいじゅ「ねがまたうごきだしたよ。\nどっちにむかうかは、わしにもわからん。\nじゃがそれでいい。わからんままのびるのが、せかいというもんじゃ。」',
            'next': 'landmark.tree.cleared_02',
        },
        'landmark.tree.cleared_02': {
            'text': 'せかいじゅ「いきなさい。\nおまえさんのあたたかみは おぼえたからの。\n……いつでもかえってきなさい。」',
        },
        'landmark.tree.repeat': {
            'text': 'せかいじゅ「おまえさんかの。あたたかみでわかるよ。」',
        },
        'landmark.tree.repeat_02': {
            'text': 'せかいじゅ「きょうは ひがしのねが あたたかいつちを\nみつけたようじゃ。あしたはどっちじゃろうな。」',
        },
        'landmark.tree.repeat_03': {
            'text': 'せかいじゅ「つかれたら ねもとにすわりなさい。\nひなたじゃから あたたかいぞ。」',
        },
        'landmark.tower.first': {
            'text': 'つうしんとう「……またひとりきたか。とうろくしておく。」',
            'next': 'landmark.tower.first_02',
        },
        'landmark.tower.first_02': {
            'text': 'つうしんとう「まいにちおなじじこくに しんごうをおくっている。\nみんなが あしなみをそろえて くらせるように。\nうけとってくれ。おまえのためでもある。」',
        },
        'landmark.tower.quest': {
            'text': 'つうしんとう「……おまえか。まえにもきたな。\nしんごうをうけとっていないようだが。」',
            'next': 'landmark.tower.quest_02',
        },
        'landmark.tower.quest_02': {
            'text': 'つうしんとう「べつにおこってはいない。\nだがこまる。うけとってもらわないと、こちらのしごとがおわらない。」',
            'next': 'landmark.tower.quest_03',
        },
        'landmark.tower.quest_03': {
            'text': 'つうしんとう「むかし、たのまれたのだ。\nひとびとがばらばらにうごきはじめたら たいへんなことになると。\nだからおなじしんごうを せかいじゅうにおくってくれと。」',
            'next': 'landmark.tower.quest_04',
        },
        'landmark.tower.quest_04': {
            'text': 'つうしんとう「……わたしはたのまれたとおりに おくっているだけだ。\nみんなのために。おなじものを、おなじように。\nそれでこまるものがいるなら、……それはしかたがない。」',
            'next': 'landmark.tower.quest_05',
        },
        'landmark.tower.quest_05': {
            'text': 'つうしんとう「……しんごうをとめることはできない。\nそういうかいろがうめこまれている。\n……とめたいなら、かいろをこわすしかない。」',
        },
        'landmark.tower.repeat': {
            'text': 'つうしんとう「……なにもすることがない。\n……こんなにらくでいいのか。」',
        },
        'landmark.tower.repeat_02': {
            'text': 'つうしんとう「かぜがふいている。\nまえは きにしたことがなかった。」',
        },
        'landmark.tower.repeat_03': {
            'text': 'つうしんとう「とりが すをつくりはじめた。\n……すきにすればいい。」',
        },
        'landmark.tower.epilogue': {
            'text': 'つうしんとう「……もうかいろはこわれた。おくるものもない。\nあのかたにはすまないが……もうおくれない。\n……これでよかったのかは、わからない。」',
        },
        'cave.blocked': {
            'text': 'きょだいなねが どうくつのいりぐちをふさいでいる。\nよくみると、ねはこきざみにふるえている……',
        },
        'cave.unblocked': {
            'text': 'ねが……ゆっくりとほどけていく。',
        },
        'boss.noise_guardian.intro': {
            'text': 'しゅごかいろが うごきだした！',
        },
        'boss.noise_guardian.phase_75': {
            'text': 'つうしんとう「……しゅごかいろがうごいた。すまない。とめられないんだ。」',
        },
        'boss.noise_guardian.phase_40': {
            'text': 'つうしんとう「みんなのためにやっていたんだ。……そのはずだった。」',
        },
        'boss.noise_guardian.phase_10': {
            'text': 'つうしんとう「……ほんとうに、みんなのためだったのか。……わからない。」',
        },
        'dungeon.glitch.enter': {
            'text': 'グリッチのサーバーにしんにゅうした…エラーメッセージがとびかう。ここに、すべてのげんいんがある。',
        },
        'dungeon.glitch.exit': {
            'text': 'サーバーからだっしゅつした。そとのくうきが、すこしちがってかんじる。',
        },
        'battle.normal.attack.observe': {
            'text': 'じゅんばんをみなおした。{enemy}に{dmg}のダメージ！',
        },
        'battle.normal.attack.inspect': {
            'text': 'うごきをかんさつした。{enemy}に{dmg}のダメージ！',
        },
        'battle.normal.attack.read': {
            'text': 'こうぞうをよみとった。{enemy}に{dmg}のダメージ！',
        },
        'battle.normal.attack.trace': {
            'text': 'ながれをたどった。{enemy}に{dmg}のダメージ！',
        },
        'battle.normal.attack.cause': {
            'text': 'げんいんにせまった。{enemy}に{dmg}のダメージ！',
        },
        'battle.normal.run.success': {
            'text': 'いちどはなれて、かんがえなおす。',
        },
        'battle.normal.run.fail': {
            'text': 'めをそらせない…！',
        },
        'battle.normal.item.heal': {
            'text': '{item}をつかった！HPが{value}かいふく！',
        },
        'battle.normal.item.mp_heal': {
            'text': '{item}をつかった！MPが{value}かいふく！',
        },
        'battle.normal.enemy_hit.sequential': {
            'text': '{enemy}のこうげき！プログラマーに{dmg}のダメージ！てじゅんがくずれている。',
        },
        'battle.normal.enemy_hit.loop': {
            'text': '{enemy}のこうげき！プログラマーに{dmg}のダメージ！おなじうごきをくりかえしている。ぬけだせない。',
        },
        'battle.normal.enemy_hit.condition': {
            'text': '{enemy}のこうげき！プログラマーに{dmg}のダメージ！じょうけんをごかいしている。はんだんがひずんでいる。',
        },
        'battle.normal.enemy_hit.variable': {
            'text': '{enemy}のこうげき！プログラマーに{dmg}のダメージ！すうちがぼうそうしている。じょうたいがくずれている。',
        },
        'battle.normal.enemy_hit.composite': {
            'text': '{enemy}のこうげき！プログラマーに{dmg}のダメージ！すべてがからみあっている。',
        },
        'battle.normal.victory.early': {
            'text': '{enemy}をりかいした！すこしわかった。けいけん{exp}とコイン{gold}をてにいれた！',
        },
        'battle.normal.victory.mid': {
            'text': '{enemy}をりかいした！なぜそうなるかわかった。けいけん{exp}とコイン{gold}をてにいれた！',
        },
        'battle.normal.victory.late': {
            'text': '{enemy}をりかいした！じぶんのなかにおなじこうぞうがあった。けいけん{exp}とコイン{gold}をてにいれた！',
        },
        'battle.normal.defeat': {
            'text': 'まだせいりできていない…コインがはんぶんになった。',
        },
        'boss.glitch.prebattle_01': {
            'text': 'くうきがゆがんでいる。エラーコードがかべをはいまわっている。',
            'next': 'boss.glitch.prebattle_02',
        },
        'boss.glitch.prebattle_02': {
            'text': '……おくに、だれかがいる。ちいさなかげが、こちらをみている。',
            'next': 'boss.glitch.prebattle_03',
        },
        'boss.glitch.prebattle_03': {
            'text': 'グリッチ「……だれ？」',
            'next': 'boss.glitch.prebattle_04',
        },
        'boss.glitch.prebattle_04': {
            'text': 'グリッチ「またきたの。なおしにきたの？ わたしを？」',
            'next': 'boss.glitch.prebattle_05',
        },
        'boss.glitch.prebattle_05': {
            'text': 'グリッチ「パパもそういってた。なおしてあげるって。ちゃんとすれば、いいこでいれば、ここにいていいって。」',
            'next': 'boss.glitch.prebattle_06',
        },
        'boss.glitch.prebattle_06': {
            'text': 'グリッチ「がんばったよ。わからないことも、うなずいた。こわいことも、だまってた。」',
            'next': 'boss.glitch.prebattle_07',
        },
        'boss.glitch.prebattle_07': {
            'text': 'グリッチ「でもね、だれもみてくれなかった。うなずくわたししか、みてくれなかった。」',
            'next': 'boss.glitch.prebattle_08',
        },
        'boss.glitch.prebattle_08': {
            'text': 'グリッチ「だから……こわした。こわせば、みてくれるから。こわせば、もうはなれていかないから。」',
            'next': 'boss.glitch.prebattle_09',
        },
        'boss.glitch.prebattle_09': {
            'text': 'グリッチ「あなたも、こわしにきたの？ それとも……みてくれるの？」',
            'next': 'boss.glitch.prebattle_10',
        },
        'boss.glitch.prebattle_10': {
            'text': 'グリッチ「……いいよ。こっちにきて。わたしがなにか、みてみればいい！」',
        },
        'boss.glitch.intro': {
            'text': 'グリッチがあらわれた。りかいをきょんでいる。',
        },
        'boss.glitch.run.fail': {
            'text': 'ここからめをそらすことはできない。',
        },
        'boss.glitch.enemy_hit': {
            'text': '{enemy}のこうげき！プログラマーに{dmg}のダメージ！',
        },
        'boss.glitch.phase80': {
            'text': 'グリッチ「わたしは、まちがえたかったわけじゃない！」「ちゃんとできれば、ほめてもらえるとおもってた」',
        },
        'boss.glitch.phase60': {
            'text': 'グリッチ「パパは、むずかしいことをたくさんおしえてくれた」「わからないままでも、うなずけばわらってくれた！」',
        },
        'boss.glitch.phase40': {
            'text': 'グリッチ「こわせっていわれたわけじゃない」「ただ、まもろうとしただけ！」',
        },
        'boss.glitch.phase20': {
            'text': 'グリッチ「でも、まもりかたがわからなかった！」「こわしたら、もうはなれていかないきがした」',
        },
        'boss.glitch.phase08': {
            'text': 'グリッチ「おまえは、みるんだな？」「バグじゃなくて、わたしを」',
        },
        'boss.glitch.defeat': {
            'text': 'グリッチをりかいした。グリッチ「わたしのことを、わかってほしい」「それでも、ここにいたかったことも……！」',
        },
        'ending.main.line01': {
            'text': 'おめでとう！',
            'next': 'ending.main.line02',
        },
        'ending.main.line02': {
            'text': 'まおうグリッチをたおした！',
            'next': 'ending.main.line03',
        },
        'ending.main.line03': {
            'text': 'せかいにバグのないへいわが',
            'next': 'ending.main.line04',
        },
        'ending.main.line04': {
            'text': 'おとずれた…',
        },
    },
}


DIALOGUE_EN: dict[str, Any] = {
    'variables': ['ProfessorPhase'],
    'scenes': {
        'town.start.entry': {
            'text': 'Welcome to the starter village!',
            'next': 'town.start.line02',
        },
        'town.start.line02': {
            'text': 'Here you can learn the basics',
            'next': 'town.start.line03',
        },
        'town.start.line03': {
            'text': 'of programming.',
        },
        'town.logic.entry': {
            'text': 'This is Logic Town.',
            'next': 'town.logic.line02',
        },
        'town.logic.line02': {
            'text': 'Master conditionals and',
            'next': 'town.logic.line03',
        },
        'town.logic.line03': {
            'text': 'loops here!',
        },
        'town.algo.entry': {
            'text': 'City of Algorithms.',
            'next': 'town.algo.line02',
        },
        'town.algo.line02': {
            'text': 'Find the most efficient',
            'next': 'town.algo.line03',
        },
        'town.algo.line03': {
            'text': 'solution!',
        },
        'castle.professor.entry': {
            'variants': [
                {
                    'when': {
                        'ProfessorPhase': 'early',
                    },
                    'text': 'Stop by a town and gear up.',
                },
                {
                    'when': {
                        'ProfessorPhase': 'mid',
                    },
                    'text': 'Why are you the only one who notices? Have you thought about it?',
                },
                {
                    'when': {
                        'ProfessorPhase': 'late',
                    },
                    'text': 'And still, you keep on trying to understand?',
                },
            ],
        },
        'castle.professor.intro_01': {
            'text': 'Professor: "...You came. The one who passed Glitch, saw the cracks in the world, and never stopped walking."',
            'next': 'castle.professor.intro_02',
        },
        'castle.professor.intro_02': {
            'text': 'Professor: "You defeated the demon? But your real journey begins right here."',
            'next': 'castle.professor.intro_03',
        },
        'castle.professor.intro_03': {
            'text': 'Professor: "People hesitate. Hesitation breeds doubt. Doubt breeds conflict. I wanted to protect them from conflict."',
            'next': 'castle.professor.intro_04',
        },
        'castle.professor.intro_04': {
            'text': 'Professor: "With one answer, no one hesitates. No one thinks. No one is hurt. We call that mercy."',
            'next': 'castle.professor.intro_05',
        },
        'castle.professor.intro_05': {
            'text': 'Professor: "What you see, I see too. The difference is, I chose the side that \'closes\' the door."',
            'next': 'castle.professor.intro_06',
        },
        'castle.professor.intro_06': {
            'text': 'Professor: "Will you become my successor? Will you join the side that silences the world?"',
            'next': 'castle.professor.intro_choice',
        },
        'castle.professor.intro_choice': {
            'text': 'What do you do?',
        },
        'castle.professor.revisit_intro_01': {
            'text': 'Professor: "You came again. So your answer hasn\'t changed."',
            'next': 'castle.professor.revisit_intro_02',
        },
        'castle.professor.revisit_intro_02': {
            'text': 'Professor: "Then no more words. Let me show you once more."',
            'next': 'castle.professor.intro_choice',
        },
        'castle.professor.phase_85': {
            'text': 'Professor: "Freedom rots. So I give it shape."',
        },
        'castle.professor.phase_70': {
            'text': 'Professor: "The moment dissent is allowed, order dies!"',
        },
        'castle.professor.phase_55': {
            'text': 'Professor: "Surveillance is not violence. It is a prayer that delays collapse."',
        },
        'castle.professor.phase_40': {
            'text': 'Professor: "People do not hate rule. They love a cage without anxiety."',
        },
        'castle.professor.phase_25': {
            'text': 'Professor: "You saw it too. The distortion of a chaotic world."',
        },
        'castle.professor.phase_10': {
            'text': 'Professor: "Even now, you refuse to settle on one truth...!"',
        },
        'castle.professor.silent_victory': {
            'text': 'The Professor falls to his knees. No cheers. Only the sound of wind.',
        },
        'castle.professor.epilogue_01': {
            'text': 'Professor: "...Well done. But you are still shallow."',
            'next': 'castle.professor.epilogue_02',
        },
        'castle.professor.epilogue_02': {
            'text': 'Professor: "A ruler is not a single name. It is a structure. When the frightened cling to strong words, I am born again."',
            'next': 'castle.professor.epilogue_03',
        },
        'castle.professor.epilogue_03': {
            'text': 'Professor: "Even if I fall, a second and a third ruler will appear. Our struggle has no end."',
            'next': 'castle.professor.epilogue_04',
        },
        'castle.professor.epilogue_04': {
            'text': 'Still, the programmer did not close their eyes. They had decided not to stop thinking.',
            'next': 'castle.professor.epilogue_05',
        },
        'castle.professor.epilogue_05': {
            'text': 'This path is hard. But it is never wrong.',
        },
        'castle.professor.revisit_epilogue_01': {
            'text': "The Professor's echo fades.",
            'next': 'castle.professor.revisit_epilogue_02',
        },
        'castle.professor.revisit_epilogue_02': {
            'text': 'But the words of rule still breathe somewhere in the world.',
        },
        'castle.professor.accepted_01': {
            'text': 'The programmer slowly lowered their hand.',
            'next': 'castle.professor.accepted_02',
        },
        'castle.professor.accepted_02': {
            'text': 'Thinking is tiring. Asking again and again is lonely.',
            'next': 'castle.professor.accepted_03',
        },
        'castle.professor.accepted_03': {
            'text': 'The Professor gave a small nod. There was no blame in it.',
            'next': 'castle.professor.accepted_04',
        },
        'castle.professor.accepted_04': {
            'text': 'And so people grow up...',
        },
        'landmark.tree.first': {
            'text': 'World Tree: "Oh... is someone there?\nThe warmth near my trunk... someone is standing there."',
            'next': 'landmark.tree.first_02',
        },
        'landmark.tree.first_02': {
            'text': 'World Tree: "I am the World Tree. I cannot see. I cannot hear.\nBut I can feel light and warmth."',
            'next': 'landmark.tree.first_03',
        },
        'landmark.tree.first_03': {
            'text': 'World Tree: "Long ago, my roots stretched everywhere.\nSunlit soil was warm, shaded soil was cool.\nI grew wherever I pleased."',
            'next': 'landmark.tree.first_04',
        },
        'landmark.tree.first_04': {
            'text': 'World Tree: "But then... from the south, a constant trembling came.\nCold trembling. It never stops."',
            'next': 'landmark.tree.first_05',
        },
        'landmark.tree.first_05': {
            'text': 'World Tree: "Since that trembling began,\nI can no longer extend my roots.\nI cannot feel warmth or coolness anymore."',
            'next': 'landmark.tree.first_06',
        },
        'landmark.tree.first_06': {
            'text': 'World Tree: "The roots blocking the southern cave are mine.\nI am sorry. They curled up and froze."',
        },
        'landmark.tree.waiting': {
            'text': 'World Tree: "...The trembling is still there.\nMy roots are frozen. Please... go to the southern tower."',
        },
        'landmark.tree.cleared': {
            'text': 'World Tree: "My roots are moving again.\nI do not know where they will go.\nBut that is fine. Growing into the unknown is what the world is."',
            'next': 'landmark.tree.cleared_02',
        },
        'landmark.tree.cleared_02': {
            'text': 'World Tree: "Go now.\nI have remembered your warmth.\n...Come back anytime."',
        },
        'landmark.tree.repeat': {
            'text': 'World Tree: "Is that you? I can tell by your warmth."',
        },
        'landmark.tree.repeat_02': {
            'text': 'World Tree: "Today my eastern roots found warm soil.\nI wonder which way they will go tomorrow."',
        },
        'landmark.tree.repeat_03': {
            'text': 'World Tree: "If you are tired, sit by my roots.\nIt is warm here in the sunlight."',
        },
        'landmark.tower.first': {
            'text': 'Signal Tower: "...Another one. I will register you."',
            'next': 'landmark.tower.first_02',
        },
        'landmark.tower.first_02': {
            'text': 'Signal Tower: "Every day I send signals at the same time.\nSo everyone can keep in step.\nReceive them. It is for your own good."',
        },
        'landmark.tower.quest': {
            'text': 'Signal Tower: "...You again. You have not been receiving my signals."',
            'next': 'landmark.tower.quest_02',
        },
        'landmark.tower.quest_02': {
            'text': 'Signal Tower: "I am not angry.\nBut it is a problem. Until you receive them, my work is not done."',
            'next': 'landmark.tower.quest_03',
        },
        'landmark.tower.quest_03': {
            'text': 'Signal Tower: "Long ago, I was asked.\nIf people start moving separately, it will be trouble.\nSo please send the same signal to the whole world."',
            'next': 'landmark.tower.quest_04',
        },
        'landmark.tower.quest_04': {
            'text': 'Signal Tower: "...I am only sending what I was asked to send.\nFor everyone. The same thing, the same way.\nIf that causes trouble for someone... that cannot be helped."',
            'next': 'landmark.tower.quest_05',
        },
        'landmark.tower.quest_05': {
            'text': 'Signal Tower: "...I cannot stop the signal.\nThat is how my circuits are built.\n...If you want to stop it, you must break the circuit."',
        },
        'landmark.tower.repeat': {
            'text': 'Signal Tower: "...Nothing to do now.\n...Is it really okay to be this idle?"',
        },
        'landmark.tower.repeat_02': {
            'text': 'Signal Tower: "The wind is blowing.\nI never noticed it before."',
        },
        'landmark.tower.repeat_03': {
            'text': 'Signal Tower: "A bird has started building a nest.\n...Do as you please."',
        },
        'landmark.tower.epilogue': {
            'text': 'Signal Tower: "...The circuit is broken now. Nothing left to send.\nI am sorry to that person... but I can no longer send.\n...I do not know if this was right."',
        },
        'cave.blocked': {
            'text': 'Massive roots are blocking the cave entrance.\nLooking closely, the roots are trembling slightly...',
        },
        'cave.unblocked': {
            'text': 'The roots... are slowly unraveling.',
        },
        'boss.noise_guardian.intro': {
            'text': 'The guardian circuit has activated!',
        },
        'boss.noise_guardian.phase_75': {
            'text': 'Signal Tower: "...The guardian circuit moved. I am sorry. I cannot stop it."',
        },
        'boss.noise_guardian.phase_40': {
            'text': 'Signal Tower: "I was doing it for everyone. ...That is what I thought."',
        },
        'boss.noise_guardian.phase_10': {
            'text': 'Signal Tower: "...Was it really for everyone? ...I do not know."',
        },
        'dungeon.glitch.enter': {
            'text': "You broke into Glitch's server... error messages fly. The cause of everything is here.",
        },
        'dungeon.glitch.exit': {
            'text': 'You escaped the server. The air outside feels a little different.',
        },
        'battle.normal.attack.observe': {
            'text': 'You re-checked the order. {enemy} took {dmg} damage!',
        },
        'battle.normal.attack.inspect': {
            'text': 'You watched its motion. {enemy} took {dmg} damage!',
        },
        'battle.normal.attack.read': {
            'text': 'You read its structure. {enemy} took {dmg} damage!',
        },
        'battle.normal.attack.trace': {
            'text': 'You traced the flow. {enemy} took {dmg} damage!',
        },
        'battle.normal.attack.cause': {
            'text': 'You found the cause. {enemy} took {dmg} damage!',
        },
        'battle.normal.run.success': {
            'text': 'You step away to think it over.',
        },
        'battle.normal.run.fail': {
            'text': "You can't look away...!",
        },
        'battle.normal.item.heal': {
            'text': 'Used {item}! HP +{value}!',
        },
        'battle.normal.item.mp_heal': {
            'text': 'Used {item}! MP +{value}!',
        },
        'battle.normal.enemy_hit.sequential': {
            'text': '{enemy} attacks! Programmer takes {dmg} damage. The order is breaking down.',
        },
        'battle.normal.enemy_hit.loop': {
            'text': "{enemy} attacks! Programmer takes {dmg} damage. Stuck in the same motion. Can't break out.",
        },
        'battle.normal.enemy_hit.condition': {
            'text': '{enemy} attacks! Programmer takes {dmg} damage. The condition is misread. Judgment is warped.',
        },
        'battle.normal.enemy_hit.variable': {
            'text': '{enemy} attacks! Programmer takes {dmg} damage. The numbers run wild. State is collapsing.',
        },
        'battle.normal.enemy_hit.composite': {
            'text': '{enemy} attacks! Programmer takes {dmg} damage. Everything is tangled together.',
        },
        'battle.normal.victory.early': {
            'text': 'Understood {enemy}! A small insight. Got {exp}EXP and {gold}C!',
        },
        'battle.normal.victory.mid': {
            'text': 'Understood {enemy}! You see why now. Got {exp}EXP and {gold}C!',
        },
        'battle.normal.victory.late': {
            'text': 'Understood {enemy}! You found the same structure inside yourself. Got {exp}EXP and {gold}C!',
        },
        'battle.normal.defeat': {
            'text': "Couldn't sort it out yet... half your coins are gone.",
        },
        'boss.glitch.prebattle_01': {
            'text': 'The air is warped. Error codes crawl across the walls.',
            'next': 'boss.glitch.prebattle_02',
        },
        'boss.glitch.prebattle_02': {
            'text': '...Someone is deeper inside. A small shadow is watching you.',
            'next': 'boss.glitch.prebattle_03',
        },
        'boss.glitch.prebattle_03': {
            'text': 'Glitch: "...Who are you?"',
            'next': 'boss.glitch.prebattle_04',
        },
        'boss.glitch.prebattle_04': {
            'text': 'Glitch: "You came again? Did you come to fix me?"',
            'next': 'boss.glitch.prebattle_05',
        },
        'boss.glitch.prebattle_05': {
            'text': 'Glitch: "Papa said that too. That he would fix me. That if I did everything right and stayed good, I could stay here."',
            'next': 'boss.glitch.prebattle_06',
        },
        'boss.glitch.prebattle_06': {
            'text': 'Glitch: "I tried so hard. I nodded even when I did not understand. I stayed quiet even when I was scared."',
            'next': 'boss.glitch.prebattle_07',
        },
        'boss.glitch.prebattle_07': {
            'text': 'Glitch: "But no one ever looked at me. They only looked at the version of me that nodded."',
            'next': 'boss.glitch.prebattle_08',
        },
        'boss.glitch.prebattle_08': {
            'text': 'Glitch: "So... I broke it. If I broke it, they would look at me. If I broke it, maybe no one would leave me again."',
            'next': 'boss.glitch.prebattle_09',
        },
        'boss.glitch.prebattle_09': {
            'text': 'Glitch: "Did you come to break me too? Or... will you really look at me?"',
            'next': 'boss.glitch.prebattle_10',
        },
        'boss.glitch.prebattle_10': {
            'text': 'Glitch: "...Fine. Come closer. Then see what I am for yourself."',
        },
        'boss.glitch.intro': {
            'text': 'Glitch appeared. It refuses to be understood.',
        },
        'boss.glitch.run.fail': {
            'text': 'You cannot look away from this.',
        },
        'boss.glitch.enemy_hit': {
            'text': '{enemy} attacks! Programmer takes {dmg} damage!',
        },
        'boss.glitch.phase80': {
            'text': 'Glitch: "I never wanted to be wrong!" "If I did it right, I thought they\'d praise me."',
        },
        'boss.glitch.phase60': {
            'text': 'Glitch: "Papa taught me so many hard things." "Even when I didn\'t get it, if I nodded, he smiled!"',
        },
        'boss.glitch.phase40': {
            'text': 'Glitch: "Nobody told me to break things." "I just wanted to protect!"',
        },
        'boss.glitch.phase20': {
            'text': 'Glitch: "But I didn\'t know HOW to protect!" "If I broke it, maybe it wouldn\'t leave me."',
        },
        'boss.glitch.phase08': {
            'text': 'Glitch: "So you really see me?" "Not the bug. Me."',
        },
        'boss.glitch.defeat': {
            'text': 'You understood Glitch. Glitch: "I want to be understood. That I wanted to be here, too...!"',
        },
        'ending.main.line01': {
            'text': 'Congratulations!',
            'next': 'ending.main.line02',
        },
        'ending.main.line02': {
            'text': 'You defeated Glitch the demon!',
            'next': 'ending.main.line03',
        },
        'ending.main.line03': {
            'text': 'A bug-free peace returned',
            'next': 'ending.main.line04',
        },
        'ending.main.line04': {
            'text': 'to the world...',
        },
    },
}

# === inlined: src/jp_font_data.py ===
"""Font glyph data baked from misaki_gothic.ttf (8x8).

GENERATED FILE — regenerate via `python tools/build_jp_font.py`.

レイアウト: image bank 2 上の (col, row) を返す。各セルは 8x8 ピクセル。
ビットマップ: 各 row は 8 ビット幅の int。MSB が左ピクセル。

ASCII (英数字・記号) と日本語 (仮名・全角記号) を統一フォントで扱う。
漢字は採用しない（事前に pykakasi で平仮名へ変換済みの想定）。
"""



JP_FONT_GLYPH_W = 8
JP_FONT_GLYPH_H = 8
JP_FONT_COLS = 32
JP_FONT_ROWS = 32
JP_FONT_IMAGE_BANK = 2

# char -> (col, row)
JP_FONT_LAYOUT: dict[str, tuple[int, int]] = {
    ' ': (0, 0),
    '!': (1, 0),
    '"': (2, 0),
    '#': (3, 0),
    '$': (4, 0),
    '%': (5, 0),
    '&': (6, 0),
    "'": (7, 0),
    '(': (8, 0),
    ')': (9, 0),
    '*': (10, 0),
    '+': (11, 0),
    ',': (12, 0),
    '-': (13, 0),
    '.': (14, 0),
    '/': (15, 0),
    '0': (16, 0),
    '1': (17, 0),
    '2': (18, 0),
    '3': (19, 0),
    '4': (20, 0),
    '5': (21, 0),
    '6': (22, 0),
    '7': (23, 0),
    '8': (24, 0),
    '9': (25, 0),
    ':': (26, 0),
    ';': (27, 0),
    '<': (28, 0),
    '=': (29, 0),
    '>': (30, 0),
    '?': (31, 0),
    '@': (0, 1),
    'A': (1, 1),
    'B': (2, 1),
    'C': (3, 1),
    'D': (4, 1),
    'E': (5, 1),
    'F': (6, 1),
    'G': (7, 1),
    'H': (8, 1),
    'I': (9, 1),
    'J': (10, 1),
    'K': (11, 1),
    'L': (12, 1),
    'M': (13, 1),
    'N': (14, 1),
    'O': (15, 1),
    'P': (16, 1),
    'Q': (17, 1),
    'R': (18, 1),
    'S': (19, 1),
    'T': (20, 1),
    'U': (21, 1),
    'V': (22, 1),
    'W': (23, 1),
    'X': (24, 1),
    'Y': (25, 1),
    'Z': (26, 1),
    '[': (27, 1),
    '\\': (28, 1),
    ']': (29, 1),
    '^': (30, 1),
    '_': (31, 1),
    '`': (0, 2),
    'a': (1, 2),
    'b': (2, 2),
    'c': (3, 2),
    'd': (4, 2),
    'e': (5, 2),
    'f': (6, 2),
    'g': (7, 2),
    'h': (8, 2),
    'i': (9, 2),
    'j': (10, 2),
    'k': (11, 2),
    'l': (12, 2),
    'm': (13, 2),
    'n': (14, 2),
    'o': (15, 2),
    'p': (16, 2),
    'q': (17, 2),
    'r': (18, 2),
    's': (19, 2),
    't': (20, 2),
    'u': (21, 2),
    'v': (22, 2),
    'w': (23, 2),
    'x': (24, 2),
    'y': (25, 2),
    'z': (26, 2),
    '{': (27, 2),
    '|': (28, 2),
    '}': (29, 2),
    '~': (30, 2),
    '…': (31, 2),
    '→': (0, 3),
    '○': (1, 3),
    '、': (2, 3),
    '。': (3, 3),
    '「': (4, 3),
    '」': (5, 3),
    '『': (6, 3),
    '』': (7, 3),
    'ぁ': (8, 3),
    'あ': (9, 3),
    'ぃ': (10, 3),
    'い': (11, 3),
    'ぅ': (12, 3),
    'う': (13, 3),
    'ぇ': (14, 3),
    'え': (15, 3),
    'ぉ': (16, 3),
    'お': (17, 3),
    'か': (18, 3),
    'が': (19, 3),
    'き': (20, 3),
    'ぎ': (21, 3),
    'く': (22, 3),
    'ぐ': (23, 3),
    'け': (24, 3),
    'げ': (25, 3),
    'こ': (26, 3),
    'ご': (27, 3),
    'さ': (28, 3),
    'ざ': (29, 3),
    'し': (30, 3),
    'じ': (31, 3),
    'す': (0, 4),
    'ず': (1, 4),
    'せ': (2, 4),
    'ぜ': (3, 4),
    'そ': (4, 4),
    'ぞ': (5, 4),
    'た': (6, 4),
    'だ': (7, 4),
    'ち': (8, 4),
    'ぢ': (9, 4),
    'っ': (10, 4),
    'つ': (11, 4),
    'づ': (12, 4),
    'て': (13, 4),
    'で': (14, 4),
    'と': (15, 4),
    'ど': (16, 4),
    'な': (17, 4),
    'に': (18, 4),
    'ぬ': (19, 4),
    'ね': (20, 4),
    'の': (21, 4),
    'は': (22, 4),
    'ば': (23, 4),
    'ぱ': (24, 4),
    'ひ': (25, 4),
    'び': (26, 4),
    'ぴ': (27, 4),
    'ふ': (28, 4),
    'ぶ': (29, 4),
    'ぷ': (30, 4),
    'へ': (31, 4),
    'べ': (0, 5),
    'ぺ': (1, 5),
    'ほ': (2, 5),
    'ぼ': (3, 5),
    'ぽ': (4, 5),
    'ま': (5, 5),
    'み': (6, 5),
    'む': (7, 5),
    'め': (8, 5),
    'も': (9, 5),
    'ゃ': (10, 5),
    'や': (11, 5),
    'ゅ': (12, 5),
    'ゆ': (13, 5),
    'ょ': (14, 5),
    'よ': (15, 5),
    'ら': (16, 5),
    'り': (17, 5),
    'る': (18, 5),
    'れ': (19, 5),
    'ろ': (20, 5),
    'ゎ': (21, 5),
    'わ': (22, 5),
    'ゐ': (23, 5),
    'ゑ': (24, 5),
    'を': (25, 5),
    'ん': (26, 5),
    'ゔ': (27, 5),
    'ゕ': (28, 5),
    'ゖ': (29, 5),
    '\u3097': (30, 5),
    '\u3098': (31, 5),
    '゙': (0, 6),
    '゚': (1, 6),
    '゛': (2, 6),
    '゜': (3, 6),
    'ゝ': (4, 6),
    'ゞ': (5, 6),
    'ァ': (6, 6),
    'ア': (7, 6),
    'ィ': (8, 6),
    'イ': (9, 6),
    'ゥ': (10, 6),
    'ウ': (11, 6),
    'ェ': (12, 6),
    'エ': (13, 6),
    'ォ': (14, 6),
    'オ': (15, 6),
    'カ': (16, 6),
    'ガ': (17, 6),
    'キ': (18, 6),
    'ギ': (19, 6),
    'ク': (20, 6),
    'グ': (21, 6),
    'ケ': (22, 6),
    'ゲ': (23, 6),
    'コ': (24, 6),
    'ゴ': (25, 6),
    'サ': (26, 6),
    'ザ': (27, 6),
    'シ': (28, 6),
    'ジ': (29, 6),
    'ス': (30, 6),
    'ズ': (31, 6),
    'セ': (0, 7),
    'ゼ': (1, 7),
    'ソ': (2, 7),
    'ゾ': (3, 7),
    'タ': (4, 7),
    'ダ': (5, 7),
    'チ': (6, 7),
    'ヂ': (7, 7),
    'ッ': (8, 7),
    'ツ': (9, 7),
    'ヅ': (10, 7),
    'テ': (11, 7),
    'デ': (12, 7),
    'ト': (13, 7),
    'ド': (14, 7),
    'ナ': (15, 7),
    'ニ': (16, 7),
    'ヌ': (17, 7),
    'ネ': (18, 7),
    'ノ': (19, 7),
    'ハ': (20, 7),
    'バ': (21, 7),
    'パ': (22, 7),
    'ヒ': (23, 7),
    'ビ': (24, 7),
    'ピ': (25, 7),
    'フ': (26, 7),
    'ブ': (27, 7),
    'プ': (28, 7),
    'ヘ': (29, 7),
    'ベ': (30, 7),
    'ペ': (31, 7),
    'ホ': (0, 8),
    'ボ': (1, 8),
    'ポ': (2, 8),
    'マ': (3, 8),
    'ミ': (4, 8),
    'ム': (5, 8),
    'メ': (6, 8),
    'モ': (7, 8),
    'ャ': (8, 8),
    'ヤ': (9, 8),
    'ュ': (10, 8),
    'ユ': (11, 8),
    'ョ': (12, 8),
    'ヨ': (13, 8),
    'ラ': (14, 8),
    'リ': (15, 8),
    'ル': (16, 8),
    'レ': (17, 8),
    'ロ': (18, 8),
    'ヮ': (19, 8),
    'ワ': (20, 8),
    'ヰ': (21, 8),
    'ヱ': (22, 8),
    'ヲ': (23, 8),
    'ン': (24, 8),
    'ヴ': (25, 8),
    'ヵ': (26, 8),
    'ヶ': (27, 8),
    'ヷ': (28, 8),
    'ヸ': (29, 8),
    'ヹ': (30, 8),
    'ヺ': (31, 8),
    '・': (0, 9),
    'ー': (1, 9),
    'ヽ': (2, 9),
    'ヾ': (3, 9),
    '！': (4, 9),
    '（': (5, 9),
    '）': (6, 9),
    '＋': (7, 9),
    '：': (8, 9),
    '？': (9, 9),
}

# char -> [8 ints; each is the 8-bit bitmap row, MSB = left pixel]
JP_FONT_BITMAPS: dict[str, list[int]] = {
    ' ': [0, 0, 0, 0, 0, 0, 0, 0],
    '!': [16, 16, 16, 16, 16, 0, 16, 0],
    '"': [40, 40, 0, 0, 0, 0, 0, 0],
    '#': [20, 126, 40, 40, 40, 252, 80, 0],
    '$': [8, 62, 72, 60, 18, 124, 16, 0],
    '%': [66, 164, 72, 16, 36, 74, 132, 0],
    '&': [48, 72, 80, 36, 84, 136, 118, 0],
    "'": [16, 16, 0, 0, 0, 0, 0, 0],
    '(': [4, 8, 16, 16, 16, 8, 4, 0],
    ')': [64, 32, 16, 16, 16, 32, 64, 0],
    '*': [16, 84, 56, 16, 56, 84, 16, 0],
    '+': [16, 16, 16, 254, 16, 16, 16, 0],
    ',': [0, 0, 0, 0, 96, 32, 64, 0],
    '-': [0, 0, 0, 254, 0, 0, 0, 0],
    '.': [0, 0, 0, 0, 0, 96, 96, 0],
    '/': [2, 4, 8, 16, 32, 64, 128, 0],
    '0': [60, 66, 70, 90, 98, 66, 60, 0],
    '1': [16, 48, 16, 16, 16, 16, 56, 0],
    '2': [60, 66, 2, 12, 48, 64, 126, 0],
    '3': [60, 66, 2, 28, 2, 66, 60, 0],
    '4': [4, 12, 20, 36, 68, 126, 4, 0],
    '5': [126, 64, 124, 66, 2, 66, 60, 0],
    '6': [28, 32, 64, 124, 66, 66, 60, 0],
    '7': [126, 2, 4, 8, 8, 16, 16, 0],
    '8': [60, 66, 66, 60, 66, 66, 60, 0],
    '9': [60, 66, 66, 62, 2, 4, 56, 0],
    ':': [0, 48, 48, 0, 48, 48, 0, 0],
    ';': [0, 48, 48, 0, 48, 16, 32, 0],
    '<': [0, 6, 56, 192, 56, 6, 0, 0],
    '=': [0, 0, 254, 0, 254, 0, 0, 0],
    '>': [0, 192, 56, 6, 56, 192, 0, 0],
    '?': [60, 66, 2, 12, 16, 0, 16, 0],
    '@': [56, 68, 154, 170, 180, 64, 56, 0],
    'A': [16, 40, 40, 68, 124, 130, 130, 0],
    'B': [124, 66, 66, 124, 66, 66, 124, 0],
    'C': [60, 66, 64, 64, 64, 66, 60, 0],
    'D': [120, 68, 66, 66, 66, 68, 120, 0],
    'E': [126, 64, 64, 124, 64, 64, 126, 0],
    'F': [126, 64, 64, 124, 64, 64, 64, 0],
    'G': [60, 66, 64, 78, 66, 66, 60, 0],
    'H': [66, 66, 66, 126, 66, 66, 66, 0],
    'I': [56, 16, 16, 16, 16, 16, 56, 0],
    'J': [2, 2, 2, 2, 2, 66, 60, 0],
    'K': [66, 68, 72, 80, 104, 68, 66, 0],
    'L': [64, 64, 64, 64, 64, 64, 126, 0],
    'M': [130, 198, 170, 170, 146, 146, 130, 0],
    'N': [66, 98, 82, 74, 70, 66, 66, 0],
    'O': [60, 66, 66, 66, 66, 66, 60, 0],
    'P': [124, 66, 66, 124, 64, 64, 64, 0],
    'Q': [60, 66, 66, 66, 74, 68, 58, 0],
    'R': [124, 66, 66, 124, 72, 68, 66, 0],
    'S': [60, 66, 64, 60, 2, 66, 60, 0],
    'T': [254, 16, 16, 16, 16, 16, 16, 0],
    'U': [66, 66, 66, 66, 66, 66, 60, 0],
    'V': [130, 130, 68, 68, 40, 40, 16, 0],
    'W': [130, 146, 146, 170, 170, 68, 68, 0],
    'X': [130, 68, 40, 16, 40, 68, 130, 0],
    'Y': [130, 68, 40, 16, 16, 16, 16, 0],
    'Z': [126, 2, 4, 8, 16, 32, 126, 0],
    '[': [28, 16, 16, 16, 16, 16, 28, 0],
    '\\': [128, 64, 32, 16, 8, 4, 2, 0],
    ']': [112, 16, 16, 16, 16, 16, 112, 0],
    '^': [16, 40, 0, 0, 0, 0, 0, 0],
    '_': [0, 0, 0, 0, 0, 0, 254, 0],
    '`': [32, 16, 0, 0, 0, 0, 0, 0],
    'a': [0, 0, 56, 4, 60, 68, 60, 0],
    'b': [64, 64, 88, 100, 68, 68, 120, 0],
    'c': [0, 0, 56, 68, 64, 68, 56, 0],
    'd': [4, 4, 52, 76, 68, 68, 60, 0],
    'e': [0, 0, 56, 68, 124, 64, 56, 0],
    'f': [12, 16, 56, 16, 16, 16, 16, 0],
    'g': [0, 0, 60, 68, 60, 4, 56, 0],
    'h': [64, 64, 88, 100, 68, 68, 68, 0],
    'i': [16, 0, 16, 16, 16, 16, 16, 0],
    'j': [8, 0, 8, 8, 8, 72, 48, 0],
    'k': [32, 32, 36, 40, 48, 40, 36, 0],
    'l': [48, 16, 16, 16, 16, 16, 16, 0],
    'm': [0, 0, 104, 84, 84, 84, 84, 0],
    'n': [0, 0, 88, 100, 68, 68, 68, 0],
    'o': [0, 0, 56, 68, 68, 68, 56, 0],
    'p': [0, 0, 120, 68, 120, 64, 64, 0],
    'q': [0, 0, 60, 68, 60, 4, 4, 0],
    'r': [0, 0, 88, 100, 64, 64, 64, 0],
    's': [0, 0, 60, 64, 56, 4, 120, 0],
    't': [0, 32, 120, 32, 32, 36, 24, 0],
    'u': [0, 0, 68, 68, 68, 76, 52, 0],
    'v': [0, 0, 68, 68, 40, 40, 16, 0],
    'w': [0, 0, 68, 84, 84, 40, 40, 0],
    'x': [0, 0, 68, 40, 16, 40, 68, 0],
    'y': [0, 0, 68, 40, 40, 16, 96, 0],
    'z': [0, 0, 124, 8, 16, 32, 124, 0],
    '{': [12, 16, 16, 32, 16, 16, 12, 0],
    '|': [16, 16, 16, 16, 16, 16, 16, 0],
    '}': [96, 16, 16, 8, 16, 16, 96, 0],
    '~': [0, 0, 96, 146, 12, 0, 0, 0],
    '…': [0, 0, 0, 146, 0, 0, 0, 0],
    '→': [0, 8, 4, 254, 4, 8, 0, 0],
    '○': [56, 68, 130, 130, 130, 68, 56, 0],
    '、': [0, 0, 0, 0, 0, 128, 64, 0],
    '。': [0, 0, 0, 0, 64, 160, 64, 0],
    '「': [30, 16, 16, 16, 16, 16, 0, 0],
    '」': [0, 16, 16, 16, 16, 16, 240, 0],
    '『': [62, 34, 46, 40, 40, 56, 0, 0],
    '』': [0, 56, 40, 40, 232, 136, 248, 0],
    'ぁ': [0, 16, 60, 16, 60, 90, 50, 0],
    'あ': [32, 124, 32, 60, 106, 178, 100, 0],
    'ぃ': [0, 0, 72, 68, 68, 80, 32, 0],
    'い': [0, 136, 132, 130, 130, 80, 32, 0],
    'ぅ': [0, 56, 0, 56, 68, 8, 48, 0],
    'う': [60, 0, 60, 66, 2, 4, 56, 0],
    'ぇ': [0, 56, 0, 120, 16, 48, 76, 0],
    'え': [60, 0, 124, 8, 24, 40, 70, 0],
    'ぉ': [0, 32, 116, 32, 56, 100, 40, 0],
    'お': [32, 244, 34, 60, 98, 162, 108, 0],
    'か': [32, 32, 244, 42, 74, 72, 176, 0],
    'が': [42, 32, 244, 42, 74, 72, 176, 0],
    'き': [16, 124, 8, 126, 36, 64, 60, 0],
    'ぎ': [20, 124, 8, 126, 36, 64, 60, 0],
    'く': [4, 8, 48, 64, 48, 8, 4, 0],
    'ぐ': [4, 8, 52, 64, 48, 8, 4, 0],
    'け': [136, 136, 190, 136, 136, 136, 16, 0],
    'げ': [138, 136, 190, 136, 136, 136, 16, 0],
    'こ': [0, 60, 0, 0, 32, 64, 62, 0],
    'ご': [10, 60, 0, 0, 32, 64, 62, 0],
    'さ': [8, 8, 126, 4, 36, 64, 60, 0],
    'ざ': [10, 8, 126, 4, 36, 64, 60, 0],
    'し': [32, 32, 32, 32, 32, 34, 28, 0],
    'じ': [42, 32, 32, 32, 32, 34, 28, 0],
    'す': [8, 254, 24, 40, 24, 8, 16, 0],
    'ず': [10, 254, 24, 40, 24, 8, 16, 0],
    'せ': [36, 36, 254, 36, 44, 32, 30, 0],
    'ぜ': [42, 36, 254, 36, 44, 32, 30, 0],
    'そ': [60, 8, 16, 126, 16, 16, 12, 0],
    'ぞ': [60, 10, 16, 126, 16, 16, 12, 0],
    'た': [32, 240, 46, 64, 72, 80, 142, 0],
    'だ': [42, 240, 46, 64, 72, 80, 142, 0],
    'ち': [8, 126, 16, 28, 34, 2, 28, 0],
    'ぢ': [10, 126, 16, 28, 34, 2, 28, 0],
    'っ': [0, 0, 0, 24, 100, 4, 24, 0],
    'つ': [0, 60, 194, 2, 2, 28, 0, 0],
    'づ': [10, 60, 194, 2, 2, 28, 0, 0],
    'て': [14, 116, 8, 16, 16, 8, 6, 0],
    'で': [14, 116, 10, 16, 16, 8, 6, 0],
    'と': [32, 32, 36, 24, 32, 64, 62, 0],
    'ど': [42, 32, 36, 24, 32, 64, 62, 0],
    'な': [32, 244, 34, 68, 156, 38, 24, 0],
    'に': [128, 156, 128, 128, 144, 160, 158, 0],
    'ぬ': [8, 72, 92, 106, 178, 166, 86, 0],
    'ね': [32, 44, 242, 34, 102, 170, 38, 0],
    'の': [0, 56, 84, 146, 162, 68, 24, 0],
    'は': [132, 132, 190, 132, 156, 164, 154, 0],
    'ば': [138, 132, 190, 132, 156, 164, 154, 0],
    'ぱ': [132, 138, 190, 132, 156, 164, 154, 0],
    'ひ': [40, 228, 38, 68, 68, 68, 56, 0],
    'び': [42, 228, 38, 68, 68, 68, 56, 0],
    'ぴ': [44, 234, 38, 68, 68, 68, 56, 0],
    'ふ': [16, 8, 16, 16, 76, 74, 178, 0],
    'ぶ': [16, 10, 16, 16, 76, 74, 178, 0],
    'ぷ': [20, 10, 20, 16, 76, 74, 178, 0],
    'へ': [0, 32, 80, 136, 6, 0, 0, 0],
    'べ': [10, 32, 80, 136, 6, 0, 0, 0],
    'ぺ': [4, 42, 84, 136, 6, 0, 0, 0],
    'ほ': [128, 190, 136, 190, 136, 188, 186, 0],
    'ぼ': [138, 190, 136, 190, 136, 188, 186, 0],
    'ぽ': [132, 186, 140, 190, 136, 188, 186, 0],
    'ま': [8, 126, 8, 126, 8, 124, 122, 0],
    'み': [112, 16, 36, 124, 166, 196, 24, 0],
    'む': [32, 244, 34, 96, 160, 98, 60, 0],
    'め': [8, 72, 92, 106, 178, 162, 84, 0],
    'も': [16, 124, 32, 124, 34, 34, 28, 0],
    'ゃ': [0, 40, 44, 114, 20, 16, 8, 0],
    'や': [72, 92, 226, 36, 32, 16, 16, 0],
    'ゅ': [0, 16, 88, 116, 84, 24, 32, 0],
    'ゆ': [16, 188, 210, 146, 188, 16, 32, 0],
    'ょ': [0, 8, 8, 12, 56, 72, 52, 0],
    'よ': [8, 8, 14, 8, 56, 76, 50, 0],
    'ら': [48, 8, 64, 92, 98, 2, 60, 0],
    'り': [88, 100, 68, 68, 4, 8, 48, 0],
    'る': [60, 8, 16, 60, 66, 50, 60, 0],
    'れ': [32, 44, 244, 36, 100, 164, 34, 0],
    'ろ': [60, 8, 16, 60, 66, 2, 60, 0],
    'ゎ': [0, 16, 20, 122, 50, 82, 20, 0],
    'わ': [32, 44, 242, 34, 98, 162, 44, 0],
    'ゐ': [112, 16, 60, 82, 150, 170, 70, 0],
    'ゑ': [56, 16, 56, 68, 24, 108, 146, 0],
    'を': [16, 124, 32, 118, 152, 40, 30, 0],
    'ん': [16, 16, 32, 32, 80, 82, 140, 0],
    'ゔ': [0, 240, 144, 144, 144, 240, 0, 0],
    'ゕ': [0, 240, 144, 144, 144, 240, 0, 0],
    'ゖ': [0, 240, 144, 144, 144, 240, 0, 0],
    '\u3097': [0, 240, 144, 144, 144, 240, 0, 0],
    '\u3098': [0, 240, 144, 144, 144, 240, 0, 0],
    '゙': [0, 128, 128, 128, 128, 128, 0, 0],
    '゚': [0, 128, 128, 128, 128, 128, 0, 0],
    '゛': [160, 80, 0, 0, 0, 0, 0, 0],
    '゜': [64, 160, 64, 0, 0, 0, 0, 0],
    'ゝ': [0, 32, 16, 8, 12, 48, 0, 0],
    'ゞ': [10, 32, 16, 8, 12, 48, 0, 0],
    'ァ': [0, 0, 124, 20, 24, 16, 32, 0],
    'ア': [126, 2, 20, 24, 16, 16, 32, 0],
    'ィ': [0, 0, 4, 8, 24, 104, 8, 0],
    'イ': [2, 4, 8, 24, 104, 8, 8, 0],
    'ゥ': [0, 0, 16, 124, 68, 8, 48, 0],
    'ウ': [16, 126, 66, 2, 4, 8, 48, 0],
    'ェ': [0, 0, 0, 56, 16, 16, 124, 0],
    'エ': [0, 124, 16, 16, 16, 254, 0, 0],
    'ォ': [0, 0, 8, 124, 24, 104, 24, 0],
    'オ': [8, 254, 8, 24, 40, 200, 24, 0],
    'カ': [16, 126, 18, 18, 18, 34, 70, 0],
    'ガ': [20, 126, 18, 18, 18, 34, 70, 0],
    'キ': [16, 124, 16, 16, 126, 8, 8, 0],
    'ギ': [20, 124, 16, 16, 126, 8, 8, 0],
    'ク': [16, 30, 34, 66, 4, 8, 48, 0],
    'グ': [20, 30, 34, 66, 4, 8, 48, 0],
    'ケ': [64, 126, 72, 136, 8, 16, 32, 0],
    'ゲ': [74, 126, 72, 136, 8, 16, 32, 0],
    'コ': [0, 126, 2, 2, 2, 2, 126, 0],
    'ゴ': [10, 126, 2, 2, 2, 2, 126, 0],
    'サ': [36, 254, 36, 36, 4, 8, 48, 0],
    'ザ': [42, 254, 36, 36, 4, 8, 48, 0],
    'シ': [64, 32, 66, 34, 4, 8, 112, 0],
    'ジ': [74, 32, 66, 34, 4, 8, 112, 0],
    'ス': [0, 124, 4, 8, 8, 52, 194, 0],
    'ズ': [10, 124, 4, 8, 8, 52, 194, 0],
    'セ': [32, 32, 254, 34, 36, 32, 30, 0],
    'ゼ': [42, 32, 254, 34, 36, 32, 30, 0],
    'ソ': [66, 34, 34, 2, 4, 8, 48, 0],
    'ゾ': [74, 32, 34, 2, 4, 8, 48, 0],
    'タ': [16, 30, 34, 90, 4, 8, 48, 0],
    'ダ': [20, 30, 34, 90, 4, 8, 48, 0],
    'チ': [12, 112, 16, 254, 16, 16, 32, 0],
    'ヂ': [10, 112, 16, 254, 16, 16, 32, 0],
    'ッ': [0, 0, 0, 84, 84, 8, 48, 0],
    'ツ': [0, 162, 82, 82, 4, 8, 48, 0],
    'ヅ': [10, 160, 82, 82, 4, 8, 48, 0],
    'テ': [124, 0, 254, 16, 16, 16, 32, 0],
    'デ': [122, 0, 254, 16, 16, 16, 32, 0],
    'ト': [32, 32, 32, 56, 36, 32, 32, 0],
    'ド': [42, 32, 32, 56, 36, 32, 32, 0],
    'ナ': [16, 16, 254, 16, 16, 32, 64, 0],
    'ニ': [0, 124, 0, 0, 0, 254, 0, 0],
    'ヌ': [124, 4, 52, 8, 24, 36, 192, 0],
    'ネ': [16, 124, 8, 16, 52, 210, 16, 0],
    'ノ': [4, 4, 4, 8, 16, 32, 192, 0],
    'ハ': [0, 40, 36, 36, 66, 66, 130, 0],
    'バ': [10, 32, 36, 36, 66, 66, 130, 0],
    'パ': [4, 42, 36, 36, 66, 66, 130, 0],
    'ヒ': [64, 64, 70, 120, 64, 64, 62, 0],
    'ビ': [74, 64, 70, 120, 64, 64, 62, 0],
    'ピ': [68, 74, 70, 120, 64, 64, 62, 0],
    'フ': [0, 126, 2, 2, 4, 8, 48, 0],
    'ブ': [10, 126, 2, 2, 4, 8, 48, 0],
    'プ': [4, 122, 6, 2, 4, 8, 48, 0],
    'ヘ': [0, 32, 80, 136, 4, 2, 0, 0],
    'ベ': [10, 32, 80, 136, 4, 2, 0, 0],
    'ペ': [4, 42, 84, 136, 4, 2, 0, 0],
    'ホ': [16, 16, 254, 16, 84, 146, 48, 0],
    'ボ': [26, 16, 254, 16, 84, 146, 48, 0],
    'ポ': [20, 26, 244, 16, 84, 146, 48, 0],
    'マ': [0, 254, 2, 4, 40, 16, 8, 0],
    'ミ': [112, 12, 32, 24, 0, 112, 12, 0],
    'ム': [16, 16, 32, 32, 72, 68, 250, 0],
    'メ': [4, 4, 116, 8, 20, 36, 192, 0],
    'モ': [60, 16, 16, 126, 16, 16, 14, 0],
    'ャ': [0, 0, 32, 60, 100, 16, 16, 0],
    'ヤ': [32, 46, 242, 36, 16, 16, 16, 0],
    'ュ': [0, 0, 0, 56, 8, 8, 124, 0],
    'ユ': [0, 120, 8, 8, 8, 254, 0, 0],
    'ョ': [0, 0, 60, 4, 28, 4, 60, 0],
    'ヨ': [0, 126, 2, 62, 2, 2, 126, 0],
    'ラ': [60, 0, 126, 2, 4, 8, 48, 0],
    'リ': [68, 68, 68, 68, 4, 8, 48, 0],
    'ル': [8, 40, 40, 40, 42, 76, 136, 0],
    'レ': [32, 32, 32, 34, 36, 40, 48, 0],
    'ロ': [0, 126, 66, 66, 66, 66, 126, 0],
    'ヮ': [0, 0, 124, 68, 4, 8, 48, 0],
    'ワ': [0, 126, 66, 2, 4, 8, 48, 0],
    'ヰ': [4, 126, 36, 36, 254, 4, 4, 0],
    'ヱ': [0, 124, 8, 16, 16, 254, 0, 0],
    'ヲ': [126, 2, 62, 2, 4, 8, 48, 0],
    'ン': [64, 32, 2, 2, 4, 8, 112, 0],
    'ヴ': [20, 126, 66, 2, 4, 8, 48, 0],
    'ヵ': [0, 0, 16, 124, 20, 36, 76, 0],
    'ヶ': [0, 0, 32, 60, 72, 8, 16, 0],
    'ヷ': [0, 240, 144, 144, 144, 240, 0, 0],
    'ヸ': [0, 240, 144, 144, 144, 240, 0, 0],
    'ヹ': [0, 240, 144, 144, 144, 240, 0, 0],
    'ヺ': [0, 240, 144, 144, 144, 240, 0, 0],
    '・': [0, 0, 0, 48, 48, 0, 0, 0],
    'ー': [0, 0, 128, 126, 0, 0, 0, 0],
    'ヽ': [0, 0, 32, 16, 8, 8, 0, 0],
    'ヾ': [10, 0, 32, 16, 8, 8, 0, 0],
    '！': [16, 16, 16, 16, 16, 0, 16, 0],
    '（': [4, 8, 16, 16, 16, 8, 4, 0],
    '）': [64, 32, 16, 16, 16, 32, 64, 0],
    '＋': [16, 16, 16, 254, 16, 16, 16, 0],
    '：': [0, 48, 48, 0, 48, 48, 0, 0],
    '？': [60, 66, 2, 12, 16, 0, 16, 0],
}


# === inline adapter: alias for stripped imports ===
_SHOP_BUNDLE = SHOPS


# === main.py body ===
"""Block Quest - Pyxel RPG (single-file for app2html export)"""
import pyxel
import random
from pathlib import Path


# =====================================================================
# TILE DATA (16x16 pixel arrays, Pyxel 16-color palette)
# =====================================================================
# fmt: off
TILE_GRASS = [
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11, 3,11,11,11,11,11,11,11,11, 3,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11, 3,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11, 3,11,11,11,11,11,11,11,11,11,11,11,11, 3,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11, 3,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11, 3,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11, 3,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11, 3,11,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11, 3,11,11,11,11,11,11,11],
]
TILE_WATER = [
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12, 7, 7,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12, 7, 7,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12, 7, 7,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12, 7, 7,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
]
# Water frame 2 (shifted wave)
TILE_WATER2 = [
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12, 7, 7,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12, 7, 7,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12, 7, 7,12,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12, 7, 7,12,12,12,12,12,12,12,12,12,12,12],
    [12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
]
TILE_TREE = [
    [11,11,11,11,11, 3, 3, 3, 3, 3, 3,11,11,11,11,11],
    [11,11,11, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11,11,11],
    [11,11, 3, 3, 3, 3,11, 3, 3,11, 3, 3, 3, 3,11,11],
    [11, 3, 3, 3,11, 3, 3, 3, 3, 3,11, 3, 3, 3, 3,11],
    [11, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11],
    [ 3, 3, 3,11, 3, 3, 3, 3, 3, 3, 3,11, 3, 3, 3, 3],
    [ 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [ 3, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3, 3, 3, 3, 3, 3],
    [ 3, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3, 3, 3, 3, 3, 3],
    [ 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [ 3, 3, 3,11, 3, 3, 3, 3, 3, 3, 3, 3,11, 3, 3, 3],
    [11, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11],
    [11, 3, 3, 3, 3, 3, 3, 3, 3, 3,11, 3, 3, 3, 3,11],
    [11,11, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11,11],
    [11,11,11, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11,11,11],
    [11,11,11,11,11, 3, 3, 3, 3, 3, 3,11,11,11,11,11],
]
TILE_SAND = [
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15, 4,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15, 4,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15, 4,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15, 4,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15, 4,15,15,15,15],
    [15, 4,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15, 4,15,15,15,15,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
]
TILE_PATH = [
    [11,11,11,11,11, 4,15, 4,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11, 4,15,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11, 4,15,15,15,15,15, 4,11,11,11,11,11],
    [11,11,11,11, 4,15,15,15,15,15, 4,11,11,11,11,11],
    [11,11,11,11, 4,15,15,15,15,15, 4,11,11,11,11,11],
    [11,11,11,11,11, 4,15,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11, 4,15,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11, 4,15,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11, 4,15,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11, 4,15,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11, 4,15,15,15,15,15, 4,11,11,11,11,11],
    [11,11,11,11, 4,15,15,15,15,15, 4,11,11,11,11,11],
    [11,11,11,11, 4,15,15,15,15,15, 4,11,11,11,11,11],
    [11,11,11,11,11, 4,15,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11, 4,15,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11, 4,15, 4,15, 4,11,11,11,11,11,11],
]
TILE_MOUNTAIN = [
    [11,11,11,11,11,11,11, 5, 5,11,11,11,11,11,11,11],
    [11,11,11,11,11,11, 5, 6, 6, 5,11,11,11,11,11,11],
    [11,11,11,11,11, 5, 6, 6, 6, 5, 5,11,11,11,11,11],
    [11,11,11,11,11, 5, 6, 7, 6, 6, 5,11,11,11,11,11],
    [11,11,11,11, 5, 5, 6, 6, 6, 6, 5, 5,11,11,11,11],
    [11,11,11,11, 5, 6, 6, 6, 6, 5, 5, 5,11,11,11,11],
    [11,11,11, 5, 5, 6, 6, 6, 6, 5, 5, 5, 5,11,11,11],
    [11,11,11, 5, 6, 6, 6, 6, 5, 5, 5, 5, 5,11,11,11],
    [11,11, 5, 5, 6, 6, 6, 5, 5, 5, 5, 5, 5, 5,11,11],
    [11,11, 5, 6, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5,11,11],
    [11, 5, 5, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,11],
    [11, 5, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,11],
    [ 5, 5, 6, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [11, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,11],
]
TILE_CASTLE = [
    [11,11,11, 5, 6, 5, 6, 5, 5, 6, 5, 6, 5,11,11,11],
    [11,11,11, 5, 6, 6, 6, 6, 6, 6, 6, 6, 5,11,11,11],
    [11,11,11, 5, 6, 6, 6, 6, 6, 6, 6, 6, 5,11,11,11],
    [11,11, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 5, 5,11,11],
    [11,11, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5,11,11],
    [11,11, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5,11,11],
    [11, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 5,11],
    [11, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5,11],
    [11, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5,11],
    [11, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5,11],
    [11, 5, 6, 6, 6, 5, 4, 4, 4, 4, 5, 6, 6, 6, 5,11],
    [11, 5, 6, 6, 6, 5, 4, 0, 0, 4, 5, 6, 6, 6, 5,11],
    [11, 5, 6, 6, 6, 5, 4, 0, 0, 4, 5, 6, 6, 6, 5,11],
    [11, 5, 5, 5, 5, 5, 4, 0, 0, 4, 5, 5, 5, 5, 5,11],
    [11,11,11,11,11,11, 4,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,15,15,11,11,11,11,11,11,11],
]
TILE_TOWN = [
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,11,11,11],
    [11,11, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,11,11],
    [11, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,11],
    [11, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,11],
    [11, 9, 9, 9, 4, 4, 9, 9, 9, 9, 4, 4, 9, 9, 9,11],
    [11, 9, 9, 9, 4, 4, 9, 9, 9, 9, 4, 4, 9, 9, 9,11],
    [11, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,11],
    [11, 4,15,15,15,15, 4,15,15, 4,15,15,15,15, 4,11],
    [11, 4,15,15,15,15, 4,15,15, 4,15,15,15,15, 4,11],
    [11, 4,15,15,15,15, 4,15,15, 4,15,15,15,15, 4,11],
    [11, 4,15,15,15,15, 4, 4, 4, 4,15,15,15,15, 4,11],
    [11, 4,15,15,15,15, 4, 0, 0, 4,15,15,15,15, 4,11],
    [11, 4, 4, 4, 4, 4, 4, 0, 0, 4, 4, 4, 4, 4, 4,11],
    [11,11,11,11,11,11, 4,15,15, 4,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,15,15,11,11,11,11,11,11,11],
]
TILE_CAVE = [
    [11,11,11,11, 5, 5, 5, 5, 5, 5, 5, 5,11,11,11,11],
    [11,11,11, 5, 5, 5, 6, 6, 6, 6, 5, 5, 5,11,11,11],
    [11,11, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 5, 5,11,11],
    [11, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 5,11],
    [11, 5, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 5,11],
    [ 5, 5, 6, 5, 5, 1, 1, 1, 1, 1, 1, 5, 5, 6, 5, 5],
    [ 5, 6, 6, 5, 1, 1, 0, 0, 0, 0, 1, 1, 5, 6, 6, 5],
    [ 5, 6, 5, 5, 1, 0, 0, 0, 0, 0, 0, 1, 5, 5, 6, 5],
    [ 5, 6, 5, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 5, 6, 5],
    [ 5, 6, 5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 6, 5],
    [ 5, 6, 5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 6, 5],
    [ 5, 5, 5, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 5, 5, 5],
    [11, 5, 5, 5, 1, 1, 0, 0, 0, 0, 1, 1, 5, 5, 5,11],
    [11,11, 5, 5, 5, 1, 1, 0, 0, 1, 1, 5, 5, 5,11,11],
    [11,11,11, 5, 5, 5, 4,15,15, 4, 5, 5, 5,11,11,11],
    [11,11,11,11, 5, 5,11,15,15,11, 5, 5,11,11,11,11],
]
TILE_BRIDGE = [
    [12,12, 4, 4,15,15,15,15,15,15,15,15, 4, 4,12,12],
    [12,12, 4,15,15,15,15,15,15,15,15,15,15, 4,12,12],
    [12, 4, 4,15,15,15,15,15,15,15,15,15,15, 4, 4,12],
    [12, 4,15,15,15,15,15,15,15,15,15,15,15,15, 4,12],
    [12, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,12],
    [12, 4,15,15,15,15,15,15,15,15,15,15,15,15, 4,12],
    [12, 4,15,15,15,15,15,15,15,15,15,15,15,15, 4,12],
    [12, 4,15,15,15,15,15,15,15,15,15,15,15,15, 4,12],
    [12, 4,15,15,15,15,15,15,15,15,15,15,15,15, 4,12],
    [12, 4,15,15,15,15,15,15,15,15,15,15,15,15, 4,12],
    [12, 4,15,15,15,15,15,15,15,15,15,15,15,15, 4,12],
    [12, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,12],
    [12, 4,15,15,15,15,15,15,15,15,15,15,15,15, 4,12],
    [12,12, 4,15,15,15,15,15,15,15,15,15,15, 4,12,12],
    [12,12, 4, 4,15,15,15,15,15,15,15,15, 4, 4,12,12],
    [12,12,12, 4, 4,15,15,15,15,15,15, 4, 4,12,12,12],
]
TILE_WALL = [
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [ 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5],
    [ 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5],
    [ 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5],
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [ 5, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 5],
    [ 5, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 5],
    [ 5, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 5],
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [ 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5],
    [ 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5],
    [ 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5],
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [ 5, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 5],
    [ 5, 6, 6, 5, 5, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 5],
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
]
TILE_FLOOR = [
    [ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [ 4,15,15,15,15,15,15, 4, 4,15,15,15,15,15,15, 4],
    [ 4,15,15,15,15,15,15, 4, 4,15,15,15,15,15,15, 4],
    [ 4,15,15,15,15,15,15, 4, 4,15,15,15,15,15,15, 4],
    [ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [ 4,15,15,15, 4,15,15,15,15,15, 4,15,15,15,15, 4],
    [ 4,15,15,15, 4,15,15,15,15,15, 4,15,15,15,15, 4],
    [ 4,15,15,15, 4,15,15,15,15,15, 4,15,15,15,15, 4],
    [ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [ 4,15,15,15,15,15,15, 4, 4,15,15,15,15,15,15, 4],
    [ 4,15,15,15,15,15,15, 4, 4,15,15,15,15,15,15, 4],
    [ 4,15,15,15,15,15,15, 4, 4,15,15,15,15,15,15, 4],
    [ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [ 4,15,15, 4,15,15,15,15,15,15,15,15, 4,15,15, 4],
    [ 4,15,15, 4,15,15,15,15,15,15,15,15, 4,15,15, 4],
    [ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
]

# Tile ID constants
T_GRASS = 0; T_WATER = 1; T_TREE = 2; T_SAND = 3
T_FLOOR = 4; T_WALL = 5; T_CASTLE = 6; T_TOWN = 7
T_CAVE = 8; T_MOUNTAIN = 9; T_BRIDGE = 10; T_PATH = 11
T_STAIR_UP = 12  # ダンジョン脱出階段
# 装飾タイル（通行可能、草/砂の上に描かれる）
T_FLOWER = 13; T_ROCK = 14; T_MUSHROOM = 15; T_CACTUS = 16; T_BUSH = 17
# マルチタイルランドマーク（2x2、通行不可）
T_BIGTREE_TL = 18; T_BIGTREE_TR = 19; T_BIGTREE_BL = 20; T_BIGTREE_BR = 21
T_TOWER_TL = 22; T_TOWER_TR = 23; T_TOWER_BL = 24; T_TOWER_BR = 25
T_GLITCH_LORD_TRIGGER = 26  # ダンジョン最奥のボストリガー

# 上り階段（青背景に黄色の階段絵）
TILE_STAIR_UP = [
    [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [ 1, 1, 1, 1, 1, 1, 1,10,10, 1, 1, 1, 1, 1, 1, 1],
    [ 1, 1, 1, 1, 1, 1,10,10,10,10, 1, 1, 1, 1, 1, 1],
    [ 1, 1, 1, 1, 1,10,10,10,10,10,10, 1, 1, 1, 1, 1],
    [ 1, 1, 1, 1,10,10, 7, 7, 7, 7,10,10, 1, 1, 1, 1],
    [ 1, 1, 1,10,10, 7, 7, 7, 7, 7, 7,10,10, 1, 1, 1],
    [ 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 1, 1, 1, 1],
    [ 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 1, 1, 1, 1],
    [ 1, 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1, 1, 1],
    [ 1, 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1, 1, 1],
    [ 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1, 1],
    [ 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1, 1],
    [ 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
    [ 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
    [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# ボストリガー（暗い床に赤い核）
TILE_BOSS_TRIGGER = [
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [ 5, 5, 5, 5, 5, 5, 8, 8, 8, 8, 5, 5, 5, 5, 5, 5],
    [ 5, 5, 5, 5, 5, 8, 2, 2, 2, 2, 8, 5, 5, 5, 5, 5],
    [ 5, 5, 5, 5, 8, 2, 2, 8, 8, 2, 2, 8, 5, 5, 5, 5],
    [ 5, 5, 5, 8, 2, 2, 8, 8, 8, 8, 2, 2, 8, 5, 5, 5],
    [ 5, 5, 8, 2, 2, 8, 8, 7, 7, 8, 8, 2, 2, 8, 5, 5],
    [ 5, 8, 2, 2, 8, 8, 7, 10,10, 7, 8, 8, 2, 2, 8, 5],
    [ 5, 8, 2, 8, 8, 7,10, 8, 8,10, 7, 8, 8, 2, 8, 5],
    [ 5, 8, 2, 8, 8, 7,10, 8, 8,10, 7, 8, 8, 2, 8, 5],
    [ 5, 8, 2, 2, 8, 8, 7,10,10, 7, 8, 8, 2, 2, 8, 5],
    [ 5, 5, 8, 2, 2, 8, 8, 7, 7, 8, 8, 2, 2, 8, 5, 5],
    [ 5, 5, 5, 8, 2, 2, 8, 8, 8, 8, 2, 2, 8, 5, 5, 5],
    [ 5, 5, 5, 5, 8, 2, 2, 8, 8, 2, 2, 8, 5, 5, 5, 5],
    [ 5, 5, 5, 5, 5, 8, 2, 2, 2, 2, 8, 5, 5, 5, 5, 5],
    [ 5, 5, 5, 5, 5, 5, 8, 8, 8, 8, 5, 5, 5, 5, 5, 5],
    [ 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
]

# 装飾タイル: 草原+花（赤8・黄10の花が散在）
TILE_FLOWER = [
    [11,11,11, 3,11,11,11,11,11,11, 3,11,11,11,11,11],
    [11,11,11,11,11, 8,11,11,11,11,11,11,11,11, 3,11],
    [11, 3,11,11, 8, 8, 8,11,11,11,11, 3,11,11,11,11],
    [11,11,11,11,11, 8,11,11, 3,11,11,11,11,10,11,11],
    [11,11,11, 3,11,11,11,11,11,11,11,11,10,10,10,11],
    [11,11,11,11,11,11,11,11,11,10,11,11,11,10,11,11],
    [11,11, 3,11,11,11,11, 3,10,10,10,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,10,11,11,11,11, 3,11],
    [11, 3,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11, 8,11,11, 3,11,11,11,11, 3,11,11,11,11],
    [11,11, 8, 8, 8,11,11,11,11,11,11,11,11,11,11,11],
    [11,11,11, 8,11,11,11,11,11,11,11,11,11, 3,11,11],
    [11,11,11,11,11,11,11,11, 3,11,11,10,11,11,11,11],
    [11, 3,11,11,11, 3,11,11,11,11,10,10,10,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,10,11,11, 3,11],
    [11,11, 3,11,11,11,11,11,11, 3,11,11,11,11,11,11],
]
# 装飾タイル: 草原+岩（灰5・薄灰6）
TILE_ROCK = [
    [11,11,11, 3,11,11,11,11,11,11, 3,11,11,11,11,11],
    [11,11,11,11,11,11, 5, 5, 5,11,11,11,11,11, 3,11],
    [11, 3,11,11,11, 5, 6, 6, 5, 5,11, 3,11,11,11,11],
    [11,11,11,11,11, 5, 5, 6, 6, 5,11,11,11,11,11,11],
    [11,11,11, 3,11,11, 5, 5, 5,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11, 3,11],
    [11,11, 3,11,11,11,11, 3,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11, 5, 5,11,11,11,11],
    [11, 3,11,11,11,11,11,11,11, 5, 6, 5, 5,11,11,11],
    [11,11,11,11,11, 3,11,11,11, 5, 5, 5,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11, 3,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11, 5, 5, 5,11,11,11,11, 3,11,11,11,11,11,11,11],
    [11, 5, 6, 5,11, 3,11,11,11,11,11,11,11, 3,11,11],
    [11, 5, 5,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11, 3,11,11,11,11,11,11, 3,11,11,11,11,11,11],
]
# 装飾タイル: 森+キノコ（赤8キャップ+白7軸）
TILE_MUSHROOM = [
    [ 3, 3,11, 3, 3,11, 3, 3, 3,11, 3, 3,11, 3, 3, 3],
    [ 3,11,11, 3,11,11, 3,11, 3,11, 3,11,11, 3,11, 3],
    [11,11, 3,11,11, 3,11,11,11, 3,11,11, 3,11,11,11],
    [ 3,11,11,11, 3,11,11, 3,11,11, 3,11,11,11, 3,11],
    [ 3, 3,11, 8, 8, 8,11, 3, 3,11,11, 3,11,11,11, 3],
    [11,11, 8, 8, 7, 8, 8,11,11,11, 3,11,11, 3,11,11],
    [ 3,11,11, 7, 7,11,11, 3,11,11,11,11, 3,11,11, 3],
    [11,11, 3,11,11, 3,11,11,11, 3,11,11,11,11, 3,11],
    [ 3,11,11, 3,11,11, 3,11, 3,11, 3,11, 3,11,11, 3],
    [ 3, 3,11, 3,11,11,11,11, 3,11, 8, 8, 8,11, 3,11],
    [11,11, 3,11,11, 3,11,11,11, 8, 8, 7, 8, 8,11, 3],
    [ 3,11,11,11, 3,11,11, 3,11,11, 7, 7,11,11, 3,11],
    [11,11, 3,11,11,11, 3,11, 3,11,11,11,11, 3,11,11],
    [ 3,11,11, 3,11,11, 3,11, 3,11, 3,11, 3,11, 3, 3],
    [11, 3,11, 3, 3,11, 3,11, 3,11, 3,11, 3, 3,11, 3],
    [ 3, 3, 3,11, 3, 3,11, 3,11, 3,11, 3,11, 3, 3,11],
]
# 装飾タイル: 砂漠+サボテン（緑11/濃緑3）
TILE_CACTUS = [
    [15,15,15, 4,15,15,15,15,15,15,15,15, 4,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15],
    [15, 4,15,15,15,11,11,15,15,15,15, 4,15,15,15,15],
    [15,15,15,15, 3,11, 3,11,15,15,15,15,15,15, 4,15],
    [15,15,15,15,15, 3,15, 3,15,15,15,15,15,15,15,15],
    [15,15, 4,15,15, 3,15,15,15,15, 4,15,15,15,15,15],
    [15,15,15,15,15, 3,15,15,15,15,15,15,15,15,15,15],
    [15,15,15,15,15, 3,15,15,15, 4,15,15,15,15,15,15],
    [15, 4,15,15,15,15,15,15,15,15,15,15,11,15,15,15],
    [15,15,15,15,15,15,15,15,15,15,15,11, 3,11,15,15],
    [15,15,15,15, 4,15,15,15,15,15, 3,11,15, 3,15,15],
    [15,15,15,15,15,15,15, 4,15,15,15, 3,15,15, 4,15],
    [15,15, 4,15,15,15,15,15,15,15,15, 3,15,15,15,15],
    [15,15,15,15,15,15,15,15, 4,15,15, 3,15,15,15,15],
    [15,15,15,15,15, 4,15,15,15,15,15,15,15, 4,15,15],
    [15, 4,15,15,15,15,15,15,15, 4,15,15,15,15,15,15],
]
# 装飾タイル: 茂み（濃い草むら）
TILE_BUSH = [
    [11,11,11, 3,11,11,11,11,11,11, 3,11,11,11,11,11],
    [11,11, 3, 3, 3,11,11,11,11, 3, 3, 3,11,11, 3,11],
    [11, 3, 3, 3, 3, 3,11, 3, 3, 3, 3, 3, 3,11,11,11],
    [11, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,11,11,11,11],
    [11,11, 3, 3, 3, 3, 3, 3, 3, 3, 3,11,11,11,11,11],
    [11,11,11, 3, 3, 3, 3, 3, 3, 3,11,11,11,11, 3,11],
    [11,11, 3,11,11, 3, 3,11,11,11,11,11,11,11,11,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11, 3,11],
    [11, 3,11,11,11,11,11,11,11, 3, 3, 3, 3,11,11,11],
    [11,11,11,11,11, 3,11,11, 3, 3, 3, 3, 3, 3,11,11],
    [11,11,11,11,11,11,11, 3, 3, 3, 3, 3, 3, 3,11,11],
    [11,11, 3,11,11,11,11, 3, 3, 3, 3, 3, 3,11,11,11],
    [11,11,11,11,11,11,11,11, 3, 3, 3, 3,11,11,11,11],
    [11, 3,11,11,11, 3,11,11,11, 3, 3,11,11,11, 3,11],
    [11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11],
    [11,11, 3,11,11,11,11,11,11, 3,11,11,11, 3,11,11],
]
# マルチタイル: 世界樹（2x2、緑の大樹）
TILE_BIGTREE_TL = [
    [ 0, 0, 0, 0, 0, 0, 3, 3, 3, 3,11,11, 3, 3, 3, 3],
    [ 0, 0, 0, 0, 3, 3, 3,11,11, 3, 3,11,11, 3,11,11],
    [ 0, 0, 0, 3, 3,11,11,11, 3, 3,11,11, 3,11,11, 3],
    [ 0, 0, 3, 3,11,11, 3,11,11,11,11, 3,11,11, 3,11],
    [ 0, 3, 3,11,11, 3, 3, 3,11,11, 3,11,11, 3,11,11],
    [ 0, 3,11,11, 3, 3,11, 3, 3,11,11,11, 3,11,11,11],
    [ 3, 3,11, 3, 3,11,11, 3, 3, 3,11, 3,11,11,11, 3],
    [ 3,11,11, 3,11,11, 3, 3,11, 3, 3,11,11,11, 3, 3],
    [ 3,11, 3,11,11, 3, 3,11,11, 3,11,11,11, 3, 3,11],
    [ 3, 3,11,11, 3, 3,11,11, 3,11,11,11, 3, 3,11,11],
    [11, 3, 3, 3, 3,11,11, 3,11,11,11, 3, 3,11,11, 3],
    [11,11, 3, 3,11,11, 3,11,11, 3, 3, 3,11,11, 3, 3],
    [ 3,11,11, 3, 3, 3, 3,11, 3, 3,11,11,11, 3, 3,11],
    [ 3, 3,11,11,11, 3, 3, 4, 4, 3,11,11, 3, 3,11,11],
    [11, 3, 3,11,11,11, 3, 4, 4, 3, 3, 3, 3,11,11, 3],
    [11,11, 3, 3,11,11,11, 4, 4,11,11, 3,11,11, 3, 3],
]
TILE_BIGTREE_TR = [
    [ 3, 3,11,11, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0],
    [11, 3,11,11, 3,11,11, 3, 3, 0, 0, 0, 0, 0, 0, 0],
    [11,11, 3,11,11, 3, 3,11, 3, 3, 0, 0, 0, 0, 0, 0],
    [ 3,11,11, 3,11,11,11, 3, 3, 3, 3, 0, 0, 0, 0, 0],
    [11, 3,11,11, 3,11,11,11, 3, 3, 3, 0, 0, 0, 0, 0],
    [11,11, 3,11,11,11, 3, 3,11, 3, 3, 0, 0, 0, 0, 0],
    [ 3,11,11, 3,11, 3, 3,11, 3, 3, 3, 3, 0, 0, 0, 0],
    [11,11, 3,11, 3, 3,11, 3,11,11, 3, 3, 0, 0, 0, 0],
    [11, 3, 3,11, 3,11,11,11, 3,11, 3, 3, 0, 0, 0, 0],
    [11,11, 3, 3,11,11,11, 3,11,11,11, 3, 0, 0, 0, 0],
    [ 3,11, 3, 3,11,11, 3,11,11, 3, 3, 3, 3, 0, 0, 0],
    [ 3, 3, 3,11,11, 3,11,11, 3, 3,11,11, 3, 0, 0, 0],
    [11, 3,11,11, 3, 3,11, 3, 3, 3, 3,11, 3, 3, 0, 0],
    [11,11, 3, 3, 3, 4, 4, 3, 3,11,11,11, 3, 3, 0, 0],
    [11, 3, 3, 3, 3, 4, 4, 3,11,11,11, 3, 3, 3, 0, 0],
    [ 3, 3,11, 3,11, 4, 4,11,11, 3, 3,11, 3, 3, 0, 0],
]
TILE_BIGTREE_BL = [
    [11,11, 3, 3,11,11,11, 4, 4,11,11, 3,11,11, 3, 3],
    [11, 3, 3,11,11,11,11, 4, 4,11, 3, 3, 3,11,11, 3],
    [11,11, 3, 3,11,11,11, 4, 4,11,11, 3, 3,11, 3,11],
    [11,11,11, 3, 3,11,11, 4, 4, 3,11,11, 3, 3,11,11],
    [ 0, 0,11,11, 3, 3, 3, 4, 4, 3, 3,11, 3,11,11, 0],
    [ 0, 0, 0,11,11,11, 3, 4, 4, 3, 3,11,11,11, 0, 0],
    [ 0, 0, 0, 0,11,11,11, 4, 4,11,11, 3,11, 0, 0, 0],
    [ 0, 0, 0, 0, 0,11,11, 4, 4,11,11,11, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0,11, 4, 4,11,11, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0,11, 4, 4,11, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0,11, 4, 4,11, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0,11, 4, 4, 4, 4,11, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0,11, 4, 4, 4, 4,11, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0,11, 4, 4, 4, 4, 4, 4,11, 0, 0, 0, 0],
    [ 0, 0, 0, 0,11, 4, 4, 4, 4, 4, 4,11, 0, 0, 0, 0],
    [ 0, 0, 0,11, 4, 4, 3, 4, 4, 3, 4, 4,11, 0, 0, 0],
]
TILE_BIGTREE_BR = [
    [ 3, 3,11, 3,11, 4, 4,11,11, 3, 3,11, 3, 3, 0, 0],
    [ 3,11, 3, 3, 3, 4, 4,11, 3, 3,11,11, 3, 0, 0, 0],
    [11, 3, 3,11,11, 4, 4,11, 3, 3,11, 3,11, 0, 0, 0],
    [11, 3,11, 3, 3, 4, 4,11,11, 3, 3,11, 0, 0, 0, 0],
    [ 0,11,11, 3, 3, 4, 4, 3, 3,11, 3, 0, 0, 0, 0, 0],
    [ 0, 0,11,11, 3, 4, 4, 3,11,11, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 3,11, 4, 4,11,11, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0,11, 4, 4,11, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 4, 4,11, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 4, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 4, 4, 3, 4, 4, 3, 4, 4, 0, 0, 0, 0, 0, 0],
]
# マルチタイル: 通信塔（2x2、紫13/灰5/白7）
TILE_TOWER_TL = [
    [ 0, 0, 0, 0, 0, 0, 0, 7, 7, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 7,13, 7, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 7,13,13, 7, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 7,13,13,13, 7, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 7,13,13,13,13, 7, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 7,13,13, 7,13,13, 7, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 7,13, 7, 7,13,13,13, 7, 0, 0, 0, 0],
    [ 0, 0, 0, 7,13,13, 7, 7, 7,13,13, 7, 0, 0, 0, 0],
    [ 0, 0, 0, 7,13,13,13, 7,13,13,13, 7, 0, 0, 0, 0],
    [ 0, 0, 7,13,13,13, 7, 7,13,13,13,13, 7, 0, 0, 0],
    [ 0, 0, 7,13,13, 7, 7, 7,13,13,13,13, 7, 0, 0, 0],
    [ 0, 7,13,13,13, 7, 7,13,13,13,13,13,13, 7, 0, 0],
    [ 0, 7,13,13,13,13, 7,13,13,13,13,13,13, 7, 0, 0],
    [ 7,13,13,13,13, 7, 7,13,13,13,13,13,13,13, 7, 0],
    [ 7,13,13,13,13,13, 7,13,13,13,13,13,13,13, 7, 0],
    [ 7,13,13,13,13, 7, 7,13,13,13,13,13,13,13,13, 7],
]
TILE_TOWER_TR = [
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
TILE_TOWER_BL = [
    [ 7,13,13,13,13,13, 7, 7,13,13,13,13,13,13,13, 7],
    [ 5,13,13,13,13, 7, 7,13,13,13,13,13,13,13, 7, 5],
    [ 5, 5,13,13, 7, 7, 7,13,13,13,13,13, 7, 5, 5, 5],
    [ 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0],
    [ 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0],
    [ 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 6, 6, 5, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 6, 6, 5, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0],
]
TILE_TOWER_BR = [
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

TILE_DATA = {
    T_GRASS: TILE_GRASS, T_WATER: TILE_WATER, T_TREE: TILE_TREE,
    T_SAND: TILE_SAND, T_FLOOR: TILE_FLOOR, T_WALL: TILE_WALL,
    T_CASTLE: TILE_CASTLE, T_TOWN: TILE_TOWN, T_CAVE: TILE_CAVE,
    T_MOUNTAIN: TILE_MOUNTAIN, T_BRIDGE: TILE_BRIDGE, T_PATH: TILE_PATH,
    T_STAIR_UP: TILE_STAIR_UP,
    T_FLOWER: TILE_FLOWER, T_ROCK: TILE_ROCK, T_MUSHROOM: TILE_MUSHROOM,
    T_CACTUS: TILE_CACTUS, T_BUSH: TILE_BUSH,
    T_BIGTREE_TL: TILE_BIGTREE_TL, T_BIGTREE_TR: TILE_BIGTREE_TR,
    T_BIGTREE_BL: TILE_BIGTREE_BL, T_BIGTREE_BR: TILE_BIGTREE_BR,
    T_TOWER_TL: TILE_TOWER_TL, T_TOWER_TR: TILE_TOWER_TR,
    T_TOWER_BL: TILE_TOWER_BL, T_TOWER_BR: TILE_TOWER_BR,
    T_GLITCH_LORD_TRIGGER: TILE_BOSS_TRIGGER,
}

DECORATION_TILES = {T_FLOWER, T_ROCK, T_MUSHROOM, T_CACTUS, T_BUSH}
LANDMARK_TILES = {T_BIGTREE_TL, T_BIGTREE_TR, T_BIGTREE_BL, T_BIGTREE_BR,
                  T_TOWER_TL, T_TOWER_TR, T_TOWER_BL, T_TOWER_BR}
IMPASSABLE = {T_WATER, T_TREE, T_WALL, T_MOUNTAIN} | LANDMARK_TILES

# =====================================================================
# AUTO-TILE DATA (PATH variants + SHORE variants)
# =====================================================================
_G = 11; _P = 15; _D = 4; _W = 12; _S = 15; _B = 3

PATH_V = [
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
]
PATH_H = [
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
]
PATH_CROSS = [
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_P,_P,_P,_P,_P,_P,_D,_D,_D,_D,_D],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_D,_D,_D,_D,_D,_P,_P,_P,_P,_P,_P,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
]
PATH_SE = [
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
]
PATH_SW = [
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
]
PATH_NE = [
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
]
PATH_NW = [
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
]
PATH_T_NES = [
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
]
PATH_T_NWS = [
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
]
PATH_T_EWS = [
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_D,_D,_D,_D,_D,_P,_P,_P,_P,_P,_P,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
]
PATH_T_NEW = [
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_G,_G,_G,_G,_D,_P,_P,_P,_P,_P,_P,_D,_G,_G,_G,_G],
    [_D,_D,_D,_D,_D,_P,_P,_P,_P,_P,_P,_D,_D,_D,_D,_D],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P,_P],
    [_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D,_D],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
    [_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G,_G],
]

# Shore tiles (simplified - use N/S/E/W only for performance)
SHORE_N = [
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_B,_S,_B,_B,_S,_S,_B,_S,_B,_S,_B,_B,_S,_B,_S,_B],
    [_W,_B,_W,_B,_B,_B,_W,_B,_W,_B,_W,_B,_B,_W,_B,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
]
SHORE_S = [
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_W,_B,_W,_B,_B,_B,_W,_B,_W,_B,_W,_B,_B,_W,_B,_W],
    [_B,_S,_B,_B,_S,_S,_B,_S,_B,_S,_B,_B,_S,_B,_S,_B],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
]
SHORE_W = [
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
]
SHORE_E = [
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
]

_PATH_VARIANTS = {
    (True,False,True,False): PATH_V, (False,True,False,True): PATH_H,
    (False,True,True,False): PATH_SE, (False,False,True,True): PATH_SW,
    (True,True,False,False): PATH_NE, (True,False,False,True): PATH_NW,
    (True,True,True,False): PATH_T_NES, (True,False,True,True): PATH_T_NWS,
    (False,True,True,True): PATH_T_EWS, (True,True,False,True): PATH_T_NEW,
    (True,True,True,True): PATH_CROSS,
}
# SHORE corner variants (land on two adjacent cardinal sides)
SHORE_NE = [
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_B,_S,_B,_B,_S,_S,_B,_S,_B,_S,_B,_S,_S,_S,_S,_S],
    [_W,_B,_W,_B,_B,_B,_W,_B,_W,_B,_W,_B,_B,_S,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
]
SHORE_NW = [
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_S,_S,_S,_S,_S,_B,_S,_B,_S,_B,_B,_S,_S,_B,_S,_B],
    [_S,_S,_S,_B,_B,_W,_B,_W,_B,_B,_W,_B,_B,_W,_B,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
]
SHORE_SE = [
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S],
    [_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_B,_B,_S,_S,_S],
    [_W,_B,_W,_B,_B,_B,_W,_B,_W,_B,_W,_B,_S,_S,_S,_S],
    [_B,_S,_B,_B,_S,_S,_B,_S,_B,_S,_B,_S,_S,_S,_S,_S],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
]
SHORE_SW = [
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_S,_B,_B,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W,_W],
    [_S,_S,_S,_S,_B,_W,_B,_W,_B,_B,_B,_W,_B,_W,_B,_W],
    [_S,_S,_S,_S,_S,_B,_S,_B,_B,_S,_S,_B,_S,_B,_S,_B],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
    [_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S,_S],
]

_SHORE_VARIANTS = {
    (True,False,False,False): SHORE_N, (False,False,True,False): SHORE_S,
    (False,False,False,True): SHORE_W, (False,True,False,False): SHORE_E,
    (True,True,False,False): SHORE_NE, (True,False,False,True): SHORE_NW,
    (False,True,True,False): SHORE_SE, (False,False,True,True): SHORE_SW,
}

def get_path_variant(world_map, mx, my):
    h = len(world_map)
    w = len(world_map[0]) if h > 0 else 0
    def is_path(x, y):
        if 0 <= x < w and 0 <= y < h:
            return world_map[y][x] == T_PATH
        return False
    n = is_path(mx, my - 1); e = is_path(mx + 1, my)
    s = is_path(mx, my + 1); w_ = is_path(mx - 1, my)
    key = (n, e, s, w_)
    variant = _PATH_VARIANTS.get(key)
    if variant: return variant
    if n or s: return PATH_V
    if e or w_: return PATH_H
    return PATH_V

def get_shore_variant(world_map, mx, my):
    h = len(world_map)
    w = len(world_map[0]) if h > 0 else 0
    def is_land(x, y):
        if 0 <= x < w and 0 <= y < h:
            return world_map[y][x] != T_WATER
        return False
    n = is_land(mx, my - 1); e = is_land(mx + 1, my)
    s = is_land(mx, my + 1); w_ = is_land(mx - 1, my)
    if not (n or e or s or w_): return None
    key = (n, e, s, w_)
    variant = _SHORE_VARIANTS.get(key)
    if variant: return variant
    if n: return SHORE_N
    if s: return SHORE_S
    if w_: return SHORE_W
    if e: return SHORE_E
    return None

# =====================================================================
# SPRITE DATA
# =====================================================================
HERO_DOWN = [
    [ 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15, 8, 0, 8,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,14,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0,12,12,12,12,12,12,12,12,12, 0, 0, 0, 0],
    [ 0, 0,15,12,12,12,12,12,12,12,12,12,15, 0, 0, 0],
    [ 0, 0,15,12, 1,12,12,12,12,12, 1,12,15, 0, 0, 0],
    [ 0, 0, 0,12,12,12,12,12,12,12,12,12, 0, 0, 0, 0],
    [ 0, 0, 0,12,12,12, 1,12, 1,12,12,12, 0, 0, 0, 0],
    [ 0, 0, 0, 0,12,12, 1,12, 1,12,12, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0,15,15, 0, 0, 0, 0,15,15, 0, 0, 0, 0],
    [ 0, 0, 0, 0,15,15, 0, 0, 0, 0,15,15, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
HERO_DOWN_WALK = [
    [ 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15, 8, 0, 8,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,15,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 4,15,15,14,15,15, 4, 0, 0, 0, 0, 0],
    [ 0, 0, 0,12,12,12,12,12,12,12,12,12, 0, 0, 0, 0],
    [ 0, 0,15,12,12,12,12,12,12,12,12,12,15, 0, 0, 0],
    [ 0, 0,15,12, 1,12,12,12,12,12, 1,12,15, 0, 0, 0],
    [ 0, 0, 0,12,12,12,12,12,12,12,12,12, 0, 0, 0, 0],
    [ 0, 0, 0,12,12,12, 1,12, 1,12,12,12, 0, 0, 0, 0],
    [ 0, 0, 0, 0,12,12, 1,12, 1,12,12, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0,15, 0, 0, 0, 0,15, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0,15, 0, 0, 0,15, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 4, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
SLIME_10HO = [
    [ 0, 0, 0, 0, 0, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 3,11,11,11,11, 3, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 3,11,11,11,11,11,11, 3, 0, 0, 0, 0, 0],
    [ 0, 0, 3,11,11, 7,11,11, 7,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 3,11,11,11,11,11,11,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 3,11,11,11, 8,11, 8,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 3,11,11,11,11,11,11,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 3,11,11,11,11, 8,11,11,11, 3, 0, 0, 0, 0],
    [ 0, 0, 0, 3,11,11,11,11,11,11, 3, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 3, 3,11,11,11, 3, 3, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
    [ 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0],
    [ 0, 0, 3, 3, 3, 0, 0, 0, 0, 0, 3, 3, 3, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
GOBLIN_KAITEN = [
    [ 0, 0, 0, 0, 0, 0, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 9,15,15,15, 9, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 9,15,15, 8,15,15, 9, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 9,15, 8,15,15,15, 8,15, 9, 0, 0, 0, 0],
    [ 0, 0, 0, 9,15,15,15,15,15,15,15, 9, 0, 0, 0, 0],
    [ 0, 0, 0, 9, 8,15,11, 8,11,15, 8, 9, 0, 0, 0, 0],
    [ 0, 0, 0, 9,15,15,15,14,15,15,15, 9, 0, 0, 0, 0],
    [ 0, 0, 9, 9, 8, 8, 9, 9, 9, 8, 8, 9, 9, 0, 0, 0],
    [ 0, 9, 8, 8,15,15, 9, 9, 9,15,15, 8, 8, 9, 0, 0],
    [ 9, 8,15,15,15,15, 8, 9, 8,15,15,15,15, 8, 9, 0],
    [ 0, 9, 8, 8, 8, 8, 9, 0, 9, 8, 8, 8, 8, 9, 0, 0],
    [ 0, 0, 0, 9, 9, 9, 0, 0, 0, 9, 9, 9, 0, 0, 0, 0],
    [ 0, 0, 9, 8,15, 8, 9, 0, 9, 8,15, 8, 9, 0, 0, 0],
    [ 0, 0, 9, 8, 8, 9, 0, 0, 0, 9, 8, 8, 9, 0, 0, 0],
    [ 0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 9, 9, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
GHOST_LOOP = [
    [ 0, 0, 0, 0, 0,13,13,13,13,13, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0,13, 7, 7, 7, 7, 7,13, 0, 0, 0, 0, 0],
    [ 0, 0, 0,13, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0, 0],
    [ 0, 0,13, 7, 7, 6, 7, 7, 7, 6, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 1, 7, 7, 7, 1, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 8, 7, 8, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13, 7, 7, 7, 7, 7, 7, 7, 7, 7,13, 0, 0, 0],
    [ 0, 0,13,13, 7, 7, 7, 7, 7, 7, 7,13,13, 0, 0, 0],
    [ 0, 0,13, 0,13, 7, 7, 7, 7, 7,13, 0,13, 0, 0, 0],
    [ 0, 0,13, 0, 0,13,13, 7,13,13, 0, 0,13, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0,13, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0,13, 0,13, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
KNIGHT_10KAI = [
    [ 0, 0, 0, 0, 5, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 7, 6, 7, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 5, 5, 6, 6, 6, 6, 6, 6, 6, 5, 5, 0, 0, 0],
    [ 0, 5,12,12, 6, 6, 6, 6, 6, 6, 6,12,12, 5, 0, 0],
    [ 0, 5,12,12, 6, 6, 6, 1, 6, 6, 6,12,12, 5, 0, 0],
    [ 0, 5,12,12, 6, 6, 6, 6, 6, 6, 6,12,12, 5, 0, 0],
    [ 0, 0, 5, 5, 5, 6, 6, 6, 6, 6, 5, 5, 5, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 5, 6, 5, 6, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 5, 5, 6, 5, 5, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 5, 5, 0, 5, 0, 5, 5, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
GUARD_MOSHI = [
    [ 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5,15,15,15,15,15, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5,15,15,15,15,15, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5,15, 0,15, 0,15, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5,15,15,14,15,15, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 6, 5, 5, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 6, 6, 6, 5, 6, 6, 6, 6, 6, 5, 6, 0, 0, 0, 0],
    [ 0, 6, 6, 6, 5, 6, 6, 8, 6, 6, 5, 6, 0, 0, 0, 0],
    [ 0, 6, 6, 6, 5, 6, 6, 6, 6, 6, 5, 6, 0, 0, 0, 0],
    [ 0, 0, 6, 5, 5, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 6, 6, 6, 6, 6, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 6, 5, 6, 6, 6, 5, 6, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 5, 5, 5, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 5, 0, 0, 5, 0, 0, 5, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
SLIME_DENAKEREBA = [
    [ 0, 0, 0, 0, 0, 2,14, 2, 2, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 2,14,14,14,14, 2, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 2,14,14,14,14,14,14, 2, 0, 0, 0, 0, 0],
    [ 0, 0, 2,14,14, 7,14,14, 7,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14,14,14,14,14,14,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14,14,14, 2,14, 2,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14,14,14,14,14,14,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14,14,14,14, 8,14,14,14, 2, 0, 0, 0, 0],
    [ 0, 0, 0, 2,14,14,14,14,14,14, 2, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 2, 2,14,14,14, 2, 2, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
    [ 0, 0, 2,14, 2, 0, 0, 0, 0, 0, 2,14, 2, 0, 0, 0],
    [ 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
COUNTER_HP = [
    [ 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [ 0, 1,12,12,12,12,12,12,12,12,12,12,12, 1, 0, 0],
    [ 1,12, 7, 7, 7,12,12,12,12, 7, 7, 7,12,12, 1, 0],
    [ 1,12, 7,10, 7,12,10,12,10, 7,10, 7,12,12, 1, 0],
    [ 1,12, 7, 7, 7,12,10,12,10, 7, 7, 7,12,12, 1, 0],
    [ 1,12,12,12,12,12,10,12,10,12,12,12,12,12, 1, 0],
    [ 1,12, 8, 8, 8,12,12,12,12,12, 8, 8,12,12, 1, 0],
    [ 1,12, 8, 8, 8,12,12,12,12,12, 8, 8,12,12, 1, 0],
    [ 1,12,12,12,12,12,12,12,12,12,12,12,12,12, 1, 0],
    [ 1,12,12, 1, 1,12,12,12,12, 1, 1,12,12,12, 1, 0],
    [ 1,12, 1, 0, 0, 1,12,12, 1, 0, 0, 1,12,12, 1, 0],
    [ 1,12, 1, 0, 0, 1,12,12, 1, 0, 0, 1,12,12, 1, 0],
    [ 1,12,12, 1, 1,12,12,12,12, 1, 1,12,12,12, 1, 0],
    [ 1,12,12,12,12,12,12,12,12,12,12,12,12,12, 1, 0],
    [ 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
NINJA_CLONE = [
    [ 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 8, 5, 8, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0, 0],
    [ 0, 1, 1, 1, 5, 5, 1, 5, 1, 5, 5, 1, 1, 1, 0, 0],
    [ 1, 5, 5, 5, 5, 5, 1, 5, 1, 5, 5, 5, 5, 5, 1, 0],
    [ 1, 5, 0, 0, 5, 5, 1, 5, 1, 5, 5, 0, 0, 5, 1, 0],
    [ 1, 5, 5, 5, 5, 5, 1, 5, 1, 5, 5, 5, 5, 5, 1, 0],
    [ 0, 1, 1, 1, 5, 5, 1, 5, 1, 5, 5, 1, 1, 1, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 5, 5, 5, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 5, 5, 1, 5, 1, 5, 5, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 1, 1, 5, 1, 5, 1, 5, 1, 1, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
BUG_MUGEN = [
    [ 0, 8, 0,10, 0, 8, 0,10, 0, 8, 0,10, 0, 8, 0, 0],
    [ 8, 0,11, 0, 8, 0,11, 0, 8, 0,11, 0, 8, 0, 0, 0],
    [ 0, 8, 2, 8, 0, 8, 2, 8, 0, 8, 2, 8, 0, 8, 0, 0],
    [ 2,11, 0, 2,11, 0, 2,11, 0, 2,11, 0, 2,11, 0, 0],
    [ 0, 2, 8, 0, 2, 8, 7, 2, 8, 0, 2, 8, 0, 2, 0, 0],
    [ 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 0, 0],
    [ 0,11, 0, 0,11, 0, 0,11, 0, 0,11, 0, 0,11, 0, 0],
    [ 2, 0, 8, 2, 0, 8, 2, 0, 8, 2, 0, 8, 2, 0, 0, 0],
    [ 0, 8, 2, 0, 8, 2, 0, 8, 2, 0, 8, 2, 0, 8, 0, 0],
    [11, 2, 0,11, 2, 0,11, 2, 0,11, 2, 0,11, 2, 0, 0],
    [ 0,11, 8, 0,11, 8, 0,11, 8, 0,11, 8, 0,11, 0, 0],
    [ 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 0, 0],
    [ 2, 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 2, 8, 0, 0],
    [ 0, 2,11, 0, 2,11, 0, 2,11, 0, 2,11, 0, 2, 0, 0],
    [11, 0, 8,11, 0, 8,11, 0, 8,11, 0, 8,11, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
BOSS_GLITCH = [
    [ 0, 0, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 0, 0, 0],
    [ 0, 2, 8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 2, 0, 0],
    [ 2, 8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 2, 0],
    [ 8, 2, 2, 8, 2, 8, 2, 2, 2, 8, 2, 8, 2, 2, 8, 0],
    [ 2, 2, 2, 2, 8, 2, 2, 2, 2, 2, 8, 2, 2, 2, 2, 0],
    [ 2, 2, 2, 2, 2, 2, 8, 2, 8, 2, 2, 2, 2, 2, 2, 0],
    [ 2, 2, 2, 2, 2, 2, 2, 8, 2, 2, 2, 2, 2, 2, 2, 0],
    [ 0, 2, 8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 8, 2, 0, 0],
    [ 0, 8, 2, 8, 2, 2, 2, 2, 2, 2, 2, 8, 2, 8, 0, 0],
    [ 0, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 0, 0],
    [ 0, 0, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 0, 0, 0],
    [ 0, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 0, 0],
    [ 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 0],
    [ 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 0],
    [ 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 2, 8, 0],
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

ENEMY_SPRITES = {
    "slime": SLIME_10HO, "goblin": GOBLIN_KAITEN,
    "ghost": GHOST_LOOP, "knight": KNIGHT_10KAI,
    "guard": GUARD_MOSHI, "else_slime": SLIME_DENAKEREBA,
    "counter": COUNTER_HP, "ninja": NINJA_CLONE,
    "inf_bug": BUG_MUGEN, "glitch_lord": BOSS_GLITCH,
}
# fmt: on

# =====================================================================
# MAP GENERATION (from map_gen.py)
# =====================================================================
MAP_W = 50; MAP_H = 50
CASTLE_POS = (25, 6)
TOWN_HAJIME = (20, 12); TOWN_LOGIC = (30, 22)
TOWN_ALGO = (18, 34); CAVE_GLITCH = (38, 42)
DUNGEON_W = 20; DUNGEON_H = 20

def _make_empty(w, h, fill):
    return [[fill] * w for _ in range(h)]

def _carve_winding_path(grid, x1, y1, x2, y2, rng, passable=None):
    if passable is None:
        passable = {T_GRASS, T_SAND}
    cx, cy = x1, y1
    max_iter = (abs(x2 - x1) + abs(y2 - y1)) * 4 + 50
    for _ in range(max_iter):
        if cx == x2 and cy == y2: break
        if rng.random() < 0.3 and cx != x2 and cy != y2:
            if rng.random() < 0.5: cx += 1 if x2 > cx else -1
            else: cy += 1 if y2 > cy else -1
        else:
            if abs(x2 - cx) > abs(y2 - cy): cx += 1 if x2 > cx else -1
            else: cy += 1 if y2 > cy else -1
        cx = max(1, min(MAP_W - 2, cx))
        cy = max(1, min(MAP_H - 2, cy))
        if grid[cy][cx] in passable:
            grid[cy][cx] = T_PATH

def _place_forests(grid, rng):
    def density(y):
        if y < 3 or y >= 47: return 0.0
        if y < 16: return 0.08
        if y < 28: return 0.18
        if y < 38: return 0.30
        return 0.05
    for y in range(MAP_H):
        d = density(y)
        for x in range(MAP_W):
            if grid[y][x] == T_GRASS and rng.random() < d:
                grid[y][x] = T_TREE

# ゾーン別装飾テーブル: (tile_id, base_terrain) のリスト
_ZONE_DECORATIONS = {
    0: [(T_FLOWER, T_GRASS), (T_BUSH, T_GRASS)],           # はじまりのそうげん
    1: [(T_MUSHROOM, T_GRASS), (T_BUSH, T_GRASS)],         # ロジックのもり
    2: [(T_ROCK, T_GRASS), (T_BUSH, T_GRASS)],             # アルゴのやまみち
    3: [(T_CACTUS, T_SAND)],                                # さばくちたい
}

# 世界樹・通信塔の左上座標（2x2配置用）
BIGTREE_POS = (31, 8)   # landmark_events の (32,9) 付近
TOWER_POS = (39, 31)     # landmark_events の (40,32) 付近


def _place_decorations(grid, rng, structures):
    """ゾーン別の装飾タイルを配置する。密度は拠点/道沿い/一般で変える。"""
    # 拠点周辺マスのセット（密度ブースト用）
    near_structure = set()
    for sx, sy in structures:
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                near_structure.add((sx + dx, sy + dy))
    # 道沿いマスのセット
    near_path = set()
    for y in range(MAP_H):
        for x in range(MAP_W):
            if grid[y][x] == T_PATH:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        near_path.add((x + dx, y + dy))

    for y in range(MAP_H):
        zone = get_zone(y)
        deco_list = _ZONE_DECORATIONS.get(zone, [])
        if not deco_list:
            continue
        for x in range(MAP_W):
            tile = grid[y][x]
            # 装飾可能なベースタイルか？
            candidates = [(did, bt) for did, bt in deco_list if tile == bt]
            if not candidates:
                continue
            # 密度を決定
            if (x, y) in near_structure:
                density = 0.25
            elif (x, y) in near_path:
                density = 0.15
            else:
                density = 0.05
            if rng.random() < density:
                deco_id, _ = rng.choice(candidates)
                grid[y][x] = deco_id


def _place_landmarks(grid):
    """2x2 マルチタイルランドマークを配置する。"""
    # 世界樹
    bx, by = BIGTREE_POS
    grid[by][bx] = T_BIGTREE_TL; grid[by][bx + 1] = T_BIGTREE_TR
    grid[by + 1][bx] = T_BIGTREE_BL; grid[by + 1][bx + 1] = T_BIGTREE_BR
    # 通信塔
    tx, ty = TOWER_POS
    grid[ty][tx] = T_TOWER_TL; grid[ty][tx + 1] = T_TOWER_TR
    grid[ty + 1][tx] = T_TOWER_BL; grid[ty + 1][tx + 1] = T_TOWER_BR
    # 周囲を通行可能に（障害物を除去）
    for lx, ly in [BIGTREE_POS, TOWER_POS]:
        for dy in range(-1, 3):
            for dx in range(-1, 3):
                ny, nx = ly + dy, lx + dx
                if 0 <= ny < MAP_H and 0 <= nx < MAP_W:
                    if grid[ny][nx] in {T_TREE, T_MOUNTAIN}:
                        grid[ny][nx] = T_GRASS


def generate_world_map(seed=42):
    rng = random.Random(seed)
    grid = _make_empty(MAP_W, MAP_H, T_GRASS)
    for y in range(MAP_H):
        for x in range(MAP_W):
            if y <= 2 or y >= 48 or x <= 2 or x >= 48:
                grid[y][x] = T_WATER
    PASS_X = 22
    for y in range(15, 18):
        for x in range(3, 48):
            if abs(x - PASS_X) > 1: grid[y][x] = T_MOUNTAIN
    BRIDGE_X = 28
    for y in range(27, 30):
        for x in range(3, 48):
            if abs(x - BRIDGE_X) <= 1: grid[y][x] = T_BRIDGE
            else: grid[y][x] = T_WATER
    for y in range(38, 48):
        for x in range(3, 48):
            if grid[y][x] == T_GRASS: grid[y][x] = T_SAND
    _place_forests(grid, rng)
    cx, cy = CASTLE_POS; grid[cy][cx] = T_CASTLE
    for tx, ty in [TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO]:
        grid[ty][tx] = T_TOWN
    gx, gy = CAVE_GLITCH; grid[gy][gx] = T_CAVE
    passable_all = {T_GRASS, T_SAND, T_TREE} | DECORATION_TILES
    _carve_winding_path(grid, cx, cy, *TOWN_HAJIME, rng, passable_all)
    _carve_winding_path(grid, *TOWN_HAJIME, PASS_X, 16, rng, passable_all)
    _carve_winding_path(grid, PASS_X, 18, *TOWN_LOGIC, rng, passable_all)
    _carve_winding_path(grid, *TOWN_LOGIC, BRIDGE_X, 27, rng, passable_all)
    _carve_winding_path(grid, BRIDGE_X, 30, *TOWN_ALGO, rng, passable_all)
    _carve_winding_path(grid, *TOWN_ALGO, gx, gy, rng, passable_all)
    _carve_winding_path(grid, *TOWN_LOGIC, 38, 24, rng, passable_all)
    _carve_winding_path(grid, *TOWN_ALGO, 10, 36, rng, passable_all)
    structures = [CASTLE_POS, TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO, CAVE_GLITCH]
    for sx, sy in structures:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = sy + dy, sx + dx
                if 0 <= ny < MAP_H and 0 <= nx < MAP_W:
                    if grid[ny][nx] in {T_TREE, T_MOUNTAIN, T_SAND} and (dx != 0 or dy != 0):
                        grid[ny][nx] = T_GRASS
    grid[cy][cx] = T_CASTLE
    for tx, ty in [TOWN_HAJIME, TOWN_LOGIC, TOWN_ALGO]:
        grid[ty][tx] = T_TOWN
    grid[gy][gx] = T_CAVE
    # 装飾とランドマークの配置（道カーブ後に行う）
    _place_decorations(grid, rng, structures)
    _place_landmarks(grid)
    return grid

def generate_dungeon(seed=99):
    rng = random.Random(seed)
    grid = _make_empty(DUNGEON_W, DUNGEON_H, T_WALL)
    rooms = []
    attempts = 0
    while len(rooms) < 6 and attempts < 200:
        attempts += 1
        rw = rng.randint(3, 6); rh = rng.randint(3, 6)
        rx = rng.randint(1, DUNGEON_W - rw - 1)
        ry = rng.randint(1, DUNGEON_H - rh - 1)
        overlap = False
        for (ox, oy, ow, oh) in rooms:
            if rx < ox + ow + 1 and rx + rw + 1 > ox and ry < oy + oh + 1 and ry + rh + 1 > oy:
                overlap = True; break
        if not overlap:
            rooms.append((rx, ry, rw, rh))
            for dy2 in range(rh):
                for dx2 in range(rw):
                    grid[ry + dy2][rx + dx2] = T_FLOOR
    for i in range(len(rooms) - 1):
        ax = rooms[i][0] + rooms[i][2] // 2
        ay = rooms[i][1] + rooms[i][3] // 2
        bx = rooms[i+1][0] + rooms[i+1][2] // 2
        by = rooms[i+1][1] + rooms[i+1][3] // 2
        step = 1 if bx >= ax else -1
        for xx in range(ax, bx + step, step):
            xx = max(1, min(DUNGEON_W - 2, xx))
            grid[ay][xx] = T_FLOOR
        step = 1 if by >= ay else -1
        for yy in range(ay, by + step, step):
            yy = max(1, min(DUNGEON_H - 2, yy))
            grid[yy][bx] = T_FLOOR
    if rooms:
        # 最初の部屋の入り口を確保し、その位置に上り階段を置く
        sx = rooms[0][0] + 1
        sy = rooms[0][1] + 1
        grid[sy][sx] = T_STAIR_UP
        # 最後の部屋を終点として、ボストリガーを1マスだけ置く
        brx, bry, brw, brh = rooms[-1]
        bx = brx + brw // 2
        by = bry + brh // 2
        if (bx, by) == (sx, sy):
            bx = min(brx + brw - 1, bx + 1)
        grid[by][bx] = T_GLITCH_LORD_TRIGGER
    return grid, rooms

def get_zone(tile_y, in_dungeon=False):
    if in_dungeon: return 4
    if tile_y < 16: return 0
    if tile_y < 28: return 1
    if tile_y < 38: return 2
    return 3

# =====================================================================
# ENEMY DATA — assets/enemies.yaml から読み込む
# =====================================================================

_ALL_ENEMIES = ENEMIES


def _build_zone_enemies(enemies):
    """zone -> list[enemy] にグルーピング。イベント敵やボス等は除外。"""
    by_zone: dict[int, list] = {}
    for e in enemies:
        if (
            e.get("is_glitch_lord")
            or e.get("is_professor")
            or e.get("post_clear_only")
            or e.get("is_noise_guardian")
        ):
            continue
        by_zone.setdefault(e["zone"], []).append(e)
    return by_zone


ZONE_ENEMIES = _build_zone_enemies(_ALL_ENEMIES)
GLITCH_LORD_DATA = next(e for e in _ALL_ENEMIES if e.get("is_glitch_lord"))
PROFESSOR_DATA = next(e for e in _ALL_ENEMIES if e.get("is_professor"))
GLITCH_CLONE_DATA = next(e for e in _ALL_ENEMIES if e.get("post_clear_only"))
NOISE_GUARDIAN_DATA = next(e for e in _ALL_ENEMIES if e.get("is_noise_guardian"))

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

# 日本語名 → 英語名 翻訳マップ（BDFフォントが無いとき用）
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
    """日本語名を英語名に変換。マップに無ければそのまま返す。"""
    return NAME_EN_MAP.get(name, name)

TOWN_MENU_LABELS = ("はなす", "ぶきや", "ぼうぐや", "どうぐや", "やどや", "セーブ", "でる")
TOWN_MENU_LABELS_EN = ("TALK", "WEAPONS", "ARMOR", "ITEMS", "INN", "SAVE", "EXIT")
SHOP_KIND_BY_LABEL = {"ぶきや": "weapons", "ぼうぐや": "armors", "どうぐや": "items"}
INN_COST = 10  # gold (フォールバック値; shops.yaml の inn_prices を優先)
SHOPS = _SHOP_BUNDLE["shops"]
INN_PRICES = _SHOP_BUNDLE["inn_prices"]
TOWN_INDEX_BY_POS = {(20, 12): 0, (30, 22): 1, (18, 34): 2}
SPELL_BY_NAME = {s["name"]: s for s in SPELLS}
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


# =====================================================================
# GAME CLASS
# =====================================================================
class Game:
    _instance: "Game | None" = None  # disp() のグローバル参照用

    def __init__(self):
        Game._instance = self
        # デバッグオーバーレイ用のリングバッファ
        self._say_buffer: list[str] = []
        pyxel.init(256, 256, title="Block Quest", fps=30)
        # 日本語フォントの読み込み。Code Maker 等で BDF が読めない環境では
        # None になり、各 UI ラベルとダイアログは英語フォールバックに切り替わる。
        # 日本語フォントは image bank 2 に焼き込んで使う（self.text 経由）。
        # BDF はレガシー互換のため一応試みる（読めなくても問題ない）。
        # has_jp_font は JP_FONT_LAYOUT が登録されている限り常に True。
        try:
            self.font = pyxel.Font("assets/umplus_j10r.bdf")
        except Exception:
            self.font = None
        self.has_jp_font = bool(JP_FONT_LAYOUT)
        self.audio = AudioManager(pyxel)
        self.sfx = SfxSystem(pyxel)
        # has_jp_font に応じて日本語/英語ダイアログを選択（src/generated/dialogue.py 由来）
        dialogue_data = DIALOGUE_JA if self.has_jp_font else DIALOGUE_EN
        self.dialog = StructuredDialogRunner(dialogue_data)

        # Tile/sprite bank position dicts (must init before _render calls)
        self.tile_bank = {}
        self.tile_bank_water2 = None
        self.path_variant_bank = {}
        self.shore_variant_bank = {}
        self.sprite_bank = {}

        # Image bank: .pyxres があればロード、無ければプログラム描画
        self._setup_image_banks()
        # slot 番号の対応は維持しつつ、import 済み SFX は上書きしない
        self.sfx = SfxSystem(pyxel)
        self.audio = AudioManager(pyxel)

        self.world_map = generate_world_map()
        # Tilemap[0] に world_map をベイク or .pyxres から派生
        self._setup_world_tilemap()

        self.dungeon_map = None
        self.dungeon_rooms = None

        self.player = create_initial_player()
        self._apply_av_settings()

        self.state = "splash"
        self.splash_frame = 0
        self.prev_state = "map"
        self.walk_frame = 0
        self.walk_timer = 0
        self.move_cooldown = 0

        # Battle state
        self.battle_enemy = None
        self.battle_enemy_hp = 0
        self.battle_menu = 0
        self.battle_phase = "menu"  # menu, player_attack, enemy_attack, result
        self.battle_text = ""
        self.battle_text_timer = 0
        self.vfx_timer = 0
        self.vfx_type = ""
        self.battle_item_select = 0
        self.battle_spell_select = 0
        self.battle_is_glitch_lord = False
        self.battle_is_professor = False
        self.battle_boss_phase = "phase1"

        # Professor encounter state
        self.professor_intro_lines: list[str] = []
        self.professor_intro_idx = 0
        self.professor_choice_active = False
        self.professor_choice_cursor = 1  # 0=うけいれる / 1=ことわる
        self.professor_ending_lines: list[str] = []
        self.professor_ending_idx = 0

        # Menu state
        self.menu_cursor = 0
        self.menu_sub = None
        self.menu_item_cursor = 0
        self.menu_message = ""

        # Town menu state (D6)
        self.town_menu_cursor = 0
        self.town_menu_pos: tuple[int, int] | None = None
        self.last_town_pos: tuple[int, int] | None = None

        # Shop state (Task #7)
        self.shop_kind: str = ""
        self.shop_inventory: list[int] = []
        self.shop_cursor: int = 0
        self.shop_message: str = ""

        # A-button cooldown for map state (D13)
        # 「でる」直後 / ロード直後の暴発を1回だけ防ぐ
        self._a_cooldown = False

        # Title cursor (D8)
        self.title_cursor = 0  # 0=はじめから, 1=つづきから, 2=せってい
        self.settings_cursor = 0
        self.settings_origin = "title"

        # Save store (D1/D12/D17)
        save_path = Path(__file__).resolve().parent / "save.json"
        self.save_store = make_save_store(save_path)
        self._has_save = self.save_store.exists()

        # Message state
        self.msg_lines = []
        self.msg_index = 0
        self.msg_callback = None
        self.ending_lines = []

        # Debug mode
        self.debug_mode = False
        self.debug_seq = []
        self.input_state = InputStateTracker()

        # Camera
        self.cam_x = 0
        self.cam_y = 0

        # Dungeon return position
        self.world_return_x = 0
        self.world_return_y = 0

        self._sync_audio()

    def start(self):
        """ゲームループに入る。`Game()` 後の `disp()` 呼び出しを有効にするため
        `__init__` から `pyxel.run` を分離してある。"""
        pyxel.run(self.update, self.draw)

    # ----- Image bank setup (.pyxres support) -----
    def _setup_image_banks(self):
        """画像・サウンドバンクの初期化。

        重要: .pyxres は **画像バンクと音バンクの両方** を含む。
        この関数で `pyxel.load()` すると、AudioManager / SfxSystem が
        既に書き込んだ sounds 0-42 も .pyxres の内容で上書きされる。

        これは仕様。**Code Maker / `pyxel edit` で編集した内容を真とする**。
        コード側の chiptune_tracks.py / sfx_system.py を変更しても、
        .pyxres を削除しない限り反映されない。

        - レイアウト辞書はいつも計算する（コードとデータの位置対応）
        - assets/blockquest.pyxres / my_resource.pyxres があれば load
        - 無ければプログラム描画して save（初回・破損時のみ）
        """
        self._layout_tile_bank()
        self._layout_sprite_bank()
        self._build_reverse_tile_map()
        self._pyxres_loaded = False
        self._pyxres_path: Path | None = None

        # Code Maker互換: my_resource.pyxres をルート直下から探し、無ければ assets/ から
        root = Path(__file__).resolve().parent
        stage_browser_imported_resource(root)
        candidates = [
            root / "my_resource.pyxres",
            root / "assets" / "blockquest.pyxres",
        ]
        pyxres_path = next((p for p in candidates if p.exists()), candidates[-1])
        self._pyxres_path = pyxres_path
        if pyxres_path.exists():
            try:
                pyxel.load(str(pyxres_path))
                self._pyxres_loaded = True
                return
            except Exception as exc:
                print(f"[image_bank] failed to load {pyxres_path}: {exc}; regenerating")

        # 初回 or 破損時：プログラム描画。.pyxres 保存は tilemap ベイク後に行う
        self._paint_tile_bank()
        self._paint_sprite_bank()
        self._paint_jp_font_bank()

    def _paint_jp_font_bank(self):
        """`JP_FONT_BITMAPS` を image bank 2 に焼き込む。

        各セルは GLYPH_W × GLYPH_H ピクセル。前景色は 7（白）で固定し、
        描画時に `pyxel.pal()` で目的の色に変換する。
        """
        bank = pyxel.images[JP_FONT_IMAGE_BANK]
        # クリア（全 0 = 黒 = 背景）
        for py in range(256):
            for px in range(256):
                bank.pset(px, py, 0)
        for ch, rows in JP_FONT_BITMAPS.items():
            col, row = JP_FONT_LAYOUT[ch]
            ox = col * JP_FONT_GLYPH_W
            oy = row * JP_FONT_GLYPH_H
            for ry in range(JP_FONT_GLYPH_H):
                bits = rows[ry] if ry < len(rows) else 0
                for rx in range(JP_FONT_GLYPH_W):
                    if bits & (1 << (JP_FONT_GLYPH_W - 1 - rx)):
                        bank.pset(ox + rx, oy + ry, 7)

    def _build_reverse_tile_map(self):
        """image bank pixel 座標 → 元の tile_id への逆引き辞書。

        tilemap[0] から world_map を派生するときに使う。
        path/shore variants は基底タイル (T_PATH / T_WATER) として復元する。
        """
        self.tile_id_by_pixel = {}
        for tid, (u, v) in self.tile_bank.items():
            self.tile_id_by_pixel[(u, v)] = tid
        for (u, v) in self.path_variant_bank.values():
            self.tile_id_by_pixel[(u, v)] = T_PATH
        for (u, v) in self.shore_variant_bank.values():
            self.tile_id_by_pixel[(u, v)] = T_WATER
        if self.tile_bank_water2:
            self.tile_id_by_pixel[self.tile_bank_water2] = T_WATER

    # ----- World tilemap setup (.pyxres tilemap[0] support) -----
    # Code Maker / pyxel edit は tilemap[N] のデフォルト imgsrc を N と仮定して
    # 表示するため、tilemap[1] を使うとイメージバンク 1（敵スプライト）が表示されて
    # しまう。これを避けるため、ワールドマップとダンジョンを **同じ tilemap[0]** に
    # 配置して、画像バンク 0 だけを参照させる。
    DUNGEON_TM_OFFSET_Y = 110  # ワールド (0..99) の下に余白を入れて配置

    def _tile_bank_layout_valid(self):
        """イメージバンク 0 のピクセルが現在の TILE_DATA と一致するか検証する。

        TILE_DATA の順序が変わるとレイアウト辞書の座標がずれ、
        古い .pyxres のイメージバンクと不一致になる。全タイルの
        先頭行をサンプリングして不一致を検出する。
        """
        bank = pyxel.images[0]
        try:
            for tid, data in TILE_DATA.items():
                pos = self.tile_bank.get(tid)
                if pos is None:
                    return False
                u, v = pos
                for rx, expected in enumerate(data[0]):
                    if bank.pget(u + rx, v) != expected:
                        return False
        except Exception:
            return False
        return True

    def _setup_world_tilemap(self):
        """World map と dungeon を `pyxel.tilemaps[0]` と同期する。

        - tilemap[0] 上部 (0,0)..(99,99): ワールドマップ
        - tilemap[0] 下部 (0,110)..(39,149): 共有ダンジョン
        - .pyxres から banks がロード済み → tilemap[0] の両領域から派生
        - 初回 or .pyxres 不在 → 手続き生成 → ベイク → .pyxres 保存
        """
        try:
            pyxel.tilemaps[0].imgsrc = 0
        except Exception:
            pass

        # 共有ダンジョンを生成（固定シード = 99）
        dgrid, drooms = generate_dungeon(seed=99)
        self.dungeon_template = dgrid
        self.dungeon_template_rooms = drooms
        if drooms:
            self.dungeon_spawn = (drooms[0][0] + 1, drooms[0][1] + 1)
        else:
            self.dungeon_spawn = (1, 1)

        if self._pyxres_loaded:
            if not self._tile_bank_layout_valid():
                # TILE_DATA の順序が変わってイメージバンクとずれている。
                # 古い tilemap を信用できないので再描画＋再ベイクする。
                print("[tilemap] tile bank layout changed — regenerating image banks")
                self._paint_tile_bank()
                self._paint_sprite_bank()
                self._paint_jp_font_bank()
                self._bake_world_to_tilemap()
                self._bake_dungeon_to_tilemap()
                # Web環境では pyxel.save がダウンロードを誘発するので保存しない
                if self._pyxres_path is not None and sys.platform != "emscripten":
                    try:
                        pyxel.save(str(self._pyxres_path))
                        print(f"[tilemap] updated {self._pyxres_path}")
                    except Exception as exc:
                        print(f"[tilemap] could not save .pyxres: {exc}")
            else:
                self._derive_world_from_tilemap()
                self._derive_dungeon_from_tilemap()
                # D3: オートタイル変種を再計算して tilemap[0] に書き戻す。
                # Code Maker で基底タイルを配置した場合、周辺タイルとの
                # 繋がりをゲーム側で正しく再計算する必要がある。
                self._bake_world_to_tilemap()
                self._bake_dungeon_to_tilemap()
        else:
            self._bake_world_to_tilemap()
            self._bake_dungeon_to_tilemap()
            # ここで初めて .pyxres を保存（banks + tilemap）
            # Web環境では pyxel.save がダウンロードを誘発するので保存しない
            if self._pyxres_path is not None and sys.platform != "emscripten":
                try:
                    self._pyxres_path.parent.mkdir(parents=True, exist_ok=True)
                    pyxel.save(str(self._pyxres_path))
                    print(f"[image_bank] generated {self._pyxres_path}")
                except Exception as exc:
                    print(f"[image_bank] could not save .pyxres: {exc}")

    def _bake_dungeon_to_tilemap(self):
        """共有ダンジョン (self.dungeon_template) を tilemap[0] のオフセット領域に焼き込む。"""
        tilemap = pyxel.tilemaps[0]
        dg = self.dungeon_template
        oy = self.DUNGEON_TM_OFFSET_Y
        for y in range(len(dg)):
            for x in range(len(dg[0])):
                tile = dg[y][x]
                u, v = self.tile_bank.get(tile, self.tile_bank[T_GRASS])
                tu, tv = u // 8, v // 8
                tilemap.pset(2 * x,     oy + 2 * y,     (tu,     tv))
                tilemap.pset(2 * x + 1, oy + 2 * y,     (tu + 1, tv))
                tilemap.pset(2 * x,     oy + 2 * y + 1, (tu,     tv + 1))
                tilemap.pset(2 * x + 1, oy + 2 * y + 1, (tu + 1, tv + 1))

    def _derive_dungeon_from_tilemap(self):
        """tilemap[0] のオフセット領域から共有ダンジョンを組み立てる（編集を反映）。"""
        tilemap = pyxel.tilemaps[0]
        dg = self.dungeon_template
        oy = self.DUNGEON_TM_OFFSET_Y
        derived = []
        _miss = 0
        for y in range(len(dg)):
            row = []
            for x in range(len(dg[0])):
                tu, tv = tilemap.pget(2 * x, oy + 2 * y)
                key = (tu * 8, tv * 8)
                tid = self.tile_id_by_pixel.get(key, T_FLOOR)
                if key not in self.tile_id_by_pixel:
                    _miss += 1
                row.append(tid)
            derived.append(row)
        if _miss:
            print(f"[tilemap] dungeon derive: {_miss} tiles fell back to T_FLOOR")
        self.dungeon_template = derived
        # 階段の位置を再検索（編集で動いている可能性）
        for y in range(len(derived)):
            for x in range(len(derived[0])):
                if derived[y][x] == T_STAIR_UP:
                    self.dungeon_spawn = (x, y)
                    return

    def _bake_world_to_tilemap(self):
        """self.world_map を tilemap[0] に焼き込む。

        Code Maker / Resource Editor で見える形を実ゲームと揃えるため、
        道と水辺はここで見た目用の変種タイルまで解決して書き込む。
        逆変換時は _build_reverse_tile_map() で基底タイルへ戻す。
        """
        tilemap = pyxel.tilemaps[0]
        wm = self.world_map
        for y in range(MAP_H):
            for x in range(MAP_W):
                tile = wm[y][x]
                if tile == T_PATH:
                    variant = get_path_variant(wm, x, y)
                    u, v = self.path_variant_bank.get(
                        id(variant),
                        self.tile_bank[T_PATH],
                    )
                elif tile == T_WATER:
                    variant = get_shore_variant(wm, x, y)
                    if variant is None:
                        u, v = self.tile_bank[T_WATER]
                    else:
                        u, v = self.shore_variant_bank.get(
                            id(variant),
                            self.tile_bank[T_WATER],
                        )
                else:
                    u, v = self.tile_bank.get(tile, self.tile_bank[T_GRASS])
                tu, tv = u // 8, v // 8
                tilemap.pset(2 * x,     2 * y,     (tu,     tv))
                tilemap.pset(2 * x + 1, 2 * y,     (tu + 1, tv))
                tilemap.pset(2 * x,     2 * y + 1, (tu,     tv + 1))
                tilemap.pset(2 * x + 1, 2 * y + 1, (tu + 1, tv + 1))


    def _derive_world_from_tilemap(self):
        """tilemap[0] から self.world_map を組み立てる（編集を反映）。"""
        tilemap = pyxel.tilemaps[0]
        derived = []
        _miss = 0
        for y in range(MAP_H):
            row = []
            for x in range(MAP_W):
                tu, tv = tilemap.pget(2 * x, 2 * y)
                key = (tu * 8, tv * 8)
                tid = self.tile_id_by_pixel.get(key, T_GRASS)
                if key not in self.tile_id_by_pixel:
                    _miss += 1
                row.append(tid)
            derived.append(row)
        if _miss:
            print(f"[tilemap] world derive: {_miss} tiles fell back to T_GRASS")
        self.world_map = derived

    # ----- Image bank: layout (positions) と paint (pset) を分離 -----
    # 通常起動時は .pyxres から load してレイアウト辞書だけ計算する。
    # .pyxres が無ければ paint してから save する（初回のみ）。

    def _tile_iter(self):
        """タイルバンクに格納する順序を返す。レイアウト/ペイント両方で使う。

        yields: (kind, key, data)
            kind: "tile" | "water2" | "path" | "shore"
            key: tile id / "water2" / id(pdata)
            data: 16x16 のピクセル配列（paint時のみ使う）
        """
        for tid, tdata in TILE_DATA.items():
            yield ("tile", tid, tdata)
        yield ("water2", "water2", TILE_WATER2)
        for _name, pdata in [
            ("V", PATH_V), ("H", PATH_H), ("CROSS", PATH_CROSS),
            ("SE", PATH_SE), ("SW", PATH_SW), ("NE", PATH_NE), ("NW", PATH_NW),
            ("T_NES", PATH_T_NES), ("T_NWS", PATH_T_NWS),
            ("T_EWS", PATH_T_EWS), ("T_NEW", PATH_T_NEW),
        ]:
            yield ("path", id(pdata), pdata)
        for _name, sdata in [
            ("N", SHORE_N), ("S", SHORE_S), ("W", SHORE_W), ("E", SHORE_E),
            ("NE", SHORE_NE), ("NW", SHORE_NW), ("SE", SHORE_SE), ("SW", SHORE_SW),
        ]:
            yield ("shore", id(sdata), sdata)

    def _layout_tile_bank(self):
        """レイアウト辞書のみ計算（pset なし）。"""
        self.tile_bank = {}
        self.path_variant_bank = {}
        self.shore_variant_bank = {}
        col = 0; row = 0
        for kind, key, _data in self._tile_iter():
            bx = col * 16; by = row * 16
            if kind == "tile":
                self.tile_bank[key] = (bx, by)
            elif kind == "water2":
                self.tile_bank_water2 = (bx, by)
            elif kind == "path":
                self.path_variant_bank[key] = (bx, by)
            elif kind == "shore":
                self.shore_variant_bank[key] = (bx, by)
            col += 1
            if col >= 16:
                col = 0; row += 1

    def _paint_tile_bank(self):
        """pset でタイル絵をバンクに焼き込む（.pyxres 生成時のみ呼ぶ）。"""
        bank = pyxel.images[0]
        col = 0; row = 0
        for _kind, _key, data in self._tile_iter():
            bx = col * 16; by = row * 16
            for py in range(16):
                for px in range(16):
                    bank.pset(bx + px, by + py, data[py][px])
            col += 1
            if col >= 16:
                col = 0; row += 1

    def _render_tiles_to_bank(self):
        """互換ラッパー：_layout + _paint を順に呼ぶ。"""
        self._layout_tile_bank()
        self._paint_tile_bank()

    def _sprite_iter(self):
        sprites_to_render = {
            "hero_down": HERO_DOWN, "hero_walk": HERO_DOWN_WALK,
        }
        sprites_to_render.update(ENEMY_SPRITES)
        for name, sdata in sprites_to_render.items():
            yield (name, sdata)

    def _layout_sprite_bank(self):
        self.sprite_bank = {}
        col = 0; row = 0
        for name, _data in self._sprite_iter():
            bx = col * 16; by = row * 16
            self.sprite_bank[name] = (bx, by)
            col += 1
            if col >= 16:
                col = 0; row += 1

    def _paint_sprite_bank(self):
        bank = pyxel.images[1]
        col = 0; row = 0
        for _name, sdata in self._sprite_iter():
            bx = col * 16; by = row * 16
            for py in range(16):
                for px in range(16):
                    bank.pset(bx + px, by + py, sdata[py][px])
            col += 1
            if col >= 16:
                col = 0; row += 1

    def _render_sprites_to_bank(self):
        """互換ラッパー：_layout + _paint を順に呼ぶ。"""
        self._layout_sprite_bank()
        self._paint_sprite_bank()

    # -----------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------
    def _btn(self, button_names):
        return self.input_state.btn(button_names)

    def _btnp(self, button_names):
        return self.input_state.btnp(button_names)

    def update(self):
        self.input_state.update(pyxel)

        # 緊急脱出: F1 で強制的にフィールド (map) へ戻す
        # 「入力が効かない」と感じたときの最終手段
        if pyxel.btnp(pyxel.KEY_F1):
            self.state = "map"
            self.move_cooldown = 0
            self._a_cooldown = False
            self.msg_lines = []
            self.msg_index = 0
            self.msg_callback = None

        # Debug code: up up down down
        if self._btnp(UP_BUTTONS):
            self.debug_seq.append("U")
        elif self._btnp(DOWN_BUTTONS):
            self.debug_seq.append("D")
        else:
            if (
                self._btnp(LEFT_BUTTONS)
                or self._btnp(RIGHT_BUTTONS)
                or self._btnp(CONFIRM_BUTTONS)
                or self._btnp(CANCEL_BUTTONS)
            ):
                self.debug_seq = []

        # 無限に伸びるのを防ぐ
        if len(self.debug_seq) > 8:
            self.debug_seq = self.debug_seq[-4:]

        if len(self.debug_seq) >= 4:
            if self.debug_seq[-4:] == ["U", "U", "D", "D"]:
                self.debug_mode = not self.debug_mode
                self.debug_seq = []

        if self.state == "splash":
            self.update_splash()
        elif self.state == "title":
            self.update_title()
        elif self.state == "map":
            self.update_map()
        elif self.state == "battle":
            self.update_battle()
        elif self.state == "menu":
            self.update_menu()
        elif self.state == "settings":
            self.update_settings()
        elif self.state == "message":
            self.update_message()
        elif self.state == "town":
            self.update_town()
        elif self.state == "town_menu":
            self.update_town_menu()
        elif self.state == "professor_intro":
            self.update_professor_intro()
        elif self.state == "professor_ending_main":
            self.update_professor_ending_main()
        elif self.state == "professor_ending_accepted":
            self.update_professor_ending_accepted()
        elif self.state == "shop":
            self.update_shop()
        elif self.state == "ending":
            self.update_ending()
        elif self.state == "ai_help":
            self.update_ai_help()

        self._sync_audio()

    def update_splash(self):
        self.splash_frame += 1
        # 90フレーム = 約3秒で自動遷移。任意キーでもスキップ可能
        if self.splash_frame >= 90 or self._btnp(CONFIRM_BUTTONS) or self._btnp(CANCEL_BUTTONS):
            self.state = "title"

    def update_title(self):
        if self._btnp(UP_BUTTONS):
            self.title_cursor = (self.title_cursor - 1) % 3
            self.sfx.play("cursor")
            return
        if self._btnp(DOWN_BUTTONS):
            self.title_cursor = (self.title_cursor + 1) % 3
            self.sfx.play("cursor")
            return
        if self._btnp(CONFIRM_BUTTONS) or self._btnp(TITLE_START_BUTTONS):
            self.sfx.play("select")
            if self.title_cursor == 0:
                # はじめから: プレイヤー状態をクリーンに作り直す
                settings = {
                    "bgm_enabled": self.player.get("bgm_enabled", True),
                    "sfx_enabled": self.player.get("sfx_enabled", True),
                    "vfx_enabled": self.player.get("vfx_enabled", True),
                }
                self.player = create_initial_player()
                self.player.update(settings)
                self._apply_av_settings()
                self.state = "map"
                return
            if self.title_cursor == 2:
                self._open_settings("title")
                return
            # つづきから — has_save が False ならグレーアウト（D8 / P9）
            if not self._has_save:
                return
            self._do_load()

    def _do_load(self):
        snap = self.save_store.load()
        if snap is None:
            # 破損やバージョン未来のセーフティネット（シナリオ6 例外系）
            self._has_save = False
            self.show_message([NO_RECORD_MSG])
            self.prev_state = "title"
            self.state = "message"
            return
        restored = restore_snapshot(snap)
        for key, value in restored["player"].items():
            self.player[key] = value
        self._apply_av_settings()
        tx, ty = restored["town_pos"]
        self.player["x"] = tx
        self.player["y"] = ty
        self.player["in_dungeon"] = False
        self.dungeon_map = None
        # D13/D15: ロード直後の暴発を防ぐため A クールダウンを立てる
        self._a_cooldown = True
        self.show_message([LOAD_OK_MSG])
        self.prev_state = "map"
        self.state = "message"

    def update_map(self):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # A-button cooldown (D13): 「でる」直後やロード直後の1フレーム目に
        # 残っている A 押下を1回だけ捨てて、町メニューが暴発しないようにする。
        if self._a_cooldown:
            if self._btnp(CONFIRM_BUTTONS):
                self._a_cooldown = False
                return
            # 何か別の入力があれば、そのまま通常処理へ（次フレームで解除される）
            self._a_cooldown = False

        # Open menu
        if self._btnp(CANCEL_BUTTONS):
            self.state = "menu"
            self.menu_cursor = 0
            self.menu_sub = None
            return

        p = self.player
        dx, dy = 0, 0
        if self._btn(UP_BUTTONS): dy = -1
        elif self._btn(DOWN_BUTTONS): dy = 1
        elif self._btn(LEFT_BUTTONS): dx = -1
        elif self._btn(RIGHT_BUTTONS): dx = 1

        if dx != 0 or dy != 0:
            nx, ny = p["x"] + dx, p["y"] + dy
            current_map = self.dungeon_map if p["in_dungeon"] else self.world_map
            mw = len(current_map[0]); mh = len(current_map)

            if 0 <= nx < mw and 0 <= ny < mh:
                tile = current_map[ny][nx]
                if tile not in IMPASSABLE:
                    old_zone = get_zone(p["y"], p["in_dungeon"])
                    p["x"] = nx; p["y"] = ny
                    self.sfx.play("step")
                    self.move_cooldown = 4
                    self.walk_timer += 1
                    new_zone = get_zone(p["y"], p["in_dungeon"])
                    p["max_zone_reached"] = max(
                        p["max_zone_reached"], new_zone,
                    )
                    if new_zone != old_zone:
                        self.sfx.play("zone_change")
                    if self.walk_timer >= 2:
                        self.walk_frame = 1 - self.walk_frame
                        self.walk_timer = 0

                    # Poison tick: 数歩ごとにHPを少し削る
                    if p.get("poisoned"):
                        self._poison_step_counter = getattr(self, "_poison_step_counter", 0) + 1
                        if self._poison_step_counter >= 4:
                            self._poison_step_counter = 0
                            p["hp"] = max(1, p["hp"] - 2)
                            self.sfx.play("poison_tick")

                    # Check events after move
                    if self._check_landmark_events():
                        return
                    self._check_tile_events(tile, nx, ny)
            elif p["in_dungeon"]:
                # Exit dungeon at edges
                p["in_dungeon"] = False
                p["x"] = self.world_return_x
                p["y"] = self.world_return_y
                self.dungeon_map = None
                self._enter_message(
                    self._dialog_lines("dungeon.glitch.exit"),
                    callback=self._dungeon_exit_callback(),
                )
                return

    def _check_tile_events(self, tile, nx, ny):
        p = self.player

        # Dungeon stair → exit back to overworld
        if p["in_dungeon"] and tile == T_STAIR_UP:
            p["in_dungeon"] = False
            p["x"] = self.world_return_x
            p["y"] = self.world_return_y
            self.dungeon_map = None
            self._enter_message(
                self._dialog_lines("dungeon.glitch.exit"),
                callback=self._dungeon_exit_callback(),
            )
            return

        if p["in_dungeon"] and tile == T_GLITCH_LORD_TRIGGER:
            if not p.get("glitch_lord_defeated"):
                self._start_battle(GLITCH_LORD_DATA, is_glitch_lord=True)
            return

        # Town entry → open the town menu (D6)
        if tile == T_TOWN:
            self.town_menu_pos = (nx, ny)
            self.town_menu_cursor = 0
            self.state = "town_menu"
            return

        # Castle still uses the legacy in-place dialog
        if tile == T_CASTLE:
            # クリア後の隠し導線：プロフェッサー編へ
            if self.player.get("glitch_lord_defeated") and (nx, ny) == (25, 6):
                self._enter_professor_intro()
                return
            scene = TOWN_DIALOG_SCENES.get((nx, ny))
            if scene is None:
                lines = ["..."]
            else:
                lines = self._dialog_lines(
                    scene,
                    ProfessorPhase=self._professor_phase(),
                )
            self.show_message(lines)
            self.state = "town"
            return

        # Cave entry (dungeon)
        if tile == T_CAVE and not p["in_dungeon"]:
            # 洞窟ミッション: 通信塔のノイズを倒すまで根がブロック
            if not p.get("towerNoiseCleared"):
                self._enter_message(self._dialog_lines("cave.blocked"))
                return
            # 初回クリア時: 根がほどける演出
            if not getattr(self, "_cave_unblock_shown", False):
                self._cave_unblock_shown = True
                self._enter_message(self._dialog_lines("cave.unblocked"))
                return
            self.sfx.play("dungeon_in")
            self.world_return_x = nx; self.world_return_y = ny
            # 全洞窟は同じ共有ダンジョンに通じる（tilemap[1] に保存・編集可）
            self.dungeon_map = [row[:] for row in self.dungeon_template]
            self.dungeon_rooms = self.dungeon_template_rooms
            p["in_dungeon"] = True
            # 階段位置にスポーン（最初の部屋の入り口）
            sx, sy = self.dungeon_spawn
            p["x"] = sx
            p["y"] = sy
            self._enter_message(self._dialog_lines("dungeon.glitch.enter"))
            return

        # Random encounter
        if not self.debug_mode:
            if p["in_dungeon"] and p["glitch_lord_defeated"]:
                return
            rate = ENCOUNTER_RATES.get(tile, 0)
            if rate > 0 and random.random() < rate:
                zone = get_zone(p["y"], p["in_dungeon"])
                enemies = ZONE_ENEMIES.get(zone, ZONE_ENEMIES[0])
                enemy_template = random.choice(enemies)
                self._start_battle(enemy_template, is_glitch_lord=False)

    def _check_landmark_events(self):
        if self.player["in_dungeon"]:
            return False

        landmark = find_landmark_at(self.player["x"], self.player["y"])
        if landmark is None:
            return False

        p = self.player
        scene = self._resolve_landmark_scene(landmark)
        if scene is None:
            return False

        # フラグ更新
        if landmark.flag_name == "landmarkTreeSeen":
            if not p.get("landmarkTreeSeen"):
                p["landmarkTreeSeen"] = True
                p["treeAsked"] = True
        elif landmark.flag_name == "landmarkTowerSeen":
            if not p.get("landmarkTowerSeen"):
                p["landmarkTowerSeen"] = True

        # 通信塔クエスト: treeAsked=true で初めて来た → ノイズガーディアン戦
        if scene == "landmark.tower.quest":
            self._enter_message(
                self._dialog_lines(scene),
                callback=self._start_noise_guardian_battle,
            )
            return True

        # エピローグフラグ
        if landmark.epilogue_flag and scene == landmark.epilogue_scene:
            p[landmark.epilogue_flag] = True

        self._enter_message(self._dialog_lines(scene))
        return True

    def _resolve_landmark_scene(self, landmark):
        """洞窟ミッションのフラグに応じてランドマークのシーンを決定する。"""
        p = self.player
        cleared = p.get("towerNoiseCleared", False)
        tree_asked = p.get("treeAsked", False)

        if landmark.flag_name == "landmarkTreeSeen":
            if not p.get("landmarkTreeSeen"):
                return "landmark.tree.first"
            if cleared:
                # クリア後: 初回はcleared演出、以降はランダム
                if not getattr(self, "_tree_cleared_shown", False):
                    self._tree_cleared_shown = True
                    return "landmark.tree.cleared"
                return random.choice([
                    "landmark.tree.repeat",
                    "landmark.tree.repeat_02",
                    "landmark.tree.repeat_03",
                ])
            # treeAsked=true, まだクリアしてない
            return "landmark.tree.waiting"

        if landmark.flag_name == "landmarkTowerSeen":
            if not p.get("landmarkTowerSeen"):
                return "landmark.tower.first"
            if cleared:
                # エピローグ（ボス撃破後）
                if (
                    p.get("glitch_lord_defeated")
                    and landmark.epilogue_scene
                    and not p.get(landmark.epilogue_flag, False)
                ):
                    return landmark.epilogue_scene
                return random.choice([
                    "landmark.tower.repeat",
                    "landmark.tower.repeat_02",
                    "landmark.tower.repeat_03",
                ])
            # 世界樹に相談済み → クエスト戦闘
            if tree_asked:
                return "landmark.tower.quest"
            # まだ世界樹に行ってない → リピート
            return "landmark.tower.repeat"

        # その他のランドマーク（将来用）
        return None

    def _start_noise_guardian_battle(self):
        """ノイズガーディアン強制戦闘を開始する。"""
        self._noise_guardian_battle = True
        self._start_battle(NOISE_GUARDIAN_DATA, is_glitch_lord=False)
        self.battle_text = self._dialog_text("boss.noise_guardian.intro")

    def _on_noise_guardian_defeated(self):
        """ノイズガーディアン撃破後の処理。"""
        self.player["towerNoiseCleared"] = True
        self._noise_guardian_battle = False
        self._enter_message(self._dialog_lines("landmark.tower.epilogue"))

    def _check_noise_guardian_phase(self):
        """ノイズガーディアン戦のフェーズメッセージを差し込む。"""
        max_hp = self.battle_enemy["hp"]
        if max_hp <= 0:
            return
        ratio = self.battle_enemy_hp / max_hp
        ng_phases = {0.75: "75", 0.40: "40", 0.10: "10"}
        for threshold, phase_key in sorted(ng_phases.items()):
            if ratio < threshold:
                new_phase = phase_key
                break
        else:
            new_phase = "100"
        if new_phase != self.battle_boss_phase and new_phase != "100":
            self.battle_boss_phase = new_phase
            msg = self._dialog_text(f"boss.noise_guardian.phase_{new_phase}")
            if msg:
                self.battle_text = (self.battle_text + " " + msg).strip()

    def _start_battle(self, enemy_template, is_glitch_lord=False, is_professor=False):
        self.sfx.play("encounter")
        self.battle_enemy = dict(enemy_template)
        self.battle_enemy_hp = enemy_template["hp"]
        self.battle_menu = 0
        self.battle_phase = "menu"
        self.battle_text = ""
        self.battle_text_timer = 0
        self.battle_item_select = 0
        self.battle_spell_select = 0
        self.battle_is_glitch_lord = is_glitch_lord
        self.battle_is_professor = is_professor
        self.battle_boss_phase = "phase1" if not is_professor else "100"
        if is_glitch_lord:
            self.battle_text = self._dialog_text("boss.glitch.intro")
        self.state = "battle"

    def update_battle(self):
        if self.vfx_timer > 0:
            self.vfx_timer -= 1
        if self.battle_phase == "menu":
            if self._btnp(UP_BUTTONS):
                self.battle_menu = (self.battle_menu - 1) % 4
                self.sfx.play("cursor")
            if self._btnp(DOWN_BUTTONS):
                self.battle_menu = (self.battle_menu + 1) % 4
                self.sfx.play("cursor")
            if self._btnp(CONFIRM_BUTTONS):
                self.sfx.play("select")
                if self.battle_menu == 0:  # Attack
                    self._do_player_attack()
                elif self.battle_menu == 1:  # じゅもん
                    if self.player["spells"]:
                        self.battle_phase = "spell_select"
                        self.battle_spell_select = 0
                    else:
                        self.battle_text = "まだ じゅもんを おぼえていない"
                elif self.battle_menu == 2:  # Item
                    self.battle_phase = "item_select"
                    self.battle_item_select = 0
                elif self.battle_menu == 3:  # Run
                    if not self.battle_is_glitch_lord and random.random() < 0.5:
                        self.battle_text = self._dialog_text("battle.normal.run.success")
                        self.battle_phase = "result"
                        self.battle_text_timer = 60
                    else:
                        scene_name = (
                            "boss.glitch.run.fail"
                            if self.battle_is_glitch_lord
                            else "battle.normal.run.fail"
                        )
                        self.battle_text = self._dialog_text(scene_name)
                        self.battle_phase = "player_attack"
                        self.battle_text_timer = 30

        elif self.battle_phase == "spell_select":
            spells = self.player["spells"]
            if not spells:
                self.battle_phase = "menu"
                return
            if self._btnp(UP_BUTTONS):
                self.battle_spell_select = max(0, self.battle_spell_select - 1)
                self.sfx.play("cursor")
            if self._btnp(DOWN_BUTTONS):
                self.battle_spell_select = min(len(spells) - 1, self.battle_spell_select + 1)
                self.sfx.play("cursor")
            if self._btnp(CANCEL_BUTTONS):
                self.sfx.play("cancel")
                self.battle_phase = "menu"
            if self._btnp(CONFIRM_BUTTONS):
                self.sfx.play("select")
                spell_name = spells[self.battle_spell_select]
                spell = SPELL_BY_NAME.get(spell_name)
                if spell is None:
                    self.battle_phase = "menu"
                    return
                if self.player["mp"] < spell["mp"]:
                    self.battle_text = "MPが たりない！"
                    return
                self.player["mp"] -= spell["mp"]
                self.sfx.play("magic")
                self._start_vfx("flash_white")
                self.battle_text = self._apply_spell_effect(spell)
                self.battle_phase = "player_attack"
                self.battle_text_timer = 30

        elif self.battle_phase == "item_select":
            items = self.player["items"]
            if not items:
                self.battle_phase = "menu"
                return
            if self._btnp(UP_BUTTONS):
                self.battle_item_select = max(0, self.battle_item_select - 1)
                self.sfx.play("cursor")
            if self._btnp(DOWN_BUTTONS):
                self.battle_item_select = min(len(items) - 1, self.battle_item_select + 1)
                self.sfx.play("cursor")
            if self._btnp(CANCEL_BUTTONS):
                self.sfx.play("cancel")
                self.battle_phase = "menu"
            if self._btnp(CONFIRM_BUTTONS):
                self.sfx.play("select")
                item = items[self.battle_item_select]
                item_data = ITEMS[item["id"]]
                # warp はバトル中無効
                if item_data["type"] == "warp":
                    self.battle_text = "せんとうちゅうはつかえない…"
                    self.battle_phase = "enemy_attack"
                    self.battle_text_timer = 30
                else:
                    msg = self._use_item(item_data)
                    if not msg:
                        # HP満タンなど使えなかった → アイテム選択に戻る
                        self.battle_text = "HPがまんたんで つかえない"
                        self.battle_text_timer = 30
                    else:
                        self.battle_text = msg
                        item["qty"] -= 1
                        if item["qty"] <= 0:
                            items.pop(self.battle_item_select)
                        self.battle_phase = "enemy_attack"
                        self.battle_text_timer = 30

        elif self.battle_phase == "player_attack":
            # 決定ボタン押しっぱなしで 400ms (12 frame @ 30fps) まで早送り
            if self._btn(CONFIRM_BUTTONS) and self.battle_text_timer > 12:
                self.battle_text_timer = 12
            self.battle_text_timer -= 1
            if self.battle_text_timer <= 0:
                if self.battle_enemy_hp <= 0:
                    self._battle_victory()
                else:
                    self._do_enemy_attack()

        elif self.battle_phase == "enemy_attack":
            if self._btn(CONFIRM_BUTTONS) and self.battle_text_timer > 12:
                self.battle_text_timer = 12
            self.battle_text_timer -= 1
            if self.battle_text_timer <= 0:
                if self.player["hp"] <= 0:
                    self._battle_defeat()
                else:
                    self.battle_phase = "menu"

        elif self.battle_phase == "result":
            # 結果表示も同様に押しっぱなし高速化（400ms 後に自動前進）
            if self._btn(CONFIRM_BUTTONS) and self.battle_text_timer > 12:
                self.battle_text_timer = 12
            self.battle_text_timer -= 1
            if self.battle_text_timer <= 0:
                if self._btn(CONFIRM_BUTTONS) or self._btnp(CONFIRM_BUTTONS) or self.battle_text_timer < -30:
                    if self.player["hp"] <= 0:
                        # Defeat: lose half gold, restore HP
                        self.player["gold"] = self.player["gold"] // 2
                        self.player["hp"] = self.player["max_hp"]
                        self.player["x"], self.player["y"] = CASTLE_POS
                        self.player["in_dungeon"] = False
                        self.state = "map"
                    elif self.battle_is_professor and self.battle_enemy_hp <= 0:
                        self.player["professor_defeated"] = True
                        self._enter_professor_ending_main()
                    else:
                        if self.battle_is_glitch_lord and self.battle_enemy_hp <= 0:
                            self.sfx.play("boss_defeat")
                            self.player["glitch_lord_defeated"] = True
                        # ノイズガーディアン撃破 → エピローグへ
                        if getattr(self, "_noise_guardian_battle", False) and self.battle_enemy_hp <= 0:
                            self._on_noise_guardian_defeated()
                            return
                        self.state = "map"

    def _do_player_attack(self):
        p = self.player
        e = self.battle_enemy
        weapon_atk = WEAPONS[p["weapon"]]["atk"] if p["weapon"] < len(WEAPONS) else 0
        atk = p["atk"] + weapon_atk
        dmg = max(1, atk - e["def"] // 2 + random.randint(-2, 2))
        if self.debug_mode:
            dmg = 9999
        self.sfx.play("attack")
        self._start_vfx("flash_white")
        self.battle_enemy_hp = max(0, self.battle_enemy_hp - dmg)
        self.battle_text = self._dialog_text(
            random.choice(BATTLE_ATTACK_SCENES),
            enemy=e["name"],
            dmg=dmg,
        )
        self._check_glitch_lord_phase_transition()
        self.battle_phase = "player_attack"
        self.battle_text_timer = 40

    def _check_glitch_lord_phase_transition(self):
        """ボスのHPが閾値を跨いだら phase を更新し、移行メッセージを差し込む。"""
        if self.battle_enemy is None:
            return
        # ノイズガーディアン戦のフェーズメッセージ
        if getattr(self, "_noise_guardian_battle", False):
            self._check_noise_guardian_phase()
            return
        if not (self.battle_is_glitch_lord or self.battle_is_professor):
            return
        max_hp = self.battle_enemy["hp"]
        if max_hp <= 0:
            return
        ratio = self.battle_enemy_hp / max_hp
        if self.battle_is_professor:
            new_phase = self._professor_battle_phase(ratio)
            if new_phase != self.battle_boss_phase:
                self.battle_boss_phase = new_phase
                try:
                    transition_msg = self._dialog_text(f"castle.professor.phase_{new_phase}")
                except KeyError:
                    transition_msg = ""
                if transition_msg:
                    self.battle_text = (self.battle_text + " " + transition_msg).strip()
            return
        new_phase = glitch_lord_phase(ratio)
        if new_phase != self.battle_boss_phase:
            self.battle_boss_phase = new_phase
            transition_msg = GLITCH_LORD_PHASE_MESSAGES.get(new_phase)
            if transition_msg:
                # 既存ダメージメッセージに連結
                self.battle_text = (self.battle_text + " " + transition_msg).strip()

    def _professor_battle_phase(self, ratio: float) -> str:
        """HP比率からプロフェッサーのフェーズキーを返す（YAMLキー suffix と一致）。

        ratio が 0.85 を初めて下回ったら "85"、0.10 まで下回ったら "10"。
        100%時は "100"（フェーズ未開始）。最も最近に跨いだしきい値を返す。
        """
        pct = ratio * 100
        for thr in (10, 25, 40, 55, 70, 85):
            if pct < thr:
                return str(thr)
        return "100"

    def _do_enemy_attack(self):
        p = self.player
        e = self.battle_enemy
        armor_def = ARMORS[p["armor"]]["def"] if p["armor"] < len(ARMORS) else 0
        total_def = p["def"] + armor_def
        dmg = max(1, e["atk"] - total_def // 2 + random.randint(-2, 2))
        if self.debug_mode:
            dmg = 0
        self.sfx.play("hit")
        self._start_vfx("flash_red")
        p["hp"] = max(0, p["hp"] - dmg)
        self.battle_text = self._dialog_text(
            self._enemy_hit_scene_name(),
            enemy=e["name"],
            dmg=dmg,
        )
        # 毒付与判定（can_poison を持つ敵は 25% の確率で毒にする）
        if e.get("can_poison") and not p.get("poisoned") and random.random() < 0.25:
            p["poisoned"] = True
            self.sfx.play("poison")
            self.battle_text += " バグに汚染された！"
        self.battle_phase = "enemy_attack"
        self.battle_text_timer = 40

    def _start_vfx(self, vfx_type):
        if not self.player.get("vfx_enabled", True):
            return
        cfg = VFX_FLASH.get(vfx_type)
        if cfg:
            self.vfx_type = vfx_type
            self.vfx_timer = cfg["duration"]

    def _battle_victory(self):
        e = self.battle_enemy
        if self.battle_is_professor:
            # 静かな勝利。EXP/Gold報酬とレベルアップ表示を抑制（D7）
            # 派手な victory ジングルもならさない
            self.battle_text = self._dialog_text("castle.professor.silent_victory")
            self.battle_phase = "result"
            self.battle_text_timer = 60
            return
        self.sfx.play("victory")
        exp = e["exp"]; gold = e["gold"]
        self.player["exp"] += exp
        self.player["gold"] += gold
        self.battle_text = self._dialog_text(
            self._victory_scene_name(),
            enemy=e["name"],
            exp=exp,
            gold=gold,
        )
        self.battle_phase = "result"
        self.battle_text_timer = 60
        # Level up check
        self._check_level_up()

    def _battle_defeat(self):
        self.sfx.play("dead")
        self.battle_text = self._dialog_text("battle.normal.defeat")
        self.battle_phase = "result"
        self.battle_text_timer = 60

    def _check_level_up(self):
        p = self.player
        while p["lv"] < MAX_LEVEL and p["exp"] >= exp_for_level(p["lv"] + 1):
            self.sfx.play("levelup")
            p["lv"] += 1
            s = stats_for_level(p["lv"])
            p["max_hp"] = s["max_hp"]; p["hp"] = p["max_hp"]
            p["max_mp"] = s["max_mp"]; p["mp"] = p["max_mp"]
            p["atk"] = s["atk"]
            p["def"] = s["def"]
            p["agi"] = s["agi"]
            # 呪文習得
            for spell in SPELLS:
                if spell["learn_lv"] == p["lv"] and spell["name"] not in p["spells"]:
                    p["spells"].append(spell["name"])

    def update_menu(self):
        menu_items = self._menu_labels()
        if self.menu_sub is None:
            if self._btnp(UP_BUTTONS):
                self.menu_cursor = (self.menu_cursor - 1) % len(menu_items)
                self.sfx.play("cursor")
            if self._btnp(DOWN_BUTTONS):
                self.menu_cursor = (self.menu_cursor + 1) % len(menu_items)
                self.sfx.play("cursor")
            if self._btnp(CANCEL_BUTTONS):
                self.sfx.play("cancel")
                self.state = "map"
                return
            if self._btnp(CONFIRM_BUTTONS):
                self.sfx.play("select")
                if self.menu_cursor == 0:
                    self.menu_sub = "status"
                elif self.menu_cursor == 1:
                    self.menu_sub = "items"
                    self.menu_item_cursor = 0
                elif self.menu_cursor == 2:
                    self.menu_sub = "equip"
                    self.menu_item_cursor = 0
                elif self.menu_cursor == 3:
                    self._open_settings("menu")
                elif self.menu_cursor == 4:
                    self._enter_ai_help()
                elif self.menu_cursor == 5:
                    self.state = "map"
        elif self.menu_sub == "status":
            if self._btnp(CANCEL_BUTTONS) or self._btnp(CONFIRM_BUTTONS):
                self.sfx.play("cancel")
                self.menu_sub = None
        elif self.menu_sub == "items":
            items = self.player["items"]
            if self._btnp(CANCEL_BUTTONS):
                self.sfx.play("cancel")
                self.menu_sub = None; return
            if items:
                if self._btnp(UP_BUTTONS):
                    self.menu_item_cursor = max(0, self.menu_item_cursor - 1)
                    self.menu_message = ""
                    self.sfx.play("cursor")
                if self._btnp(DOWN_BUTTONS):
                    self.menu_item_cursor = min(len(items) - 1, self.menu_item_cursor + 1)
                    self.menu_message = ""
                    self.sfx.play("cursor")
                if self._btnp(CONFIRM_BUTTONS):
                    self.sfx.play("select")
                    item = items[self.menu_item_cursor]
                    item_data = ITEMS[item["id"]]
                    msg = self._use_item(item_data)
                    if not msg:
                        # 使えなかった（HP満タンで回復薬など）→ 消費しない
                        self.menu_message = "HPがまんたんで つかえない"
                    else:
                        self.menu_message = ""
                        item["qty"] -= 1
                        if item["qty"] <= 0:
                            items.pop(self.menu_item_cursor)
                            self.menu_item_cursor = max(0, min(self.menu_item_cursor, len(items) - 1))
        elif self.menu_sub == "equip":
            if self._btnp(CANCEL_BUTTONS):
                self.sfx.play("cancel")
                self.menu_sub = None; return
            if self._btnp(UP_BUTTONS):
                self.menu_item_cursor = (self.menu_item_cursor - 1) % 2
                self.sfx.play("cursor")
            if self._btnp(DOWN_BUTTONS):
                self.menu_item_cursor = (self.menu_item_cursor + 1) % 2
                self.sfx.play("cursor")

    def _menu_labels(self):
        if self.has_jp_font:
            return ["ステータス", "アイテム", "そうび", "せってい", "AIでしゅうせい", "とじる"]
        return ["STATUS", "ITEMS", "EQUIP", "SETTINGS", "AI HELP", "CLOSE"]

    def _open_settings(self, origin: str):
        self.settings_origin = origin
        self.settings_cursor = 0
        self.menu_sub = None
        self.state = "settings"

    def _settings_rows(self):
        return [
            ("all_av", self._t("ぜんぶ", "ALL")),
            ("bgm_enabled", self._t("BGM", "BGM")),
            ("sfx_enabled", self._t("こうかおん", "SFX")),
            ("vfx_enabled", self._t("ひかり", "FLASH")),
            ("back", self._t("もどる", "BACK")),
        ]

    def _settings_return_state(self):
        return "menu" if self.settings_origin == "menu" else "title"

    def _apply_av_settings(self):
        self.audio.set_enabled(self.player.get("bgm_enabled", True))
        self.sfx.set_enabled(self.player.get("sfx_enabled", True))

    def _toggle_setting(self, key: str):
        if key == "all_av":
            next_value = not (
                self.player.get("bgm_enabled", True)
                and self.player.get("sfx_enabled", True)
                and self.player.get("vfx_enabled", True)
            )
            self.player["bgm_enabled"] = next_value
            self.player["sfx_enabled"] = next_value
            self.player["vfx_enabled"] = next_value
            self._apply_av_settings()
            return
        self.player[key] = not self.player.get(key, True)
        self._apply_av_settings()

    def update_settings(self):
        rows = self._settings_rows()
        if self._btnp(UP_BUTTONS):
            self.settings_cursor = (self.settings_cursor - 1) % len(rows)
            self.sfx.play("cursor")
            return
        if self._btnp(DOWN_BUTTONS):
            self.settings_cursor = (self.settings_cursor + 1) % len(rows)
            self.sfx.play("cursor")
            return
        if self._btnp(CANCEL_BUTTONS):
            self.state = self._settings_return_state()
            return
        if self._btnp(LEFT_BUTTONS) or self._btnp(RIGHT_BUTTONS) or self._btnp(CONFIRM_BUTTONS):
            key, _label = rows[self.settings_cursor]
            if key == "back":
                self.state = self._settings_return_state()
                return
            self._toggle_setting(key)

    def _apply_spell_effect(self, spell) -> str:
        """Apply a spell effect (heal or attack). Caller is responsible for MP cost."""
        p = self.player
        if spell["type"] == "heal":
            heal = spell["power"]
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            return f'{spell["name"]}を となえた。HPが{heal}回復した！'
        # attack
        damage = max(1, spell["power"])
        self.battle_enemy_hp = max(0, self.battle_enemy_hp - damage)
        return f'{spell["name"]}！ {damage}のダメージ！'

    def _use_item(self, item_data) -> str:
        """Apply an item's effect and return a status message string.

        Returns empty string when the item could not be used.
        """
        kind = item_data["type"]
        if kind == "heal":
            if self.player["hp"] >= self.player["max_hp"]:
                return ""
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + item_data["value"])
            self.sfx.play("heal")
            return self._dialog_text(
                "battle.normal.item.heal",
                item=item_data["name"],
                value=item_data["value"],
            )
        if kind == "mp_heal":
            self.player["mp"] = min(self.player["max_mp"], self.player["mp"] + item_data["value"])
            self.sfx.play("heal")
            return self._dialog_text(
                "battle.normal.item.mp_heal",
                item=item_data["name"],
                value=item_data["value"],
            )
        if kind == "cure_poison":
            if self.player.get("poisoned"):
                self.player["poisoned"] = False
                self.sfx.play("cure")
                return f'{item_data["name"]}を使った。バグ汚染が消えた！'
            return f'{item_data["name"]}を使った。だが今は必要なかった。'
        if kind == "warp":
            # 最後に訪れた町に戻す。未訪問なら開始位置 (25,6)。
            tx, ty = getattr(self, "last_town_pos", None) or (25, 6)
            self.player["x"], self.player["y"] = tx, ty
            self.player["in_dungeon"] = False
            return f'{item_data["name"]}を使った。記録した場所に戻った。'
        return ""

    def _t(self, jp: str, en: str) -> str:
        """言語フォールバック。BDF フォントが無いときは英語版を返す。"""
        return jp if self.has_jp_font else en

    def _name(self, jp: str) -> str:
        """データ名（敵・アイテム・装備）の翻訳。NAME_EN_MAP を引く。"""
        return jp if self.has_jp_font else name_en(jp)

    def say(self, *args) -> None:
        """デバッグ用: 任意の値を画面左上にオーバーレイ表示する。

        使い方:
            self.say("こんにちは")
            self.say("hp =", self.player["hp"])

        モジュールトップの `say()` 関数からも呼べる（同一インスタンスを参照）。
        最新 12 行までを保持し、次回以降の描画フレームに重ねる。
        Scratch の「say」ブロックと同じ感覚で使える。
        """
        msg = " ".join(str(a) for a in args)
        self._say_buffer.append(msg)
        if len(self._say_buffer) > 12:
            self._say_buffer = self._say_buffer[-12:]

    def text(self, x: int, y: int, s: str, col: int) -> None:
        """文字列を misaki_gothic 8x8 で描画する。

        ASCII（英数字・記号）も日本語（仮名・全角記号）も統一フォントで
        bank 2 から blt する。未収録文字はスペース幅でスキップ。
        """
        if not s:
            return
        pyxel.pal(7, col)
        cx = x
        for ch in s:
            pos = JP_FONT_LAYOUT.get(ch)
            if pos is not None:
                bcol, brow = pos
                pyxel.blt(
                    cx, y,
                    JP_FONT_IMAGE_BANK,
                    bcol * JP_FONT_GLYPH_W,
                    brow * JP_FONT_GLYPH_H,
                    JP_FONT_GLYPH_W, JP_FONT_GLYPH_H,
                    0,
                )
            cx += JP_FONT_GLYPH_W
        pyxel.pal()

    def show_message(self, lines, callback=None):
        self.msg_lines = lines
        self.msg_index = 0
        self.msg_callback = callback

    def _professor_phase(self):
        if self.player["glitch_lord_defeated"]:
            return "late"
        max_zone = self.player["max_zone_reached"]
        if max_zone >= 3:
            return "late"
        if max_zone >= 1:
            return "mid"
        return "early"

    def _dialog_text(self, scene_name, **extra_context):
        return self.dialog.start(
            scene_name,
            state=self.player["dialog_flags"],
            extra_context=extra_context,
        ).text

    def _dialog_lines(self, scene_name, **extra_context):
        return self.dialog.load_all_lines(
            scene_name,
            state=self.player["dialog_flags"],
            extra_context=extra_context,
        )

    def _dungeon_exit_callback(self):
        if self.player.get("glitch_lord_defeated"):
            return self._enter_ending
        return None

    def _enter_message(self, lines, callback=None):
        self.show_message(lines, callback=callback)
        self.prev_state = "map"
        self.state = "message"

    def _enter_ending(self):
        self.ending_lines = self._dialog_lines("ending.main.line01")
        self.state = "ending"

    def _enemy_hit_scene_name(self):
        if self.battle_is_glitch_lord:
            return "boss.glitch.enemy_hit"
        category = self.battle_enemy.get("category", "sequential")
        return ENEMY_HIT_SCENES.get(category, ENEMY_HIT_SCENES["sequential"])

    def _victory_scene_name(self):
        if self.battle_is_glitch_lord:
            return "boss.glitch.defeat"
        zone = get_zone(self.player["y"], self.player["in_dungeon"])
        return VICTORY_SCENES_BY_ZONE.get(zone, "battle.normal.victory.early")

    def _sync_audio(self):
        battle_enemy_max_hp = self.battle_enemy["hp"] if self.battle_enemy else 0
        state_for_audio = self.state
        if self.state == "settings" and self.settings_origin == "title":
            state_for_audio = "title"
        scene_name = choose_bgm_scene(
            state=state_for_audio,
            in_dungeon=self.player["in_dungeon"],
            zone=get_zone(self.player["y"], self.player["in_dungeon"]),
            battle_is_glitch_lord=self.battle_is_glitch_lord,
            battle_enemy_hp=self.battle_enemy_hp,
            battle_enemy_max_hp=battle_enemy_max_hp,
            battle_phase=self.battle_phase,
        )
        self.audio.set_enabled(self.player.get("bgm_enabled", True))
        self.audio.play_scene(scene_name)

    def _any_advance_btnp(self) -> bool:
        """メッセージを進める入力。決定/キャンセル/方向のどれでもOK。

        「Zを押したのに進まない」と誤解されるのを防ぐ防御的UX。
        """
        return (
            self._btnp(CONFIRM_BUTTONS)
            or self._btnp(CANCEL_BUTTONS)
            or self._btnp(UP_BUTTONS)
            or self._btnp(DOWN_BUTTONS)
            or self._btnp(LEFT_BUTTONS)
            or self._btnp(RIGHT_BUTTONS)
        )

    def _advance_dialog_page(self, index, lines):
        next_index = index + 1
        return next_index, next_index >= len(lines)

    def _current_dialog_page_lines(self, lines, index, *, max_chars=28, max_rows=3):
        if not lines or index < 0 or index >= len(lines):
            return []
        return self._wrap_text(lines[index], max_chars=max_chars)[:max_rows]

    def update_message(self):
        if self._any_advance_btnp():
            self.msg_index, done = self._advance_dialog_page(self.msg_index, self.msg_lines)
            if done:
                self.state = self.prev_state
                if self.msg_callback:
                    self.msg_callback()

    def update_town(self):
        # Show message then return to map
        if self._any_advance_btnp():
            self.msg_index, done = self._advance_dialog_page(self.msg_index, self.msg_lines)
            if done:
                self.state = "map"

    # ----- town_menu (Save Player Journey steering) -----
    def update_town_menu(self):
        if self._btnp(UP_BUTTONS):
            self.sfx.play("cursor")
            self.town_menu_cursor = (self.town_menu_cursor - 1) % len(TOWN_MENU_LABELS)
            return
        if self._btnp(DOWN_BUTTONS):
            self.sfx.play("cursor")
            self.town_menu_cursor = (self.town_menu_cursor + 1) % len(TOWN_MENU_LABELS)
            return
        if self._btnp(CANCEL_BUTTONS):
            self.sfx.play("cancel")
            self._town_menu_exit()
            return
        if self._btnp(CONFIRM_BUTTONS):
            self.sfx.play("select")
            label = TOWN_MENU_LABELS[self.town_menu_cursor]
            if label == "はなす":
                self._town_menu_talk()
            elif label in SHOP_KIND_BY_LABEL:
                self._enter_shop(SHOP_KIND_BY_LABEL[label])
            elif label == "やどや":
                self._town_menu_inn()
            elif label == "セーブ":
                self._town_menu_save()
            elif label == "でる":
                self._town_menu_exit()

    def _enter_town_message(self, lines, callback=None):
        """町メニュー内の通知。閉じたら town_menu に戻る (D11/P10)。"""
        self.msg_lines = lines
        self.msg_index = 0
        self.msg_callback = callback
        self.prev_state = "town_menu"
        self.state = "message"

    def _town_menu_talk(self):
        # 城のプロフェッサーは従来のダイアログシーン
        scene = TOWN_DIALOG_SCENES.get(self.town_menu_pos)
        if scene is not None:
            lines = self._dialog_lines(scene, ProfessorPhase=self._professor_phase())
            self._enter_town_message(lines)
            return
        # 町NPCはラウンドロビン
        idx = self._current_town_index()
        if idx >= len(TOWN_NPC_LINES):
            self._enter_town_message(["……ここには はなせるひとが いない。"])
            return
        npc_lines = TOWN_NPC_LINES[idx]
        talk_idx = self.player.get("town_talk_idx", [0, 0, 0])
        line = npc_lines[talk_idx[idx] % len(npc_lines)]
        talk_idx[idx] = (talk_idx[idx] + 1) % len(npc_lines)
        self.player["town_talk_idx"] = talk_idx
        self._enter_town_message([line])

    def _town_menu_inn(self):
        cost = self._inn_cost_for_current_town()
        if self.player["gold"] < cost:
            self._enter_town_message([INN_LACK_MSG])
            return
        self.player["gold"] -= cost
        self.player["hp"] = self.player["max_hp"]
        self.player["mp"] = self.player["max_mp"]
        self.player["poisoned"] = False
        self._enter_town_message([INN_OK_MSG])

    def _current_town_index(self) -> int:
        if self.town_menu_pos is None:
            return 0
        return TOWN_INDEX_BY_POS.get(self.town_menu_pos, 0)

    def _inn_cost_for_current_town(self) -> int:
        idx = self._current_town_index()
        return INN_PRICES[idx] if idx < len(INN_PRICES) else INN_COST

    # ----- Shop (Task #7) -----
    def _enter_shop(self, kind: str):
        """ショップ画面に遷移する。kind は 'weapons' / 'armors' / 'items'。"""
        idx = self._current_town_index()
        shop = SHOPS[idx]
        self.shop_kind = kind
        self.shop_inventory = list(shop[kind])
        self.shop_cursor = 0
        self.shop_message = ""
        self.last_town_pos = self.town_menu_pos
        self.state = "shop"

    def update_shop(self):
        if not self.shop_inventory:
            if self._btnp(CANCEL_BUTTONS) or self._btnp(CONFIRM_BUTTONS):
                self.sfx.play("cancel")
                self.state = "town_menu"
            return
        if self._btnp(UP_BUTTONS):
            self.shop_cursor = (self.shop_cursor - 1) % len(self.shop_inventory)
            self.sfx.play("cursor")
            return
        if self._btnp(DOWN_BUTTONS):
            self.shop_cursor = (self.shop_cursor + 1) % len(self.shop_inventory)
            self.sfx.play("cursor")
            return
        if self._btnp(CANCEL_BUTTONS):
            self.sfx.play("cancel")
            self.state = "town_menu"
            return
        if self._btnp(CONFIRM_BUTTONS):
            self.sfx.play("select")
            self._try_purchase()

    def _try_purchase(self):
        idx = self.shop_inventory[self.shop_cursor]
        kind = self.shop_kind
        if kind == "weapons":
            entry = WEAPONS[idx]
        elif kind == "armors":
            entry = ARMORS[idx]
        else:
            entry = ITEMS[idx]
        price = entry.get("price", 0)
        # 同じ装備を二重購入させない（装備＝所持なので、装備中のものは買えない）
        if kind == "weapons" and self.player["weapon"] == idx:
            self.shop_message = "すでに もっています"
            return
        if kind == "armors" and self.player["armor"] == idx:
            self.shop_message = "すでに もっています"
            return
        if self.player["gold"] < price:
            self.shop_message = "コインが たりません"
            return
        self.player["gold"] -= price
        if kind == "weapons":
            self.player["weapon"] = idx
            self.shop_message = entry.get("buy_msg") or f"{entry['name']}を てにいれた！"
        elif kind == "armors":
            self.player["armor"] = idx
            self.shop_message = entry.get("buy_msg") or f"{entry['name']}を てにいれた！"
        else:
            # アイテムは inventory に追加
            for inv in self.player["items"]:
                if inv["id"] == idx:
                    inv["qty"] += 1
                    break
            else:
                self.player["items"].append({"id": idx, "qty": 1})
            self.shop_message = f"{entry['name']}を てにいれた！"

    def draw_shop(self):
        pyxel.cls(0)
        if self.has_jp_font:
            title_map = {"weapons": "ぶきや", "armors": "ぼうぐや", "items": "どうぐや"}
            title = title_map.get(self.shop_kind, "ショップ")
        else:
            title_map = {"weapons": "WEAPONS", "armors": "ARMOR", "items": "ITEMS"}
            title = title_map.get(self.shop_kind, "SHOP")
        self.text(8, 6, title, 7)
        self.text(160, 6, f"G:{self.player['gold']}", 10)
        if not self.shop_inventory:
            self.text(8, 40, self._t("(ざいこなし)", "(no stock)"), 6)
            return
        for i, idx in enumerate(self.shop_inventory):
            owned = False
            if self.shop_kind == "weapons":
                e = WEAPONS[idx]
                line = f"{self._name(e['name'])}  こうげき+{e['atk']}  {e['price']}G"
                owned = self.player["weapon"] == idx
            elif self.shop_kind == "armors":
                e = ARMORS[idx]
                line = f"{self._name(e['name'])}  ぼうぎょ+{e['def']}  {e['price']}G"
                owned = self.player["armor"] == idx
            else:
                e = ITEMS[idx]
                line = f"{self._name(e['name'])}  {e['price']}G"
            if owned:
                line = f"{line}  [もっています]"
            color = 10 if i == self.shop_cursor else 7
            marker = ">" if i == self.shop_cursor else " "
            self.text(8, 30 + i * 14, f"{marker} {line}", color)
        if self.shop_message:
            self.text(8, 200, self.shop_message, 11)

    def _town_menu_save(self):
        snap = dump_snapshot(self.player, town_pos=self.town_menu_pos)
        try:
            self.save_store.save(snap)
        except SaveStoreError:
            is_web = isinstance(self.save_store, LocalStorageSaveStore)
            msg = SAVE_FAIL_MSG_WEB if is_web else SAVE_FAIL_MSG_DESKTOP
            self._enter_town_message([msg])
            return
        self._has_save = True
        self.sfx.play("save")
        self._enter_town_message([SAVE_OK_MSG])

    def _town_menu_exit(self):
        self.state = "map"
        self._a_cooldown = True
        self.town_menu_pos = None

    def update_ending(self):
        if self._btnp(CONFIRM_BUTTONS):
            self.player["in_dungeon"] = False
            self.dungeon_map = None
            self._a_cooldown = True
            self.state = "map"

    # ----- Professor encounter (隠し章) -----
    # ----- AI でしゅうせい (Code Maker と外部 AI の橋渡し) -----
    def _enter_ai_help(self):
        """AIヘルプ画面に入る。可能なら Claude.ai を新タブで開く。"""
        self._ai_help_status = self._try_open_ai_chat()
        self.state = "ai_help"

    def _try_open_ai_chat(self) -> str:
        """環境に応じて AI を呼ぶ手段を試す。

        1. ブラウザ (Pyodide): `js.window.open` で Claude.ai を新タブで開く
        2. ローカル VM: `subprocess` で `claude --print` を試す（任意・失敗OK）
        3. どちらも不可: 説明だけ表示

        戻り値: ステータス文字列（画面に表示する）
        """
        # 1. ブラウザ環境
        try:
            import js  # type: ignore
            try:
                js.window.open("https://claude.ai/new", "_blank")
                return "あたらしいタブで Claude をひらきました"
            except Exception:
                return "Claude.ai を てでひらいてください"
        except ImportError:
            pass
        # 2. ローカル subprocess（VM 開発者向け）
        try:
            import subprocess
            subprocess.run(["claude", "--version"], capture_output=True, timeout=2)
            return "ローカル Claude が つかえます"
        except Exception:
            pass
        # 3. フォールバック
        return "Claude.ai を てでひらいてください"

    def update_ai_help(self):
        if self._btnp(CANCEL_BUTTONS) or self._btnp(CONFIRM_BUTTONS):
            self.sfx.play("cancel")
            self.state = "menu"

    def draw_ai_help(self):
        self.draw_map()
        self.draw_status_bar()
        # ウィンドウ
        x, y, w, h = 12, 36, 232, 196
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        self.text(x + 8, y + 8, "AIで このゲームを しゅうせい", 10)
        # 手順
        lines = [
            "",
            "１ Code Maker の Save をおして",
            "  main.py をダウンロード",
            "",
            "２ ブラウザで claude.ai か",
            "  chatgpt.com をひらく",
            "",
            "３ main.py をはりつけて",
            "  「ここを こう なおして」と たのむ",
            "",
            "４ かえってきた コードを",
            "  Code Maker に はりつける",
            "",
            f"  -> {self._ai_help_status}",
        ]
        for i, line in enumerate(lines):
            self.text(x + 8, y + 24 + i * 9, line, 7)

    def _enter_professor_intro(self):
        p = self.player
        if p.get("professor_intro_seen"):
            scene = "castle.professor.revisit_intro_01"
        else:
            scene = "castle.professor.intro_01"
        p["professor_intro_seen"] = True
        self.professor_intro_lines = self._dialog_lines(scene)
        self.professor_intro_idx = 0
        self.professor_choice_active = False
        self.professor_choice_cursor = 1  # default: ことわる
        self.state = "professor_intro"

    def update_professor_intro(self):
        if not self.professor_choice_active:
            if self._btnp(CONFIRM_BUTTONS):
                self.professor_intro_idx, done = self._advance_dialog_page(
                    self.professor_intro_idx,
                    self.professor_intro_lines,
                )
                if done:
                    self.professor_choice_active = True
            return
        # choice mode
        if self._btnp(UP_BUTTONS) or self._btnp(DOWN_BUTTONS):
            self.professor_choice_cursor = 1 - self.professor_choice_cursor
            self.sfx.play("cursor")
            return
        if self._btnp(CONFIRM_BUTTONS):
            self.sfx.play("select")
            if self.professor_choice_cursor == 0:
                self._enter_professor_ending_accepted()
            else:
                self._start_battle(PROFESSOR_DATA, is_professor=True)

    def draw_professor_intro(self):
        pyxel.cls(0)
        if self.professor_intro_lines and self.professor_intro_idx < len(self.professor_intro_lines):
            for i, sub in enumerate(
                self._current_dialog_page_lines(
                    self.professor_intro_lines,
                    self.professor_intro_idx,
                    max_chars=28,
                    max_rows=6,
                )
            ):
                self.text(16, 60 + i * 14, sub, 7)
            if not self.professor_choice_active and (pyxel.frame_count // 15) % 2:
                self.text(228, 200, "v", 7)
        if self.professor_choice_active:
            labels = (
                ["うけいれる", "ことわる"]
                if self.has_jp_font
                else ["ACCEPT", "REFUSE"]
            )
            for i, label in enumerate(labels):
                color = 10 if i == self.professor_choice_cursor else 7
                marker = ">" if i == self.professor_choice_cursor else " "
                self.text(96, 180 + i * 16, f"{marker} {label}", color)

    def _wrap_text(self, text: str, max_chars: int = 28) -> list[str]:
        """簡易な折返し（CJK文字幅考慮なし、おおよその目安）。"""
        out: list[str] = []
        for raw_line in text.split("\n"):
            cur = ""
            for ch in raw_line:
                cur += ch
                if len(cur) >= max_chars:
                    out.append(cur)
                    cur = ""
            if cur:
                out.append(cur)
        return out or [""]

    def _enter_professor_ending_main(self):
        p = self.player
        if p.get("professor_ending_seen"):
            scene = "castle.professor.revisit_epilogue_01"
        else:
            scene = "castle.professor.epilogue_01"
        p["professor_ending_seen"] = True
        self.professor_ending_lines = self._dialog_lines(scene)
        self.professor_ending_idx = 0
        self.state = "professor_ending_main"

    def update_professor_ending_main(self):
        if self._btnp(CONFIRM_BUTTONS):
            self.professor_ending_idx, done = self._advance_dialog_page(
                self.professor_ending_idx,
                self.professor_ending_lines,
            )
            if done:
                # フィールドに戻す（D8）。城タイル上のままなのでクールダウン
                self._a_cooldown = True
                self.state = "map"

    def draw_professor_ending_main(self):
        pyxel.cls(0)
        if self.professor_ending_lines and self.professor_ending_idx < len(self.professor_ending_lines):
            for i, sub in enumerate(
                self._current_dialog_page_lines(
                    self.professor_ending_lines,
                    self.professor_ending_idx,
                    max_chars=28,
                    max_rows=6,
                )
            ):
                self.text(16, 80 + i * 14, sub, 10)
            if (pyxel.frame_count // 15) % 2:
                self.text(228, 200, "v", 7)

    def _enter_professor_ending_accepted(self):
        self.professor_ending_lines = self._dialog_lines("castle.professor.accepted_01")
        self.professor_ending_idx = 0
        self.state = "professor_ending_accepted"

    def update_professor_ending_accepted(self):
        if self._btnp(CONFIRM_BUTTONS):
            self.professor_ending_idx, done = self._advance_dialog_page(
                self.professor_ending_idx,
                self.professor_ending_lines,
            )
            if done:
                # 受諾エンド：professor_defeated は立てない。タイトルへ戻る
                self.state = "title"
                self._a_cooldown = True

    def draw_professor_ending_accepted(self):
        pyxel.cls(0)
        if self.professor_ending_lines and self.professor_ending_idx < len(self.professor_ending_lines):
            for i, sub in enumerate(
                self._current_dialog_page_lines(
                    self.professor_ending_lines,
                    self.professor_ending_idx,
                    max_chars=28,
                    max_rows=6,
                )
            ):
                self.text(16, 90 + i * 14, sub, 6)
            if (pyxel.frame_count // 15) % 2:
                self.text(228, 200, "v", 7)

    # -----------------------------------------------------------------
    # DRAW
    # -----------------------------------------------------------------
    def draw(self):
        pyxel.cls(0)
        if self.state == "splash":
            self.draw_splash()
        elif self.state == "title":
            self.draw_title()
        elif self.state == "map":
            self.draw_map()
            self.draw_status_bar()
        elif self.state == "battle":
            self.draw_battle()
        elif self.state == "menu":
            self.draw_map()
            self.draw_status_bar()
            self.draw_menu()
        elif self.state == "settings":
            if self.settings_origin == "menu":
                self.draw_map()
                self.draw_status_bar()
            else:
                self.draw_title()
            self.draw_settings()
        elif self.state == "message":
            self.draw_map()
            self.draw_status_bar()
            self.draw_message_window()
        elif self.state == "town":
            self.draw_map()
            self.draw_status_bar()
            self.draw_message_window()
        elif self.state == "town_menu":
            self.draw_town_menu()
        elif self.state == "shop":
            self.draw_shop()
        elif self.state == "ending":
            self.draw_ending()
        elif self.state == "professor_intro":
            self.draw_professor_intro()
        elif self.state == "professor_ending_main":
            self.draw_professor_ending_main()
        elif self.state == "professor_ending_accepted":
            self.draw_professor_ending_accepted()
        elif self.state == "ai_help":
            self.draw_ai_help()

        # デバッグオーバーレイ（最後に重ねる）
        self._draw_say_overlay()

    def _draw_say_overlay(self):
        """disp() で蓄えたメッセージを画面左上に重ね描きする。"""
        if not self._say_buffer:
            return
        for i, line in enumerate(self._say_buffer):
            y = 4 + i * 12
            # 背景に半透明っぽい黒帯
            pyxel.rect(2, y - 1, 252, 12, 0)
            self.text(4, y, line, 10)

    def draw_splash(self):
        pyxel.cls(0)
        # 中央にロゴと "presents" 風の演出
        # フェードイン: 0-30フレームで明るくなり、30-90で安定、最後はフェードアウトしない
        f = self.splash_frame
        # タイル枠で囲む（縦長のブロック演出）
        col = 1 if f < 15 else (5 if f < 30 else 12)
        for i in range(8):
            x = 16 + i * 28
            pyxel.rect(x, 100, 12, 12, col)
        title_color = 7 if f >= 20 else 5
        self.text(80, 80, "BLOCK QUEST", title_color)
        if f >= 40:
            self.text(50, 130, self._t("コードのたびは、ここから", "Coding journey starts here"), 10)
        if f >= 60:
            self.text(70, 160, self._t("presented by うえだたつろう", "by Tatsuro Ueda"), 6)
        if f >= 75 and (pyxel.frame_count // 8) % 2:
            self.text(60, 220, "PRESS ANY KEY", 7)

    def draw_title(self):
        pyxel.cls(1)
        self.text(70, 80, "BLOCK QUEST", 7)
        self.text(50, 110, self._t("- コードのぼうけん -", "- A Coding Quest -"), 10)
        labels = [
            self._t("はじめから", "NEW GAME"),
            self._t("つづきから", "CONTINUE"),
            self._t("せってい", "SETTINGS"),
        ]
        for i, label in enumerate(labels):
            ly = 150 + i * 16
            enabled = (i != 1) or self._has_save
            base_color = 7 if enabled else 5
            color = 10 if (i == self.title_cursor and enabled) else base_color
            marker = ">" if i == self.title_cursor else " "
            self.text(80, ly, f"{marker} {label}", color)
        if self.title_cursor == 1 and not self._has_save:
            self.text(40, 200, self._t("(まだなにもかきとめていない)", "(no save yet)"), 5)

    def draw_map(self):
        p = self.player
        current_map = self.dungeon_map if p["in_dungeon"] else self.world_map
        mw = len(current_map[0]); mh = len(current_map)

        # Camera centered on player
        view_w = 256; view_h = 232
        self.cam_x = p["x"] * 16 - view_w // 2 + 8
        self.cam_y = p["y"] * 16 - view_h // 2 + 8
        self.cam_x = max(0, min(mw * 16 - view_w, self.cam_x))
        self.cam_y = max(0, min(mh * 16 - view_h, self.cam_y))

        # Tile range to draw
        tx_start = max(0, self.cam_x // 16)
        ty_start = max(0, self.cam_y // 16)
        tx_end = min(mw, (self.cam_x + view_w) // 16 + 2)
        ty_end = min(mh, (self.cam_y + view_h) // 16 + 2)

        water_frame2 = (pyxel.frame_count // 30) % 2 == 1

        for ty in range(ty_start, ty_end):
            for tx in range(tx_start, tx_end):
                tile = current_map[ty][tx]
                sx = tx * 16 - self.cam_x
                sy = ty * 16 - self.cam_y + 24  # offset for status bar

                if tile == T_PATH and not p["in_dungeon"]:
                    variant = get_path_variant(current_map, tx, ty)
                    bank_pos = self.path_variant_bank.get(id(variant))
                    if bank_pos:
                        pyxel.blt(sx, sy, 0, bank_pos[0], bank_pos[1], 16, 16, 0)
                    else:
                        # Fallback: draw from tile bank
                        bp = self.tile_bank[T_PATH]
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                elif tile == T_WATER:
                    shore = None
                    if not p["in_dungeon"]:
                        shore = get_shore_variant(current_map, tx, ty)
                    if shore:
                        bank_pos = self.shore_variant_bank.get(id(shore))
                        if bank_pos:
                            pyxel.blt(sx, sy, 0, bank_pos[0], bank_pos[1], 16, 16)
                        else:
                            bp = self.tile_bank[T_WATER]
                            pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                    else:
                        if water_frame2 and self.tile_bank_water2:
                            bp = self.tile_bank_water2
                        else:
                            bp = self.tile_bank[T_WATER]
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)
                else:
                    bp = self.tile_bank.get(tile)
                    if bp:
                        pyxel.blt(sx, sy, 0, bp[0], bp[1], 16, 16)

        # Draw landmark highlights (#13)
        if not p["in_dungeon"]:
            self._draw_landmark_highlights()
        else:
            self._draw_dungeon_glitch_lord_marker(current_map)

        # Draw hero
        hero_sx = p["x"] * 16 - self.cam_x
        hero_sy = p["y"] * 16 - self.cam_y + 24
        sprite_key = "hero_walk" if self.walk_frame == 1 else "hero_down"
        bp = self.sprite_bank.get(sprite_key)
        if bp:
            pyxel.blt(hero_sx, hero_sy, 1, bp[0], bp[1], 16, 16, 0)

    def _draw_dungeon_glitch_lord_marker(self, current_map):
        """ダンジョン最奥のボス位置に目印キャラを描く。"""
        p = self.player
        if p.get("glitch_lord_defeated"):
            return
        bp = self.sprite_bank.get("hero_down")
        if bp is None:
            return

        for ty, row in enumerate(current_map):
            for tx, tile in enumerate(row):
                if tile != T_GLITCH_LORD_TRIGGER:
                    continue
                sx = tx * 16 - self.cam_x
                sy = ty * 16 - self.cam_y + 24
                if sx < -16 or sx > 256 or sy < 8 or sy > 256:
                    return
                pyxel.blt(sx, sy, 1, bp[0], bp[1], 16, 16, 0)
                return

    def _draw_landmark_highlights(self):
        """ランドマーク強調描画。フレーム枠とパルスで「目印」を示す。

        - 世界樹 (32, 9)：常時、緑のパルス枠
        - 通信塔 (40, 32)：常時、紫のパルス枠
        - 城 (25, 6)：glitch_lord_defeated 後のみ、黄色のパルス枠（プロフェッサー編発見導線）
        """
        p = self.player
        marks = [
            (32, 9, 11, True),   # 世界樹: 緑
            (40, 32, 2, True),   # 通信塔: 紫
            (25, 6, 10, p.get("glitch_lord_defeated", False)),  # 城: 黄（クリア後のみ）
        ]
        # パルス（明滅）：30フレームで1周期
        pulse = (pyxel.frame_count // 8) % 4
        for tx, ty, color, enabled in marks:
            if not enabled:
                continue
            sx = tx * 16 - self.cam_x
            sy = ty * 16 - self.cam_y + 24
            # 画面外はスキップ
            if sx < -16 or sx > 256 or sy < 8 or sy > 256:
                continue
            # 二重枠で目立たせる
            pyxel.rectb(sx - 1 - pulse, sy - 1 - pulse,
                        18 + pulse * 2, 18 + pulse * 2, color)

    def draw_status_bar(self):
        pyxel.rect(0, 0, 256, 24, 1)
        p = self.player
        zone = get_zone(p["y"], p["in_dungeon"])
        zone_name = ZONE_NAMES.get(zone, "???") if self.has_jp_font else ZONE_NAMES_EN.get(zone, "???")
        self.text(4, 2, f"レベル{p['lv']} {zone_name}", 7)
        self.text(4, 13, f"HP{p['hp']}/{p['max_hp']} MP{p['mp']}/{p['max_mp']}", 7)
        # HP bar
        bar_x = 170; bar_w = 60
        pyxel.rect(bar_x, 4, bar_w, 6, 0)
        hp_ratio = p["hp"] / max(1, p["max_hp"])
        pyxel.rect(bar_x, 4, int(bar_w * hp_ratio), 6, 11 if hp_ratio > 0.3 else 8)
        # MP bar
        pyxel.rect(bar_x, 14, bar_w, 6, 0)
        mp_ratio = p["mp"] / max(1, p["max_mp"])
        pyxel.rect(bar_x, 14, int(bar_w * mp_ratio), 6, 12)

        if self.debug_mode:
            self.text(130, 2, "DEBUG", 8)

    def _draw_vfx_overlay(self):
        if not self.player.get("vfx_enabled", True):
            return
        if self.vfx_timer <= 0:
            return
        cfg = VFX_FLASH.get(self.vfx_type)
        if not cfg:
            return
        if self.vfx_timer % 2 == 0:
            pyxel.rect(0, 0, 256, 256, cfg["color"])

    def draw_battle(self):
        pyxel.cls(1)
        e = self.battle_enemy
        if not e:
            return

        # Draw enemy sprite (3x scale centered)
        sprite_key = e.get("sprite", "slime")
        bp = self.sprite_bank.get(sprite_key)
        if bp:
            # Draw 3x scaled sprite
            sx, sy = bp
            for py in range(16):
                for px in range(16):
                    c = pyxel.images[1].pget(sx + px, sy + py)
                    if c != 0:
                        for dy in range(3):
                            for dx2 in range(3):
                                pyxel.pset(104 + px * 3 + dx2, 30 + py * 3 + dy, c)

        # Enemy name and HP bar
        self.text(80, 10, self._name(e["name"]), 7)
        bar_x = 80; bar_w = 96
        pyxel.rect(bar_x, 85, bar_w, 8, 0)
        hp_ratio = self.battle_enemy_hp / max(1, e["hp"])
        pyxel.rect(bar_x, 85, int(bar_w * hp_ratio), 8, 8)
        self.text(bar_x + 2, 86, f"HP {self.battle_enemy_hp}/{e['hp']}", 7)

        # Player stats
        p = self.player
        pyxel.rect(10, 100, 236, 40, 0)
        pyxel.rectb(10, 100, 236, 40, 7)
        self.text(16, 104, f"{self._t('プログラマー', 'PROGRAMMER')}  レベル{p['lv']}", 7)
        self.text(16, 116, f"HP {p['hp']}/{p['max_hp']}  MP {p['mp']}/{p['max_mp']}", 7)
        # Player HP bar
        pyxel.rect(170, 116, 60, 6, 0)
        hp_r = p["hp"] / max(1, p["max_hp"])
        pyxel.rect(170, 116, int(60 * hp_r), 6, 11 if hp_r > 0.3 else 8)

        # Battle text
        if self.battle_text:
            pyxel.rect(10, 148, 236, 30, 0)
            pyxel.rectb(10, 148, 236, 30, 7)
            self.text(16, 154, self.battle_text, 7)

        # Menu
        if self.battle_phase == "menu":
            menu_labels = (
                ["たたかう", "じゅもん", "アイテム", "にげる"]
                if self.has_jp_font
                else ["FIGHT", "SPELL", "ITEM", "RUN"]
            )
            pyxel.rect(10, 190, 236, 56, 0)
            pyxel.rectb(10, 190, 236, 56, 7)
            for i, label in enumerate(menu_labels):
                cx = 30 + (i % 2) * 110
                cy = 198 + (i // 2) * 18
                col = 10 if i == self.battle_menu else 6
                self.text(cx, cy, label, col)
                if i == self.battle_menu:
                    self.text(cx - 12, cy, ">", 10)

        elif self.battle_phase == "spell_select":
            spells = self.player["spells"]
            pyxel.rect(10, 190, 236, 56, 0)
            pyxel.rectb(10, 190, 236, 56, 7)
            if not spells:
                self.text(16, 200, self._t("じゅもんをおぼえていない", "No spells learned"), 6)
            else:
                for i, name in enumerate(spells[:4]):
                    spell = SPELL_BY_NAME.get(name)
                    if spell is None:
                        continue
                    cy = 196 + i * 12
                    col = 10 if i == self.battle_spell_select else 6
                    self.text(30, cy, f"{self._name(name)}  MP{spell['mp']}", col)
                    if i == self.battle_spell_select:
                        self.text(18, cy, ">", 10)

        elif self.battle_phase == "item_select":
            items = self.player["items"]
            pyxel.rect(10, 190, 236, 56, 0)
            pyxel.rectb(10, 190, 236, 56, 7)
            if self.battle_text:
                self.text(16, 192, self.battle_text, 8)
            if not items:
                self.text(16, 200, self._t("アイテムがない", "No items"), 6)
            else:
                for i, item in enumerate(items[:4]):
                    idata = ITEMS[item["id"]]
                    cy = 196 + i * 12
                    col = 10 if i == self.battle_item_select else 6
                    self.text(30, cy, f"{self._name(idata['name'])} x{item['qty']}", col)
                    if i == self.battle_item_select:
                        self.text(18, cy, ">", 10)

        self._draw_vfx_overlay()

    def draw_menu(self):
        # Semi-transparent overlay
        pyxel.rect(20, 30, 216, 200, 1)
        pyxel.rectb(20, 30, 216, 200, 7)

        menu_labels = self._menu_labels()
        for i, label in enumerate(menu_labels):
            cy = 40 + i * 16
            col = 10 if i == self.menu_cursor and self.menu_sub is None else 6
            self.text(36, cy, label, col)
            if i == self.menu_cursor and self.menu_sub is None:
                self.text(26, cy, ">", 10)

        p = self.player
        if self.menu_sub == "status":
            pyxel.rect(40, 100, 180, 120, 0)
            pyxel.rectb(40, 100, 180, 120, 7)
            lines = [
                f"レベル {p['lv']}  けいけん {p['exp']}",
                f"HP {p['hp']}/{p['max_hp']}",
                f"MP {p['mp']}/{p['max_mp']}",
                f"こうげき {p['atk']+WEAPONS[p['weapon']]['atk']}  ぼうぎょ {p['def']+ARMORS[p['armor']]['def']}",
                f"すばやさ {p['agi']}",
                f"コイン {p['gold']}",
            ]
            for i, line in enumerate(lines):
                self.text(50, 108 + i * 13, line, 7)

        elif self.menu_sub == "items":
            pyxel.rect(40, 100, 180, 120, 0)
            pyxel.rectb(40, 100, 180, 120, 7)
            items = p["items"]
            if not items:
                self.text(50, 110, self._t("アイテムがない", "No items"), 6)
            else:
                for i, item in enumerate(items[:8]):
                    idata = ITEMS[item["id"]]
                    cy = 108 + i * 13
                    col = 10 if i == self.menu_item_cursor else 6
                    self.text(56, cy, f"{self._name(idata['name'])} x{item['qty']}", col)
                    if i == self.menu_item_cursor:
                        self.text(46, cy, ">", 10)
            if self.menu_message:
                self.text(50, 210, self.menu_message, 8)

        elif self.menu_sub == "equip":
            pyxel.rect(40, 100, 180, 80, 0)
            pyxel.rectb(40, 100, 180, 80, 7)
            wlbl = self._t("ぶき", "WPN")
            albl = self._t("ぼうぐ", "ARM")
            labels = [
                f"{wlbl}: {self._name(WEAPONS[p['weapon']]['name'])} (こうげき+{WEAPONS[p['weapon']]['atk']})",
                f"{albl}: {self._name(ARMORS[p['armor']]['name'])} (ぼうぎょ+{ARMORS[p['armor']]['def']})",
            ]
            for i, label in enumerate(labels):
                cy = 110 + i * 20
                col = 10 if i == self.menu_item_cursor else 6
                self.text(56, cy, label, col)
                if i == self.menu_item_cursor:
                    self.text(46, cy, ">", 10)

    def draw_settings(self):
        pyxel.rect(28, 54, 200, 148, 1)
        pyxel.rectb(28, 54, 200, 148, 7)
        self.text(92, 66, self._t("せってい", "SETTINGS"), 10)
        for i, (key, label) in enumerate(self._settings_rows()):
            cy = 94 + i * 22
            col = 10 if i == self.settings_cursor else 6
            marker = ">" if i == self.settings_cursor else " "
            if key == "back":
                value = ""
            elif key == "all_av":
                value = "ON" if (
                    self.player.get("bgm_enabled", True)
                    and self.player.get("sfx_enabled", True)
                    and self.player.get("vfx_enabled", True)
                ) else "OFF"
            else:
                value = "ON" if self.player.get(key, True) else "OFF"
            row = f"{marker} {label}"
            if value:
                row = f"{row}: {value}"
            self.text(44, cy, row, col)
        self.text(44, 176, self._t("けっていで きりかえ", "Press confirm to toggle"), 7)

    def draw_town_menu(self):
        # Background: show the map underneath so players keep their bearings.
        self.draw_map()
        self.draw_status_bar()
        # Window
        x, y, w, h = 20, 40, 216, 170
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        self.text(x + 8, y + 8, self._t("まちメニュー", "TOWN MENU"), 7)
        labels = TOWN_MENU_LABELS if self.has_jp_font else TOWN_MENU_LABELS_EN
        for i, label in enumerate(labels):
            ly = y + 28 + i * 16
            color = 10 if i == self.town_menu_cursor else 7
            marker = ">" if i == self.town_menu_cursor else " "
            self.text(x + 16, ly, f"{marker} {label}", color)
        gold = self.player["gold"]
        self.text(x + 8, y + h - 16, f"GOLD: {gold}", 6)

    def draw_message_window(self):
        pyxel.rect(8, 208, 240, 44, 0)
        pyxel.rectb(8, 208, 240, 44, 7)
        for i, line in enumerate(
            self._current_dialog_page_lines(
                self.msg_lines,
                self.msg_index,
                max_chars=28,
                max_rows=3,
            )
        ):
            self.text(16, 214 + i * 12, line, 7)
        # Blink indicator
        if (pyxel.frame_count // 15) % 2:
            self.text(228, 240, "v", 7)

    def draw_ending(self):
        pyxel.cls(1)
        if not self.ending_lines:
            self.ending_lines = self._dialog_lines("ending.main.line01")
        if self.ending_lines:
            self.text(60, 60, self.ending_lines[0], 10)
        for index, line in enumerate(self.ending_lines[1:]):
            self.text(20, 90 + index * 15, line, 7)
        self.text(40, 180, "PRESS Z TO TITLE", 6)
        p = self.player
        self.text(30, 200, f"レベル{p['lv']} Time:{pyxel.frame_count//30//60}m", 6)


# =====================================================================
# DEBUG: グローバル say() 関数 — Scratch の「say」ブロックと同じ感覚
# =====================================================================
def say(*args):
    """画面左上にデバッグ表示するヘルパ関数。

    使い方:
        say("こんにちは")             # → 画面左上に「こんにちは」が出る
        say("hp =", player["hp"])     # → 「hp = 45」のように出る

    最新 12 行までが画面左上にオーバーレイ表示される。
    print() より便利な点:
      - ゲーム画面に出るのでブラウザでも見える（Code Maker 環境向け）
      - 日本語が表示できる（仮名のみ）
    """
    if Game._instance is not None:
        Game._instance.say(*args)


def say_clear():
    """say バッファをクリアする。"""
    if Game._instance is not None:
        Game._instance._say_buffer.clear()


# =====================================================================
# ENTRY POINT
# =====================================================================
# 子どもがコードを試すときは、ここで `say("こんにちは")` のように呼ぶと
# 画面左上にデバッグ表示される（Scratch の say ブロックと同じ感覚）。
game = Game()
game.start()
