# Dungeon Boss Trigger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ダンジョン最奥の部屋にボストリガーを配置し、踏んだときだけ `まおうグリッチ` 戦が始まるようにする

**Architecture:** `generate_dungeon()` が最奥部屋へ専用トリガータイルを置き、`Game._check_tile_events()` がそのタイルを踏んだときだけ `_start_battle(BOSS_DATA, is_boss=True)` を呼ぶ。通常探索の `zone 4` ランダムエンカウントはそのまま維持し、`boss_defeated` で再発火を止める。

**Tech Stack:** Python, Pyxel, pytest, monolithic `main.py`

---

### Task 1: 最奥部屋配置の Red/Green

**Files:**
- Modify: `main.py`
- Test: `test/test_dungeon_boss_trigger.py`

- [ ] **Step 1: 最奥配置の failing test を書く**

```python
def test_generate_dungeon_places_single_boss_trigger_in_last_room(self):
    grid, rooms = M.generate_dungeon(seed=99)
    last_room = rooms[-1]
    boss_tiles = [
        (x, y)
        for y, row in enumerate(grid)
        for x, tile in enumerate(row)
        if tile == M.T_BOSS_TRIGGER
    ]

    self.assertEqual(len(boss_tiles), 1)
    bx, by = boss_tiles[0]
    rx, ry, rw, rh = last_room
    self.assertTrue(rx <= bx < rx + rw)
    self.assertTrue(ry <= by < ry + rh)
    self.assertNotEqual(grid[rooms[0][1] + 1][rooms[0][0] + 1], M.T_BOSS_TRIGGER)
```

- [ ] **Step 2: テストが正しく fail することを確認する**

Run: `python -m pytest test/test_dungeon_boss_trigger.py -q`
Expected: `AttributeError` or assertion failure because `T_BOSS_TRIGGER` / boss placement is missing

- [ ] **Step 3: 最小実装で最奥配置を通す**

```python
T_BOSS_TRIGGER = 26
TILE_DATA[T_BOSS_TRIGGER] = TILE_BOSS_TRIGGER

def generate_dungeon(seed=99):
    ...
    if rooms:
        sx = rooms[0][0] + 1
        sy = rooms[0][1] + 1
        grid[sy][sx] = T_STAIR_UP

        brx, bry, brw, brh = rooms[-1]
        bx = brx + brw // 2
        by = bry + brh // 2
        if (bx, by) == (sx, sy):
            bx = min(brx + brw - 1, bx + 1)
        grid[by][bx] = T_BOSS_TRIGGER
    return grid, rooms
```

- [ ] **Step 4: focused test を再実行して pass を確認する**

Run: `python -m pytest test/test_dungeon_boss_trigger.py -q`
Expected: 最奥配置テストが PASS

- [ ] **Step 5: Commit**

```bash
git add main.py test/test_dungeon_boss_trigger.py docs/superpowers/plans/2026-04-13-dungeon-boss-trigger.md
git commit -m "fix: place dungeon boss trigger in final room"
```

### Task 2: ボス踏み判定の Red/Green

**Files:**
- Modify: `main.py`
- Test: `test/test_dungeon_boss_trigger.py`

- [ ] **Step 1: 踏み判定の failing test を書く**

```python
def test_check_tile_events_starts_boss_battle_on_boss_trigger(self):
    game = self.make_game()
    game.player = {"in_dungeon": True, "boss_defeated": False}
    game._start_battle = MagicMock()

    M.Game._check_tile_events(game, M.T_BOSS_TRIGGER, 7, 8)

    game._start_battle.assert_called_once_with(M.BOSS_DATA, is_boss=True)
```

- [ ] **Step 2: Red を確認する**

Run: `python -m pytest test/test_dungeon_boss_trigger.py -q`
Expected: `_start_battle` not called

- [ ] **Step 3: 最小実装で踏み判定を追加する**

```python
def _check_tile_events(self, tile, nx, ny):
    p = self.player

    if p["in_dungeon"] and tile == T_BOSS_TRIGGER:
        if not p.get("boss_defeated"):
            self._start_battle(BOSS_DATA, is_boss=True)
        return
```

- [ ] **Step 4: focused test を再実行して pass を確認する**

Run: `python -m pytest test/test_dungeon_boss_trigger.py -q`
Expected: 踏み判定テストが PASS

- [ ] **Step 5: Commit**

```bash
git add main.py test/test_dungeon_boss_trigger.py
git commit -m "fix: trigger dungeon boss battle from final room tile"
```

### Task 3: 再発火防止と回帰確認

**Files:**
- Modify: `main.py` (必要なら最小調整のみ)
- Test: `test/test_dungeon_boss_trigger.py`

- [ ] **Step 1: 再発火防止テストを書く**

```python
def test_check_tile_events_ignores_boss_trigger_after_boss_defeated(self):
    game = self.make_game()
    game.player = {"in_dungeon": True, "boss_defeated": True}
    game._start_battle = MagicMock()

    M.Game._check_tile_events(game, M.T_BOSS_TRIGGER, 7, 8)

    game._start_battle.assert_not_called()
```

- [ ] **Step 2: Red を確認する**

Run: `python -m pytest test/test_dungeon_boss_trigger.py -q`
Expected: 既存実装次第で fail、少なくとも期待挙動が未固定ならここで詰める

- [ ] **Step 3: 必要な最小修正だけ入れる**

```python
if p["in_dungeon"] and tile == T_BOSS_TRIGGER:
    if not p.get("boss_defeated"):
        self._start_battle(BOSS_DATA, is_boss=True)
    return
```

- [ ] **Step 4: focused test と全体テストを実行する**

Run: `python -m pytest test/test_dungeon_boss_trigger.py -q`
Expected: PASS

Run: `python -m pytest test/ -q`
Expected: 全体 PASS

- [ ] **Step 5: Commit**

```bash
git add main.py test/test_dungeon_boss_trigger.py
git commit -m "test: lock dungeon boss trigger behavior"
```
