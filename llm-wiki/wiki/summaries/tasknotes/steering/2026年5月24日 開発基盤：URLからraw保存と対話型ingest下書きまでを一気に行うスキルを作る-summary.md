---
source: raw/tasknotes/steering/2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：URLからraw保存と対話型ingest下書きまでを一気に行うスキルを作る Summary Draft

## summary

この note は、URL や source 発見直後の摩擦を減らすため、raw 保存から対話型 ingest 下書きまでを 1 本の `capture-and-ingest-source` skill にまとめた記録です。related page 更新までは広げず、summary draft で止まる設計にして repo ごとの local schema 読みも両立させました。

## key_points

- `capture-source` と `interactive-ingest-draft` を 1 本化すると、source 発見直後の摩擦が減る
- ただし related page 更新まで入れると責務が広がるので、summary draft で止める方が Karpathy の対話 ingest に合う
- 共通 skill にしたことで、repo ごとの local schema を読む入口と既定 path の fallback を両立できた

## important_quotes

- "`capture-source` と `interactive-ingest-draft` を 1 本化すると、source 発見直後の摩擦が減る"
- "related page 更新まで入れると責務が広がるので、summary draft で止める方が Karpathy の対話 ingest に合う"

## open_questions

- なし。
