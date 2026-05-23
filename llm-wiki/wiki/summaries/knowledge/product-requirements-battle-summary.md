---
source: raw/knowledge/docs/product-requirements-battle.md
source_type: doc
status: active
origin:
  - docs/product-requirements-battle.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: large
---

# Product Requirements Battle Summary

## TL;DR

この source は、敵・呪文・全体バランスの改造を `すぐ試せる` と `別の仕組みを壊さない` の両方で定義する。中心は `enemy/spell data を揃える` `戦闘中にちゃんと見えて使える` `MP 不足など失敗理由を伝える` `後半だけ強くするような範囲調整を安全に回す` である。

## 主要トピック

- 強すぎる敵をすぐ弱め、EXP/GOLD/レベルアップまで壊さない
- 新しい敵はデータ、出現ゾーン、スプライト表示まで揃えて追加する
- 新しい呪文は MP、威力、説明、習得レベルを持ち、戦闘中に正しく使える
- MP 不足などの失敗は理由を短く明示する
- ゾーン単位や後半だけの一括バランス調整を、通しプレイ可能性とセットで扱う

## 深い洞察

- battle の価値は `数値を変えられること` ではなく `変えた結果をすぐ判断できること` にある
- 新しい敵や呪文はデータ追加だけでは不十分で、出現と可視化まで一体で完了になる
- 外部フィードバックを回す前提なので、 balance は静的設計より loop の速さが重要になる

## キーワード

- product-requirements-battle
- enemy balance
- spells
- battle loop
- data-driven tuning
- fast feedback

## 注意点

- UX 時間目標はあるが自動保証ではない
- zone 単位の一括調整 UI や generic spell builder はまだ製品機能として固定されていない
