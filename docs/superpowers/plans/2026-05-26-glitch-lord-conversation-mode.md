# Glitch Lord Conversation Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 魔王トリガーを即戦闘から共通の全画面ページ送り会話へ差し替え、読み切り後に一度だけ戦闘へ入るようにする。

**Architecture:** `page_dialog` という共通 full-screen scene を 1 つ追加し、`ExplorePresenter` はそこへ魔王戦前会話を渡す。ページ送りの advance / page_lines / prompt 判定は shared helper に切り出し、Professor 側の非分岐ページ送りも同じ helper を使う。

**Tech Stack:** Python 3, Pyxel runtime scene dispatch, pytest

---

### Task 1: Failing tests で未完了点を固定する

**Files:**
- Modify: `test/test_dungeon_boss_trigger.py`
- Modify: `test/test_dialogue_paging.py`

- [ ] **Step 1: trigger 時点で battle が始まらない failing test を追加**

```python
def test_check_tile_events_starts_prebattle_dialog_before_glitch_lord_battle(self):
    game = self.make_game()
    game.page_dialog_scene = MagicMock()

    game.explore_scene._check_tile_events(self.main.T_GLITCH_LORD_TRIGGER, 7, 8)

    game.page_dialog_scene.enter_scene.assert_called_once()
    game.battle_scene.start.assert_not_called()
```

- [ ] **Step 2: full-screen page dialog の終端で callback が 1 回だけ呼ばれる failing test を追加**

```python
def test_page_dialog_calls_callback_once_after_last_page(self):
    game = self.make_game()
    game.page_dialog_scene.enter_lines(["a", "b"], callback=MagicMock())
    game.input_state.btnp = lambda buttons: buttons == self.main.CONFIRM_BUTTONS

    game.page_dialog_scene.update()
    game.page_dialog_scene.update()

    callback.assert_called_once_with()
```

- [ ] **Step 3: failing を確認**

Run: `python -m pytest test/test_dungeon_boss_trigger.py test/test_dialogue_paging.py -q`
Expected: 魔王トリガー / page_dialog 未実装で FAIL

### Task 2: 共通 page dialog scene と helper を追加する

**Files:**
- Create: `src/shared/services/page_dialog_flow.py`
- Create: `src/scenes/page_dialog/model.py`
- Create: `src/scenes/page_dialog/view_model.py`
- Create: `src/scenes/page_dialog/view.py`
- Create: `src/scenes/page_dialog/presenter.py`
- Create: `src/scenes/page_dialog/scene.py`
- Modify: `src/runtime/app.py`

- [ ] **Step 1: shared helper を追加**
- [ ] **Step 2: generic full-screen scene を追加**
- [ ] **Step 3: runtime dispatch に `page_dialog` を登録**
- [ ] **Step 4: targeted tests を再実行**

Run: `python -m pytest test/test_dungeon_boss_trigger.py test/test_dialogue_paging.py -q`
Expected: 新しい page_dialog の基礎テストが PASS

### Task 3: Explore / Professor を共通 helper へ接続する

**Files:**
- Modify: `src/scenes/explore/presenter.py`
- Modify: `src/scenes/professor/presenter.py`

- [ ] **Step 1: ExplorePresenter の魔王トリガーを `page_dialog_scene.enter_scene("boss.glitch.prebattle_01", ...)` に差し替える**
- [ ] **Step 2: ProfessorPresenter の intro 非分岐 / ending ページ送りで shared helper を使う**
- [ ] **Step 3: regression test を実行**

Run: `python -m pytest test/test_dungeon_boss_trigger.py test/test_dialogue_integration.py test/test_dialogue_paging.py -q`
Expected: PASS

### Task 4: 検証と close 更新

**Files:**
- Modify: `steering/20260418 アプリ：cj09-glitch-lord-conversation-mode.md`
- Modify: `llm-wiki/raw/tasknotes/steering/2026年5月26日 アプリ：魔王グリッチ会話導線の完了確認と仕上げ.md`

- [ ] **Step 1: full pytest を実行**

Run: `python -m pytest test/ -q`
Expected: PASS

- [ ] **Step 2: development checklist を `/tmp` にコピーしてレビュー結果を note に残す**

Run: `cp docs/development-checklist.md /tmp/development-checklist-20260526-1537.md`
Expected: `/tmp` にレビュー用コピーができる

- [ ] **Step 3: steering / tasknote を close 可能状態へ更新**
- [ ] **Step 4: 必要なら commit → merge**
