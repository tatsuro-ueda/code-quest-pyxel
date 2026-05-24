---
source: raw/tasknotes/steering/done/20260505-rewrite-tests-for-imagebank-ssot.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 imagebank SSoT 化に伴う test 群の書き換え Summary Draft

## summary

この note は、imagebank SSoT 化に合わせて world/dungeon 系 test の仕込み方を共通 helper へ寄せ直した記録です。依存タスクが先に進んだ結果、当初の大規模書き換えは不要になり、重複の高い 3 file を絞って整理する形へスコープが縮みました。

## key_points

- `test/_helpers/imagebank_stub.py` を新設し、fake tilemap とバックアップ/復元の重複を helper 1 本へ集約した。
- `test_dungeon_boss_trigger.py`、`test_world_map_ssot.py`、`test_tilemap_editor_truth.py` を新 helper 前提へ整理した。
- 起票時想定の多くは関連タスク完了で既達成となっており、着手前の再見積もりが重要だと記録した。

## important_quotes

- "`依存タスクが先に走るとスコープが半分以上消える`"
- "`重複削減の費用対効果`"

## open_questions

- dormant 扱いにした残り test 群を、どの条件で helper 化対象へ再昇格させるべきか。
- `conftest.py` の import 方針を他 helper 群まで広げるべきか。
