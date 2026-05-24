---
source: raw/tasknotes/steering/done/20260509-stakeholder-voices-source-traceability.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 stakeholder_voices source traceability Summary Draft

## summary

この note は、stakeholder_voices に `doc_id:stable_ref` 形式の structured traceability を入れた記録です。人向け path 参照と checker 向け stable ref を分離し、active requirement/acceptance の structured 移植率を 100% まで押し上げました。

## key_points

- `facts.source_documents` 6 件を追加し、requirement/acceptance 10+10 件へ `source_trace_refs` を付与した。
- `source_traceability_integrity` rule が doc id、catalog path、stable token の存在を deterministic に検証するようになった。
- `source_refs` と `source_trace_refs` を分離し、人向け参照と機械参照の役割を明確にした。

## important_quotes

- "`source_refs と source_trace_refs を分離`"
- "`structured traceability 100%`"

## open_questions

- `customer-jobs.md` の stable id catalog をどう設計して jobs 層も structured trace 対象にするべきか。
- semantic な「本当に適切な対応先か」の判断を、将来どこまで補うべきか。
