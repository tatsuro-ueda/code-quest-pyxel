---
source: raw/tasknotes/steering/done/20260418-cj42-post-boss-dungeon-exit-ending.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月18日 CJ42 魔王撃破後のダンジョン脱出をメッセージ後エンディングへつなぐ Summary Draft

## summary

この tasknote は、魔王を倒したあとに map へ戻るだけで終わっていた流れを、脱出後のメッセージとエンディングまで閉じる `CJ42` の問題として扱い直した記録です。焦点は、旧 JS 版にあった `ボス撃破後に脱出してその先へ進む` 流れが current repo では最後の一歩だけ切れており、それを単なるセリフ追加ではなく `最後まで遊べる` 体験の接続問題として整理したことでした。

## key_points

- 旧 JS 版では、魔王撃破後に脱出してメッセージと ending へ進む流れがあった。
- current repo には出口文言はあるが、出口処理は map に戻るだけで止まっていた。
- これは `CJ42` の `ボスを倒す → エンディングに到達する` が最後の一歩で切れている問題だと整理した。
- 対応はセリフ追加よりも、進行を最後までつなぐ customer journey の接続として扱うべきだとした。
- `CJ42` を主、`CJ30` を関連として human expectation と実装差分を固定した。
- build や隠し導線への影響もあるため、単純な callback 差し戻しだけで済むかは切り分けが必要だと残した。

## important_quotes

- "ボスを倒す → エンディングに到達する"
- "最後の一歩で切れている"
- "メッセージが流れ、その先へ進む"

## open_questions

- この repo で `最後まで遊べる` とは、どこまでつながっていれば十分なのか。
- ボス撃破後の導線は、既存の隠し要素や build 前提とどう両立させるべきか。
