---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/customer-jobs-summary.md
  - ../summaries/knowledge/customer-journeys-summary.md
  - ../summaries/knowledge/old-customer-jobs-summary.md
  - ../summaries/knowledge/product-requirements-platform-summary.md
  - ../summaries/knowledge/ux-policy-summary.md
  - ../../raw/knowledge/docs/customer-jobs.md
  - ../../raw/knowledge/docs/customer-journeys.md
  - ../../raw/knowledge/docs/old-customer-jobs.md
  - ../../raw/knowledge/docs/product-requirements-platform.md
  - ../../raw/knowledge/docs/ux-policy.md
---

# Low Friction Sharing

## 核心

子どもが作ったものを `すぐ体験してもらえる` ことと、友達が `その場で気軽に試せる` ことは別々ではありません。この source は、共有の摩擦が高いと、子どもの社会的進歩と友達の参加意欲が同時に止まると見ています。

## 子どもと友達のジョブ

- `JSC_CHILD_SOCIAL`: 自分の作ったものをすぐ体験してもらい、反応を得たい
- `JFR_FRIEND_LOW_FRICTION`: 何かを試すときの手間や心理的ハードルを下げたい

## 競合が止まる点

- Scratch は公開できても、友達にその場で届く速さが弱い
- Roblox は広く届くが、DL や登録や文化の壁がある
- RPG Maker は作品化できるが、共有導線の摩擦が大きい
- 自前配信は自由だが、信頼や操作の壁が残りやすい

## 共有 loop としての補強

- `customer-journeys` では `友達に見せる` `実公開で遊ばれた記録が見える` `友達のフィードバックを反映する` が一つの共有 loop として並ぶ
- `old-customer-jobs` では、スマホ URL で即プレイできることが、友達まで loop を広げる条件とされる
- `product-requirements-platform` は URL 即プレイ、全画面、再共有、play log を具体運用まで落としている

## この repo への含意

- 公開や配布の議論では、`作った後に誰かがすぐ遊べるか` を第一条件として見る
- sharing friction は子どもの social job だけでなく、friend job の入口としても扱う
- analytics や play log も、監視でなく feedback loop の材料として設計する
- UX 的にも、共有導線は説明の少なさと起動の速さを優先する

## 関連ページ

- [Continuous Experience Loop](./continuous-experience-loop.md)
- [Parent Support Without Control](./parent-support-without-control.md)
- [Fast Feedback Development Loop](./fast-feedback-development-loop.md)
- [Platform Sharing And Approval Ops](./platform-sharing-and-approval-ops.md)
