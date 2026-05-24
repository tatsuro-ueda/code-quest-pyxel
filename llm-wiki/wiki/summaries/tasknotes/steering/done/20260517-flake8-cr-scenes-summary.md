---
source: raw/tasknotes/steering/done/20260517-flake8-cr-scenes.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月17日 src/scenes に flake8-cr を適用して直す Summary Draft

## summary

この note は、`src/scenes/` へ flake8-cr を初適用し、違反の全体像を洗ってタスク A/B/C へ分解した親記録です。最初から全部を直そうとせず、CR202 大物、ルール拡張、残 27 件という実施単位へ切ったことが主眼でした。

## key_points

- 初回スキャンで CR502、CR203、E501、CR601、CR201 などの大量違反を件数付きで把握した。
- CR202 大物 30 件は別 tasknote へ切り出し、親 note は全体 inventory とルート固定を担った。
- public→private 委譲や述語変数化など、後続タスクで再利用する機械的パターンを整理した。

## important_quotes

- "`CR202（関数 20 行超）残 30 件`"
- "`述語変数で吸収`"

## open_questions

- lint を inventory で止める親 note と、実装子 note の切り分けを今後どこまで標準化するべきか。
- docstring / naming / structure 系違反の優先順を、次回はどこまで自動で決められるべきか。
