---
source: raw/tasknotes/steering/done/20260425-brushup-customer-journeys.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月25日 カスタマージャーニーをブラッシュアップして競合分析を要件に落とす Summary Draft

## summary

この tasknote は、`docs/customer-journeys.md` の 42 ジャーニーすべてに competitor-before の視点とカテゴリタグを加え、競合分析を requirements に落とし込める形へ磨き直した記録です。進め方の核は、既存の journey 構造を壊さずに各 mermaid の左端へ `subgraph Competitor` を足し、末尾に `customer-jobs.md` のカテゴリ参照タグを 1 行だけ増やす最小ルールを守ったことでした。

## key_points

- 対象は 42 ジャーニー全体で、開発 / デバッグ / 演出 / 共有 / 承認 / 発展 / ガードレールのクラスターごとに分けて進めた。
- 各ジャーニーに competitor-before subgraph を左端追加し、末尾へカテゴリタグを 1 行足した。
- Scratch / Roblox / SMM2 / RPG Maker / vibe coding / 自前配信 / 教育系 SaaS などをカテゴリに応じて比較対象へ使った。
- 既存ノード書き換え禁止、左端追加、末尾 1 行タグ、感情列維持という最小ルールを崩さず進めた。
- grep で competitor subgraph 42 個、カテゴリタグ 42 個、pytest 702 passed を確認した。
- 次の仕事は、この enriched journey を各 PRD 改良へ波及させることだと整理した。

## important_quotes

- "全 42 ジャーニー"
- "subgraph Competitor["競合Before"]"
- "PRD（`product-requirements-platform.md` 等）を新ジャーニーから改良・詳細化する後続タスク"

## open_questions

- 競合Before の比較軸を、どの PRD から先に要求へ翻訳するべきか。
- 42 ジャーニーのカテゴリタグを、今後どの review 導線で参照させるべきか。
