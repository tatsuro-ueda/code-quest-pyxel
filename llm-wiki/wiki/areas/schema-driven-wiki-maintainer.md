---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md
  - ../../raw/knowledge/2026-04-04-karpathy-llm-wiki.md
---

# Schema Driven Wiki Maintainer

## 核心

Karpathy は schema を「generic chatbot を disciplined wiki maintainer に変える設定ファイル」として扱う。raw と wiki だけでは足りず、どの path を使い、いつ何を更新し、query や lint でどう振る舞うかを schema が規律として与える。

## schema が担うもの

- wiki の構造と命名規則
- ingest 時の更新範囲
- query 時の保存基準
- lint 時の点検観点
- batch や例外条件の扱い

## この repo への含意

- `docs/llm-wiki-ops-schema.md` は first-cycle で実証できた defaults だけを書く
- 1 回成功だけでは固定せず、同じルールが 2 回連続で通ったときに更新する
- AGENTS からの参照は 2 セッション連続で崩れなかった後に行う

## 関連ページ

- [Persistent Wiki Vs RAG](./persistent-wiki-vs-rag.md)
- [Ingest Query Lint Loop](./ingest-query-lint-loop.md)
