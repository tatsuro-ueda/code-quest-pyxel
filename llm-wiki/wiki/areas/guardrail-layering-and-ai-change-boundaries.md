---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/product-requirements-guardrails-summary.md
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/knowledge/repository-structure-summary.md
  - ../summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md
  - ../summaries/tasknotes/done/20260412-g15-test-pinning-summary.md
  - ../summaries/tasknotes/done/20260412-guardrails-1-ssot-codegen-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-2-hooks-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-3-headless-test-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation-summary.md
  - ../../raw/knowledge/docs/product-requirements-guardrails.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/knowledge/docs/repository-structure.md
  - ../../raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md
  - ../../raw/tasknotes/done/20260412-g15-test-pinning.md
  - ../../raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-2-hooks.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-3-headless-test.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation.md
---

# Guardrail Layering And AI Change Boundaries

## 核心

`product-requirements-guardrails` は、AI 改造を `触ってよい層` と `人へ戻すべき層` に切り分けた上で、起動ゲート、SSoT、M1-M5、resource 境界、headless test を重ねて守る。ポイントは「AI を止めること」ではなく、「壊れた版が子どもに届かないこと」である。

## 能力境界

- data、text、logic、flags、system rules は AI が扱える
- map の地形、sprite、Sound/Music の実体は Code Maker に戻す
- `.pyxres` や generated code は、編集入口そのものを制限する
- data を触るときは YAML 正本を編集し、`src/generated/*.py` は codegen の結果として扱う
- generated file や `.pyxres` の direct edit は、hook で手前から block して正しい authoring path へ戻す

## 防御スタック

- docs と runtime map で責務を見える化する
- hooks と権限で誤った入口を止める
- build と headless test で壊れた版を止める
- Code Maker resource freshness と Web 配布確認で実物のずれを止める
- 壊れた pytest lane や stale fixture path を放置せず、failure signal 自体を先に復旧する
- Code Maker zip の `main.py` / `pyxres` 一致と headless 起動確認で、配布 artifact のずれを止める
- `.claude/settings.json` と `tools/hooks/*.sh` は、wrong-path edit を最初に止める物理バリアとして機能する
- `tools/test_headless.py` は、import / 初期化 / 1 フレーム描画の失敗を build gate で止める最後のバリアになる
- `.pyxres` mismatch は runtime self-heal より build / packaging / verify 側で止める方が current truth に合う

## この repo への含意

- AI への依頼は「何を変えるか」だけでなく「どの layer を触るか」で表現しやすくする
- build 成功の意味は unit test だけでなく、子どもが触る通り道を通ったことまで含む
- repo structure は guardrail の地図、 framework-rule はそのルール本体である
- guardrail は「触る層の制限」だけでなく、「生成し直す経路」と「配布物を検証する経路」まで含めて成立する
- guardrail を code review の注意事項だけで終わらせず、hook と headless build に落とすことで再現性が上がる

## 関連ページ

- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
- [Repository Operating Structure](./repository-operating-structure.md)
- [Single Source Of Truth And Golden Path](./single-source-of-truth-and-golden-path.md)
- [View Presenter Model Boundaries](./view-presenter-model-boundaries.md)
