---
source: raw/tasknotes/steering/done/2026年5月23日 開発基盤：タスクノートlintをリポジトリへ配線する.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月23日 開発基盤：タスクノートlintをリポジトリへ配線する Summary Draft

## summary

この note は、shared tasknote lint をこの repo に配線し、repo 固有設定を薄く保ったまま pre-commit へつなげた記録です。`npm exec` と tracked hook 委譲で、追加 package やローカル hook 依存を増やさず運用できる形に寄せました。

## key_points

- shared tasknote lint は repo 固有設定を薄く持つだけで再利用できた
- `package.json` を増やさず `npm exec` で済ませたのは、この repo では運用が軽い
- local `.git/hooks/pre-commit` を tracked hook へ委譲したので、今後の差分確認も楽になる

## important_quotes

- "`package.json` を増やさず `npm exec` で済ませたのは、この repo では運用が軽い"
- "local `.git/hooks/pre-commit` を tracked hook へ委譲したので、今後の差分確認も楽になる"

## open_questions

- なし。
