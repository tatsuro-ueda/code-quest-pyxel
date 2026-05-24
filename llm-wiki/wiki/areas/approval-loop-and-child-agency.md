---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/customer-journeys-summary.md
  - ../summaries/knowledge/product-requirements-platform-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j38-preview-build-flow-summary.md
  - ../../raw/knowledge/docs/customer-journeys.md
  - ../../raw/knowledge/docs/product-requirements-platform.md
  - ../../raw/tasknotes/steering/done/20260412-j38-preview-build-flow.md
---

# Approval Loop And Child Agency

## 核心

`customer-journeys` は、子どもの主体性を感情論でなく仕組みとして守るために、承認ループを product の一部として置く。承認、却下、選んで適用、巻き戻しまでを queue 化することで、親や AI が「勝手に反映する」状態を防ぐ。

## 承認ループが守るもの

- 子どもが変更を承認できる
- 子どもが変更を却下できる
- 子どもが複数案から選べる
- 子どもが「やっぱり戻す」を自分で言える
- 子どもが development と production を遊び比べて決められる
- 却下した版が勝手に本番へ上がらない

## 止まる条件

- 親が先に適用してしまう
- 選択肢が 1 つしかない
- 巻き戻し導線がない

## この repo への含意

- AI の速さは、そのままだと親主導を加速させる危険もある
- だから approval loop は nice-to-have ではなく、主体性を壊さないための core mechanism である
- platform 側の build / approve / reject / rollback は、全部この child agency を支える ops である
- preview build が current に混ざらず、`--promote` でだけ昇格する構造そのものが
  child agency の guardrail になる

## 関連ページ

- [Fast Feedback Development Loop](./fast-feedback-development-loop.md)
- [Parent Support Without Control](./parent-support-without-control.md)
- [Platform Sharing And Approval Ops](./platform-sharing-and-approval-ops.md)
- [Child Readable UX And Parent Assist](./child-readable-ux-and-parent-assist.md)
