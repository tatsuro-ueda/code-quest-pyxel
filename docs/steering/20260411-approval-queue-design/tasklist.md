# Tasklist: Approval Queue（承認キュー — 2版ビルド方式）

- 設計書: [`../20260411-approval-queue-design.md`](../20260411-approval-queue-design.md)
- status: done

---

## Phase 1: selector.html テンプレート

- [x] 1-1. `templates/selector.html` を作成する
  - おためしばん / もとのままばん の2カード
  - `{{CHANGE_LIST}}` プレースホルダ（ビルド時にpreview_meta.jsonから注入）
  - ひらがな表記、sans-serifフォント、スマホ対応
  - 既存 wrapper.html のスタイルポリシー（黒背景、全画面iframe）を踏襲

## Phase 2: --preview フラグ

- [x] 2-1. テスト: `--preview` で2版ビルドされる（Red）
  - main_preview.py が存在するとき → pyxel.html + pyxel-preview.html + index.html（selector）が生成される
- [x] 2-2. テスト: `--preview` で main_preview.py がないときエラー（Red）
- [x] 2-3. テスト: preview_meta.json の内容が selector.html に注入される（Red）
- [x] 2-4. `build_web_release.py` に `--preview` フラグを実装する（Green）
  - main.py → pyxel.html（もとのまま版）
  - main_preview.py → pyxel-preview.html（おためし版）
  - preview_meta.json + selector.html → index.html
- [x] 2-5. テスト: `--preview` なしは既存動作と同じ（回帰テスト）

## Phase 3: --promote コマンド

- [x] 3-1. テスト: `--promote preview` でおためし版が昇格する（Red→Green）
  - main_preview.py → main.py にリネーム
  - preview_meta.json を削除
- [x] 3-2. テスト: `--promote current` でもとのまま版が維持される（Red→Green）
  - main_preview.py を削除
  - preview_meta.json を削除
- [x] 3-3. `build_web_release.py` に `--promote` コマンドを実装する（Green）

---

## 実装後の振り返り

- 実装完了日: 2026-04-11
- 計画と実績の差分: Phase 2と3のテスト・実装を同時に書いた（テストが先に全部書けたため）。Red→Greenの間隔が短い
- 変更ファイル:
  - `templates/selector.html` — 新規（選択ページテンプレート）
  - `tools/build_web_release.py` — `generate_selector`, `validate_preview_files`, `promote`, `build_preview_release` 追加 + argparse CLI
  - `test/test_build_web_release.py` — 新規（5テスト）
- main.py への変更: なし（設計通り）
- 全139テストGreen、回帰なし
