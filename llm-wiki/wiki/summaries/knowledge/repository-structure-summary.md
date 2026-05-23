---
source: raw/knowledge/docs/repository-structure.md
source_type: doc
status: active
origin:
  - docs/repository-structure.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: large
---

# Repository Structure Summary

## TL;DR

この source は、repo 内の責務分担表であり `どこを正本とし、どの file が何を担当するか` を固定する。中心は `src/ と assets/ を SSoT にする` `runtime 入口は src/runtime/app.py::Game に一本化する` `scenes/shared/services/shared/state の役割を分ける` `build runbook と dependency rule を迷わない形で残す` である。

## 主要トピック

- docs と code がずれたら code でなく仕様ずれとして扱う
- runtime root、GameState、SceneManager、DebugService、PlayerModel の現在地を明示する
- scenes は MVP、services は scene 横断ロジック、state は dataclass rule holder として切る
- assets、generated、tools、dist、docs の責務を明文化する
- build_web_release と build_codemaker の runbook と落とし穴をまとめる
- layer dependency と循環依存禁止を文書で固定する

## 深い洞察

- この doc 自体が AI 向け guardrail であり、責務の曖昧さを減らす operating map になっている
- `どこを直すか` を決める情報が明文化されていることが、AI 修正の安全性を上げる
- pyxres、dist、runtime entry の扱いが build / packaging / debugging を分ける基準になる

## キーワード

- repository-structure
- responsibility map
- runtime root
- build runbook
- services
- GameState
- dependency rules

## 注意点

- 行数や scene 数などは時点情報なので、変更後は stale 化しやすい
- framework-rule と AGENTS.md と合わせて読まないと、 why より where の説明に寄りやすい
