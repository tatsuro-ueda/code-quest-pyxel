---
source: raw/tasknotes/steering/done/20260412-guardrails-2-hooks.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 ガードレール(2) Hooks設計・実装 Summary Draft

## summary

この tasknote は、AI が壊しやすい編集経路を runtime の外側で物理的に閉じるために、`.claude/settings.json` と `tools/hooks/*.sh` で hook guard を入れた記録です。中心は `src/generated/*.py` の直編集、`.pyxres` の直編集、`src.generated` の直 import をその場で止め、YAML 正本や `src/game_data.py` loader へ誘導することでした。

## key_points

- 深層的目的は、AI が壊せるパスを物理的に封じることだった。
- hook の共有定義を `.claude/settings.json` に置き、`settings.local.json` とは分けて管理する方針を取った。
- 初回リリースでは G1、G2、G3、G14 を対象にし、generated 直編集、`.pyxres` 直編集、generated 直 import を block した。
- `tools/hooks/guard_post_gen.sh` で `assets/*.yaml` 編集後に codegen を自動実行する経路を用意した。
- デバッグ用に `CLAUDE_GUARD_BYPASS=1` を設け、hook を一時的に無効化できるようにした。
- G5、G7 の lint warning 系は誤検知リスクを考えて初回には含めず、後日に分離した。

## important_quotes

- "AIが壊せるパスを物理的に封じる。"
- "初回リリース: G1, G2, G3, G14"
- "このファイルは生成物です。assets/*.yaml を編集してください"

## open_questions

- G5、G7 の lint warning hook をいつ追加するか。
- `tools/gen_data.py` が未配置だった当時の前提を、現在の codegen 実装とどう突き合わせるか。
- shared `.claude/settings.json` と repo guardrail の責務境界をどこまで固定するか。
