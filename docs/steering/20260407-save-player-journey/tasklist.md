---
status: done
---

# 町セーブ機能 実装プラン

> **For agentic workers:** This plan follows TDD (Red→Green) and uses small bite-sized steps. `[ ]`→`[x]` を逐次更新すること。

**Goal:** ブロッククエストに「町でのみセーブできる」永続化機能を追加し、`はじめから`/`つづきから` のタイトルフローを完成させる。

**Architecture:** `src/save_store.py`（永続化抽象＋3実装）と `src/player_snapshot.py`（純粋関数）を新規追加し、`main.py` の `Game` クラスを最小限改修して `town_menu` ステートを追加する。デスクトップは `save.json` ファイル、web (Pyodide) は `localStorage` を使い、ビジネスロジックは同一。

**Tech Stack:** Python 3.12 / Pyxel / 標準 unittest（pytest 不要）

**スコープ補足:** 「はなす」のNPCリスト化（D14）は **既存 `TOWN_DIALOG_SCENES` を1町=1NPC として扱う最小実装** に留め、複数NPC化は本steeringのフォローアップとする。`ぶきや/ぼうぐや/どうぐや` は **`工事中` プレースホルダ** とし、本steeringの主目的（セーブ）に集中する。これらは `journey.md` のスコープ外注記と整合。

---

## ファイル構成

| ファイル | 種別 | 責務 |
|---|---|---|
| `src/player_snapshot.py` | 新規 | `Game.player` ↔ dict の純粋関数。`SAVED_KEYS` を明示 |
| `src/save_store.py` | 新規 | `SaveStore` Protocol + `FileSaveStore` + `LocalStorageSaveStore` + `InMemorySaveStore` + `make_save_store()` ファクトリ |
| `test/test_player_snapshot.py` | 新規 | dump/restore ラウンドトリップ、debug_mode リーク防止 |
| `test/test_save_store.py` | 新規 | FileSaveStore のアトミック書込・破損検知・スキーマバージョン、InMemorySaveStore、ファクトリ |
| `main.py` | 修正 | 既存 `town` state を `town_menu` に置換／Aクールダウン／タイトル continue／do_save / do_inn / do_load |

---

## Phase 1: PlayerSnapshot

### Task 1: PlayerSnapshot dump/restore

**Files:**
- Create: `src/player_snapshot.py`
- Test: `test/test_player_snapshot.py`

- [x] **Step 1.1: Failing test - dump returns SAVED_KEYS only**

`test/test_player_snapshot.py`:

```python
from __future__ import annotations

import sys
import unittest
from pathlib import Path

PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))

from src.player_snapshot import (
    SAVE_VERSION,
    SAVED_PLAYER_KEYS,
    dump_snapshot,
    restore_snapshot,
)


def _sample_player():
    return {
        "x": 20, "y": 12,
        "hp": 25, "max_hp": 30, "mp": 8, "max_mp": 10,
        "atk": 5, "def": 3, "agi": 5,
        "lv": 2, "exp": 15, "gold": 50,
        "weapon": 1, "armor": 0,
        "items": [{"id": 0, "qty": 3}],
        "spells": [],
        "poisoned": False,
        "in_dungeon": False,
        "boss_defeated": False,
        "max_zone_reached": 1,
        "landmarkTreeSeen": True,
        "landmarkTowerSeen": False,
        "dialog_flags": {"foo": True},
    }


class PlayerSnapshotTest(unittest.TestCase):
    def test_dump_includes_all_saved_keys(self):
        player = _sample_player()
        snap = dump_snapshot(player, town_pos=(20, 12))
        self.assertEqual(snap["save_version"], SAVE_VERSION)
        self.assertEqual(snap["town_pos"], [20, 12])
        for key in SAVED_PLAYER_KEYS:
            self.assertIn(key, snap["player"])

    def test_dump_excludes_non_saved_keys(self):
        player = _sample_player()
        player["debug_mode"] = True  # うっかりリーク検証
        player["temp_battle_state"] = "phase_1"
        snap = dump_snapshot(player, town_pos=(20, 12))
        self.assertNotIn("debug_mode", snap["player"])
        self.assertNotIn("temp_battle_state", snap["player"])

    def test_restore_round_trip(self):
        player = _sample_player()
        snap = dump_snapshot(player, town_pos=(20, 12))
        restored = restore_snapshot(snap)
        for key in SAVED_PLAYER_KEYS:
            self.assertEqual(restored["player"][key], player[key], key)
        self.assertEqual(restored["town_pos"], (20, 12))


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 1.2: Run test to verify it fails**

```bash
python -m unittest test.test_player_snapshot -v
```

Expected: ImportError (no module `src.player_snapshot`)

- [x] **Step 1.3: Create minimal implementation**

`src/player_snapshot.py`:

```python
"""Pure functions for serializing player state to a savable dict.

Only keys in SAVED_PLAYER_KEYS are persisted, preventing accidental leakage
of debug-only or transient battle state into save files.
"""
from __future__ import annotations

