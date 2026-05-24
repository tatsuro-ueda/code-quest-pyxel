---
source: raw/tasknotes/steering/done/20260509-scene-mvp-boundary-deterministic-promotion.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 scene MVP boundary の deterministic 昇格 Summary Draft

## summary

この note は、`scene_mvp_boundary` rule を warning 読みではなく deterministic checker へ昇格した記録です。static に見える範囲だけを machine rule に上げ、人判断が残る部分には autofix を足さないままにしました。

## key_points

- `docs/architecture_rules.yml` の `scene_mvp_boundary` を deterministic 化した。
- `tools/check_architecture_rules.py` に `scene_static_boundary_checks` を追加した。
- real repo expectation と fixture warning test を checker test に追加した。

## important_quotes

- "`static に判定できる範囲だけで十分だった`"
- "`autofix を増やさなかった`"

## open_questions

- scene boundary の残る人判断部分を、どこまで checker へ寄せる価値があるか。
- pytest 側の static guard を checker 昇格候補として毎回どう見直すべきか。
