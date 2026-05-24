---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/product-requirements-platform-summary.md
  - ../summaries/knowledge/ux-policy-summary.md
  - ../../raw/knowledge/docs/product-requirements-platform.md
  - ../../raw/knowledge/docs/ux-policy.md
---

# Platform Sharing And Approval Ops

## 核心

`product-requirements-platform` は、共有、再修正、承認、巻き戻しを 1 つの運用系としてまとめる。友達に URL を送るだけで遊べ、感想を受けて数分で直し、子どもが development と production を比べて採否を決めるところまでが platform の仕事になる。

## 共有と承認の loop

- URL だけで即プレイできる低摩擦共有
- フィードバックをその場で修正して再共有できる loop
- play log で「届いたか」を次の行動へつなげる
- 開発版 / 本番版の比較で承認、却下、再提案、巻き戻しを回す

## Code Maker との接続

- 持ち出す zip はその時点の候補と一致している必要がある
- 取り込むときは resource を戻し、 zip 内の main.py は採用しない
- 編集面で見えたものが実ゲームの真実であることを壊さない

## この repo への含意

- platform 変更では deployment だけでなく child agency まで done 条件に入る
- build や selector は単なる配布物生成でなく、 approval queue の UI/ops でもある
- UX policy の読みやすさと危険操作確認は、この approval flow の説明面を支える

## 関連ページ

- [Approval Loop And Child Agency](./approval-loop-and-child-agency.md)
- [Low Friction Sharing](./low-friction-sharing.md)
- [Child Readable UX And Parent Assist](./child-readable-ux-and-parent-assist.md)
- [Parent Support Without Control](./parent-support-without-control.md)
