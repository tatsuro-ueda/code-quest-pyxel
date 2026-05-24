---
source: raw/tasknotes/steering/2026年5月24日 開発基盤：capture-and-ingest-sourceにルーチン型lintゲートを足す.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：capture-and-ingest-sourceにルーチン型lintゲートを足す Summary Draft

## summary

この note は、`capture-and-ingest-source` に 2 つの user gate を機械的に読める lint を足し、`go ahead` でも gate 1 と gate 2 を飛ばさない shape に寄せた記録です。既存 gated profile を再利用し、停止点の崩れを rule で止める方針を取りました。

## key_points

- 既存 gated profile を使い回す方が rule の増殖を防げる
- user が気にしていたのは gate の数なので、`go ahead` path でも gate 1 と gate 2 を残すのが本筋である
- routine lint は停止点の崩れを止め、運用側は 2 回の user 確認を守る役に分けられる

## important_quotes

- "user が気にしていたのは gate の数なので、`go ahead` path でも gate 1 と gate 2 を残すのが本筋である"
- "residual risk は `run_skill_lint.mjs` が `ruby` 前提のままな点だけで、skill 本文自体の family lint は通っている"

## open_questions

- なし。
