---
source: raw/tasknotes/steering/done/20260505-imagebank-direct-cleanup.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 imagebank 直読の中間スナップショット撤去（world_map / bake リネーム） Summary Draft

## summary

この note は、`world_map` 中間 snapshot を物理撤去し、`bake_world_to_tilemap` を fallback 専用へ改名するための縮小設計です。test 書き換えを runtime 撤去より先に行う順序まで含めて、`pyxres` を唯一の真実に戻す段取りを固定しています。

## key_points

- `game.world_map` / `GameState.world_map` を runtime と state から消す方向を確定した。
- 事前 grep により、想定 12 file ではなく `game.world_map =` 仕込みは 3 test file に絞られると分かった。
- commit 順序を `test 書き換え -> runtime 撤去 -> static guard` に固定し、中途 red を避ける方針を明文化した。

## important_quotes

- "`2 つの真実が並走`"
- "`regenerate_world_tilemap_fallback`"

## open_questions

- paired で残る dungeon 側 cleanup を、どの時点で同じ guard 強度まで揃えるべきか。
- tilemap 直読前提の test helper をどこまで共通化してよいか。