from typing import Any, Iterable

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
    "boss_defeated",
    "max_zone_reached",
    "landmarkTreeSeen", "landmarkTowerSeen",
    "dialog_flags",
)


def dump_snapshot(player: dict[str, Any], town_pos: tuple[int, int]) -> dict[str, Any]:
    """Game.player から保存用 dict を組み立てる。

    town_pos は SaveStore からは見えない情報なので呼び出し側で渡す
    （セーブを実行した町の座標を意味し、ロード時に同じ場所に出現させる）。
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
    return {
        "player": dict(snapshot["player"]),
        "town_pos": (int(raw_pos[0]), int(raw_pos[1])),
    }
```

- [x] **Step 1.4: Run tests to verify they pass**

```bash
python -m unittest test.test_player_snapshot -v
```

Expected: PASS (3 tests)

- [x] **Step 1.5: Add round-trip with non-existent key**

```python
def test_restore_does_not_require_all_keys(self):
    player = {"x": 1, "y": 2, "hp": 5}  # 一部キーだけ
    snap = dump_snapshot(player, town_pos=(1, 2))
    restored = restore_snapshot(snap)
    self.assertEqual(restored["player"]["hp"], 5)
    self.assertNotIn("max_hp", restored["player"])
```

Run: `python -m unittest test.test_player_snapshot -v` → PASS

---

## Phase 2: SaveStore

### Task 2: SaveStore Protocol + InMemorySaveStore

**Files:**
- Create: `src/save_store.py`
- Test: `test/test_save_store.py`

- [ ] **Step 2.1: Failing test - InMemorySaveStore round trip**

`test/test_save_store.py`:

```python
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))

from src.save_store import (
    FileSaveStore,
    InMemorySaveStore,
    SaveStoreError,
    make_save_store,
)


SAMPLE_DATA = {
    "save_version": 1,
    "town_pos": [20, 12],
    "player": {"x": 20, "y": 12, "hp": 25, "gold": 50},
}


class InMemorySaveStoreTest(unittest.TestCase):
    def test_starts_empty(self):
        store = InMemorySaveStore()
        self.assertFalse(store.exists())
        self.assertIsNone(store.load())

    def test_save_then_load(self):
        store = InMemorySaveStore()
        store.save(SAMPLE_DATA)
        self.assertTrue(store.exists())
        self.assertEqual(store.load(), SAMPLE_DATA)

    def test_overwrite(self):
        store = InMemorySaveStore()
        store.save({"save_version": 1, "town_pos": [0, 0], "player": {}})
        store.save(SAMPLE_DATA)
        self.assertEqual(store.load(), SAMPLE_DATA)
```

- [ ] **Step 2.2: Run to verify failure**

```bash
python -m unittest test.test_save_store -v
```

Expected: ImportError

- [ ] **Step 2.3: Implement Protocol + InMemorySaveStore**

`src/save_store.py`:

```python
"""Persistence layer for Block Quest save data.

Three implementations:
  * FileSaveStore         — desktop, atomic write to save.json
  * LocalStorageSaveStore — Pyxel web (Pyodide), via js.localStorage
  * InMemorySaveStore     — unit tests

