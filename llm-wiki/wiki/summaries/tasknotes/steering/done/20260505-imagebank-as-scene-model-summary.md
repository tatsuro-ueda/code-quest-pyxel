---
source: raw/tasknotes/steering/done/20260505-imagebank-as-scene-model.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 imagebank をシーン Model に直結する（world_map 中間層を廃止） Summary Draft

## summary

この tasknote は、explore 系の map 読み取りを `world_map` 中間層から imagebank / tilemap 直読へ寄せ、scene model が Pyxel の resource DB をそのまま主語にできるようにした記録です。実装の中心は、ExploreModel に `get_tile` / `is_walkable` / `current_tilemap_id` を追加して image_banks を DI し、ExplorePresenter が `bltm` 引数を組み立て、ExploreView が `pyxel.bltm` 1 回で地形を描く構造へ切り替えたことでした。

## key_points

- A 案は `imagebank をシーン Model に直結し world_map 中間層を薄くする` 方針だった。
- ExploreModel が `pyxel.tilemaps[0].pget` を使う時点で、Code Maker 編集即反映の仕組みは成立すると整理した。
- ExplorePresenter は `bltm` 引数とボスマーカー位置を組み立て、ExploreView は地形を 1 回の `bltm` で描くようになった。
- `framework-rule.md` の M1 / M4-2 / M4-3 と guard test も、この新構造に合わせて更新した。
- 一方で `GameState.world_map` と `ImageBanks.bake/derive` は legacy 互換のため残置し、scope を縮めて完走した。
- water animation、path/shore variant、自動接続、legacy field 削除は follow-up task として分離した。

## important_quotes

- "Code Maker 編集即反映の仕組みは、ExploreModel.get_tile / is_walkable が `pyxel.tilemaps[0].pget` を呼び出す時点で達成されている。"
- "pyxel.bltm 1回呼び化"
- "GameState.world_map field と ImageBanks.bake_world_to_tilemap / derive_world_from_tilemap は legacy 互換のため残置"

## open_questions

- water animation と path/shore variant を、直読モデルのままどう復活させるべきか。
- legacy 互換で残した `world_map` と `ImageBanks` の中間層を、いつ物理削除するべきか。
