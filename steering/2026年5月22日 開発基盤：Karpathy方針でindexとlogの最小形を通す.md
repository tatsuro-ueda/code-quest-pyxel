---
status: open
priority: high
scheduled: 2026-05-22T21:30:00.000+09:00
dateCreated: 2026-05-22T21:30:00.000+09:00
dateModified: 2026-05-23T04:10:24+00:00
tags:
  - task
  - llm-wiki
  - karpathy
  - index
  - log
---

# 2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す

> 状態：④ Design
> 次のゲート：（CC）`wiki/wiki/index.md` と `wiki/wiki/log.md` の雛形を作り、`tools/gen_wiki.py` に書き戻す責務を持たせるかを決める

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 Karpathy gist に明示されている最小ナビゲーション層を先に通し、query 前の探索導線をシンプルにする
> 補足：やらないこと repo 固有 area 分類や current-state ページは今は作らない

1. 前提条件
   1. 💦 `wiki/raw/...` と `wiki/wiki/summaries/...` には spot ingest の成果物がすでにある
   2. 💦 Karpathy gist は `index.md` と `log.md` を明示している
   3. 💦 `area current-state` は repo ローカル extension として保留に戻した

2. Before
   1. 💦 summary はあるが、一覧入口の `index.md` と時系列入口の `log.md` がまだ無い
   2. 💦 次回セッションで「何が入っていて、直近何を ingest したか」を 1 ファイルで見渡せない
   3. ❌ 迷う

3. After
   1. 💦 `index.md` で wiki の中身を一覧できる
   2. ✅ `log.md` で ingest の履歴を時系列で見られる
   3. ❤️ 安心

4. 例外
   1. まずは spot ingest の 2 source だけを対象にしてよい
   2. full ingest 時に format が足りなければ後で frontmatter や metadata を足してよい

5. 境界条件
   1. 今回は `index.md` と `log.md` の最小実装だけ
   2. query / checklist / search は後続 note

6. 委任度
   1. 🟢 全体として CC 単独で進められる：既存 raw/summaries を読めば最小 index/log は作れる
   2. 🟢 CCのみで可：手動雛形か generator 追記かの判断
   3. 🟡 後で人の判断があり得る：log の粒度、index の metadata 量

---

## 2) ユーザーストーリーマップ

> 委任度：🟢 最小 index/log までは CC が進められる
> 残る曖昧さ：`tools/gen_wiki.py` が index/log を自動更新するかは未確定

### 話題一覧

#### 話題1：一覧入口を作る

##### ユーザー：私

1. 当初計画
    1. 👀 summaries を一覧する
    2. 📝 `index.md` にリンクと 1 行要約を書く
    3. 🔗 raw への導線も残す

#### 話題2：時系列入口を作る

##### ユーザー：私

1. 当初計画
    1. 👀 今回の ingest 事実を集める
    2. 📝 `log.md` に 1 件 append する
    3. 🧭 将来 `gen_wiki.py` が append する形に寄せるか判断する

---

## 3) Gherkin（完了条件）

> 委任度：🟢 最小形の実装までは CC が完走できる
> 残る曖昧さ：なし

### シナリオ一覧

- [ ] シナリオ1：`index.md` から今ある wiki ページへ辿れる

1. 🧱 summaries が複数ファイルに分かれている
2. 🎬 `index.md` に summary ページ一覧と 1 行説明を書く
3. ✅ 次回セッションは index から relevant page を選べる

- [ ] シナリオ2：`log.md` から直近の ingest が分かる

1. 🧱 raw/summaries はできたが履歴の入口が無い
2. 🎬 `log.md` に今回の ingest を append する
3. ✅ 「いつ何を入れたか」を時系列で見られる

---

## 4) Design（どうやるか）

### 【参照】

- Steering: `steering/done/2026年5月22日 Karpathy方針へ寄せてindexとlogを先に通しarea current-stateを採用しない.md`
- Steering: `steering/done/2026年5月22日 練習用プロジェクトでminimal ingestとsummariesを通す.md`
- External: Andrej Karpathy `LLM Wiki` gist

### 変更範囲

- やること:
  - `wiki/wiki/index.md` の雛形を作る
  - `wiki/wiki/log.md` の雛形を作る
  - `tools/gen_wiki.py` の責務に含めるか判断する
- やらないこと:
  - `area current-state`
  - query 実装
  - checklist 実装

### 中断メモ

- session close 2026-05-23:
  - 現在の状態：Design まで完了。Karpathy 寄り方針と `list-tasknotes` skill は保存対象へ含める
  - 次に再開すること：`wiki/wiki/index.md` と `wiki/wiki/log.md` の最小仕様を確定し、必要なら `tools/gen_wiki.py` のテストから始める
