---
source: docs/product-requirements-guardrails.md
source_type: doc
status: active
origin:
  - docs/product-requirements-guardrails.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: large
---

# Product Requirements Guardrails Summary

## TL;DR

この source は、AI 改造を止めるのでなく `壊れた版を子どもに届けない` ための多層ガードレールを定義する。中心は `AI の能力境界` `0-6 の改造レイヤー` `CJG35 起動検証ゲート` `CJG36 SSoT と codegen` `CJG37 の M1-M5 規約` `CJG44 の resource 境界` である。

## 主要トピック

- AI ができる改造と Code Maker へ案内すべき改造を明示する
- 責務・構造、データ、コンテンツ、イベント、システム、メタ構造、技術基盤の 7 レイヤーに分ける
- 起動しない版や主要シナリオで死ぬ版を build 時点で止める
- SSoT と generated code の入口を固定し、 generated 直編集や直接 import を止める
- `.pyxres` と Sound/Music authoring は人が持ち、AI は import / build / verify に絞る
- hooks、権限、docs、pre-commit、pytest を防御層として重ねる

## 深い洞察

- guardrail は開発速度の敵ではなく、速く回した変更を安全に届けるための運用機構である
- `正しい入口から壊す` 可能性もあるため、入口制御と挙動テストの両方が必要になる
- M1-M5 は style guide でなく、AI が触る境界を機械検証へ落とすための骨組みである

## キーワード

- product-requirements-guardrails
- AI change boundary
- startup gate
- SSoT
- hooks
- M1-M5
- CJG44

## 注意点

- 文書は目標状態を含むため、実装済みと未実装の差分を常に併記して読む必要がある
- guardrail の一部は concept 先行で、 repo の全箇所で完全自動化されているわけではない
