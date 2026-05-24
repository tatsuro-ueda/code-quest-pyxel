---
source: raw/tasknotes/steering/done/20260505-player-state-shim-removal.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 player_state.py 旧 API shim 群の撤去（M4-4 完成） Summary Draft

## summary

この note は、`player_state.py` に残った旧 API shim を取り除いて M4-4 を閉じるための planning 記録です。`PlayerModel` を中心に snapshot / stats 責務を寄せ直し、test と bundle 互換を見ながら 3 ループで shim を削る段取りを定めています。

## key_points

- `stats_for_level`、`create_initial_player`、`dump_snapshot`、`restore_snapshot`、`player_model_to_dict` の 5 shim を棚卸しした。
- `PlayerModel.stats_for_level` と `PlayerModel.from_snapshot` を軸に test 書換えと shim 削除を進める方針を取った。
- bundle 再エクスポートと save 互換確認を必須チェックとして残した。

## important_quotes

- "`旧 API shim 群`"
- "`PlayerModel.from_snapshot`"

## open_questions

- bundle/export 側に残る compatibility shim をどこまで許容し、いつ完全撤去へ切り替えるべきか。
- save 互換確認を `pytest` 以外のどこまで実物検証に広げるべきか。
