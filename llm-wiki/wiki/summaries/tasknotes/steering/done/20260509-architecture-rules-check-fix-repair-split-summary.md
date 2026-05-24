---
source: raw/tasknotes/steering/done/20260509-architecture-rules-check-fix-repair-split.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 architecture rules check fix repair split Summary Draft

## summary

この note は、`guardian` という曖昧名を `check / fix / repair` へ分解し、active tooling を `tools/architecture_rules/` package と薄い CLI shim に整理した記録です。責務名と import 経路を揃えて、歴史名と live 名の境界も言語化しました。

## key_points

- `check_architecture_rules.py`、`fix_architecture_rules.py`、`repair_architecture_rules.py` と package import へ active code を寄せた。
- `architecture_guardian` は history 名として残し、test / coverage も `repair_autofix` へ寄せた。
- history docs と unrelated dist diff をそのままにし、live 更新対象だけを絞る運用判断を記録した。

## important_quotes

- "`check / fix / repair`"
- "`薄い CLI shim`"

## open_questions

- history docs の旧名を grep で混線させないために、どの追加整理が要るか。
- repair_* 集計名の互換をいつまで維持し、どの段階で rename すべきか。
