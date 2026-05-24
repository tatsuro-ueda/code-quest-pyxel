---
source: raw/tasknotes/steering/done/20260509-architecture-rules-checker-improvements.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 architecture_rules checker 改良 Summary Draft

## summary

この note は、architecture checker の rule 数を増やす前に「信用できる壊れ方」と「再実行しやすさ」を固めるべきだと整理した proposal です。実装はまだ行わず、先に上げるべき改善軸を 3 点に絞っています。

## key_points

- この note 自体は `起票のみ。未実装。` で、実コード変更は含まない。
- 優先軸を rule 定義ミスの自己検知、1 rule 再実行、expected/observed を持つ warning の 3 点に絞った。
- `llm_assisted` rule を増やす前に checker の壊れ方を trustworthy にする順序を明示した。

## important_quotes

- "`起票のみ。未実装。`"
- "`信用できる壊れ方`"

## open_questions

- 3 つの改善軸のうち、どれから着手すると運用密度が最も上がるか。
- 現在の JSON consumer を壊さずに expected/observed を広げるには何が必要か。
