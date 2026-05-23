---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/product-requirements-map-summary.md
  - ../summaries/knowledge/product-requirements-platform-summary.md
  - ../../raw/knowledge/docs/product-requirements-map.md
  - ../../raw/knowledge/docs/product-requirements-platform.md
---

# Map Authorship And Tile Expression

## 核心

`product-requirements-map` と `product-requirements-platform` を合わせて読むと、map 編集の本質は `子どもが見た地形の意味をそのまま遊べること` になる。道、森、水辺、迷路、ランドマークは decoration でなく、移動、発見、物語の予感まで含む作者の表現面である。

## 地形の意味

- 道は見た目のつながりと歩けることが一致する
- 森や水辺は通れない理由が見て分かる
- 装飾は世界を豊かにしても基本動線を壊さない
- ランドマークは navigation と世界観の両方を支える

## この repo への含意

- editor と runtime の見え方差分は高優先の health-check 対象になる
- auto correction や runtime-only rule を増やすほど、子どもの予測可能性が下がる
- map 議論では pathfinding や collision だけでなく `表現面の ownership` を含めて判断する

## 関連ページ

- [Platform Sharing And Approval Ops](./platform-sharing-and-approval-ops.md)
- [Story Theme And Landmark Symbolism](./story-theme-and-landmark-symbolism.md)
