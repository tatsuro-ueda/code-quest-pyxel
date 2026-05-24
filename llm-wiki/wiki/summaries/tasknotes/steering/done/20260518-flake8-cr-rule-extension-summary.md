---
source: raw/tasknotes/steering/done/20260518-flake8-cr-rule-extension.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月18日 flake8-cr に構造化リファクタ誘導ルールを追加（タスク B） Summary Draft

## summary

この note は、flake8-cr に「step list only」系の構造化リファクタ誘導ルール CR204 を足した記録です。Task A で人がやった望ましい形を linter へ落とし込み、後続の scene 掃除を機械支援できるようにしました。

## key_points

- `_step_list_only.py` 相当の検出ロジックと test を dotfiles 側へ追加した。
- public 関数だけを対象に、述語+private 呼び出し+return のステップ列を許可し、式直書きを違反にした。
- dotfiles commit/push まで完了し、後続 Task C のスコープを CR202 残り 27 件へ絞った。

## important_quotes

- "`ステップ列のみの public 関数`"
- "`CR204`"

## open_questions

- CR204 の誤検出が増えた時、閾値導入とルール緩和のどちらが先に必要か。
- step list only ルールを、今後 tools や runtime にも同じ強さで適用すべきか。
