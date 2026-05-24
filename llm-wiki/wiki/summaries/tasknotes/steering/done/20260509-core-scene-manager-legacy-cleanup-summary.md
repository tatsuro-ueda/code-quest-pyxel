---
source: raw/tasknotes/steering/done/20260509-core-scene-manager-legacy-cleanup.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 core scene_manager legacy 整理 Summary Draft

## summary

この note は、旧 `src/core/scene_manager.py` を live code から外し、shared state holder 前提へ揃えた整理記録です。test、manifest、docs、guard を同時に更新し、二重の SceneManager 名が並ぶ状態を解消しました。

## key_points

- `src/core/scene_manager.py` を削除し、live な SceneManager を shared 側へ一本化した。
- `test_scene_responsibilities` を shared `SceneManager` 前提へ更新した。
- manifest / architecture rules / docs と復活 guard も追従させた。

## important_quotes

- "`src/core/scene_manager.py` を削除した"
- "`shared state holder`"

## open_questions

- 旧 protocol helper や同名概念の残りを、どの順で棚卸しして消すべきか。
- runtime legacy cleanup と test 互換整理を今後どこまで同時実施に寄せるべきか。
