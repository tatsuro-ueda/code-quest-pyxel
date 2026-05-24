---
source: raw/tasknotes/steering/done/20260508-architecture-rules-yaml.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月8日 architecture.md を architecture_rules.yml に段階移行 Summary Draft

## summary

この note は、`docs/architecture_rules.yml` を AI と人の共通正本として立ち上げた初版実装記録です。`meta / facts / validation_rules` の 3 層構造で、repo の責務説明と warning-only checker 前提の rule 定義を同じ YAML に収めました。

## key_points

- sample ではなく実 schema へ置き換え、`intended_replacement_for`、audiences、facts、validation rules を持つ live YAML にした。
- `deterministic` / `llm_assisted` / `manual` の enforcement mode を持つ warning-only rule set として始めた。
- full yaml、coverage spot check、CJ link、scene_to_cj map、pytest まで通し、初版の実用性を確認した。

## important_quotes

- "`facts`"
- "`validation_rules`"

## open_questions

- warning-only から先に harden すべき rule はどれか。
- live docs と YAML の役割分担を、どの時点でさらに YAML 側へ寄せるべきか。
