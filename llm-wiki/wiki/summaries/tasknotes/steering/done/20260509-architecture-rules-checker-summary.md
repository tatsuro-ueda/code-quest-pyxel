---
source: raw/tasknotes/steering/done/20260509-architecture-rules-checker.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 architecture_rules.yml checker 初版 Summary Draft

## summary

この note は、`architecture_rules.yml` を読む初版 checker を warning-only で立ち上げた記録です。`deterministic` rule だけを JSON で返し、`llm_assisted` と `manual` は skip として残す最初の実装線を引きました。

## key_points

- `tools/check_architecture_rules.py` と `test/test_architecture_rules_checker.py` を新設し、checker 実装と回帰 test を用意した。
- `docs/architecture_rules.yml` 側には `suggested_actions` を追加し、warning の意味づけを強めた。
- warning-only として開始し、CI の強制力より機械可読な観測を先に優先した。

## important_quotes

- "`warning-only`"
- "`deterministic` だけ実行"

## open_questions

- どの warning から fail 条件へ昇格させると効果が高いか。
- skip 扱いの `llm_assisted` / `manual` rule を downstream tool へどう見せるべきか。
