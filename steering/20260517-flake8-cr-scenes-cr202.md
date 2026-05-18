---
status: in-progress
priority: normal
scheduled: 2026-05-17T00:00:00.000+09:00
dateCreated: 2026-05-17T00:00:00.000+09:00
dateModified: 2026-05-18T00:00:00.000+09:00
tags:
  - task
  - lint
  - scenes
---

# 2026年5月17日 src/scenes の CR202 大物 3 件を AI で個別リファクタ（タスク A）

> 状態：④ Design
> 次のゲート：（ユーザー）Design を確認して承認するか直しの希望を伝える

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 機械的に直しにくい大物 3 関数を、責務が読み取れる単位まで AI 判断で分割する
> 補足：やらないこと 残り 27 件のリファクタ、SKILL.md 改訂、flake8-cr ルール改訂
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 親 `steering/done/20260517-flake8-cr-scenes.md` で CR202 以外の警告は解消済み
   2. 💦 残 30 件のうち 3 件は大物（92/89/79 行）で構造判断が要り、機械化前に AI で先行処理する

2. Before
   1. 💦 `_check_tile_events`(92), `_run_build_view_model`(89), `_run_update`(79) が責務混在で読みにくい
   2. ❌ もどかしい

3. After
   1. ✅ 大物 3 関数が全て 20 行以下に分割される
   2. ✅ pytest / make verify / make build がすべて緑
   3. ❤️ スッキリ

4. 例外
   1. 線形な計算（プレイヤー攻撃など）で乱数・副作用順を変える分割は行わない（対象 3 件は該当なし想定）

5. 境界条件
   1. 対象は上記 3 関数のみ。残り 27 件はタスク C で処理する
   2. 挙動は変えない（テスト緑を維持）
   3. リファクタ方針は SKILL.md ではなく flake8-cr ルール改訂を優先（B で対応、当タスクは個別判断）

6. 委任度
   1. 🟡 分割境界の最終判断は人と擦り合わせる -> OK
   2. 🟢 述語切り出し・private 切り出しの実装は CC のみで可
   3. 🔴 ロジックの本質を変える分割は人の判断が要る -> 聞いて下さい

---

## 2) ユーザーストーリーマップ

> 委任度：🟡 分割境界の最終判断はユーザー確認、機械的な実装と検証は CC のみで可
> 残る曖昧さ：`_check_tile_events` がタイル副作用順序に敏感かは、実コードと既存テストを読まないと確定しない

### 事前確認

- [x] tasknote確認済み: 
  - [x] 親 `steering/done/20260517-flake8-cr-scenes.md`
  - [x] 後続B `steering/20260518-flake8-cr-rule-extension.md`
  - [x] 後続C `steering/20260518-flake8-cr-scenes-rest27.md`
- [x] skill・tool・MCP確認済み: 
  - [x] `check-python-coding-guide` Skill
  - [x] `flake8-cr` / `pytest` / `make verify` / `make build`
- [x] 永続的ドキュメント確認済み: 
  - [x] `~/.claude/skills/check-python-coding-guide/SKILL.md`
  - [x] `docs/repository-structure.md`
  - [x] `docs/framework-rule.md`

### 本体

1. 👀 `flake8-cr src/scenes/explore/presenter.py` を実行し、CR202 対象 3 関数（102行目 `_run_update` / 189行目 `_run_build_view_model` / 288行目 `_check_tile_events`）と各長さ（79/89/92）を再確認する
2. 💦 3 関数の責務を読み、ステップ列・述語・private 切り出しの境界を仮置きする。副作用順序に敏感な `_check_tile_events` を優先して精査する
3. 🎬 1 関数ずつ、述語切り出し → private 切り出し → 早期 return の順で適用し、20 行以下まで分割する
4. ✅ 各分割ごとに `pytest` / `make verify` / `make build` が緑であることを確認し、差分は最小コミットで残す
5. 🎬 分割後の構造から、タスク B のルール候補（CR204 など）に渡す「望ましい構造」のメモを抽出する
6. ❤️ explore/presenter.py が責務単位で読めるようになり、A→B→C の連結が始められる

---

## 3) Gherkin（完了条件）

> 委任度：🟡 機械的に確認できるシナリオは CC のみで可、分割境界・本質変更は人の判断
> 残る曖昧さ：`_check_tile_events` の副作用順序の許容範囲は、実テスト結果を見ないと最終確定しない

### シナリオ一覧

- [ ] シナリオ1：対象 3 関数の長さが 20 行以下になる

1. 🧱 explore/presenter.py に CR202 の 3 関数（`_run_update` / `_run_build_view_model` / `_check_tile_events`）が違反として残っている
2. 🎬 CC が 1 関数ずつ責務を読み、述語切り出し → private 切り出し → 早期 return の順で分割する
3. ✅ `flake8-cr src/scenes/explore/presenter.py` の出力に 3 関数の CR202 警告が出ない

```gherkin
Given src/scenes/explore/presenter.py に `_run_update` (79行) / `_run_build_view_model` (89行) / `_check_tile_events` (92行) の3関数が存在し、CR202 違反として検出されている
When CC が責務を読み解き、述語切り出し・private 切り出し・早期 return を用いて 1 関数ずつ分割する
Then 3 関数とも docstring 除く本体が 20 行以下に収まる
And `flake8-cr src/scenes/explore/presenter.py` の出力に 3 関数の CR202 警告が出ない
```

