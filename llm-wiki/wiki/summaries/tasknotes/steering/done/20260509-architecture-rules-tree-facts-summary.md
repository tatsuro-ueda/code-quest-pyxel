---
source: raw/tasknotes/steering/done/20260509-architecture-rules-tree-facts.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 architecture_rules facts を木構造へ再編 Summary Draft

## summary

この note は、`architecture_rules.yml` の facts を tree-first 構造へ再編し、checker / guardian / test fixture を新 schema に追従させた記録です。repo の地図を人にも AI にも読みやすくしつつ、検査責務との分離も強めました。

## key_points

- `facts` を tree-first へ組み替え、`flows` / `entry_points` / `runbooks` を横断情報として分離した。
- checker は tree node lookup、guardian は tree node / entry_points 更新へ追従し、fixture も新 schema 前提へ更新した。
- `赤テスト -> YAML 再編 -> checker -> guardian -> full verify` の順序が安全だったと記録した。

## important_quotes

- "`tree-first`"
- "`説明責務と検査責務を混ぜない`"

## open_questions

- tree-first schema の上で、`llm_assisted` / `manual` coverage を次にどこまで増やすべきか。
- tree が豊かになった後も、人向け派生 docs をどこまで残すべきか。
