---
source: raw/tasknotes/steering/done/20260507-verify-scripts-and-makefile.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月7日 検証スクリプト群と Makefile 統合（B1 + C1 + C2 + B2 + C4 の本体） Summary Draft

## summary

この note は、docstring drift と CJ/CJob 参照整合を検査する verify script 群を作り、`Makefile` へ組み込んだ本体実装記録です。build 前に docs/code/journey の整合を見る lane を 1 つ増やしました。

## key_points

- `tools/verify_module_docstrings.py` と `tools/verify_cj_cjob.py` を追加し、AST / Markdown の両方を機械検査できるようにした。
- `Makefile` に `verify-module-docstrings`、`verify-cj-cjob`、`verify` を追加し、`build` が `verify gen test` に依存する形へ変えた。
- `docs/customer-journeys.md` のカテゴリ番号 drift を副次修正し、注入テストで drift 時に fail することも確認した。

## important_quotes

- "`build: verify gen test`"
- "`83 files OK`"

## open_questions

- skip-missing-docstring 前提を、どの段階で完全 hard gate へ近づけるべきか。
- verify lane にさらにどの docs consistency check を足すと価値が高いか。
