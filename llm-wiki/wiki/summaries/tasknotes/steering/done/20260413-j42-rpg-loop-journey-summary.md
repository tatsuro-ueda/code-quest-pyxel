---
source: raw/tasknotes/steering/done/20260413-j42-rpg-loop-journey.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月13日 J42 子どもが冒険を最後までやり切れる Summary Draft

## summary

この tasknote は、バグ修正を「壊れていないこと」だけでなく、「子どもが RPG を最後まで遊び切れること」で捉え直すために、`CJ42` を customer journey と guardrail 群へ追加した記録です。中心は `逃走失敗後に敵ターンが来ない` のような不具合を単発バグとしてではなく、完走体験を壊す問題として扱えるよう、docs 側の正の体験と保護ルールをつなぎ直したことでした。

## key_points

- `customer-journeys.md` に `CJ42: 子どもが冒険を最後までやり切れる` を追加した。
- `product-requirements-guardrails.md` の対象 journey を `CJ35-CJ42` に広げた。
- `CJG38/CJG39` の本文を、完走体験を守る説明へ更新した。
- 主要パス scenario を `探索 → 通常戦闘 → 経験値獲得 → 成長確認 → ボス撃破 → エンディング` まで強化した。
- `逃走失敗後も戦闘ターンが継続する` を guardrail scenario として追加した。
- runtime を増改築する前に、まず docs 上で「何を守るのか」を正の体験として固定した。

## important_quotes

- "最後まで遊べるRPG"
- "逃走失敗後も戦闘ターンが継続する"
- "正のカスタマージャーニーとそれを守る guardrail をセットで置く必要がある。"

## open_questions

- この repo で「最後まで遊べる」とは、どこまでできれば十分なのか。
- 完走体験を守る guardrail は、戦闘以外のどの経路まで含めるべきか。
