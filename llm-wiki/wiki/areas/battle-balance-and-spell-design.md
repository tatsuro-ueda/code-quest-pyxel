---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/product-requirements-battle-summary.md
  - ../../raw/knowledge/docs/product-requirements-battle.md
---

# Battle Balance And Spell Design

## 核心

`product-requirements-battle` は、戦闘改造を `すぐ試せる変更単位` に分解している。敵を弱める、新しい敵を出す、新しい呪文を覚える、後半だけ難しくする、といった要求を、 data と test-play loop の組み合わせで安全に回す設計である。

## 安定した変更単位

- 敵は `データ追加 + 出現ゾーン + スプライト表示` で 1 単位
- 呪文は `必要情報 + 戦闘表示 + MP 消費 + 失敗理由` で 1 単位
- バランス調整は `対象範囲の限定 + 通しプレイ成立` で 1 単位

## この repo への含意

- battle 系相談では「どの data を変えるか」と「何で壊れていないと判断するか」を常にセットで持つ
- balance は static な正解でなく、友達の感想まで含む feedback loop として扱う
- feature 追加でも、見える場所と使える場所が揃わない変更は未完扱いにする

## 関連ページ

- [Fast Feedback Development Loop](./fast-feedback-development-loop.md)
- [Guardrail Layering And AI Change Boundaries](./guardrail-layering-and-ai-change-boundaries.md)
