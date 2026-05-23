---
status: active
created: 2026-05-23
question_type: comparison
sources:
  - ../summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md
  - ../areas/persistent-wiki-vs-rag.md
  - ../areas/ingest-query-lint-loop.md
---

# Why Persistent Wiki Beats RAG

## Question

Why does Karpathy argue that a persistent wiki compounds better than plain RAG?

## Answer

Karpathy の答えは、「plain RAG は質問のたびに raw から knowledge を再組み立てするが、persistent wiki は一度 compile した synthesis を維持し続ける」からです。persistent wiki では summary、cross-reference、contradiction の整理が質問前にすでに進んでいるので、次の query は毎回ゼロから探索し直さずに済みます。さらに ingest だけでなく good answer も wiki に filed back できるため、調査そのものが新しい知識として残ります。[Summary](../summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md) [Persistent Wiki Vs RAG](../areas/persistent-wiki-vs-rag.md)

## Evidence

- plain RAG では subtle な multi-document synthesis を毎回やり直す、という問題設定が source の core idea にある
- persistent wiki は new source のたびに summary と related page を更新し、knowledge を compounding artifact にする
- query answer も wiki へ戻せるので、exploration が chat history に埋もれない

## Confidence

High. 主要論点は source の core idea と operations の両方で繰り返されている。
