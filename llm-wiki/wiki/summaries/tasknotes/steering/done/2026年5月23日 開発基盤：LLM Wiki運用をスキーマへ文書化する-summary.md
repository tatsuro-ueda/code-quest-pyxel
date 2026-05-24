---
source: raw/tasknotes/steering/done/2026年5月23日 開発基盤：LLM Wiki運用をスキーマへ文書化する.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月23日 開発基盤：LLM Wiki運用をスキーマへ文書化する Summary Draft

## summary

この note は、LLM Wiki の運用ルールをすぐ schema 化せず、initial loop の実績が安定してから `docs/llm-wiki-ops-schema.md` へ昇格する方針を固めた記録です。1 回成功では固定せず、2 回連続成功で schema、2 セッション安定で AGENTS 参照へ進める基準を置きました。

## key_points

- schema 化は initial loop の log を見てからの方が誤固定を避けやすい
- schema はメモ集ではなく、future session 用の短い憲法にする
- 1 回成功だけでは更新せず、2 回連続成功で schema、2 セッション安定で AGENTS 参照に進む

## important_quotes

- "今回作った `docs/llm-wiki-ops-schema.md` は draft として保存し、固定条件は本文内に残した"
- "schema はメモ集ではなく、future session 用の短い憲法にする"

## open_questions

- どの run を `連続成功` と見なすかを、今後どこまで厳密に数えるべきか。
