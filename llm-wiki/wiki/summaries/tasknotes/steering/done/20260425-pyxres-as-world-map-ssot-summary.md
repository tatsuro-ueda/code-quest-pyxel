---
source: raw/tasknotes/steering/done/20260425-pyxres-as-world-map-ssot.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月25日 pyxres を world_map の SSoT にする（procedural 上書きを止める） Summary Draft

## summary

この tasknote は、`pyxres` を world map の SSoT とみなし、起動時の procedural bake が Code Maker 編集済みタイルを上書きしないようにした変更を、夜間委任まで含めて記録したものです。修正の中心は、`bake_world_to_tilemap` 冒頭で `if self.pyxres_loaded: return` を入れ、probe・pytest・bundle 再ビルドで `(30,21)` や `(28,20)` の道形状が BEFORE / AFTER 一致になることを確認したことでした。

## key_points

- ねらいは `pyxres` に刻まれた world map を起動時の procedural 処理で潰さないことだった。
- 夜間委任は probe → failing test → fix → bundle rebuild の TDD 順で自走させた。
- 最小修正は `image_banks.py` の `bake_world_to_tilemap` 冒頭に `if self.pyxres_loaded: return` を置くことだった。
- probe で `(30,21)` と `(28,20)` の BEFORE = AFTER 一致を確認し、bundle 内 `main.py` にも guard が入っていることを見た。
- pyxres 退避→再生成→復元の scenario も通し、fallback 生成経路は維持した。
- dungeon bake、path variant、unknown tile fallback などの follow-up は別タスク候補として残した。

## important_quotes

- "pyxres を world_map の SSoT にする"
- "`if self.pyxres_loaded: return`"
- "(30,21) と (28,20) の BEFORE = AFTER 完全一致"

## open_questions

- dungeon bake や path variant の同型問題を、どこまで同じ SSoT ルールで扱うべきか。
- unknown tile fallback を grass へ潰さないために、どの derive ルールが必要か。
