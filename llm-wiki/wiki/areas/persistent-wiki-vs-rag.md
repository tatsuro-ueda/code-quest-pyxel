---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md
  - ../../raw/knowledge/2026-04-04-karpathy-llm-wiki.md
---

# Persistent Wiki Vs RAG

## 核心

Karpathy の論点は「query のたびに raw から再発見する plain RAG」より、「一度 wiki に compile してから維持する persistent wiki」の方が知識が蓄積する、という点にある。persistent wiki では cross-reference、contradiction、synthesis が質問前にすでに整っている。

## 根拠

- raw から毎回 relevant chunk を拾うだけでは subtle な multi-document synthesis が毎回やり直しになる
- persistent wiki は新 source ごとに summary と related page を更新し、知識を compounding artifact にする
- query だけでなく、良い answer も wiki に filed back できるため、exploration 自体が資産になる

## この repo への含意

- `llm-wiki/wiki/` は chat の一時回答ではなく、更新され続ける knowledge layer として扱う
- query answer も再利用価値があれば `wiki/query/` に残す
- health-check は「蓄積された wiki が壊れていないか」を見る工程になる

## 関連ページ

- [Ingest Query Lint Loop](./ingest-query-lint-loop.md)
- [Schema Driven Wiki Maintainer](./schema-driven-wiki-maintainer.md)