- [ ] シナリオ2：分割の各ステップで挙動が壊れない

1. 🧱 main 相当の状態で `pytest` / `make verify` / `make build` がすべて緑
2. 🎬 CC が 1 関数ごとの分割直後に検証コマンドを走らせ、最小コミットで差分を残す
3. ✅ 同じ 3 コマンドが分割直後も緑で完走する

```gherkin
Given main 相当の状態で `pytest` / `make verify` / `make build` がすべて緑
When CC が 3 関数のいずれかを分割し、その分の差分を最小コミットとして残す
Then 同じ 3 コマンドが分割直後も緑で完走する
And いずれかが赤になった場合は、CC はその差分を作業ログに記録した上で分割を見直す
```

- [ ] シナリオ3：タスクB に渡すルール候補メモが出力される

1. 🧱 3 関数の分割が完了している
2. 🎬 CC が分割後の共通構造を箇条書きで抽出する
3. ✅ メモが Discussion セクションまたは別 tasknote に記入され、タスク B から参照できる

```gherkin
Given 3 関数とも 20 行以下に分割済みで、pytest / make verify / make build が緑
When CC が分割後の共通構造を箇条書きで抽出する
Then タスク B（`steering/20260518-flake8-cr-rule-extension.md`）の参考文献から参照できる位置にメモが置かれる
And メモには「述語呼び出し + private 呼び出し + return のステップ列」「early return パターン」など、機械検出に落とせる粒度の構造が並ぶ
```

- [ ] シナリオ4：分割境界に迷ったら CC は止まる

1. 🧱 CC が 3 関数のいずれかの分割境界を判断しようとしている
2. 🎬 複数の妥当な分割案を思いつき、責務分担の文脈だけでは選定の根拠が決まらない
3. ✅ CC は実装を止め、選択肢と論点を Discussion または会話に出してユーザー判断を仰ぐ

```gherkin
Given CC が 3 関数のいずれかを分割しようとしている
When 複数の妥当な分割案を思いつき、選定の根拠が責務分担の文脈だけでは決まらない
Then CC は分割を一旦止め、現状の選択肢と論点を Discussion または会話に出す
And ユーザーが境界を選んでから CC は実装に進む
```

- [ ] シナリオ5：ロジックの本質を変える分割は CC 単独で決めない

1. 🧱 CC が分割案を組み立てている
2. 🎬 分割によって呼び出し順・条件式の意味・ループ停止条件のいずれかが変わる疑いがある
3. ✅ CC はその案を採用せず、別案または現状維持を提示してユーザー判断を仰ぐ

```gherkin
Given CC が 3 関数のいずれかについて分割案を組み立てている
When 分割によって呼び出し順、条件分岐の意味、ループの停止条件のいずれかが変わる疑いがある
Then CC はその分割案を採用せず、別の分割案または現状維持を選択肢として提示する
And ユーザーが「変えてよい」と判断するまで実装を進めない
```

- [ ] シナリオ6：副作用順序に敏感な処理では順序を変える分割を採用しない

1. 🧱 `_check_tile_events` のようにタイル副作用順序に敏感な関数を扱っている
2. 🎬 分割によってタイル更新やイベント発火の順序が変わる可能性がある分割案を検討する
3. ✅ 順序を変える案は採用せず、判定 / 副作用適用 / 結果収集の責務境界だけを切る分割案を採用する

```gherkin
Given CC が `_check_tile_events` (288行目) のように副作用順序に敏感な関数を分割しようとしている
When 分割によってタイル更新やイベント発火の順序が変わる可能性がある
Then CC はその分割案を採用せず、責務（判定 / 副作用適用 / 結果収集）の境界だけを切る分割案を採用する
And 既存の `pytest` テストで副作用順序が記録されている場合は、そのテストが緑のまま通ることを確認する
```

---

## 4) Design（どうやるか）

（Gherkin 承認後に記入）

---

## 5) Tasklist

（Design 承認後に記入）

---

## 6) Result（成果物）

### 対象 3 件

| ファイル | 関数 | 行数 |
|---|---|---|
| `src/scenes/explore/presenter.py` | `_check_tile_events` | 92 |
| `src/scenes/explore/presenter.py` | `_run_build_view_model` | 89 |
| `src/scenes/explore/presenter.py` | `_run_update` | 79 |

---

## 7) Discussion（残課題の起票）

> Close 前に、残課題があるなら別 tasknote 化し、そのタイトルやパスをここに残す。

### 残課題メモ

- 残り 27 件は別タスク：`steering/20260518-flake8-cr-scenes-rest27.md`（前提条件にタスク B 完了を持つ）
- flake8-cr ルール改訂は別タスク：`steering/20260518-flake8-cr-rule-extension.md`（前提条件にタスク A 完了を持つ）

---

## 8) 参考文献

- 親タスクノート（完了済）: `steering/done/20260517-flake8-cr-scenes.md`
- 後続タスク B（flake8-cr ルール改訂）: `steering/20260518-flake8-cr-rule-extension.md`
- 後続タスク C（残り 27 件適用）: `steering/20260518-flake8-cr-scenes-rest27.md`
- 初回スキャン: `/tmp/flake8-cr-scenes-initial.txt`
