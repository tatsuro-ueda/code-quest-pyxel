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

- **深層的目的**：`game.world_map` 撤去と対称に、`dungeon_map` も中間スナップショットを廃止する
- **やらないこと**：dungeon の Code Maker 編集対応（dungeon は依然 procedural のみ）

## 2) Gherkin（要素のみ）

- src 全域で `game.dungeon_map` がマッチ 0 件
- `GameState.dungeon_map` フィールドが消える
- dungeon の入退出ロジックは `in_dungeon` フラグ + `dungeon_template` 直読で代替されている
- title / ending / explore の 3 シーンで `game.dungeon_map = None / [...]` を削除した結果、dungeon に入って戻る一連のフローが pytest で green

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
