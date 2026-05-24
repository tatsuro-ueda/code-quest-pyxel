---
source: raw/tasknotes/steering/done/20260509-architecture-rules-tree-coverage-expansion.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 architecture_rules tree-first 後の rule coverage 拡張 Summary Draft

## summary

この note は、tree-first 化した architecture rules の coverage を棚卸しし、どこまで static checker へ昇格できるかを分類した記録です。deterministic / llm_assisted / manual の境界を数え上げ、次の unit task 名まで切り出しています。

## key_points

- `deterministic` 4 件、`llm_assisted` 3 件、`manual` 1 件という coverage 構成を明示した。
- `scene_static_boundary_checks` と `shared_directory_role_checks` を次の static 昇格単位として提示した。
- Code Maker primary editor と pyxres source of truth は、当面 human / llm 判断が必要だと切り分けた。

## important_quotes

- "`rule coverage 拡張`"
- "`scene_static_boundary_checks`"

## open_questions

- noise を増やさずに static 昇格できる境界は、どこまで existing test と再利用可能か。
- Code Maker / pyxres 系 rule を llm/manual に留める判断根拠を、どこまで formalize すべきか。
