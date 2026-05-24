---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/repository-structure-summary.md
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md
  - ../summaries/tasknotes/done/20260412-guardrails-1-ssot-codegen-summary.md
  - ../../raw/knowledge/docs/repository-structure.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md
  - ../../raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md
---

# Repository Operating Structure

## 核心

`repository-structure` は、repo を `どこを直すべきか迷わない operating map` として固定する。`framework-rule` が why を与え、こちらが where を与える関係で、runtime 入口、scene/service/state の置き場、build runbook、dependency rule を実務レベルまで落としている。

## source ownership

- `src/` と `assets/` が source of truth
- `dist/` は配布物置き場で source ではない
- `src/runtime/app.py::Game` が実装の窓口
- scenes、services、state、generated の責務を分ける
- `assets/*.yaml -> tools/gen_data.py -> src/generated/*.py -> src/game_data.py` が data 系の更新経路になる
- Code Maker 向け `code-maker.zip` は build 生成物だが、中身は `main.py` と `blockquest.pyxres` の現行正本に追従する必要がある

## 運用上の意味

- build の順序と落とし穴が明文化されている
- `docs と code がずれたら未実装/仕様ずれ` の扱いを固定する
- AI 修正時に `どこを触ってはいけないか` も含めて案内できる
- generated pipeline と packaging lane の両方を知っていると、AI が直す場所と regenerate する場所を混同しにくい

## この repo への含意

- architecture review や ingest/query 時の root reference として使いやすい
- guardrail の多くは、この責務分担が前提になっている
- repo structure が stale になると、AI の修正面も stale になる
- packaging artifact や generated data の通り道が stale になると、AI の修正入口そのものがずれていく

## 関連ページ

- [View Presenter Model Boundaries](./view-presenter-model-boundaries.md)
- [Single Source Of Truth And Golden Path](./single-source-of-truth-and-golden-path.md)
- [Guardrail Layering And AI Change Boundaries](./guardrail-layering-and-ai-change-boundaries.md)
- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
