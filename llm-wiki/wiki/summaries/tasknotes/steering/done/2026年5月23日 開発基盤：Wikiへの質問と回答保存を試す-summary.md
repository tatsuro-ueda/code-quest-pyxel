---
source: raw/tasknotes/steering/done/2026年5月23日 開発基盤：Wikiへの質問と回答保存を試す.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月23日 開発基盤：Wikiへの質問と回答保存を試す Summary Draft

## summary

この note は、LLM Wiki へ質問して答えを保存する最初の query route を試し、`master-index -> summaries -> areas` の順で読む前提と、再利用価値がある答えだけ page 化する方針を固めた記録です。wiki 外の事実は answer に直書きせず candidate source へ戻す線引きも置きました。

## key_points

- query は child `02` の summary / index / areas を読んで進める
- 迷ったら markdown、再利用価値がある答えだけ page 化する
- wiki 外の事実は answer に直混ぜせず、candidate source に戻す

## important_quotes

- "query は child `02` の summary / index / areas を読んで進める"
- "optional tooling の gap は `qmd / Obsidian tooling` の candidate source として切り分けた"

## open_questions

- なし。
