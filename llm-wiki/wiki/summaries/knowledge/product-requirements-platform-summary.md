---
source: docs/product-requirements-platform.md
source_type: doc
status: active
origin:
  - docs/product-requirements-platform.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: large
---

# Product Requirements Platform Summary

## TL;DR

この source は、配信、Code Maker 制約、approval flow、共有後の再修正までをまとめた運用 PRD である。中心は `URL だけで遊べる低摩擦共有` `感想を数分で修正版へ返す loop` `Code Maker が見える真実であり続けること` `development と production を分けて子どもが承認 / 却下 / 選択 / 巻き戻しできること` である。

## 主要トピック

- バグ修正や再テストを 5 分単位で回す fast recovery loop
- スマホ URL で即プレイできる友達共有
- フィードバックを受けて修正し、再共有を複数回回せる
- 公開 URL の play log を次の行動へつなげる
- Code Maker zip の持ち出しと取り込みを通じて resource を戻す
- 開発版 / 本番版の比較で子どもが承認、却下、選択、巻き戻しできる

## 深い洞察

- `自分たちのゲーム` 感は編集面、配布面、承認面が一貫して初めて成立する
- Code Maker から戻すときに `main.py` を採用しない境界が、AI 修正と子どもの resource 編集を両立させる
- approval flow は UI ではなく、子どもの決定権を product に埋め込むための仕組みである

## キーワード

- product-requirements-platform
- sharing
- approval queue
- Code Maker
- development vs production
- play log
- rollback

## 注意点

- 一部の説明自動生成や environment 差分吸収はまだ改善余地がある
- editor と runtime の完全一致、 resource freshness、 rollback 専用 UI などは継続監視が必要である
