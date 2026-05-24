---
source: raw/tasknotes/steering/done/20260517-inn-skip-when-full-hp.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月17日 やどやでHP満タンなら泊まらずメッセージだけ出す Summary Draft

## summary

この note は、宿屋で HP/MP 満タンなら泊まらずメッセージだけ返すようにした記録です。満タン判定は `PlayerModel` へ集約し、支払い判定より先に「そもそも不要」を返す形で child-friendly な挙動へ寄せました。

## key_points

- `INN_FULL_MSG` を shared constants に追加し、`PlayerModel.is_full_hp_mp()` を新設した。
- `_stay_at_inn` 冒頭で満タン判定を見て、True ならメッセージだけで return するようにした。
- 満タン判定を coin 判定より先に置き、「払えないのに満タン」という残念さを避けた。

## important_quotes

- "`すでに げんきまんたんだ！`"
- "`満タン判定をコイン不足判定より先`"

## open_questions

- 毒だけ残っている時も泊まらない現仕様を、いつ再検討するべきか。
- 宿屋の状態判定を、どこまで `PlayerModel` API として共通化するべきか。
