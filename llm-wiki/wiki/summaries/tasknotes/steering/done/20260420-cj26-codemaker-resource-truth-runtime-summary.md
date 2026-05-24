---
source: raw/tasknotes/steering/done/20260420-cj26-codemaker-resource-truth-runtime.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月20日 CJ26 Code Maker で直した image bank を runtime が巻き戻さないようにする Summary Draft

## summary

この tasknote は、Code Maker で直した image bank を runtime が巻き戻していた原因を、描画 API の不足ではなく guardrail の責務ずれとして整理し直した記録です。主な判断は、`_tile_bank_layout_valid()` と self-heal が child-edited resource を `不一致` 扱いしていた以上、truth を runtime repair に置かず build / verify へ戻すべきだと定義し直したことでした。

## key_points

- `my_resource.pyxres` は読めていても、`_tile_bank_layout_valid()` が Code Maker で変えた image bank を不一致扱いしていた。
- `_paint_tile_bank()` / `_paint_sprite_bank()` / `pyxel.save()` が child-edited resource を runtime で巻き戻していた。
- 問題は `pyxel.blt` の有無ではなく、旧ガードレール前提の self-heal が残っていたことだった。
- truth は runtime repair ではなく build / verify に戻すべきだと整理した。
- `CJ26` を主に、runtime / build / staging / test の責務を切り分ける note として再定義した。

## important_quotes

- "Code Maker で変えた image bank を「不一致」とみなし"
- "runtime repair ではなく build / verify の責務へ戻す必要がある。"
- "runtime が旧ガードレール前提の self-heal を持ち続けている問題だった。"

## open_questions

- runtime self-heal のうち、どこまでを build / verify 側へ移すべきか。
- stale resource / bank 競合を、どの検査で止めるのが最も自然か。
