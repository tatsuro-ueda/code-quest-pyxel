---
source: raw/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月16日 J47 preview を新しい変更の受け皿に固定し選択ページ説明を自動化する Summary Draft

## summary

この tasknote は、preview-first 運用と selector 説明の Source of Truth を揃えるために、preview の change list を手書き metadata から build-owned な自動生成へ寄せた記録です。中心は、`main.py` と `main_preview.py` の差分から preview 説明を作り、`preview_meta.json` を build が再生成する中間成果物へ下げることで、手更新の説明を SoT から外したことでした。

## key_points

- docs では preview-first を採っていたが、実装は `top_changes.json` / `preview_meta.json` の手更新前提が残っていた。
- Red テストで、selector が手書き metadata を読んでいることを固定した。
- preview diff から change list を自動生成する方式へ切り替えた。
- `preview_meta.json` は人手管理ではなく、build-owned な中間成果物へ位置づけ直した。
- selector は生成済み metadata を読むだけにして、説明の SoT を build 側へ寄せた。
- preview build、全体 pytest、web compat で説明と実差分の一致を確認した。

## important_quotes

- "preview を遊ばせる比較導線と selector 説明の SoT がまた分離する。"
- "build-owned な中間成果物"
- "preview diff からの自動 change list 生成"

## open_questions

- preview の説明は、build がどこまで自動で持つべきか。
- current 側の変更説明も、同じ build-owned 方式へどこまで寄せるべきか。
