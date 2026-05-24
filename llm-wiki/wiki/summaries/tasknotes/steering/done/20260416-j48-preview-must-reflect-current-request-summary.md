---
source: raw/tasknotes/steering/done/20260416-j48-preview-must-reflect-current-request.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月16日 J48 おためしばんは今の依頼内容を表すと CJ31/CJG31 で明確化する Summary Draft

## summary

この tasknote は、preview の問題を「説明が古いこと」ではなく、「おためしばんが今の依頼内容を表していないこと」と整理し直した記録です。修正の中心は、主問題を `CJ31`、従属問題を `CJ33` と切り分け、`今の依頼に対応する preview だけを見せる` という期待を docs と gherkin に先に固定したことでした。

## key_points

- トップページの説明文は、古いのではなく当時の preview 差分を正しく表していた。
- 問題は説明の古さより、preview 自体の意味づけが弱いことだった。
- 主問題を `CJ31`、従属問題を `CJ33` と整理した。
- `おためしばん` は「今の依頼内容を表すもの」という期待を明文化した。
- `CJG31/CJG33` に、前の preview を今の依頼として見せない条件を追記した。
- 実装に走る前に、先に docs 側で preview の意味を固定した。

## important_quotes

- "主問題を `CJ31`、従属問題を `CJ33`"
- "今の依頼に対応する preview だけを見せる"
- "問題は `CJ33` の説明不一致ではなく、`おためしばん` 自体が『今の依頼内容』を表していないことだった。"

## open_questions

- 「今の依頼を表す preview」とは、どんな状態を指すのか。
- preview の意味づけを、docs だけでなくコードにもどう落とすべきか。
