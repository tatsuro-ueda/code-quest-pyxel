---
source: raw/knowledge/docs/framework-rule.md
source_type: knowledge
status: active
last_ingested: 2026-05-23
size_class: medium
---

# コーディング原則

## TL;DR

この source は「コーディング原則」を扱う markdown で、主要トピックは 1. 正本を一つにする（SSoT / Single Source of Truth）、2. 本番の通り道を必ず通す（Golden Path Test / End-to-End Smoke Test）、3. Migration Safety、4. No Silent Failure です。データや状態の「正しい置き場所」を一つに決め、他は必ずそこを経由して参照する。

## 主要トピック

- 1. 正本を一つにする（SSoT / Single Source of Truth）
- 2. 本番の通り道を必ず通す（Golden Path Test / End-to-End Smoke Test）
- 3. Migration Safety
- 4. No Silent Failure
- 依存方向
- 補足：学校の劇で例えると
- 1 フレームの流れ
- M1-1. Pyxel API 使用規約
- 描画系 API（`blt / bltm / text / line / rect / rectb / circ / circb / cls / pset` 等）
- 読み取り系 API（`pyxel.tilemaps[n].pget`, `pyxel.images[n].pget`）
- 入力系 API（`pyxel.btn / btnp`）
- 描画命令の制限
- M1-2. 入力規約
- 禁止
- M1-3. View の描画範囲
- 検証の目安
- M2-1. View 責務
- Viewの役割
- Viewでやってよいこと
- Viewで禁止すること
- Viewの原則
- M2-2. ViewModel / RenderData 規約
- View は Model を直接受け取らない
- RenderData は「解釈済み」にする
- 検証の目安
- M3-1. Presenter 責務
- Presenterの役割
- Presenterでやってよいこと
- Presenterで禁止すること
- Presenterの分割
- M3-2. Scene 規約
- Scene の責務
- Sceneで禁止
- つまり
- Scene interface を統一
- M3-3. コマンド規約
- 理由
- 検証の目安
- M4-1. Model 責務
- Modelの役割
- Modelでやってよいこと
- Modelで禁止すること
- Modelの形
- M4-2. Service 規約
- Service の分類を分ける
- Service に状態を持たせる基準
- M4-3. GameState 規約
- GameState に入れるもの
- GameState に入れないもの
- `Game` クラス削除方針
- M4-3 段階移行ステータス（2026-05-05 改訂）
- M4-4. PlayerModel と GameState 圧縮（本プロジェクト適用）
- Level 1: scene-local Model にルールを引き上げる
- Level 2: `PlayerModel` を新設し、`player` dict を吸収する
- Level 3: Scene 横断かつ player 以外のルールは Domain Support Service に残す
- GameState の圧縮（目標形）
- GameState から出すもの
- 検証の目安
- M5-1. 命名規約
- ファイル命名
- クラス命名
- メソッド命名
- M5-2. テスト規約
- 一番大事な優先順位
- Presenter テストで見るもの
- 禁止テスト
- M5-3. AI 向けガードレール文面
- AI 実装ルール例
- 文書 2 層構造（2026-05-05 改訂）
- 検証の目安
- 結論1
- 結論2
- 結論3
- 進める順序
- 旧章番号との対応（本書き換え 2026-04-24 時点）

## キーワード

- framework-rule
- コーディング原則
- 1. 正本を一つにする（SSoT / Single Source of Truth）
- 2. 本番の通り道を必ず通す（Golden Path Test / End-to-End Smoke Test）
- 3. Migration Safety
- 4. No Silent Failure
- 依存方向
- 補足：学校の劇で例えると

## 注意点

- 見出し抽出ベースの summary なので、細かな根拠は raw を参照する
