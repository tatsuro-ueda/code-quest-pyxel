---
source: raw/tasknotes/steering/done/20260509-stakeholder-voices-coverage-report.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 stakeholder_voices coverage report Summary Draft

## summary

この note は、stakeholder voices の source trace coverage を document 単位で測る JSON report を追加した記録です。`source_documents` の extraction contract と report CLI を入れ、どの docs の stable ref が何件未移植かを定量で見えるようにしました。

## key_points

- `facts.source_documents` 7 件に extraction contract を追加した。
- `source_trace_coverage.py` と `report_source_trace_coverage.py` を新設し、`total/referenced/missing` を JSON で返せるようにした。
- `customer_journeys 31`, `product_requirements_map 7`, `guardrails 5` などの missing count を real repo で定量化した。

## important_quotes

- "`JSON で十分だった`"
- "`missing stable ref を次タスク候補として拾える`"

## open_questions

- regex ベースの extraction を、将来どこまで section-level や意味的 coverage へ広げるべきか。
- 大量の missing を、どの粒度の tasknote に分割すると運用しやすいか。
