---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md
  - ../../raw/knowledge/2026-04-04-karpathy-llm-wiki.md
---

# Ingest Query Lint Loop

## 核心

Karpathy の pattern は、source を入れる ingest、wiki に質問する query、wiki の健全性を見る lint の 3 レーンで回る。3 つは独立ではなく、query の答えが wiki に戻り、lint が次の source や question を生むことで循環する。

## ingest

- raw source を immutable に保存する
- summary page を作る
- index を更新する
- related page を更新する
- log に append する

## query

- index を入口に related page を探す
- evidence 付き answer を作る
- 良い answer は saved page として残す
- wiki 外の事実は candidate source に切り出す

## lint

- contradictions
- stale claims
- orphan pages
- missing concepts
- missing crossrefs

## この repo への含意

- initial loop では `setup -> ingest -> query -> health-check` を 1 回回せばよい
- batch や schema 固定は、この loop が通ったあとに乗せる

## 関連ページ

- [Persistent Wiki Vs RAG](./persistent-wiki-vs-rag.md)
- [Schema Driven Wiki Maintainer](./schema-driven-wiki-maintainer.md)
