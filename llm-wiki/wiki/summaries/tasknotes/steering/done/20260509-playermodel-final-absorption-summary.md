---
source: raw/tasknotes/steering/done/20260509-playermodel-final-absorption.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 PlayerModel 最終吸収（item_use / player_state） Summary Draft

## summary

この note は、`item_use` と `player_state` の production 依存を `PlayerModel` へ吸収し、残りを互換 shim として再定義した記録です。live import を 먼저切り、bundle/test 互換だけを legacy 側へ残す形で M4-4 の最後を詰めています。

## key_points

- `src/shared/state/player_model.py` に item 使用ルールを寄せた。
- menu / battle presenter と `main_runtime.py` から `item_use.py` / `player_state.py` の live import を削除した。
- `item_use.py` と `player_state.py` は bundle / test 互換の shim として位置づけ直し、再侵入 guard も追加した。

## important_quotes

- "`production の正本ではなくなった`"
- "`legacy helper を残す場合でも production import は先に切る`"

## open_questions

- `player_state.py` の bundle 互換を、どの時点でさらに薄くして完全削除へ向かうべきか。
- shim を残したままでも live import 復活をどう継続監視するべきか。
