---
source: raw/tasknotes/steering/done/2026年5月24日 開発基盤：LLM Wikiへの質問回答保存スキルを作る.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：LLM Wikiへの質問回答保存スキルを作る Summary Draft

## summary

この note は、LLM Wiki へ質問し、必要なら回答を保存する `query-wiki` skill の scope を `query-wiki / file-answer / candidate-source` の 3 route に固定した記録です。保存の最終判断は user gate に置き、wiki 外の事実は candidate source へ戻す前提を明文化しました。

## key_points

- `query-wiki` を 1 本の skill 名とし、scope は `query-wiki / file-answer / candidate-source` の 3 route に固定した
- 保存価値の最終判断は AI でなく user gate に置き、request に save intent が明示されているときだけ `yes` 扱いを許す
- current repo の query read order は `master-index -> summaries/knowledge -> areas` に固定した

## important_quotes

- "`query-wiki` を 1 本の skill 名とし、scope は `query-wiki / file-answer / candidate-source` の 3 route に固定した"
- "保存価値の最終判断は AI でなく user gate に置き、request に save intent が明示されているときだけ `yes` 扱いを許す"

## open_questions

- なし。
