---
source: raw/knowledge/docs/architecture_rules.yml
source_type: knowledge
status: draft
replacement_of:
  - docs/repository-structure.md
last_ingested: 2026-05-23
size_class: large
---

# architecture_rules

## TL;DR

この source は yaml 形式で、top-level keys は meta、facts、validation_rules です。facts 配下では principles、tree、flows、entry_points を持ちます。

## 主要トピック

- meta: document_id, version, status, intended_replacement_for
- facts: principles, tree, flows, entry_points
- validation_rules

## キーワード

- architecture_rules
- meta
- facts
- validation_rules
- principles
- tree
- flows
- entry_points

## 注意点

- top-level key と代表 subkey の抽出ベースなので、詳細 field は raw を参照する
