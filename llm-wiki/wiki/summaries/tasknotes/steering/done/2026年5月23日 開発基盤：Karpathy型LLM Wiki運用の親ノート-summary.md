---
source: raw/tasknotes/steering/done/2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月23日 開発基盤：Karpathy型LLM Wiki運用の親ノート Summary Draft

## summary

この note は、Karpathy 型 LLM Wiki 運用の親ルートを `setup -> ingest -> query -> health-check` に固定した親ノートです。初回 1 周を回す main route と、batch/schema の later note を分けて、次セッションの迷いを減らすことが主目的でした。

## key_points

- child `01-04` を main route とし、最初の health-check までの順序を固定した。
- batch と schema は初回 1 周の後段へ回し、main route から分離した。
- 親 note は route と done 条件だけを持ち、実作業は child note へ寄せる構造にした。

## important_quotes

- "`setup -> ingest -> query -> health-check`"
- "`child `01-04``"

## open_questions

- later note 化した batch/schema を、どの段階で main route に近づけてよいか。
- query saved answer と health-check の done 条件を、将来どこまで formalize するべきか。
