---
source: raw/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月14日 J44 stale preview を子どもに見せない Summary Draft

## summary

この tasknote は、preview source が無いのに stale な preview artifact を selector 経由で子どもへ見せ続けていた問題を、preview を見せる条件そのものを引き締めることで直した記録です。中心は、失われた `main_preview.py` を推測復元するのではなく、preview source が無いときは stale artifact を掃除し、selector から `おためしばん` を外す方が `CJ31/CJ33` の期待に合うと判断したことでした。

## key_points

- current は修正済みでも、preview 側は古い `battle_phase = "enemy_attack"` のままだった。
- selector では preview の説明が出ているのに、中身は stale artifact というズレが起きていた。
- 問題は preview 実装より、preview source 不在でも preview artifact を配っていた build/runtime 導線だった。
- 最小修正は preview source が無いときに stale preview を掃除し、preview card を出さないことだった。
- `main_preview.py` を無理に復元するより、preview を見せない判断のほうが user expectation に合っていた。
- 実装後は path / process / file を実世界レベルで確認し、全体 pytest も通した。

## important_quotes

- "source 不在時は preview を出さない"
- "stale artifact を掃除"
- "preview source がないのに stale preview artifact を配り続けている"

## open_questions

- preview を見せない条件は、何を基準に決めるのがいちばん安全か。
- preview が無いとき、その理由を user にどう伝えるのがよいか。
