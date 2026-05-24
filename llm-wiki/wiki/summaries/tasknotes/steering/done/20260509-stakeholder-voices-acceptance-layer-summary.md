---
source: raw/tasknotes/steering/done/20260509-stakeholder-voices-acceptance-layer.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 stakeholder_voices acceptance layer Summary Draft

## summary

この note は、`stakeholder_voices.yml` に acceptance layer を追加し、requirement と検証単位を分けて扱えるようにした記録です。acceptance id、verification mode、tasknote frontmatter まで整備し、request-first 台帳の次の層を作りました。

## key_points

- `facts.acceptance` を追加し、active P0/P1 requirement 10 件すべてへ `acceptance_ids` を付けた。
- checker に `requirement_acceptance_integrity` と `acceptance_has_verification` を実装し、verification refs まで見るようにした。
- safe normalization も `acceptance_ids` へ広げたが、acceptance prose 自体は autofix させていない。

## important_quotes

- "`要望の根拠` と `検証単位` を混ぜない"
- "`facts.acceptance`"

## open_questions

- `verification.refs` を path 参照から executable proof まで、どこまで表現するべきか。
- tasknote frontmatter と requirement/acceptance contract の整合を、どこまで deterministic に見るべきか。
