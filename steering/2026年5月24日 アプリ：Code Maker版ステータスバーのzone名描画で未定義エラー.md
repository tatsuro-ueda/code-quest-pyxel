---
status: open
priority: high
scheduled: 2026-05-24T04:12:33+00:00
dateCreated: 2026-05-24T04:12:33+00:00
dateModified: 2026-05-24T04:12:33+00:00
tags:
  - task
  - bugfix
  - codemaker
  - bundle
  - status-bar
---

# 2026年5月24日 アプリ：Code Maker版ステータスバーのzone名描画で未定義エラー

> 状態：① Journey 起票完了
> 次のゲート：（CC）bundle smoke に赤テストを足し、`runtime` alias 欠落を直す

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 子どもが Code Maker 版を開いた直後の map で落ちず、zone 名を自然に読める
> 補足：やらないこと status bar の全面改修や `.pyxres` 編集
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 例外は Code Maker bundle の draw 中に出る
   2. 💦 `status_bar.py` は `runtime` alias で zone を引く
   3. 💦 bundler header は `M` だけを定義する

2. Before
   1. 💦 Code Maker 版 map 描画で `runtime` 未定義エラーになる
   2. 💦 通常実行では再現せず bundle smoke も未検知
   3. ❌ もどかしい

3. After
   1. ✅ Code Maker bundle でも zone 名を描ける
   2. ✅ bundle smoke が alias 欠落を検知できる
   3. ❤️ 安心

4. 例外
   1. `runtime` 以外も落ちるなら bundler 規則を広く見直す

5. 境界条件
   1. bundler と bundle smoke だけを直す
   2. status bar の表示仕様は変えない

6. 委任度
   1. 🟢 root cause は特定済み
   2. 🟢 test追加と修正は CC で可
   3. 🔴 人判断なし

---

## 2) ユーザーストーリーマップ

> 委任度：🟢 root cause まで掘れているので、そのまま TDD で進められる
> 残る曖昧さ：なし

### 事前確認

- [x] tasknote確認済み:
  - [x] `steering/done/20260517 アプリ：battle-stale-spell-message.md`
- [x] skill・tool・MCP確認済み:
  - [x] `manage-tasknotes`
  - [x] `superpowers:systematic-debugging`
  - [x] `superpowers:test-driven-development`
  - [x] `pytest`
- [x] 永続的ドキュメント確認済み:
  - [x] `AGENTS.md`
  - [x] `docs/framework-rule.md`

### 本体

1. 現状 bundle source の `_resolve_zone_name()` 出力を固定する
2. `test/test_codemaker_bundle_smoke.py` に赤テストを足す
3. `tools/codemaker_bundler.py` で module import alias を補強する
4. targeted pytest で smoke を緑に戻す
5. 必要なら全体 pytest を回して回帰を確認する

---

## 3) Gherkin（完了条件）

> 委任度：🟢 Design と実装まで CC が続けて進められる
> 残る曖昧さ：なし

### シナリオ一覧

- [ ] シナリオ1：Code Maker bundle でも zone 名解決で落ちない

1. 🧱 bundle を exec した module に `StatusBar` と `get_zone` が載っている
2. 🎬 fake game と fake player で `_resolve_zone_name()` を呼ぶ
3. ✅ `NameError` にならず zone 名文字列を返す

```gherkin
Given Code Maker bundle を build_bundled_source() から生成できる
And bundle を exec した module に StatusBar と get_zone が載っている
When fake game と fake player で StatusBar._resolve_zone_name() を呼ぶ
Then runtime 未定義の NameError は起きない
And zone 名の文字列が返る
```

- [ ] シナリオ2：既存の M alias 経路は壊さない

1. 🧱 既存 bundle smoke は `M` alias 前提で通っている
2. 🎬 `runtime` alias 対応を追加する
3. ✅ 既存の `M` 経路もそのまま通る

