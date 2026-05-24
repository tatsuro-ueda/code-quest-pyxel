---
source: raw/tasknotes/steering/done/20260509-customer-jobs-stable-trace-ids.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 customer-jobs stable trace ids Summary Draft

## summary

この note は、`customer-jobs.md` に stable token を入れ、active request から customer job を deterministic に辿れるようにした記録です。heading の揺れではなく本文 token を正にし、stakeholder_voices の request trace を jobs 層へ初めて接続しました。

## key_points

- `customer-jobs.md` の top-level job 10 件へ stable token を追加し、重複する `JSC` も token で分離した。
- `stakeholder_voices.yml` に `customer_jobs` source document を追加し、active request へ `source_trace_refs` を付与した。
- checker と safe normalization を request trace まで拡張し、壊れた job trace を deterministic warning 化した。

## important_quotes

- "`stable token を正にした方が checker 実装が単純`"
- "`customer_jobs:*`"

## open_questions

- `customer_jobs` 専用の extraction contract を、coverage report へどう組み込むべきか。
- technical trace のみで支えている request を、どこまで job root へつなぎ直すべきか。
