---
source: raw/tasknotes/steering/done/20260509-stakeholder-voices-battle-prd-migration.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 stakeholder_voices battle PRD migration Summary Draft

## summary

この note は、Battle PRD の残り 4 項目を stakeholder_voices の requirement/acceptance へ移植した記録です。request を増やさず既存の ownership / fast feedback request にぶら下げ、battle 調整ループを traceable にしました。

## key_points

- `req_enemy_balance_adjustable` など battle requirement 4 件と acceptance 4 件を追加した。
- `customer_journeys` と `product_requirements_battle` の両方を `source_trace_refs` で結んだ。
- coverage red を `requirements == 17 -> 21+` と missing refs 0 で閉じた。

## important_quotes

- "`request を増やさずに整理できた`"
- "`manual と deterministic を混在させたのは妥当`"

## open_questions

- battle の未移植 journey 群を、次はどのテーマ単位で束ねるべきか。
- assets YAML と runtime の整合を、battle acceptance でどこまで deterministic proof に寄せるべきか。
