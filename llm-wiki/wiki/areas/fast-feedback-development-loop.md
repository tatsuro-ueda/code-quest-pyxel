---
status: active
last_updated: '2026-05-24'
sources:
- ../summaries/knowledge/customer-journeys-summary.md
- ../summaries/knowledge/old-customer-jobs-summary.md
- ../../../docs/customer-journeys.md
- ../../raw/knowledge/docs/old-customer-jobs.md
- ../summaries/tasknotes/steering/done/2026年5月24日 開発基盤：存在価値が薄いテストを整理して実行時間を削る-summary.md
- ../../raw/tasknotes/steering/done/2026年5月24日 開発基盤：存在価値が薄いテストを整理して実行時間を削る.md
- ../summaries/tasknotes/steering/done/2026年5月24日 開発基盤：日常pytestをさらに軽くするため重い全走査テストを別枠化する-summary.md
- ../../raw/tasknotes/steering/done/2026年5月24日 開発基盤：日常pytestをさらに軽くするため重い全走査テストを別枠化する.md
---


# Fast Feedback Development Loop

## 核心

この repo の価値は、親子のあいだで `作る -> 遊ぶ -> 直す -> また遊ぶ` が短時間で閉じることにある。`customer-journeys` はそれを開発 / デバッグ / 共有の複数ループへ展開し、`old-customer-jobs` は AI によって「翌日修正」から「数分修正」へ変わった点を核として説明する。

## ループの構造

- 子どもは Code Maker や実プレイで違和感を見つける
- 親はその違和感を AI へ翻訳する
- 修正結果はすぐ development 候補へ戻る
- 子どもが再度遊んで次の判断を返す

## 止まる条件

- 変更反映が遅い
- 修正の責任範囲が曖昧で壊れやすい
- 親が主導しすぎて子どもが乗客になる

## この repo への含意

- 機能追加は「何を足せるか」だけでなく「数分〜数十分で次の 1 周が閉じるか」で判断する
- 開発速度とガードレールは対立ではなく、同じ loop を守るための両輪である

- the two May 24 testing notes made the fast loop more explicit by cutting helper-only and repo-scan-heavy tests out of the daily path while preserving smoke entrypoints for higher-cost checks.

## 関連ページ

- [Approval Loop And Child Agency](./approval-loop-and-child-agency.md)
- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
- [Parent Support Without Control](./parent-support-without-control.md)
