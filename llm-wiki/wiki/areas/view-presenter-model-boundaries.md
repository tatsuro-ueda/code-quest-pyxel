---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/knowledge/product-requirements-guardrails-summary.md
  - ../summaries/knowledge/repository-structure-summary.md
  - ../../../docs/framework-rule.md
  - ../../../docs/product-requirements-guardrails.md
  - ../../../docs/repository-structure.md
---

# View Presenter Model Boundaries

## 核心

`framework-rule` の M1-M4 は、Pyxel RPG を AI と一緒に直すときの壊れ方を減らすために、入力、描画、判断、状態を分離する。短く言うと `入力は Presenter、状態は Model、描画は View、Pyxel は View だけ` である。

## 境界

- M1: Pyxel API と入力は View と最外殻に閉じる
- M2: View は ViewModel しか見ない
- M3: Presenter は入力解釈、遷移、副作用指揮のみ
- M4: Model は dataclass 中心で shared state を明示する

## これが必要な理由

- View が賢くなると見た目修正でゲーム判断まで壊す
- Presenter が肥大すると責務が曖昧になる
- Model が副作用や Pyxel を知るとヘッドレス検証が難しくなる

## この repo への含意

- AI に修正を頼むときも、どの層へ触るかを明示しやすくなる
- guardrail や checklist で grep / test の検証点を持ちやすい
- `src/runtime/app.py::Game` は組み立ての窓口であり、 scene.py は薄い配線に保つ
- repository structure は、この境界を file system 上で迷わないための operating map になる

## 関連ページ

- [Single Source Of Truth And Golden Path](./single-source-of-truth-and-golden-path.md)
- [No Silent Failure And Migration Safety](./no-silent-failure-and-migration-safety.md)
- [Repository Operating Structure](./repository-operating-structure.md)
- [Guardrail Layering And AI Change Boundaries](./guardrail-layering-and-ai-change-boundaries.md)
