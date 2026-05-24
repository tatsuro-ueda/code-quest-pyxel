---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/customer-journeys-summary.md
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/knowledge/product-requirements-guardrails-summary.md
  - ../summaries/knowledge/repository-structure-summary.md
  - ../summaries/tasknotes/done/20260412-g15-test-pinning-summary.md
  - ../summaries/tasknotes/done/20260412-guardrails-1-ssot-codegen-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-5-save-compat-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-2-hooks-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-3-headless-test-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation-summary.md
  - ../../raw/knowledge/docs/customer-journeys.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/knowledge/docs/product-requirements-guardrails.md
  - ../../raw/knowledge/docs/repository-structure.md
  - ../../raw/tasknotes/done/20260412-g15-test-pinning.md
  - ../../raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-5-save-compat.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-2-hooks.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-3-headless-test.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation.md
---

# Guardrails Protect The Loop

## 核心

ガードレールは「品質向上のための後付け」ではなく、親子の好循環を壊さないための前提である。`customer-journeys` は壊れた AI 出力が子どもに届くと逆フィードバックになると明示し、`framework-rule` はそのための規律を SSoT、Golden Path、No Silent Failure などで固定する。

## 守る対象

- クラッシュした版を子どもに渡さない
- 古い API や曖昧な責務で別の場所を壊さない
- 技術基盤変更で Web 配信や Code Maker 連携を壊さない

## 主要な規律

- 正本を一つにする
- 本番の通り道を通す
- silent failure を禁止する
- migration の取り残しを機械的に検出する
- 起動ゲートで壊れた版を承認キューから除外する
- Code Maker resource の境界を越えない
- 壊れた test lane を先に直し、failure signal 自体を guardrail として回復させる
- hook で generated / `.pyxres` / wrong import path をその場で止め、誤った入口から壊させない
- headless 起動 gate を通し、壊れた版を approval queue の手前で落とす
- save compatibility test を通し、既存データを壊す版を approval queue の手前で落とす

## この repo への含意

- guardrail は開発速度の敵でなく、速度を子どもへ安全に届けるための条件である
- 好循環が速くなるほど、guardrail の重要度も上がる
- docs、runtime map、hooks、build、pytest を別々でなく防御層として束ねて見る必要がある
- YAML 正本 + codegen のような structural guardrail は、修正速度が上がるほど価値が増す
- `.pyxres` mismatch を runtime self-heal に逃がさず、verify で止める方が current truth と child trust を守りやすい

## 関連ページ

- [Fast Feedback Development Loop](./fast-feedback-development-loop.md)
- [Single Source Of Truth And Golden Path](./single-source-of-truth-and-golden-path.md)
- [No Silent Failure And Migration Safety](./no-silent-failure-and-migration-safety.md)
- [Guardrail Layering And AI Change Boundaries](./guardrail-layering-and-ai-change-boundaries.md)
- [Repository Operating Structure](./repository-operating-structure.md)
