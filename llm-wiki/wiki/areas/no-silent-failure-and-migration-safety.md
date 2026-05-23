---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/knowledge/product-requirements-guardrails-summary.md
  - ../summaries/knowledge/repository-structure-summary.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/knowledge/docs/product-requirements-guardrails.md
  - ../../raw/knowledge/docs/repository-structure.md
---

# No Silent Failure And Migration Safety

## 核心

`framework-rule` は、失敗時に黙って fallback したり、移行の取り残しを目視で済ませたりしないことを強く要求する。これにより「直ったように見えるが別の場所で壊れている」という AI 修正の典型事故を減らす。

## No Silent Failure

- エラーを握りつぶさない
- ユーザー編集データを無言で上書きしない
- 読み込み失敗を default 生成でごまかさない
- 成功したように見せない

## Migration Safety

- 旧 API や旧 field 名の残存を機械的に検出する
- grep や目視だけで移行完了と判断しない
- manifest や設定追加を記憶に頼らない

## この repo への含意

- AI が大きめの修正をするときほど、静的検査や禁止パターン検出が重要になる
- 壊れた版を隠すより、明示的に止めて人が気づける方がましである
- `実公開で記録されるはず` のような思い込みも silent failure の一種として扱う
- build runbook や startup gate は migration safety を運用へ落とした形である

## 関連ページ

- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
- [View Presenter Model Boundaries](./view-presenter-model-boundaries.md)
- [Repository Operating Structure](./repository-operating-structure.md)
