---
source: raw/tasknotes/steering/done/2026年5月24日 開発基盤：ClaudeのPushover通知文をセッションごとに固定できるようにする.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：ClaudeのPushover通知文をセッションごとに固定できるようにする Summary Draft

## summary

この note は、Claude の Pushover 通知文を session ごとに固定できるようにし、通常会話へ混ぜずに hook JSON で保存する contract を置いた記録です。`set_session_name "..."` の 1 形式に絞り、Stop hook の既存責務を増やさない形で実装しました。

## key_points

- `set_session_name "..."` の許容構文は double quote 付き 1 形式に絞った
- Stop hook は既存の file contract を維持し、通知の責務を増やしていない
- prompt を通常会話へ流さないため、保存時は hook JSON で `continue: false` を返す

## important_quotes

- "`set_session_name "..."` の許容構文は double quote 付き 1 形式に絞った"
- "prompt を通常会話へ流さないため、保存時は hook JSON で `continue: false` を返す"

## open_questions

- なし。
