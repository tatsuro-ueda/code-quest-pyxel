---
source: raw/tasknotes/done/20260412-g15-test-pinning.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 G15 テストコードによる挙動固定 Summary Draft

## summary

この tasknote は、pytest 系が壊れたままだと AI 改変の regressions を即検知できないため、まず test lane 自体を復旧して「壊れたらすぐ分かる」状態を取り戻した記録です。対応は `simple_yaml` 削除後の import 漏れと stale な test fixture 参照を直すことに絞られ、既存 130 テストの全通過によって挙動固定の guardrail を回復させました。

## key_points

- 壊れていた 3 件の import/test failure の主因は、削除済み `simple_yaml` 参照と stale な fixture path だった。
- `src/game_data.py` と `tools/gen_data.py` を `yaml.safe_load` ベースへ置き換えた。
- `test/test_game_data.py` の削除済み `dialogue.yaml` 参照を `enemies.yaml` に修正した。
- 既存テストだけで G15 の 4 シナリオはすでにカバーされていたため、新規テスト追加は不要と判断した。
- 全 130 テスト通過によって、AI 改変後に failure signal がすぐ返る状態を回復した。
- 反省点として、dependency 削除やファイル移動の影響が長期間放置されないよう、CI や migration guard の必要性が明確になった。

## important_quotes

- "AIの改変で壊れたらテストが即座に教えてくれる状態にする"
- "全シナリオが既存テストでカバー済み。追加不要。"
- "テスト追加は不要。壊れたテストを直すだけで「挙動固定」が機能する状態になった。"

## open_questions

- broken test lane を長期間放置しないために、CI や定期 test gate をどこまで入れるか。
- dependency 削除やファイル移動の影響を、pytest 実行前に検知する migration guard を足すか。
- この note を structural guardrail 系の tasknote と同じ lane でまとめるか。
