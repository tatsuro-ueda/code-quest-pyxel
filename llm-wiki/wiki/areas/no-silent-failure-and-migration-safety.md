---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/knowledge/product-requirements-guardrails-summary.md
  - ../summaries/knowledge/repository-structure-summary.md
  - ../summaries/tasknotes/done/20260412-g15-test-pinning-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-5-save-compat-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-3-headless-test-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation-summary.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/knowledge/docs/product-requirements-guardrails.md
  - ../../raw/knowledge/docs/repository-structure.md
  - ../../raw/tasknotes/done/20260412-g15-test-pinning.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-5-save-compat.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-3-headless-test.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation.md
  - ../summaries/tasknotes/steering/done/20260424-town-framework-rule-align-summary.md
  - ../../raw/tasknotes/steering/done/20260424-town-framework-rule-align.md
  - ../summaries/tasknotes/steering/done/20260422-play-session-ip-ua-browser-summary.md
  - ../../raw/tasknotes/steering/done/20260422-play-session-ip-ua-browser.md
  - ../summaries/tasknotes/steering/done/20260505-architecture-md-decision-summary.md
  - ../../raw/tasknotes/steering/done/20260505-architecture-md-decision.md
  - ../summaries/tasknotes/steering/done/20260505-docs-sync-with-recent-steering-summary.md
  - ../../raw/tasknotes/steering/done/20260505-docs-sync-with-recent-steering.md
  - ../summaries/tasknotes/steering/done/20260505-rename-production-to-dist-summary.md
  - ../../raw/tasknotes/steering/done/20260505-rename-production-to-dist.md
  - ../summaries/tasknotes/steering/done/20260505-detach-index-html-from-build-summary.md
  - ../../raw/tasknotes/steering/done/20260505-detach-index-html-from-build.md
  - ../summaries/tasknotes/steering/done/20260505-remove-tile-water2-deadcode-summary.md
  - ../../raw/tasknotes/steering/done/20260505-remove-tile-water2-deadcode.md
  - ../summaries/tasknotes/steering/done/20260507-build-hook-ci-integration-summary.md
  - ../../raw/tasknotes/steering/done/20260507-build-hook-ci-integration.md
  - ../summaries/tasknotes/steering/done/20260507-build-runbook-summary.md
  - ../../raw/tasknotes/steering/done/20260507-build-runbook.md
  - ../summaries/tasknotes/steering/done/20260507-verify-scripts-and-makefile-summary.md
  - ../../raw/tasknotes/steering/done/20260507-verify-scripts-and-makefile.md
  - ../summaries/tasknotes/steering/done/20260508-architecture-rules-yaml-summary.md
  - ../../raw/tasknotes/steering/done/20260508-architecture-rules-yaml.md
  - ../summaries/tasknotes/steering/done/20260509-architecture-guardian-summary.md
  - ../../raw/tasknotes/steering/done/20260509-architecture-guardian.md
  - ../summaries/tasknotes/steering/done/20260509-architecture-md-removal-summary.md
  - ../../raw/tasknotes/steering/done/20260509-architecture-md-removal.md
  - ../summaries/tasknotes/steering/done/20260509-architecture-rules-check-fix-repair-split-summary.md
  - ../../raw/tasknotes/steering/done/20260509-architecture-rules-check-fix-repair-split.md
  - ../summaries/tasknotes/steering/done/20260509-architecture-rules-checker-improvements-summary.md
  - ../../raw/tasknotes/steering/done/20260509-architecture-rules-checker-improvements.md
  - ../summaries/tasknotes/steering/done/20260509-architecture-rules-checker-summary.md
  - ../../raw/tasknotes/steering/done/20260509-architecture-rules-checker.md
---

# No Silent Failure And Migration Safety

## 核心

`framework-rule` は、失敗時に黙って fallback したり、移行の取り残しを目視で済ませたりしないことを強く要求する。これにより「直ったように見えるが別の場所で壊れている」という AI 修正の典型事故を減らす。

## No Silent Failure

- エラーを握りつぶさない
- ユーザー編集データを無言で上書きしない
- 読み込み失敗を default 生成でごまかさない
- 成功したように見せない
- resource mismatch を startup self-heal で見えなくしない

## Migration Safety

- 旧 API や旧 field 名の残存を機械的に検出する
- grep や目視だけで移行完了と判断しない
- manifest や設定追加を記憶に頼らない
- 削除済み dependency の import や obsolete test fixture path を放置しない
- fixed save fixture を使う restore test で、`SAVED_PLAYER_KEYS` や save schema の変更が既存データを壊さないかを機械的に止める

## この repo への含意

- AI が大きめの修正をするときほど、静的検査や禁止パターン検出が重要になる
- 壊れた版を隠すより、明示的に止めて人が気づける方がましである
- `実公開で記録されるはず` のような思い込みも silent failure の一種として扱う
- build runbook や startup gate は migration safety を運用へ落とした形である
- pytest import error を「テストが無い」扱いで見逃さず、guardrail の欠損として最優先で直す
- headless 起動で NameError / ImportError / init crash を先に落とし、子どもの前で初めて壊れる状態を防ぐ
- save compatibility test に失敗した版を approval queue の手前で落とし、「遊ぶ前に既存データが壊れる」事故を防ぐ
- `player` dict 廃止、`scene.py` 削除、shop→town 旧参照除去を grep と pytest で確認した例は、移行を「たぶん終わった」で済ませない migration safety の具体例である。
- play session schema に IP / UA を足す変更でも、`ALTER TABLE` migration と NULL 保存テストを先に持つことで、observability 拡張を silent failure にしない進め方ができる。

- dist rename explicitly recorded leaked staged changes and remaining external references instead of silently normalizing them away.
- index build detach, verify scripts, hook/CI integration, and runbook docs converted hidden artifact regressions into visible failures or named procedures.
- architecture.md removal and architecture_rules checker/guardian work favored warning-rich, inspectable migrations over quiet replacement.

## 関連ページ

- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
- [View Presenter Model Boundaries](./view-presenter-model-boundaries.md)
- [Repository Operating Structure](./repository-operating-structure.md)