Use make_save_store() to pick the right one for the current environment.
"""
from __future__ import annotations

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


class InMemorySaveStore:
    """Test-only store. Holds a single in-RAM dict."""

    def __init__(self) -> None:
        self._data: Optional[dict[str, Any]] = None

    def exists(self) -> bool:
        return self._data is not None

    def load(self) -> Optional[dict[str, Any]]:
        if self._data is None:
            return None
        # JSON round-trip to mimic real stores (catches non-serializable values).
        return json.loads(json.dumps(self._data))

    def save(self, data: dict[str, Any]) -> None:
        self._data = json.loads(json.dumps(data))
```

- [ ] **Step 2.4: Run to verify**

```bash
python -m unittest test.test_save_store.InMemorySaveStoreTest -v
```

Expected: PASS (3 tests)

### Task 3: FileSaveStore (atomic write)

- [ ] **Step 3.1: Failing test - file round trip**

Append to `test/test_save_store.py`:

```python
class FileSaveStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "save.json"
        self.store = FileSaveStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_does_not_exist_initially(self):
        self.assertFalse(self.store.exists())
        self.assertIsNone(self.store.load())

    def test_save_creates_file(self):
        self.store.save(SAMPLE_DATA)
        self.assertTrue(self.path.exists())
        self.assertEqual(json.loads(self.path.read_text("utf-8")), SAMPLE_DATA)

    def test_load_after_save(self):
        self.store.save(SAMPLE_DATA)
        self.assertEqual(self.store.load(), SAMPLE_DATA)

    def test_atomic_temp_file_removed(self):
        self.store.save(SAMPLE_DATA)
        # tmp ファイルは残してはならない
        leftover = list(self.path.parent.glob("*.tmp*"))
        self.assertEqual(leftover, [])

    def test_corrupt_json_returns_none(self):
        self.path.write_text("not valid json {{{", "utf-8")
        self.assertIsNone(self.store.load())

    def test_unknown_save_version_returns_none(self):
        self.path.write_text(
            json.dumps({"save_version": 999, "town_pos": [0, 0], "player": {}}),
            "utf-8",
        )
        self.assertIsNone(self.store.load())

    def test_save_failure_raises_save_store_error(self):
        # 存在しないディレクトリを指定して書き込み失敗を強制
        bogus = FileSaveStore(Path(self.tmp.name) / "no_such_dir" / "save.json")
        with self.assertRaises(SaveStoreError):
            bogus.save(SAMPLE_DATA)
```

- [ ] **Step 3.2: Run to confirm failure**

`python -m unittest test.test_save_store.FileSaveStoreTest -v`
Expected: AttributeError (FileSaveStore not defined)

- [ ] **Step 3.3: Implement FileSaveStore**

Append to `src/save_store.py`:

```python
class FileSaveStore:
    """Desktop store. Atomic write via tmp file + os.replace."""

    SUPPORTED_SAVE_VERSIONS = (1,)

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
        if not isinstance(data, dict):
            return None
        version = data.get("save_version")
        if version not in self.SUPPORTED_SAVE_VERSIONS:
            return None
        return data

    def save(self, data: dict[str, Any]) -> None:
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        try:
            tmp_path.write_text(json.dumps(data, ensure_ascii=False), "utf-8")
            os.replace(tmp_path, self._path)
        except OSError as exc:
            # Clean up the half-written tmp file if it exists.
            try:
                tmp_path.unlink()
            except OSError:
                pass
            raise SaveStoreError(str(exc)) from exc
```

- [ ] **Step 3.4: Run all save_store tests**

`python -m unittest test.test_save_store -v`
Expected: PASS (3 + 7)

### Task 4: LocalStorageSaveStore (skeleton, untested in pytest)

- [ ] **Step 4.1: Skeleton class**

Append to `src/save_store.py`:

```python
class LocalStorageSaveStore:
    """Web store. Backed by browser localStorage via Pyodide's `js` module.

    Imported lazily so desktop Python (which lacks `js`) can still import
    this module without errors.
    """

    KEY = "blockquest_save_v1"
    SUPPORTED_SAVE_VERSIONS = (1,)

    def __init__(self) -> None:
        # `import js` is intentionally inside __init__ so module-level
        # imports never break on desktop Python.
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
        if not isinstance(data, dict):
            return None
        if data.get("save_version") not in self.SUPPORTED_SAVE_VERSIONS:
            return None
        return data

    def save(self, data: dict[str, Any]) -> None:
        try:
            self._js.localStorage.setItem(self.KEY, json.dumps(data, ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001 - js exceptions vary
            raise SaveStoreError(str(exc)) from exc
```

> **Note:** No unit test runs against `LocalStorageSaveStore` in CI because Pyodide is not in the host venv. Manual web E2E (Phase 6 verification) covers it.

### Task 5: make_save_store() factory

- [ ] **Step 5.1: Failing test for factory in desktop env**

Append:

```python
class FactoryTest(unittest.TestCase):
    def test_returns_file_save_store_on_desktop(self):
        with tempfile.TemporaryDirectory() as d:
            store = make_save_store(file_path=Path(d) / "save.json")
            self.assertIsInstance(store, FileSaveStore)
```

- [ ] **Step 5.2: Run → AttributeError on `make_save_store`**

- [ ] **Step 5.3: Implement factory**

Append to `src/save_store.py`:

```python
def make_save_store(file_path: Path) -> SaveStore:
    """Pick the right SaveStore for the current Python runtime.

    On Pyodide (web Pyxel) the `js` module exists; on desktop it doesn't.
    """
    try:
        import js  # noqa: F401
        return LocalStorageSaveStore()
    except ImportError:
        return FileSaveStore(file_path)
```

- [ ] **Step 5.4: Run all save_store tests**

`python -m unittest test.test_save_store -v` → PASS (all)

---

## Phase 3: town_menu state in main.py

### Task 6: Replace `town` state with `town_menu`

**Files:**
- Modify: `main.py` (Game class)

The existing `town` state is just a message popup after entering a town tile. We replace it with a proper 7-item menu state. The "はなす" item will reuse the existing `TOWN_DIALOG_SCENES` lookup.

- [ ] **Step 6.1: Add module-level constants for town menu**

Insert after `TOWN_DIALOG_SCENES`:

```python
TOWN_MENU_LABELS = ("はなす", "ぶきや", "ぼうぐや", "どうぐや", "やどや", "セーブ", "でる")
INN_COST = 10  # gold
SAVE_OK_MSG = "ここまでの理解を書き留めた。"
LOAD_OK_MSG = "記録を読み返した。理解が戻ってくる。"
NO_RECORD_MSG = "まだ何も書き留めていない…"
SAVE_FAIL_MSG_DESKTOP = "セーブに失敗しました（権限/容量を確認してください）"
SAVE_FAIL_MSG_WEB = "セーブに失敗しました（ブラウザの保存領域を確認してください）"
INN_OK_MSG = "安全な場所で休んだ。思考が冴える。HPとMPが かいふくした！"
INN_LACK_MSG = "コインが たりません"
SHOP_WIP_MSG = "工事中：本機能はフォローアップで実装予定"
```

- [ ] **Step 6.2: Initialize `town_menu_cursor` and `_a_cooldown` and SaveStore in `__init__`**

Add to `Game.__init__` after `self.menu_item_cursor = 0`:

```python
        # Town menu state
        self.town_menu_cursor = 0
        self.town_menu_pos = None  # 入った町のタイル座標 (D15)

        # Map A-button cooldown (D13) — 「でる」直後とロード直後の暴発防止
        self._a_cooldown = False

        # Save store
        from src.save_store import make_save_store
        from src.player_snapshot import dump_snapshot, restore_snapshot
        self._dump_snapshot = dump_snapshot
        self._restore_snapshot = restore_snapshot
        save_path = Path(__file__).resolve().parent / "save.json"
        self.save_store = make_save_store(save_path)
        self._has_save = self.save_store.exists()
```

Also add `from pathlib import Path` to the top of `main.py` if not already imported.

- [ ] **Step 6.3: Modify `_check_tile_events` to enter `town_menu` state**

Replace this block:

```python
        # Town/Castle entry
        if tile == T_TOWN or tile == T_CASTLE:
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
```

with:

```python
        # Town entry → open the town menu (D6)
        if tile == T_TOWN:
            self.town_menu_pos = (nx, ny)
            self.town_menu_cursor = 0
            self.state = "town_menu"
            return

        # Castle still uses the legacy in-place dialog
        if tile == T_CASTLE:
            scene = TOWN_DIALOG_SCENES.get((nx, ny))
            if scene is None:
                lines = ["..."]
            else:
                lines = self._dialog_lines(scene, ProfessorPhase=self._professor_phase())
            self.show_message(lines)
            self.state = "town"
            return
```

- [ ] **Step 6.4: Add `update_town_menu` method**

Insert after `update_town`:

```python
    def update_town_menu(self):
        if self._btnp(UP_BUTTONS):
            self.town_menu_cursor = (self.town_menu_cursor - 1) % len(TOWN_MENU_LABELS)
            return
        if self._btnp(DOWN_BUTTONS):
            self.town_menu_cursor = (self.town_menu_cursor + 1) % len(TOWN_MENU_LABELS)
            return
        if self._btnp(CANCEL_BUTTONS):
            # キャンセル＝でる と等価
            self._town_menu_exit()
            return
        if self._btnp(CONFIRM_BUTTONS):
            label = TOWN_MENU_LABELS[self.town_menu_cursor]
            if label == "はなす":
                self._town_menu_talk()
            elif label in ("ぶきや", "ぼうぐや", "どうぐや"):
                self._enter_town_message([SHOP_WIP_MSG])
            elif label == "やどや":
                self._town_menu_inn()
            elif label == "セーブ":
                self._town_menu_save()
            elif label == "でる":
                self._town_menu_exit()

    def _enter_town_message(self, lines, callback=None):
        """町メニュー内の通知。閉じたら town_menu に戻る。"""
        self.msg_lines = lines
        self.msg_index = 0
        self.msg_callback = callback
        self.prev_state = "town_menu"
        self.state = "message"

    def _town_menu_talk(self):
        scene = TOWN_DIALOG_SCENES.get(self.town_menu_pos)
        if scene is None:
            self._enter_town_message(["……ここには 話せる人が いない。"])
            return
        lines = self._dialog_lines(scene, ProfessorPhase=self._professor_phase())
        self._enter_town_message(lines)

    def _town_menu_inn(self):
        if self.player["gold"] < INN_COST:
            self._enter_town_message([INN_LACK_MSG])
            return
        self.player["gold"] -= INN_COST
        self.player["hp"] = self.player["max_hp"]
        self.player["mp"] = self.player["max_mp"]
        self.player["poisoned"] = False
        self._enter_town_message([INN_OK_MSG])

    def _town_menu_save(self):
        snap = self._dump_snapshot(self.player, town_pos=self.town_menu_pos)
        try:
            self.save_store.save(snap)
        except Exception:  # noqa: BLE001
            from src.save_store import LocalStorageSaveStore
            is_web = isinstance(self.save_store, LocalStorageSaveStore)
            msg = SAVE_FAIL_MSG_WEB if is_web else SAVE_FAIL_MSG_DESKTOP
            self._enter_town_message([msg])
            return
        self._has_save = True
        self._enter_town_message([SAVE_OK_MSG])

    def _town_menu_exit(self):
        self.state = "map"
        self._a_cooldown = True
        self.town_menu_pos = None
```

- [ ] **Step 6.5: Wire `town_menu` into update dispatch**

In the `update()` method, add this branch (after the `town` branch):

```python
        elif self.state == "town_menu":
            self.update_town_menu()
```

- [ ] **Step 6.6: Add `draw_town_menu`**

Insert after `draw_message_window` (or wherever `draw_menu` lives):

```python
    def draw_town_menu(self):
        # Background: dimmed map
        self.draw_map()
        self.draw_status_bar()
        # Window
        x, y, w, h = 20, 50, 216, 150
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        pyxel.text(x + 8, y + 8, "町メニュー", 7, self.font)
        for i, label in enumerate(TOWN_MENU_LABELS):
            ly = y + 28 + i * 14
            color = 10 if i == self.town_menu_cursor else 7
            cursor = "▶ " if i == self.town_menu_cursor else "  "
            pyxel.text(x + 16, ly, cursor + label, color, self.font)
        # Footer hint
        gold = self.player["gold"]
        pyxel.text(x + 8, y + h - 16, f"GOLD: {gold}    A:決定 B:でる", 6, self.font)
```

- [ ] **Step 6.7: Wire `town_menu` into draw dispatch**

In `draw()`, add:

```python
        elif self.state == "town_menu":
            self.draw_town_menu()
```

- [ ] **Step 6.8: Apply A-cooldown in `update_map`**

At the top of `update_map`, after `if self.move_cooldown > 0` block:

```python
        if self._a_cooldown:
            # クールダウン中は A の押下を1回破棄して解除（D13）
            if self._btnp(CONFIRM_BUTTONS):
                self._a_cooldown = False
                return
            # それ以外の入力（移動など）は通常処理を続ける
```

> **Note:** `_btnp` の押下は1フレームに1回しか発生しないので、移動キーや B を読みつつ A だけ捨てる構造にする。

### Task 7: Manual import/syntax check

- [ ] **Step 7.1: Verify main.py compiles**

```bash
python -c "import ast; ast.parse(open('main.py').read()); print('main.py parses ok')"
```

Expected: `main.py parses ok`

- [ ] **Step 7.2: Run all unit tests**

```bash
python -m unittest discover test/ -v 2>&1 | tail -10
```

Expected: All previous tests still pass + new player_snapshot/save_store tests pass.

---

## Phase 4: Title screen continue / load

### Task 8: Title cursor with はじめから / つづきから

**Files:**
- Modify: `main.py` (`__init__`, `update_title`, `draw_title`)

- [ ] **Step 8.1: Add title cursor in `__init__`**

After town menu state init:

```python
        # Title cursor
        self.title_cursor = 0  # 0=はじめから, 1=つづきから
```

- [ ] **Step 8.2: Replace `update_title`**

```python
    def update_title(self):
        if self._btnp(UP_BUTTONS):
            self.title_cursor = (self.title_cursor - 1) % 2
            return
        if self._btnp(DOWN_BUTTONS):
            self.title_cursor = (self.title_cursor + 1) % 2
            return
        if self._btnp(CONFIRM_BUTTONS):
            if self.title_cursor == 0:
                # はじめから
                self.state = "map"
                return
            # つづきから — has_save が False なら無視（D8 グレーアウト）
            if not self._has_save:
                return
            self._do_load()
        # Legacy: 旧バインド (Z/SPACE/ENTER) も「はじめから」として残す
        if self._btnp(TITLE_START_BUTTONS):
            self.state = "map"

    def _do_load(self):
        snap = self.save_store.load()
        if snap is None:
            # 破損 / バージョン未来などのセーフティネット
            self._has_save = False
            self.show_message([NO_RECORD_MSG])
            self.prev_state = "title"
            self.state = "message"
            return
        restored = self._restore_snapshot(snap)
        # player の各キーを上書き
        for key, value in restored["player"].items():
            self.player[key] = value
        tx, ty = restored["town_pos"]
        self.player["x"] = tx
        self.player["y"] = ty
        self.player["in_dungeon"] = False
        self.dungeon_map = None
        self._a_cooldown = True  # ロード直後の暴発防止 (D13/D15)
        self.show_message([LOAD_OK_MSG])
        self.prev_state = "map"
        self.state = "message"
```

- [ ] **Step 8.3: Replace `draw_title`**

```python
    def draw_title(self):
        pyxel.cls(1)
        pyxel.text(70, 80, "BLOCK QUEST", 7, self.font)
        pyxel.text(50, 110, "- コードの冒険 -", 10, self.font)
        # Menu items
        labels = ["はじめから", "つづきから"]
        for i, label in enumerate(labels):
            ly = 150 + i * 16
            enabled = (i == 0) or self._has_save
            base_color = 7 if enabled else 5
            color = 10 if (i == self.title_cursor and enabled) else base_color
            cursor = "▶ " if i == self.title_cursor else "  "
            pyxel.text(80, ly, cursor + label, color, self.font)
        # If cursor is on a disabled item, hint
        if self.title_cursor == 1 and not self._has_save:
            pyxel.text(40, 200, "(まだ何も書き留めていない)", 5, self.font)
```

- [ ] **Step 8.4: Verify import again**

```bash
python -c "import ast; ast.parse(open('main.py').read()); print('ok')"
```

---

## Phase 5: 検証

### Task 9: Run all unit tests

- [ ] **Step 9.1**

```bash
python -m unittest discover test/ -v 2>&1 | tail -15
```

Expected: 既存 44 テスト + 新規 player_snapshot/save_store テスト全て PASS。

### Task 10: Smoke imports for main.py

- [ ] **Step 10.1**: main.py をモジュールとしてロードし、`Game` クラスを参照できることを確認（pyxel.init は呼ばずに）。

```bash
python -c "
import sys, importlib.util
spec = importlib.util.spec_from_file_location('main', 'main.py')
mod = importlib.util.module_from_spec(spec)
# pyxel.init を実行されると本物のウィンドウが開くので、Game クラスの定義だけ確認したい。
# 代替: ast パースだけ通せばクラス定義がコンパイルされていることが分かる。
import ast
tree = ast.parse(open('main.py').read())
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
print('classes:', classes)
print('has update_town_menu:', 'update_town_menu' in funcs)
print('has _do_load:', '_do_load' in funcs)
print('has _town_menu_save:', '_town_menu_save' in funcs)
"
```

Expected: `Game` クラスがあり、town_menu / load / save 関連関数がすべて定義されている。

### Task 11: SaveStore round trip with real file

- [ ] **Step 11.1**: 実際に save.json を作って読めるか確認

```bash
python -c "
import sys, tempfile, json
from pathlib import Path
sys.path.insert(0, '.')
from src.save_store import FileSaveStore, make_save_store
from src.player_snapshot import dump_snapshot, restore_snapshot

with tempfile.TemporaryDirectory() as d:
    p = Path(d) / 'save.json'
    store = make_save_store(p)
    print('store type:', type(store).__name__)
    # 仮の player
    player = {'x':20, 'y':12, 'hp':25, 'max_hp':30, 'gold':50, 'lv':2,
              'mp':5, 'max_mp':10, 'atk':5, 'def':3, 'agi':5,
              'exp':15, 'weapon':1, 'armor':0, 'items':[{'id':0,'qty':3}],
              'spells':[], 'poisoned':False, 'in_dungeon':False,
              'boss_defeated':False, 'max_zone_reached':1,
              'landmarkTreeSeen':True, 'landmarkTowerSeen':False,
              'dialog_flags':{}}
    snap = dump_snapshot(player, (20, 12))
    store.save(snap)
    print('saved, exists:', store.exists())
    loaded = store.load()
    restored = restore_snapshot(loaded)
    print('restored hp:', restored['player']['hp'])
    print('restored town_pos:', restored['town_pos'])
"
```

Expected: `store type: FileSaveStore`, exists True, hp 25, town_pos (20, 12)

---

## 実装後の振り返り

- **実装完了日**: 2026-04-07
- **テスト結果**: 59/59 PASS（既存44 + 新規15: player_snapshot 4 + save_store 11）。リグレッション無し。

### 計画と実績の差分

- **NPC リスト化（D14）は最小実装に留めた**: 既存 `TOWN_DIALOG_SCENES` を1町=1NPC として `はなす` で再生する形にした。複数NPC化は本steeringのフォローアップ。journey.md のスコープ（プレイヤー体験のみ）と整合。
- **ぶきや/ぼうぐや/どうぐや は `工事中` プレースホルダ**: セーブ機能の主目的に集中するため。個別ショップUIは別steering案件として切り出すべき。
- **A クールダウンの実装をシンプル化**: design.md では「A 押下を1回破棄してフラグ降ろし」だったが、実装では「何の入力でも次フレームで降ろす」のシンプル形にした。1フレームだけ持続するので暴発防止には十分。
- **LocalStorageSaveStore は実機テスト未実施**: ホスト Python に Pyodide が無いため。`import js` の遅延読み込み構造だけ用意し、デスクトップ Python での import は壊れないことを確認した。Phase 6（web実機確認）はフォローアップ。

### 学んだこと

- **Protocol + 環境検出ファクトリが正解**: `try: import js` 1ヶ所で分岐するシンプルな構造が、テスト容易性と本番互換性を両立した。
- **既存 `town` state を残したまま `town_menu` を併設**: 城（T_CASTLE）は既存の即時ダイアログを使い続けるので、両方の state を共存させた方が破壊的変更が少なかった。
- **`prev_state` パターンが効いた**: `_enter_town_message` で `prev_state = "town_menu"` を立てることで、メッセージを閉じたあと自動的に town_menu に戻る。新しいフロー制御を増やさずに済んだ。

### 次回への改善提案

1. **Game クラスのユニットテスト**: 現状 `pyxel.init()` を呼ぶため `Game` を直接インスタンス化できない。`Game` のロジック部分（`_town_menu_save` 等）を Pyxel から切り離し、ヘッドレスでテスト可能にすると `do_save` 経路の自動テストが書ける。
2. **NPC リスト化の本実装**: `TOWN_NPCS: dict[TownId, list[NPC]]` を `assets/dialogue.yaml` から読み込む形に変える。
3. **ぶきや/ぼうぐや/どうぐや の本実装**: 既存ショップ設計（gherkin）を別 steering で詳細化してから着手。
4. **web 実機検証**: `tools/build_web_release.py` でビルド → ブラウザで `localStorage` 永続を確認 → プライベートブラウジングでエラーパス確認。
5. **Pyxel ウィンドウを開かずに `Game.__init__` の途中まで走らせる**: monkeypatch で `pyxel.init/run` をスタブ化したテストを書けば、save_store 注入と state 遷移の統合テストができる。
