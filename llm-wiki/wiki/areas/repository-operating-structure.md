---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/repository-structure-summary.md
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md
  - ../summaries/tasknotes/done/20260412-guardrails-1-ssot-codegen-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-5-save-compat-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-2-hooks-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-3-headless-test-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j31-fix-selector-links-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j36-dialogue-ssot-summary.md
  - ../../raw/knowledge/docs/repository-structure.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md
  - ../../raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-5-save-compat.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-2-hooks.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-3-headless-test.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation.md
  - ../../raw/tasknotes/steering/done/20260412-j31-fix-selector-links.md
  - ../../raw/tasknotes/steering/done/20260412-j36-dialogue-ssot.md
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
- `.claude/settings.json` と `tools/hooks/*.sh` が generated / `.pyxres` / import path の誤操作を止める guardrail entrypoint になる
- `tools/test_headless.py` が build 前段で import / init / 1 フレーム描画を検査する runtime guardrail になる
- `tests/fixtures/save_v1.json` と `tools/test_save_compat.py` が save schema 変更の migration safety を守る tool layer になる
- `generate_wrapper()` で作る `play.html` は selector page から実ゲームへつなぐ user-facing artifact lane の一部である
- dialogue も `assets/dialogue.yaml -> tools/gen_data.py -> src/generated/dialogue.py -> src/game_data.py` と `tools/sync_main_data.py` の同期経路へ収まる

## 運用上の意味

- build の順序と落とし穴が明文化されている
- `docs と code がずれたら未実装/仕様ずれ` の扱いを固定する
- AI 修正時に `どこを触ってはいけないか` も含めて案内できる
- generated pipeline と packaging lane の両方を知っていると、AI が直す場所と regenerate する場所を混同しにくい
- hooks、headless test、resource verify の置き場が見えていると、guardrail を「仕組み」として保守しやすい

## この repo への含意

- architecture review や ingest/query 時の root reference として使いやすい
- guardrail の多くは、この責務分担が前提になっている
- repo structure が stale になると、AI の修正面も stale になる
- packaging artifact や generated data の通り道が stale になると、AI の修正入口そのものがずれていく
- `.pyxres` の current truth が変わったときも、runtime self-heal と build verify のどちらが正式経路かを repo map に反映しておく必要がある
- selector から辿る wrapper artifact が欠けるだけでも、repo map と child-facing delivery は同時に壊れる
- dialogue のような旧来の直書き data は、single-file `main.py` 同期まで含めて repo map に戻さないと半端な二重管理になる

## 関連ページ

- [View Presenter Model Boundaries](./view-presenter-model-boundaries.md)
- [Single Source Of Truth And Golden Path](./single-source-of-truth-and-golden-path.md)
- [Guardrail Layering And AI Change Boundaries](./guardrail-layering-and-ai-change-boundaries.md)
- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
