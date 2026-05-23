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

# Single Source Of Truth And Golden Path

## 核心

`framework-rule` は、AI が壊しやすい場所を「正本を一つにする」と「本番の通り道を通す」で先に封じる。データの正しい置き場と、実際のユーザー導線を固定しておけば、見かけだけの green を減らせる。

## SSoT

- 同じ意味のデータを複数箇所に持たない
- 生データ直読みや都合のよい参照先切り替えをしない
- ユーザー編集より自動生成を優先しない
- `src/` と `assets/` を正本にし、 `dist/` を source 扱いしない

## Golden Path

- unit test green だけで終わらない
- 起動、メニュー、戦闘、配布物など本番導線を最低 1 回は通す
- bundle や実物確認を後回しにしない
- Code Maker zip、公開 URL、play log のような user-facing artifact も通り道に含める

## この repo への含意

- docs、pyxres、配布物、save payload のどれが正本かを先に固定する
- 「直した」ではなく「ユーザーが触る通り道で動いた」ことを done とみなす

## 関連ページ

- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
- [View Presenter Model Boundaries](./view-presenter-model-boundaries.md)
- [Repository Operating Structure](./repository-operating-structure.md)
