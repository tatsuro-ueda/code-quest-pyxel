---
source: raw/knowledge/docs/product-requirements-map.md
source_type: doc
status: active
origin:
  - docs/product-requirements-map.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: large
---

# Product Requirements Map Summary

## TL;DR

この source は、タイル配置、道、森、水辺、装飾、迷路、ランドマークを通じて `子どもが見た編集結果をそのまま遊べる` ことを約束する。中心は `Tilemap エディタで見えた形が本編でも同じ` `通行ルールが見た目と一致する` `飾りは世界を豊かにしても遊びやすさは壊さない` である。

## 主要トピック

- 最初の 1 タイル配置で変化がすぐ見え、そのままテストプレイできる
- 道は見た目のつながりと通行可能性が一致する
- 森や水辺は通れない意味を持ち、草や隙間は通れる意味を残す
- 装飾は見た目の個性を増やしても基本の歩きやすさを壊さない
- 迷路とランドマークは世界の構造理解と発見を支える

## 深い洞察

- map 編集で大事なのは機能追加より `見えているものが真実であること` である
- タイルの意味が見た目と移動ルールで分離すると、子どもは編集の因果を失う
- ランドマークは navigation と story symbolism の両方を担う

## キーワード

- product-requirements-map
- tilemap
- path
- forest
- water
- landmark
- editor equals runtime

## 注意点

- Code Maker / Resource Editor と runtime の完全一致はまだ弱い領域が残る
- 迷路完成判定や専用チュートリアルは今後の補助機能として残っている
