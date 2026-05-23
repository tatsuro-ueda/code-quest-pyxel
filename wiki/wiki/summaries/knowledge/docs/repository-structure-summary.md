---
source: raw/knowledge/docs/repository-structure.md
source_type: knowledge
status: active
last_ingested: 2026-05-23
size_class: medium
---

# リポジトリ構造定義書

## TL;DR

この source は「リポジトリ構造定義書」を扱う markdown で、主要トピックは 1. 目的、2. 設計原則、3. 全体構造、3.5 build の起動方法（runbook） です。この文書は「どの file / 関数が何を担当するか」を固定する責務分担表である。`docs` と `code` がずれたら **未実装 / バグ / 仕様ずれ** として扱い、コードではなくこの文書を正本とする（AI が読める分担表の維持は [CJ37](customer-journeys.md) 「責務が曖昧で直すほど別の所が壊れる」のガードレール）。

## 主要トピック

- 1. 目的
- 2. 設計原則
- 3. 全体構造
- 3.5 build の起動方法（runbook）
- 3.5.1 dist/code-maker.zip だけを再生成する
- 3.5.2 dist/ 配下の全 release artifacts を再生成する
- 3.5.3 BGM / pyxres / view / scene を変更したときの順序
- 3.5.4 よくある落とし穴
- 4. ディレクトリ詳細
- 4.1 `src/runtime/app.py`（**実装の窓口**）
- 4.2 `src/game_data.py`
- 4.3 削除済み legacy runtime helper
- 4.4 `src/scenes/`（11 scene、MVP パターン）
- 4.5 `src/shared/services/`（18 サービス）
- 4.5.1 `src/shared/state/`（M4-4 で新設）
- 4.6 `src/shared/ui/`
- 4.7 `src/shared/constants/`
- 4.8 `src/shared/assets/`
- 4.9 `src/generated/`（自動生成、手で触らない）
- 4.10 `src/runtime/`（**実行入口**）
- 5. その他のトップレベル
- 5.1 `assets/`（人が直す正本）
- 5.2 `tools/`
- 5.3 `test/`
- 5.4 `templates/`
- 5.5 `dist/`
- 5.6 `docs/` と上位文書
- 6. 依存関係のルール
- 6.1 レイヤー依存
- 6.2 循環依存の禁止
- 7. 責務の線引き（書かないべきこと）
- 8. 使用ライブラリ
- 9. 現状と残タスク（J53 / M4 / M5）

## キーワード

- repository-structure
- リポジトリ構造定義書
- 1. 目的
- 2. 設計原則
- 3. 全体構造
- 3.5 build の起動方法（runbook）
- 3.5.1 dist/code-maker.zip だけを再生成する
- 3.5.2 dist/ 配下の全 release artifacts を再生成する

## 注意点

- 見出し抽出ベースの summary なので、細かな根拠は raw を参照する
