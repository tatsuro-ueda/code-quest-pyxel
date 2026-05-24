---
source: raw/tasknotes/steering/done/2026-04-20-pytest-cj-progress-design.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# Pytest CJ Progress Design Summary Draft

## summary

この tasknote は、`CJG` の達成率を pytest から見える形にし、進捗を実装の有無ではなく metric として扱えるようにする設計メモです。他の steering tasknote よりも設計色が強く、`Source of Truth` と `Metric Definitions` を先に固めることで、customer journey の進み具合をどの証拠で測るかをそろえようとしていました。

## key_points

- ゴールは新機能追加よりも、`CJG` の進捗を pytest から読めるようにする設計にある。
- 見出しは `Goal` `Problem` `Scope` `Source of Truth` `Metric Definitions` `CJG 達成率` と、測定設計中心で並んでいる。
- この note は tasklist よりも metric 定義と計測対象の整理に重点がある。
- `Source of Truth` を先に置くことで、進捗判定の根拠が docs なのか test なのかを明確にしようとしている。
- `CJG 達成率` を数えるには、どの scenario を達成とみなすかの基準整理が前提になる。
- この note は、journey 進捗を設計的に見える化する土台メモとして読むのが自然だった。

## important_quotes

- "Source of Truth"
- "Metric Definitions"
- "CJG 達成率"

## open_questions

- `CJG 達成率` は、どの粒度の証拠を積み上げて計算するのが自然か。
- progress 指標の正本は、pytest 結果と docs 上の scenario のどちらを先に置くべきか。
