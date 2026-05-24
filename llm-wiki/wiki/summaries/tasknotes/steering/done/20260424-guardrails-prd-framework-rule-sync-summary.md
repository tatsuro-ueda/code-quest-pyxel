---
source: raw/tasknotes/steering/done/20260424-guardrails-prd-framework-rule-sync.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月24日 product-requirements-guardrails.md を現状と framework-rule.md に同期する Summary Draft

## summary

この tasknote は、`docs/product-requirements-guardrails.md` を J53 後の現状と `framework-rule.md` の M1〜M5 構造へ同期し直した記録です。修正の中心は、古い `main.py` 前提や CJG 番号のずれを解消し、`customer-journeys.md` を正本に据えたまま PRD 側へ新 `CJG37 = framework-rule 対応` と `CJG44 = リソース境界` を整理し、G16〜G20 の guardrail 行まで含めて docs の土台をそろえたことでした。

## key_points

- town refactor を進める中で、guardrails PRD の現状表、`main.py` 表現、CJG 割り当て、参照リンクが stale だと分かった。
- PRD の同期にスコープを絞り、hook / lint / test の実装は別 note に切り分けた。
- `framework-rule.md` を M1〜M5 の 5 メタ構造へ寄せ、PRD 側もその親 Rule と Why / Scenario / link 構成へ合わせた。
- 旧 `CJG37` を `CJG44 = リソース境界` として再配置し、新 `CJG37` を framework-rule 対応の節として新設した。
- G16〜G20 を未実装 guardrail 行として追加し、リンク切れと孤児 CJG 参照が 0 件になるまで grep で確認した。
- `python -m pytest test/ -q` 233 passed, 2 skipped と docs commit 2 本の main 到達を確認して閉じた。

## important_quotes

- "customer-journeys.md が正本。PRD はそれに追従する。"
- "M1〜M5 の 5 メタルール"
- "旧 `CJG37` 内容は `CJG44` = リソース境界 として独立番号で再配置"

## open_questions

- G16〜G20 の未実装 guardrail を、どの順で hook / lint / test へ落とすべきか。
- 他 PRD へも同じ M1〜M5 / CJG 再整理をどこまで波及させるべきか。
