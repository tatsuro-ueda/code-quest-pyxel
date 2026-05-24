---
source: raw/tasknotes/steering/done/20260505-remove-tile-water2-deadcode.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 TILE_WATER2 / tile_bank_water2 削除と view_model docstring の stale 記述更新 Summary Draft

## summary

この note は、`TILE_WATER2` 系 dead code を削除し、image bank layout 変更後の `.pyxres` 再生成を CC 環境で再現可能にした記録です。runtime cleanup に加えて `tools/rebake_pyxres.py` という運用レールも整えています。

## key_points

- `pyxel.bltm` 1 回描画化の残りとして `TILE_WATER2 / tile_bank_water2` を真の dead code と特定した。
- CC 環境で Pyxel を headless install し、`tools/rebake_pyxres.py` で fallback 経路から `pyxel.save` を再現できるようにした。
- dead code 0 件、docstring 整合、build artifact 再生成までを完了し、目視確認だけを人作業として残した。

## important_quotes

- "`真の dead code 候補`"
- "`tools/rebake_pyxres.py`"

## open_questions

- image bank layout 変更時の rebake 手順を README/CONTRIBUTING のどこへ正式化するべきか。
- Code Maker 上での見た目検証を将来どこまで自動化できるか。
