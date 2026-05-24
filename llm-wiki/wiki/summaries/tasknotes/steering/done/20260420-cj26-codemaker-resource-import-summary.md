---
source: raw/tasknotes/steering/done/20260420-cj26-codemaker-resource-import.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月20日 CJ26 Code Maker zip から resource だけを取り込めるようにする Summary Draft

## summary

この tasknote は、Code Maker で保存した zip を selector からゲームへ戻す入口を `resource だけを運ぶ import` として作り直した記録です。修正の中心は、zip 内の code を採用せず `my_resource.pyxres` だけを server staging と build candidate に渡す責務分離を入れ、selector、runtime server、build の 3 箇所で同じ契約を確認できるようにしたことでした。

## key_points

- selector には preview zip を持ち出す導線しかなく、Code Maker から戻す入口が欠けていた。
- zip の code は無視し、resource だけを opaque に運ぶ契約へ切り替えた。
- `codemaker_resource_store`、status/upload endpoint、hidden upload panel を追加し、import の役割を service / server / UI に分けた。
- `development_meta.json` に code/resource の両ハッシュと `uses_preview_code` / `uses_imported_resource` を記録するようにした。
- `ignored_code_entries` を test と curl の両方で確認し、zip 内 `main.py` を採用しない境界を固定した。

## important_quotes

- "zip の code を無視して resource だけを opaque に運ぶ"
- "selector は file picker、server は HTTP と rebuild trigger、service は zip 取り扱い、build は配布責務に限定できた。"
- "ignored_code_entries=["block-quest/main.py"]"

## open_questions

- resource import の説明を、子どもにも親にもどこまで見せるべきか。
- import 済み resource を current へ昇格するとき、どの追加 guardrail を必須にするべきか。
