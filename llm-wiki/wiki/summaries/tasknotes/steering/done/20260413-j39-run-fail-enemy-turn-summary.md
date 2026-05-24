---
source: raw/tasknotes/steering/done/20260413-j39-run-fail-enemy-turn.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月13日 J39 逃走失敗後に敵ターンが来ない Summary Draft

## summary

この tasknote は、`にげる` 失敗後に敵が攻撃してこず、何度でも逃走を試せてしまう不具合を、battle phase の責務ずれとして直した記録です。要点は、失敗テストで `enemy_attack` phase が「敵行動そのもの」ではなく「敵行動後の表示」に使われていたことを固定し、最小修正で本来の戦闘ループへ戻したことでした。

## key_points

- failing test で、逃走失敗後に `_do_enemy_attack()` が一度も呼ばれないことを Red で固定した。
- 根本原因は、逃走失敗時に `enemy_attack` phase を使っていたことだった。
- `enemy_attack` phase は敵行動実行ではなく、敵行動後メッセージ表示の責務だった。
- 最小修正として、逃走失敗時の流れを `player_attack` 系の戦闘ループへ戻した。
- 逃走成功ケースと通常戦闘の回帰も focused test で確認した。
- この修正は `CJ39` だけでなく、`CJ42` の完走体験を守る実装修正として位置づけられた。

## important_quotes

- "逃走失敗後も戦闘ターンが継続する"
- "敵行動そのものを起こす phase ではなかった。"
- "最小範囲で固定するのが妥当。"

## open_questions

- 戦闘の順番ミスを防ぐには、どの phase まで共通ルールとして整理するべきか。
- `CJ42` の完走体験を守る観点を、ほかの戦闘系不具合にもどう広げるべきか。
