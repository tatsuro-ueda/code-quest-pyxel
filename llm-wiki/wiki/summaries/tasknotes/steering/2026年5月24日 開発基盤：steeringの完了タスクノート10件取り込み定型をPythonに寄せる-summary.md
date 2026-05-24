---
source: raw/tasknotes/steering/2026年5月24日 開発基盤：steeringの完了タスクノート10件取り込み定型をPythonに寄せる.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：steeringの完了タスクノート10件取り込み定型をPythonに寄せる Summary Draft

## summary

この note は、`steering/done` の oldest 10 件 batch ingest に残っていた定型作業を Python helper に寄せ、selection・scaffold・related page shortlist を決定的に並べる方針を固めた記録です。意味づけは LLM に残しつつ、batch 前処理だけを機械化しました。

## key_points

- 1 本ずつの source helper だけでは batch ingest の定型コストがまだ残る
- Python に寄せるのは `決まった形に並べる仕事` までで、意味づけは LLM に残す
- related page 候補出しは完全自動確定ではなく、LLM review 前提の shortlist 生成として扱う

## important_quotes

- "Python に寄せるのは `決まった形に並べる仕事` までで、意味づけは LLM に残す"
- "shortlist の scoring は `ingest-log` 履歴 token と text overlap の弱い合算に留め、過剰な意味づけを避ける"

## open_questions

- なし。
