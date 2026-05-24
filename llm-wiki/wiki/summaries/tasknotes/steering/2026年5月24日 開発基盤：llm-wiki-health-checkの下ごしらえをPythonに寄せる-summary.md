---
source: raw/tasknotes/steering/2026年5月24日 開発基盤：llm-wiki-health-checkの下ごしらえをPythonに寄せる.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：llm-wiki-health-checkの下ごしらえをPythonに寄せる Summary Draft

## summary

この note は、LLM Wiki health-check の deterministic な下ごしらえを Python helper に寄せ、signal と AI の judgment を分ける方針を固めた記録です。orphan や stale は helper では signal 止まりにし、6 分類への意味判断は AI 側に残しました。

## key_points

- 今日の先行例に合わせ、Python は deterministic prep に限定する
- health-check の意味判断は source ingest より曖昧さが強いため、signal と judgment を分ける
- orphan や stale の候補は helper では signal 止まりにし、issue 断定は AI に残す

## important_quotes

- "repo-local helper は `master-index` 起点の active graph と thin connectivity を先に返し、skill 側はそれを読んで 6分類へ落とす"
- "orphan や stale の候補は helper では signal 止まりにし、issue 断定は AI に残す"

## open_questions

- なし。
