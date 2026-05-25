---
source: docs/product-requirements-av.md
source_type: doc
status: active
origin:
  - docs/product-requirements-av.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: large
---

# Product Requirements AV Summary

## TL;DR

この source は、BGM・SFX・VFX を「あとから足す飾り」でなく、子どもが違いを実感するための core 体験として扱う。中心は `scene ごとの BGM 切り替え` `イベントに結びつく SFX/VFX` `Code Maker で人が作った音を本編へそのまま運ぶこと`、そして `複雑な設定 UI を増やさず常時 ON でシンプルに保つこと` である。

## 主要トピック

- ゾーンや scene ごとに違う BGM を鳴らして場所の個性を伝える
- 戦闘開始、勝利、場面転換で音の切り替わりを明確にする
- 攻撃、回復、レベルアップ、ダメージで SFX/VFX を結びつける
- Sound / Music の authoring は Code Maker 側、人は音を作り AI は import / build を担う
- CJ44 により BGM/SFX/VFX の個別 ON/OFF UI は撤去し、常時 ON の単純さを優先する

## 深い洞察

- `音の実体を誰が決めるか` と `ゲーム内でいつ鳴るか` は別責務として分けられている
- pyxres を SSoT に保つことが、子どもに見える編集面を真実にする
- シンプルさは機能削減ではなく、比較と反映を速くするための guardrail である

## キーワード

- product-requirements-av
- BGM
- SFX
- VFX
- pyxres SSoT
- Code Maker audio authoring
- simplicity

## 注意点

- ゾーン 0-3 の固有 BGM や Sound エディタ結果の end-to-end 固定はまだ目標状態が残る
- runtime 側の SFX fallback と Code Maker 由来の音の優先順位は今後も health-check 対象になる
