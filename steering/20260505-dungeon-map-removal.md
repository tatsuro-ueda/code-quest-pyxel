---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:30:00+09:00
dateModified: 2026-05-05T17:30:00+09:00
tags:
  - task
  - ssot
  - dungeon
  - cleanup
---

# 2026年5月5日 game.dungeon_map / GameState.dungeon_map 撤去

> 状態：① Journey 略式（フォロータスク起票のみ）

## 1) Journey

- **深層的目的**：状況をシンプルにして好循環を起こしたい

1. 💦 （開発者・AI）ダンジョンに関する機能を追加したりバグ修正したい（コードエディタ）
2. 💦 （開発者・AI）リポジトリを眺める（コードエディタ）
3. Before
  1. ❌ もう使っていないファイルや関数が残っている（コードエディタ）
  2. ❌ （開発者・AI）わかりにくい
4. After
  1. ✅ もう使っていないファイルや関数が残っていない（コードエディタ）
  1. ✅ すべてImageBankに移行済み（コードエディタ）
  1. ✅ 状況がシンプル（コードエディタ）
  2. ♥️ （開発者・AI）嬉しい

## 2) Gherkin

- **やらないこと**：dungeon の Code Maker 編集対応（dungeon は依然 procedural のみ）

### シナリオ1：使っていない field の仕込みが src/ から消える
> 🧱 Given: 改修後の src/。`runtime/app.py:79` の `self.dungeon_map = None` 初期化と、title / ending / explore 3 シーンの `game.dungeon_map = None / [...]` 代入が撤去されている。🎬 When: `grep -rnE 'game\.dungeon_map\|self\.dungeon_map' src/ --include='*.py'` を実行。✅ Then: マッチ 0 件。読んだ開発者・AI が「dungeon 状態は別の場所にある」と誤認しなくなる。

### シナリオ2：GameState から dungeon_map フィールドが消える
> 🧱 Given: 改修後の `src/shared/services/game_state.py`。🎬 When: `dungeon_map` を grep。✅ Then: マッチ 0 件。GameState 目標形（framework-rule.md M4-3 改訂版）に揃う。

### シナリオ3：dungeon の tile 読み取りが ImageBank 直読に一本化される
> 🧱 Given: 改修後の Explore シーン。🎬 When: 子どもがダンジョン内を移動して描画／衝突判定が走る。✅ Then: `ExploreModel.get_tile(x, y, in_dungeon=True)` が `pyxel.tilemaps[0].pget` の Y オフセット領域 (`DUNGEON_TM_OFFSET_Y`) を読み、`image_banks.tile_id_by_pixel` で tile id を解決する経路だけで完結する。`shared/state` や `game.*` から dungeon タイル配列を読み取る経路は存在しない（Journey After (2)「すべて ImageBank に移行済み」と整合）。

### シナリオ4：dungeon の入退出フローが `in_dungeon` フラグだけで完結する
> 🧱 Given: 改修後の repo。🎬 When: 子どもが洞窟に入る → ダンジョン内を歩く → 階段で脱出する → エンディング to dungeon 不在 になる、の一連を fake game で辿る。✅ Then: 各遷移で `player_model.in_dungeon` の True/False の切替と `dungeon_template` への直接アクセスだけで成立する。`game.dungeon_map` への代入が一度も発生しない。pytest が green。

### シナリオ5：`bake_dungeon_to_tilemap` は残置されている（fallback 経路の保全）
> 🧱 Given: 改修後の `src/shared/services/image_banks.py`。🎬 When: `setup_world_tilemap` 経由でゲーム起動。✅ Then: `bake_dungeon_to_tilemap` が tilemap[0] の dungeon 領域 (`DUNGEON_TM_OFFSET_Y` 以降) に `dungeon_template` を焼く処理は残っており、`ExploreModel.get_tile(in_dungeon=True)` が正しい tile を返せる。dungeon の Code Maker 編集対応は別タスク扱いだが、procedural 生成→tilemap 焼き付けの経路は壊さない。

### シナリオ6：再侵入を防ぐ静的ガード
> 🧱 Given: 改修完了後、将来的に新規コードで `game.dungeon_map` を復活させる懸念。🎬 When: `test_cjg_framework_rule_guards.py` に「src/ 配下に `game\.dungeon_map\|self\.dungeon_map` が侵入していないこと」を assert する grep ガードを 1 件追加する。✅ Then: 古いパターンの再侵入が pytest で即 fail。Journey After「状況がシンプル」が将来も保たれる。

### シナリオ7：既存テストへの影響は別タスクで吸収
> 🧱 Given: `test_dungeon_boss_trigger.py` 等が `game.dungeon_map = [[T_FLOOR]]` を仕込む箇所あり。🎬 When: 本タスク commit 直後の pytest。✅ Then: 動的属性として代入が通り pytest は green を維持する。test 群の物理書き換えは別タスク `20260505-rewrite-tests-for-imagebank-ssot.md` のスコープ。本タスクは「runtime が読まなくする」までを担当。

## 3) Design

### 影響範囲（src）
- `src/runtime/app.py:79` — `self.dungeon_map = None`
- `src/scenes/title/presenter.py:78` — `game.dungeon_map = None`（new game 時）
- `src/scenes/ending/presenter.py:21` — `game.dungeon_map = None`（ending 時）
- `src/scenes/explore/presenter.py:100, 116, 164` — dungeon 入退出での切替

### 方針
- ExploreModel.get_tile が `in_dungeon=True` で pyxel.tilemaps[0] の Y オフセット領域を読む（既に実装済み）
- dungeon_template そのものは「procedural ベース」なので残置。ただし「現在 dungeon に居るか」のマーカーは `player_model.in_dungeon` で十分
- dungeon_template を tilemap[0] の dungeon 領域に焼く `bake_dungeon_to_tilemap` は残す（pyxel.tilemaps からの直読を成立させるために必要）

## 4) Tasklist

（着手時に作成）

## 5) Result / 6) Discussion

（着手時に追記）