```gherkin
Given 既存 bundle smoke は M alias 前提で通っている
When runtime alias にも対応するよう bundler を修正する
Then import src.runtime.main_runtime as M の既存回帰は壊れない
And test/test_codemaker_bundle_smoke.py が green になる
```

---

## 4) Design（どうやるか）

### 責務分担概要

| 親ディレクトリ | 責務概要 |
| --- | --- |
| `tools/` | Code Maker bundle の import 除去と alias 変換を担う |
| `test/` | bundle exec と zone 名解決の回帰を固定する |
| `src/shared/ui/` | status bar 本体。今回は仕様変更しない |

### 責務分担概要図

```mermaid
flowchart TD
    A[status_bar.py<br/>runtime alias を参照] --> B[codemaker_bundler.py<br/>local import を strip]
    B --> C[bundle single file<br/>runtime binding 欠落]
    C --> D[test_codemaker_bundle_smoke.py<br/>赤テスト追加]
    D --> E[bundler 修正]
    E --> F[targeted pytest]
```

### 責務分担詳細

- `test/test_codemaker_bundle_smoke.py` （➕：status bar の zone 名経路を回帰テストに加える）
- `tools/codemaker_bundler.py` （✏️：module import alias の rewrite を補強する）
- `src/shared/ui/status_bar.py` （❌：今回は表示仕様を変えない）

### 【参照】

- Steering: `steering/done/20260517 アプリ：battle-stale-spell-message.md`
- Architecture: `AGENTS.md`
- UXPolicy: `docs/framework-rule.md`

### 変更範囲

- やること:
  - bundle smoke に zone 名経路の赤テストを追加する
  - bundler の module import alias を直す
- やらないこと:
  - status bar の見た目変更
  - runtime scene の仕様変更
  - `.pyxres` の編集

### 検証

- 検証コマンド:
  - `python -m pytest test/test_codemaker_bundle_smoke.py -q`
  - `python -m pytest test/ -q`
- 成功条件:
  - 新規 smoke が通る
  - 全体 pytest でも回帰が出ない
- 未実施時の扱い:
  - 全体 pytest 未実施なら done にしない

---

## 5) Tasklist

- [ ] bundle source の `_resolve_zone_name()` 現状出力を記録する
- [ ] `test/test_codemaker_bundle_smoke.py` に赤テストを追加する
- [ ] `tools/codemaker_bundler.py` を最小差分で修正する
- [ ] targeted pytest を通す
- [ ] 必要なら全体 pytest を通す

---

## 6) 作業ログ

- 2026-05-24 04:12: traceback と bundle source を照合し、`runtime` binding 欠落を root cause として記録した
- 2026-05-24 04:12: 本 tasknote を起票し、TDD 順で進める手順を固定した

## 7) 評価と成果物

> 評価：🟡 起票は完了。実装と検証はこれから。

### 成果物

- `steering/2026年5月24日 アプリ：Code Maker版ステータスバーのzone名描画で未定義エラー.md`
- root cause 要約：bundle された `_resolve_zone_name()` に `runtime` binding が残っていない

---

## 8) Discussion

### 懸念事項

- `runtime` 以外の module alias でも同じ欠落が起きる可能性がある
- 今回は status bar 経路だけを固定し、横展開は修正後の bundle source を見て判断する

### 残課題のルール化

#### 残課題1: module import alias 全般の横展開確認

- 背景: 今見えている実害は `runtime` だけだが、同種の alias が他にもあるかもしれない
- 判断: 本ノートの実装後に再判定

---

## 9) Closing

- 状態: open
- 次のゲート: （CC）bundle smoke に赤テストを足す
- close 条件:
  - [ ] new regression test が追加されている
  - [ ] bundle smoke が green
  - [ ] 全体 pytest の結果が note に反映されている

---

## 10) 参考資料

- 関連コード：`src/shared/ui/status_bar.py`
- 関連コード：`tools/codemaker_bundler.py`
- 関連テスト：`test/test_codemaker_bundle_smoke.py`
