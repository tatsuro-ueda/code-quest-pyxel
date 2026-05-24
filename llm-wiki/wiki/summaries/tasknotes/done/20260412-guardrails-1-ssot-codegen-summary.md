---
source: raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 ガードレール(1) SSoT + Codegen基盤 Summary Draft

## summary

この tasknote は、ゲームデータが複数箇所へ散在して update 漏れを起こす構造を断つために、YAML を正本にし、`tools/gen_data.py` から `src/generated/*.py` を生成し、`src/game_data.py` を loader 境界にする基盤を入れた記録です。狙いは「AI が全部の辞書を手で合わせる」運用をやめ、1 箇所編集と再生成で一貫性を保つ structural guardrail を作ることでした。

## key_points

- 深層的目的は、データ散在による不整合を構造的に防ぐことだった。
- 編集入口を `assets/*.yaml` に寄せ、6 種のデータを 1 箇所ずつ管理する形に変えた。
- `tools/gen_data.py` が `src/generated/*.py` を生成する codegen lane を追加した。
- `src/game_data.py` を generated data の loader 境界として置いた。
- `Makefile` に `gen` と `build` ターゲットを加え、再生成と build の通り道を固定した。
- hook 実装は別 task に切り分け、まず SSoT + codegen の基盤だけを先に通した。

## important_quotes

- "データ散在による不整合を構造的に防ぐ。"
- "assets/spells.yamlを1箇所編集"
- "全参照が自動で一貫更新"

## open_questions

- generated code をどこまで再生成前提で守り、どこから direct edit を禁止するか。
- `gen` 実行忘れを防ぐ hook や CI を後続 guardrail としてどこまで強制するか。
- この基盤を test pinning や packaging 系 tasknote とまとめて 1 本の guardrail lane にするか。
