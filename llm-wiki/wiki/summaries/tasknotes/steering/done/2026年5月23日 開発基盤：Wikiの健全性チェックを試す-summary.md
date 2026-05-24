---
source: raw/tasknotes/steering/done/2026年5月23日 開発基盤：Wikiの健全性チェックを試す.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月23日 開発基盤：Wikiの健全性チェックを試す Summary Draft

## summary

この note は、LLM Wiki の health-check を初回実施し、`問題ゼロ` ではなく `分類付きの log を残せること` を成功条件に置いた記録です。core 5 観点を毎回見て、wiki 外の不足は candidate source に止める運用を試しました。

## key_points

- health-check の成功条件は「問題ゼロ」ではなく、「分類付き log が残ること」である
- core 5 を毎回見て、web が要る gap は candidate source に止める
- 初回結果は `contradictions: none` `stale_claims: none` `orphan_pages: none` で、optional tooling を `next_ingest` に送った

## important_quotes

- "初回結果は `contradictions: none` `stale_claims: none` `orphan_pages: none` で、optional tooling を `next_ingest` に送った"
- "`fix now / next ingest / candidate source` の分類が残っている"

## open_questions

- optional tooling のような次 ingest 候補を、どの段階で issue から candidate source へ切り分けるべきか。
