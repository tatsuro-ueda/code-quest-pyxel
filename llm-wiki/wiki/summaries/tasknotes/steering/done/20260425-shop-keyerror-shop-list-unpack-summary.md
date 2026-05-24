---
source: raw/tasknotes/steering/done/20260425-shop-keyerror-shop-list-unpack.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月25日 shop で KeyError：SHOPS 辞書形状の unpack 取りこぼし（さかのぼり） Summary Draft

## summary

この tasknote は、shop で `M.SHOPS` の古い辞書形状を前提にして落ちる KeyError と、menu 側の item use shim ずれを一緒に修復したさかのぼり記録です。修正の中心は、scene が raw generated shape を直読みせず `SHOP_LIST` と `item_use` service の経路へ戻るよう直し、同種バグを grep ガードと smoke test で防ぐ方針を残したことでした。

## key_points

- `src/scenes/shop/scene.py` は古い `M.SHOPS[idx]` 形状を前提にしており、`SHOP_LIST` へ戻す必要があった。
- `src/scenes/menu/scene.py` の `game.use_item(...)` も、scene 間で shim がずれていたため `item_use` service 経由へ直した。
- generated data の shape 変更に scene がどこで追従すべきかが曖昧で、SSoT 再エクスポートの運用不足が露出した。
- shop enter→purchase の integration 風 smoke test がなく、scene レベルの確認が不足していた。
- `generated/*.py` 直参照や存在しない shim 呼び出しを grep で止める案を M5 / AGENTS 候補へ返した。

## important_quotes

- "SSoT 再エクスポートの運用が scenes 側に明示されていない。"
- "「存在しないメソッド」が scene 間で混在"
- "`generated/*.py` を直接 import していないか"

## open_questions

- scene が raw generated shape へ依存しないことを、どの static guard で固定するべきか。
- shop〜item use〜save/load を headless で通す smoke test を、どこまで厚くするべきか。
