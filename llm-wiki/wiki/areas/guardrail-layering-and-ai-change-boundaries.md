---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/product-requirements-guardrails-summary.md
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/knowledge/repository-structure-summary.md
  - ../../raw/knowledge/docs/product-requirements-guardrails.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/knowledge/docs/repository-structure.md
---

# Guardrail Layering And AI Change Boundaries

## 核心

`product-requirements-guardrails` は、AI 改造を `触ってよい層` と `人へ戻すべき層` に切り分けた上で、起動ゲート、SSoT、M1-M5、resource 境界、headless test を重ねて守る。ポイントは「AI を止めること」ではなく、「壊れた版が子どもに届かないこと」である。

## 能力境界

- data、text、logic、flags、system rules は AI が扱える
- map の地形、sprite、Sound/Music の実体は Code Maker に戻す
- `.pyxres` や generated code は、編集入口そのものを制限する

## 防御スタック

- docs と runtime map で責務を見える化する
- hooks と権限で誤った入口を止める
- build と headless test で壊れた版を止める
- Code Maker resource freshness と Web 配布確認で実物のずれを止める

## この repo への含意

- AI への依頼は「何を変えるか」だけでなく「どの layer を触るか」で表現しやすくする
- build 成功の意味は unit test だけでなく、子どもが触る通り道を通ったことまで含む
- repo structure は guardrail の地図、 framework-rule はそのルール本体である

## 関連ページ

- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
- [Repository Operating Structure](./repository-operating-structure.md)
- [Single Source Of Truth And Golden Path](./single-source-of-truth-and-golden-path.md)
