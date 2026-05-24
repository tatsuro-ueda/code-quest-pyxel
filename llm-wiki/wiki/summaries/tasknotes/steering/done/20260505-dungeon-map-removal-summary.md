---
source: raw/tasknotes/steering/done/20260505-dungeon-map-removal.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 game.dungeon_map / GameState.dungeon_map 撤去 Summary Draft

## summary

この note は、`game.dungeon_map` と `GameState.dungeon_map` を消し、dungeon も world_map と同じく `pyxres` / tilemap 直読を真実にするための follow-up 設計です。runtime の snapshot 撤去、fallback 専用 regenerate への改名、再侵入ガード、test 書き換えの分離までを 3 commit 単位で固めています。

## key_points

- `dungeon_map` snapshot を消し、Explore 側の dungeon tile 読み取りを tilemap 直読へ一本化する方針を固定した。
- `bake_dungeon_to_tilemap` を fallback 専用関数へ改め、Code Maker 編集が pyxres 読み込み後に上書きされない対称構造を目指した。
- `rewrite-tests-for-imagebank-ssot` を別 task に分け、本 note は runtime 撤去と static guard の設計に集中した。

## important_quotes

- "`game.dungeon_map / GameState.dungeon_map 撤去`"
- "`fallback 専用`"

## open_questions

- `dungeon_template` と `dungeon_rooms` の残り方を、どこまで service 内部事情として閉じるべきか。
- dungeon 側でも world_map と同じ強さの static guard をどこまで増やすべきか。
