---
source: raw/knowledge/2026-04-04-karpathy-llm-wiki.md
source_type: gist
status: active
origin:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: medium
---

# Karpathy LLM Wiki Summary

## TL;DR

この source は `LLM Wiki` という idea file で、主要トピックは persistent wiki と plain RAG の差、raw / wiki / schema の 3 層、ingest / query / lint の運用ループ、index と log の役割です。要点は「知識を毎回取り直すのではなく、一度 wiki へ compile して蓄積し続ける」ことにあります。

## 主要トピック

- persistent wiki は raw source と質問のあいだに立つ compounding artifact である
- raw sources は immutable、wiki は LLM が保守し、schema は運用規律を与える
- ingest は summary、index、関連ページ、log をまとめて更新する
- query は citations 付き回答を作り、良い答えは wiki へ filed back する
- lint は contradictions、stale claims、orphan pages、missing concepts、missing crossrefs を見る
- index は content-oriented、log は chronological で役割が違う

## 運用レーン

- ingest: 1 source を raw に置き、summary / index / related pages / log を更新する
- query: index から relevant page を探し、答えを synthesize して保存する
- lint: contradictions、stale claims、orphan pages、missing concepts、missing crossrefs、data_gaps を見て、次の source や質問候補を作る

## キーワード

- persistent wiki
- compounding artifact
- ingest
- query
- lint
- raw / wiki / schema
- index
- log
- citations

## 注意点

- source 自体は intentionally abstract で、実装詳細は各 repo / domain に合わせて決める前提
- optional tooling は提案であり、初回 loop の必須条件ではない
