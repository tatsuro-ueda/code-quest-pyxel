---
source: raw/tasknotes/steering/2026年5月24日 開発基盤：LLM Wikiのupdate-schemaスキルを作る.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：LLM Wikiのupdate-schemaスキルを作る Summary Draft

## summary

この note は、`health-check-log` と compiled wiki を主入力にして stable rule だけを schema へ昇格する `update-schema` skill の scope を固めた記録です。tasknote 原文をそのまま rule 化せず、安定した回だけ更新する前提を置きました。

## key_points

- `update-schema` は tasknote 原文をそのまま rule 化せず、log と compiled wiki を主入力にする
- stable rule の無い回は schema を更新しない
- 親ノートの 5 バケット表現は、現行 schema 見出しへの内部対応で吸収する

## important_quotes

- "`update-schema` は tasknote 原文をそのまま rule 化せず、log と compiled wiki を主入力にする"
- "最新 `health-check-log` の stale/orphan は page-level cleanup であり、追加 schema 更新なしで止める dry-run が成立した"

## open_questions

- なし。
