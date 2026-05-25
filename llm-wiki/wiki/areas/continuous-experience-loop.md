---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/customer-jobs-summary.md
  - ../summaries/knowledge/customer-journeys-summary.md
  - ../summaries/knowledge/old-customer-jobs-summary.md
  - ../summaries/tasknotes/steering/done/20260413-j42-rpg-loop-journey-summary.md
  - ../summaries/tasknotes/steering/done/20260413-j39-run-fail-enemy-turn-summary.md
  - ../../../docs/customer-jobs.md
  - ../../../docs/customer-journeys.md
  - ../../../docs/old-customer-jobs.md
  - ../../raw/tasknotes/steering/done/20260413-j42-rpg-loop-journey.md
  - ../../raw/tasknotes/steering/done/20260413-j39-run-fail-enemy-turn.md
  - ../summaries/tasknotes/steering/done/20260425-brushup-customer-journeys-summary.md
  - ../../raw/tasknotes/steering/done/20260425-brushup-customer-journeys.md
---

# Continuous Experience Loop

## 核心

この source が最も強く言っているのは、子どもの体験を `遊ぶ -> 作る -> 自分で判断する -> 共有する` の連続したループとして守ることです。どこか一段だけが強くても、次へ進むたびに止まるなら進歩は壊れます。

## 子ども側の連続性

- `JPL_CHILD_PLAYER` は没入が切れずに遊び続けられることを求める
- `JCR_CHILD_CREATOR` は自分の感覚で自由に表現できることを求める
- `JCT_CHILD_CRITIC` は他人の正解でなく、自分の感覚で良し悪しを決めたい
- `JSC_CHILD_SOCIAL` は作ったものをすぐ体験してもらい、反応を得たい

## 競合が途切れさせる点

- Scratch は入りやすいが、完成度や比較判断、即時共有で止まりやすい
- Roblox は体験や共有は強いが、自作へ戻ると連続性が崩れる
- RPG Maker は深く作れるが、主体性や速度の面で詰まりやすい
- vibe coding は速いが、体験の主体が AI 側へ流れやすい

## loop として見た補強

- `customer-journeys` は、この連続性を `開発` `デバッグ` `演出` `共有` `発展` `承認` `ガードレール` の具体ループへ展開する
- `old-customer-jobs` は、親子の good cycle が AI による数分修正で初めて回ると説明する
- `J42` は、この連続性の終点を `最後まで遊び切れる` まで明文化し、guardrail もその完走体験を守る前提へ広げた
- `J39` は、逃走失敗後に敵ターンが飛ぶような一見小さな battle bug でも、`最後まで遊ぶ` 連続体験を途中で空洞化させると示した

## この repo への含意

- product docs や feature 議論では、単発機能がどの段の進歩を押し、どこで途切れさせるかを確認する
- `作れる` `遊べる` `共有できる` を別物として最適化しすぎない
- `作る -> 遊ぶ -> 直す -> また遊ぶ` が閉じる速さも、連続体験の一部として扱う
- 戦闘や進行の修正では、`止まらないこと` だけでなく `最後までやり切れること` を done 条件に含める
- 42 journey すべてへ competitor-before を足したことで、`遊ぶ -> 作る -> 判断する -> 共有する` 連続体験が競合のどこで途切れやすいかを requirements 側から見比べやすくなった。

## 関連ページ

- [Parent Support Without Control](./parent-support-without-control.md)
- [Low Friction Sharing](./low-friction-sharing.md)
- [Fast Feedback Development Loop](./fast-feedback-development-loop.md)
