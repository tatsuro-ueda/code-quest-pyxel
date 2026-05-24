---
source: raw/tasknotes/steering/done/20260509-architecture-md-removal.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 docs/architecture.md 廃止と人用詳細の置き換え Summary Draft

## summary

この note は、live repo から `docs/architecture.md` を外し、`docs/repository-structure.md` を人用詳細の正へ戻した記録です。旧名が履歴には残ることを受け入れつつ、live docs / tests / guards の参照だけを整理しました。

## key_points

- `AGENTS.md`、`README.md`、`docs/framework-rule.md`、`docs/product-requirements-guardrails.md`、test の live 参照を `repository-structure.md` へ揃えた。
- `docs/architecture_rules.yml` の replacement target も新しい live 文書名に更新した。
- historical な `steering/done/` はそのまま残し、live docs と history docs の役割を分けた。

## important_quotes

- "`人用詳細の正`"
- "`historical な `steering/done/` は当時`"

## open_questions

- `repository-structure.md` の中を、将来 build runbook と責務表に分割する価値があるか。
- history docs に旧名が残ることを、grep 上でどう明示的に扱うべきか。
