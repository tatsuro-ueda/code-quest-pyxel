---
source: raw/knowledge/docs/ux-policy.md
source_type: doc
status: active
origin:
  - docs/ux-policy.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: small
---

# UX Policy Summary

## TL;DR

この source は、子どもに見える UI と親の補助の線引きを短い policy として固定する。中心は `ひらがな中心の表記` `いま選ぶ操作だけを見せる` `押した実感を返す` `危険操作を無言で通さない` `Web 共有の見せやすさ` `親は補助者であり決定者ではない` の 6 本柱である。

## 主要トピック

- 子どもが読める文言と内部用語を出さない方針
- 競合する案内を重ねず、次の一歩だけを見せる方針
- 見た目や音で入力の手応えを返す方針
- 保存上書きや削除など危険操作に確認を入れる方針
- スマホ URL と全画面を含む見せやすい共有導線
- 親の補助は翻訳や支援に留め、子どもの決定権を残す方針

## 深い洞察

- UX policy は単なる文言規則でなく、 CJ44 の simplicity と child agency を UI 面へ翻訳したものになる
- `見せやすさ` は aesthetic より feedback loop の速さを支える条件である
- 危険操作の確認は data safety だけでなく、子どもの ownership を守る意味も持つ

## キーワード

- ux-policy
- child-readable
- one next action
- immediate feedback
- safe confirmation
- parent assist

## 注意点

- 短い policy 文書なので、具体 feature 設計では platform や narrative PRD と併読する必要がある
