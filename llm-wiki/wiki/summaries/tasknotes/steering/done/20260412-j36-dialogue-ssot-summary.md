---
source: raw/tasknotes/steering/done/20260412-j36-dialogue-ssot.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 J36 セリフデータSSoT一方通行化 Summary Draft

## summary

この tasknote は、dialogue だけが `src/dialogue_data.py` 直書きで残っていた状態を、`assets/dialogue.yaml -> tools/gen_data.py -> src/generated/dialogue.py -> src/game_data.py` の一方向へ寄せ、互換レイヤーと `main.py` 同期まで含めて既存動作を壊さず SSoT 化した記録です。TDD で未実装箇所を先に fail させ、dialogue データの正本を repo 全体の data pipeline に戻しました。

## key_points

- 深層的目的は、セリフの元データを 1 か所にまとめることだった。
- `assets/dialogue.yaml` を原本にし、dialogue も他データと同じ YAML -> generated の pipeline に寄せた。
- `tools/gen_data.py` に `dialogue` target を追加し、`src/generated/dialogue.py` に `DIALOGUE_JA` と `DIALOGUE_EN` を生成するようにした。
- `src/game_data.py` に `load_dialogue()` を追加し、dialogue 取得の loader 境界を明示した。
- `src/dialogue_data.py` は辞書本体を持たず、generated 由来データを公開する薄い互換レイヤーにした。
- `tools/sync_main_data.py` を拡張し、`main.py` の dialogue 節も generated data と同期するようにした。
- Red test で `dialogue` target 未登録、`load_dialogue()` 未実装、`build_inlined_dialogue_section()` 未実装を先に落としてから埋めた。

## important_quotes

- "セリフの元データを1か所にまとめる"
- "SSoT一方通行、hookでガードレールが効く"
- "main.py は単一ファイル版を別途同期しているため、src/dialogue_data.py だけ直しても足りない"

## open_questions

- dialogue 以外の narrative data も同じ粒度で YAML 正本化していくか。
- `tools/test_headless.py` の不安定さを別 guardrail tasknote として formalize するか。
- 将来 `src.dialogue_data.py` の互換レイヤーをどこまで薄くできるか。
