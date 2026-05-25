---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/product-requirements-battle-summary.md
  - ../summaries/tasknotes/steering/done/20260413-j42-rpg-loop-journey-summary.md
  - ../summaries/tasknotes/steering/done/20260413-j39-run-fail-enemy-turn-summary.md
  - ../summaries/tasknotes/steering/done/20260414-j45-noise-guardian-event-only-preview-summary.md
  - ../../../docs/product-requirements-battle.md
  - ../../raw/tasknotes/steering/done/20260413-j42-rpg-loop-journey.md
  - ../../raw/tasknotes/steering/done/20260413-j39-run-fail-enemy-turn.md
  - ../../raw/tasknotes/steering/done/20260414-j45-noise-guardian-event-only-preview.md
  - ../summaries/tasknotes/steering/done/20260509-stakeholder-voices-battle-prd-migration-summary.md
  - ../../raw/tasknotes/steering/done/20260509-stakeholder-voices-battle-prd-migration.md
---

# Battle Balance And Spell Design

## 核心

`product-requirements-battle` は、戦闘改造を `すぐ試せる変更単位` に分解している。敵を弱める、新しい敵を出す、新しい呪文を覚える、後半だけ難しくする、といった要求を、 data と test-play loop の組み合わせで安全に回す設計である。

## 安定した変更単位

- 敵は `データ追加 + 出現ゾーン + スプライト表示` で 1 単位
- 呪文は `必要情報 + 戦闘表示 + MP 消費 + 失敗理由` で 1 単位
- バランス調整は `対象範囲の限定 + 通しプレイ成立` で 1 単位
- 戦闘フロー修正は `phase の責務` `敵ターン継続` `通しプレイ成立` までそろって 1 単位になる
- イベント専用敵は `通常遭遇候補から除外` `専用イベント戦は維持` `preview で比較確認` を 1 単位として扱うと壊れにくい

## この repo への含意

- battle 系相談では「どの data を変えるか」と「何で壊れていないと判断するか」を常にセットで持つ
- balance は static な正解でなく、友達の感想まで含む feedback loop として扱う
- feature 追加でも、見える場所と使える場所が揃わない変更は未完扱いにする
- `にげる` 失敗のような順番ミスは、数値 balance 調整とは別に `戦闘ループが成立しているか` の問題として固定する
- `is_noise_guardian` のような既存 data flag を使い切ってから、新しい encounter 仕組みを足す

- the stakeholder battle PRD migration turned enemy balance, new enemy/spell loops, and replay-safe tuning into traced requirements plus acceptance instead of scattered battle wishes.

## 関連ページ

- [Fast Feedback Development Loop](./fast-feedback-development-loop.md)
- [Guardrail Layering And AI Change Boundaries](./guardrail-layering-and-ai-change-boundaries.md)
