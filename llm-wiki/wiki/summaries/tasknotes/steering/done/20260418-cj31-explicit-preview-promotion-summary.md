---
source: raw/tasknotes/steering/done/20260418-cj31-explicit-preview-promotion.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月18日 CJ31 preview 昇格を明示コマンドに一本化する Summary Draft

## summary

この tasknote は、preview の意味が docs と build のあいだで揺れていた問題を、`候補版` ではなく `明示承認で current に上げる版` として定義し直した記録です。中心は、自動繰り上げを残すと子どもの承認よりも `次の依頼が来たか` が本番更新の条件になってしまうため、`CJ31/CJ32` の意図に合わせて approve / reject を軸にした昇格モデルへそろえ直すことでした。

## key_points

- preview の定義が `候補版` なのか `次に通る版` なのかで docs と build が食い違っていた。
- 自動繰り上げを維持すると、承認より `次の依頼` が本番更新の条件になってしまうと整理した。
- preview を明示 approve / reject コマンドで確定するモデルへ再定義した。
- `CJ31/CJG31/CJG32/CJG33` を新しい昇格モデルに合わせて書き換える前提を固定した。
- build から自動繰り上げと note 依存を外し、承認ルールを明示的に扱う方向へ寄せた。
- この note は、preview/current の運用ルールを子どもの承認中心へ戻すための設計メモになった。

## important_quotes

- "preview を明示 approve/reject コマンドで確定する"
- "次の依頼が来たか"
- "子どもの承認より「次の依頼が来たか」が本番更新のトリガーになる"

## open_questions

- preview を `承認待ちの候補版` として保つには、どこまで build 側で明示ルールを持つべきか。
- approve / reject の判断は、どの操作までを子どもの承認として扱うべきか。
