---
source: raw/tasknotes/steering/done/20260509-shared-boundary-deterministic-promotion.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 shared boundary の deterministic 昇格 Summary Draft

## summary

この note は、`shared_service_vs_state_boundary` rule を deterministic checker に上げた記録です。shared 層は配置と依存を静的に見ればかなり守れると判断し、legacy shim 再侵入も checker 側で拾えるようにしました。

## key_points

- `shared_service_vs_state_boundary` を deterministic 化し、`shared_directory_role_checks` を追加した。
- checker test に fixture warning を足し、legacy shim 再侵入 guard も checker 側へ昇格した。
- file move の autofix は誤爆コストが高いため warning 止まりにした。

## important_quotes

- "`shared boundary は「配置」と「依存」を静的に見れば十分`"
- "`warning で止める方が正しい`"

## open_questions

- shared 例外を追加した時、facts.tree と checker 期待をどの順で同期するべきか。
- service/state 境界のうち、今後さらに deterministic 化できる signal は何か。
