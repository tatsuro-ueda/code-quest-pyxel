---
source: raw/tasknotes/steering/done/20260505-architecture-md-decision.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 ARCHITECTURE.md 整備 vs AGENTS.md 単独運用の判定（M5-3） Summary Draft

## summary

この note は、M5-3 観点で repo 文書の入口を `AGENTS.md` -> `docs/architecture.md` -> `docs/framework-rule.md` の 2 層構造へ固定するための planning 記録です。AI 用最優先文書と人用詳細文書の役割分担、README 導線、static guard まで一式で定義しています。

## key_points

- AI 用は root `AGENTS.md`、人用詳細は `docs/architecture.md`、規約本体は `docs/framework-rule.md` と優先順位を固定した。
- `docs/repository-structure.md` を `docs/architecture.md` へ寄せる rename と、AGENTS 100 行制限を前提にした。
- README 導線と `test_cjg_framework_rule_guards.py` の guard まで含めて運用像を描いた。

## important_quotes

- "`AI 用 = `AGENTS.md``"
- "`2 層構造`"

## open_questions

- 人用詳細を将来さらに分割するなら、責務表と runbook のどちらから分けるべきか。
- `AGENTS.md` の 100 行 budget を今後も hard guard として維持すべきか。
