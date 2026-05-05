---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:30:00+09:00
dateModified: 2026-05-05T17:30:00+09:00
tags:
  - task
  - testing
  - ssot
  - imagebank
  - cleanup
---

# 2026年5月5日 imagebank SSoT 化に伴う test 群の書き換え

> 状態：① Journey 略式（フォロータスク起票のみ）

## 1) Journey

- **深層的目的**：`game.world_map` / `game.dungeon_map` 撤去後、test 群が「runtime が読まなくなった field」を仕込み続ける状態を解消する
- **やらないこと**：test 観点そのものの追加 / 削除（既存観点を新仕様で書き直すだけ）

## 2) Gherkin（要素のみ）

- 14 ファイルから `game.world_map = ...` / `game.dungeon_map = ...` の仕込みが撤去されている
- 代わりに `pyxel.tilemaps[0].pget` をモックして tile id を返す形になっている
- `image_banks.tile_id_by_pixel` を test 内で仕込むパターンが整理されている
- pytest 全 green（既存 711 + 本タスクで増減があれば追記）

## 3) Design

### 対象 14 ファイル
- test/test_world_map_ssot.py
- test/test_setup_world_tilemap_preserves_user_edits.py
- test/test_world_map_contract.py
- test/test_runtime_shim.py
- test/test_world_generation.py
- test/test_tilemap_editor_truth.py
- test/test_dungeon_boss_trigger.py
- test/test_cj24_sound_editor_truth.py
- test/test_architecture_layout.py
- test/test_cjg_explore_model_imagebank_read.py（新仕様で書かれているので影響なしのはず、要確認）
- test/test_cjg_ending_scene_behavior.py
- test/test_cjg_title_scene_behavior.py
- test/test_cjg_map_tile_transitions.py
- test/test_cjg_town_entry_sets_current_town.py

### パターン共通化
- `_set_tilemap_pget(returns: dict[(tu, tv), (cell_tu, cell_tv)])` ヘルパを作る（test/_helpers/imagebank_stub.py 等）
- 既存 `make_*_game` の `game.world_map = [...]` を `_set_tilemap_pget(...)` に置換
- `tile_id_by_pixel` も同 helper で仕込む

## 4) Tasklist

（着手時に 14 ファイル分の小タスクに分解）

## 5) Result / 6) Discussion

（着手時に追記）
