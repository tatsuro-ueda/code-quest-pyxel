---
source: raw/knowledge/docs/framework-rule.md
source_type: doc
status: active
origin:
  - docs/framework-rule.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: large
---

# Framework Rule Summary

## TL;DR

この source は、Pyxel 用 MVP 規約とコーディング原則の本体です。中心は `SSoT` `Golden Path Test` `Migration Safety` `No Silent Failure` と、M1-M5 による `View / Presenter / Model / Service / GameState` の境界固定です。

## 主要トピック

- 正本を一つにする（SSoT）
- 本番の通り道を通す（Golden Path）
- Migration Safety と No Silent Failure
- M1: Pyxel API と入力は View と最外殻へ閉じる
- M2: View は ViewModel しか見ない
- M3: Presenter は入力解釈・Scene 遷移・副作用指揮のみ
- M4: Model は dataclass 中心、共有状態は明示する
- M5: 層規約は AI が自力で検証できる形で可視化する

## キーワード

- framework-rule
- SSoT
- golden path
- migration safety
- no silent failure
- presenter
- model
- viewmodel
- gamestate

## 注意点

- これは checklist ではなく規約本体であり、理由と禁止事項まで含む
- 実装判断では `AGENTS.md` と `repository-structure.md` も併読する必要がある
