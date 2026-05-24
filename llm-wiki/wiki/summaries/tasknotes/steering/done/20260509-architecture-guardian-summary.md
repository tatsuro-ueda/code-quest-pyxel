---
source: raw/tasknotes/steering/done/20260509-architecture-guardian.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 architecture guardian 自動修復ループ Summary Draft

## summary

この note は、architecture checker を `checker -> fixer -> recheck` の guardian loop へ発展させた記録です。最大 5 周まで自動修復し、直せないものは `NEEDS_HUMAN` で止めることで、守りと自動化の境界を明示しました。

## key_points

- `tools/check_architecture_rules.py` を強化し、schema validation、`--rule-id`、`--fail-on-warning`、expected/observed などを追加した。
- `tools/architecture_guardian.py` を新設し、自動修復ループと stop 条件を test 付きで実装した。
- guardian は commit せず working tree 差分を残す設計とし、人の最終確認責務を外さなかった。

## important_quotes

- "`自動修復ループ`"
- "`NEEDS_HUMAN`"

## open_questions

- 次にどの fixer を増やしても安全かを、どの基準で見極めるべきか。
- guardian の出力を local repair と CI fail のどちらへどこまで寄せるべきか。
