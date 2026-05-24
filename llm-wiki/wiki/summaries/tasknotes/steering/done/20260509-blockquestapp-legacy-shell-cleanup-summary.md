---
source: raw/tasknotes/steering/done/20260509-blockquestapp-legacy-shell-cleanup.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 BlockQuestApp legacy shell 整理 Summary Draft

## summary

この note は、`BlockQuestApp` legacy shell を live runtime から外し、`src/app.py` を削除した整理記録です。bundle と manifest と docs を同時に見て、互換名を残すより「不要を実物確認して消す」方針へ寄せました。

## key_points

- `src/app.py` を削除し、runtime の live 入口をさらに単純化した。
- `tools/codemaker_manifest.txt` と `docs/architecture_rules.yml` から旧 shell 参照を外した。
- docs と guard test も `src/app.py` 不在を前提に更新し、再侵入を止めた。

## important_quotes

- "`src/app.py` を削除した"
- "`不要を実 bundle で確認して消す`"

## open_questions

- 残る legacy helper を消す前に、bundle 実行でどこまで互換経路を確かめるべきか。
- `core/scene_manager` 系 cleanup と runtime cleanup を、次はどこまで同時に進めるべきか。
