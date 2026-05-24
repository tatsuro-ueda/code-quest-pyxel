---
source: raw/tasknotes/steering/done/20260419-cj26-preview-codemaker-freshness.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月19日 CJ26 開発版 Code Maker zip は今の preview と一致すると保証する Summary Draft

## summary

この tasknote は、download link があるだけでは足りず、落とした zip が今の preview 実物と一致していることまで `CJ26` で保証する話をまとめた記録です。要点は、公開ページは新しいのに `code-maker-preview.zip` だけ古い、という不整合を `link がある` ではなく `今の preview と一致して編集に入れる` 条件の不足として捉え直し、stale zip を弾く test まで必要だと整理したことでした。

## key_points

- `CJG26` には preview zip 導線の存在はあるが、zip の freshness を守る条件は無かった。
- 実際に、公開ページは新しいのに `code-maker-preview.zip` だけ古い不整合が起きていた。
- 問題の本体を `CJ31` の意味づけより一段手前の、`CJ26` の編集導線が閉じていないことだと整理した。
- `リンクがある` ではなく、`今の preview と一致していてそのまま Code Maker で編集に入れる` を条件へ上げた。
- `CJG26` に freshness と `Code Maker で開いて編集できる` scenario を追加する前提を固定した。
- この note は、preview 実物と配布 zip を同時にそろえる guardrail の必要性を明文化した。

## important_quotes

- "preview はあるのに zip だけ古い"
- "今の preview と一致していて、そのまま Code Maker で編集に入れる"
- "リンクがある"

## open_questions

- `今の preview と一致する` とは、どの artifact まで同時にそろっている状態を指すのか。
- freshness guardrail は、download 導線のどの段階で fail させるべきか。
