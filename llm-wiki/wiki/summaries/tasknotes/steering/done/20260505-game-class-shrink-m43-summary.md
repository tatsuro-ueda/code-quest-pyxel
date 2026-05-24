---
source: raw/tasknotes/steering/done/20260505-game-class-shrink-m43.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 Game クラス state 7 件の段階移行（M4-3 圧縮） Summary Draft

## summary

この note は、`Game` クラスを runtime shell に縮めるために 7 つの field を 5 ループで外へ逃がす M4-3 設計です。field ごとの参照件数と移送先を先に確定し、1 ループ 1 commit で revert 可能に保つ進め方を明文化しています。

## key_points

- `current_town`、camera、scene state、debug state、`dungeon_rooms` の移送先を GameState / ExploreModel / SceneManager / DebugService に割り当てた。
- 最小スコープから最大スコープへ進む 5 ループ順序で、`state` / `prev_state` は最後に回す設計にした。
- 最後に `ALLOWED_GAME_FIELDS` 的な static guard を置き、runtime shell への到達を future-proof する前提を置いた。

## important_quotes

- "`Game = ランタイム殻`"
- "`1 ループ = 1 commit`"

## open_questions

- `state` / `prev_state` の 72 箇所移行は、どこで PR 分割して人 review を挟むべきか。
- 最終的な Game field allowlist を、どの粒度で docs と test の両方に固定すべきか。
