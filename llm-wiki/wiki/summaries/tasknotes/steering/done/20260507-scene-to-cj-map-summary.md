---
source: raw/tasknotes/steering/done/20260507-scene-to-cj-map.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月7日 scene ↔ CJ 対応表と影響範囲提示 CLI（C3） Summary Draft

## summary

この note は、scene / area の差分から関連 customer journey を即座に引ける CLI を追加した記録です。修正後に「この変更が誰のどの体験に触るか」を説明しやすくし、verify とは別の情報レーンを用意しています。

## key_points

- `tools/scene_to_cj.json` と `tools/scene_to_cj.py` を新設し、`--list` / `--since` / `--verify-only` の 3 モードを用意した。
- git diff から scene / area を抽出して、対応 CJ とカテゴリを表示する情報補助 tool として位置づけた。
- Makefile には入れず、`fail` 条件ではなく影響範囲可視化として扱うと判断した。

## important_quotes

- "`scene ↔ CJ 対応表`"
- "`対応表は粗版`"

## open_questions

- 手書き対応表の精度を、どのイベントやレビューで継続的に上げるべきか。
- この情報 lane のうち何を future guard / CI へ昇格させるべきか。
