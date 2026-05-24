---
source: raw/tasknotes/steering/done/20260425-tests-that-prevent-runtime-crashes.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月25日 落ちないことを保証するテスト群を docs/ 駆動で整備する Summary Draft

## summary

この tasknote は、新しく大きな crash harness を作る前に、既存の `test_cjg_*` 群が runtime crash prevention の観点をどこまで既にカバーしているかを棚卸しし、必要な部分だけ残して撤収した監査記録です。結論として、30 以上の test file と 65 件の再確認で主要観点は既にカバーされており、本 note は「不足」より「追跡漏れ」の整理を役割に変えました。

## key_points

- 起票時の `[ ]` 12 項目のうち、7 項目は既存テストで実質完了済み、5 項目は撤収判定になった。
- Phase F〜I で想定していた crash-prevention 観点は、すでに 30+ の `test_cjg_*.py` 群へ分散して実装されていた。
- 新しい共通ハーネスや統合 smoke を追加するより、既存テストの coverage map を整理する方が合理的だと判断した。
- 65 件 / 262 subtests の再確認で、カバー実績が green であることを確認した。
- 今後は新規バグを Phase B 形式の regression test として 1 ファイルずつ足す運用へ寄せる方針にした。

## important_quotes

- "「やり残し」よりも「カバー実績の追跡漏れ」を整理する役割が中心"
- "共通ハーネスや統合 smoke を新設する価値は薄い"
- "新規バグが発覚したら Phase B 形式で 1 ファイル regression test を追加"

## open_questions

- 既存 crash-prevention coverage の地図を、どの document で継続管理するべきか。
- 新しい実機 crash が出たとき、どの粒度で `test_cjg_*` へ吸収するべきか。
