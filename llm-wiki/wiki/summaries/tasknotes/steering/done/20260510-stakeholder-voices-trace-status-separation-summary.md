---
source: raw/tasknotes/steering/done/20260510-stakeholder-voices-trace-status-separation.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月10日 stakeholder_voices trace status separation Summary Draft

## summary

この note は、source trace coverage を `active` 専用から tracked status 群へ広げ、trace completeness と implementation status を分離した記録です。`later` や `wont` を active に寄せずに coverage 完了を示せるようになりました。

## key_points

- `TRACKED_TRACE_STATUSES = {"active", "later", "wont"}` を導入し、coverage 集計を tracked-status ベースへ切り替えた。
- `source_traceability_integrity` も同じ status 群を見るようにした。
- implementation-oriented rule には触れず、trace completeness の軸だけを分離した。

## important_quotes

- "`trace completeness は implementation status から切り離せた`"
- "`later/wont の trace drift`"

## open_questions

- `archived` や `draft` を tracked status に含めるかを、どの基準で決めるべきか。
- implementation status 専用の field や dashboard を、どこで正として設計するべきか。
