---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/ux-policy-summary.md
  - ../summaries/knowledge/product-requirements-platform-summary.md
  - ../summaries/knowledge/product-requirements-narrative-summary.md
  - ../../raw/knowledge/docs/ux-policy.md
  - ../../raw/knowledge/docs/product-requirements-platform.md
  - ../../raw/knowledge/docs/product-requirements-narrative.md
---

# Child Readable UX And Parent Assist

## 核心

`ux-policy` は、子どもに見える画面を `読める` `今やることが分かる` `押した実感が返る` に固定する。同時に `platform` と `narrative` は、親が通訳や決定者になりすぎず、説明と承認と導線が子ども側で理解できることを要求している。

## 見える interaction rule

- ひらがな中心で内部用語を出しすぎない
- 同時に複数の案内を重ねない
- 押した直後の feedback を返す
- 危険操作は確認を入れて無言で通さない

## 親の補助境界

- 親は技術翻訳や実装手数を引き受けても、決定権は奪わない
- 次の目的地や変更説明は、親の口頭補足なしでも分かる形を目指す
- 共有や approval UI も子どもが自分で比較判断できる説明面を持つ

## この repo への含意

- UX review では文言、layout、input feedback、agency の 4 つを同時に見る
- Code Maker 境界や CJ44 simplicity は UX の外側の話ではなく、子どもの理解可能性に直結する

## 関連ページ

- [Platform Sharing And Approval Ops](./platform-sharing-and-approval-ops.md)
- [Narrative Branching And Player Guidance](./narrative-branching-and-player-guidance.md)
- [Parent Support Without Control](./parent-support-without-control.md)
- [Approval Loop And Child Agency](./approval-loop-and-child-agency.md)
