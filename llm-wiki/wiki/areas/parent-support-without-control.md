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

# Parent Support Without Control

## 核心

親の役割は `教える人` や `管理する人` に固定されません。この source は、親が子どもの意思決定を奪わず、でも前進のための手数は引き受けるという微妙な立場を価値の中心に置いています。

## 親ジョブ

- `JPA_PARENT_ROOT`: 子どもと同じ体験を共有しながら関わりたい
- `JSC_PARENT_GROWTH`: 子どもに合う成長機会を自然に渡したい
- `JIS_PARENT_AUTONOMY`: 子どもが自分で選び決める状態を支えたい
- `JRE_PARENT_PROGRESS`: 関わった意味や記憶を残したい
- `JUN_PARENT_UNDERSTANDING`: 子どもの今の関心や状態を自然に理解したい

## 支えるが奪わない条件

- 決定権は子どもに残す
- 親はコード修正、ビルド、配信などの実装手数を引き受けてもよい
- ただし親主導で進めすぎると `支援` が `支配` に反転する
- 詳細な可視化も、やり方を誤ると `理解` ではなく `監視` になる
- `old-customer-jobs` は、親の役割を AI 翻訳者と明言し、「何を直すか」を親が決めない線引きを追加する
- `customer-journeys` は、その線引きを承認キューのような仕組みへ落とす
- `ux-policy` は、親向け補助 UI でも子どもの決定権を奪わない表示面を要求する

## この repo への含意

- feature 設計では `親が楽になるか` だけでなく `子の主体性を消さないか` を同時に問う
- AI 活用でも、親や AI が主役になりすぎる運用は避ける
- 親の仕事は選択肢や技術翻訳を出すことまでで、最終選択を奪わないことにある
- platform の approve / reject / change list も、親の操作権と子どもの決定権を分けて設計する

## 関連ページ

- [Continuous Experience Loop](./continuous-experience-loop.md)
- [Low Friction Sharing](./low-friction-sharing.md)
- [Approval Loop And Child Agency](./approval-loop-and-child-agency.md)
- [Child Readable UX And Parent Assist](./child-readable-ux-and-parent-assist.md)
