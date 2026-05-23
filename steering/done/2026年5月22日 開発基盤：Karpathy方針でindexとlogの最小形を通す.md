---
status: done
priority: high
scheduled: 2026-05-22T21:30:00.000+09:00
dateCreated: 2026-05-22T21:30:00.000+09:00
dateModified: 2026-05-23T09:30:00+00:00
tags:
  - task
  - llm-wiki
  - karpathy
  - index
  - log
---

# 2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す

> 状態：⑧ Closing
> 次のゲート：（CC）なし

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

### Tasklist

- [x] `wiki/wiki/index.md` を生成した
- [x] `wiki/wiki/log.md` を生成した
- [x] `tools/gen_wiki.py` に index/log 生成責務を持たせた
- [x] `wiki/wiki/indexes/tasknotes.md` を追加し、repo-local の open/done tasknote を一覧できるようにした
- [x] `wiki/wiki/query/README.md` を追加し、read-only query の入口を固定した

### Result

- `tools/gen_wiki.py` が raw/summaries の生成後に `index.md` / `log.md` / `indexes/tasknotes.md` / `query/README.md` / `candidates/*.md` を deterministic に再生成するようになった
- `wiki/wiki/index.md` から knowledge / tasknote / checklist summary の入口を辿れるようになった
- `wiki/wiki/log.md` から ingest 日付ごとの source を時系列で追えるようになった
- repo-local rollout では `areas/current-state` を採らず、`index.md` / `log.md` / `indexes/tasknotes.md` を query 入口とする方針を実物へ反映した

### Discussion

- `areas/current-state` は引き続き保留。navigation が不足した時点で再検討する
- query の自動化はまだ行わず、06 では read-only ルールと spot-check の記録を先に通した

### Closing

- 状態: done
- 次のゲート: なし
- close 条件:
    - [x] `wiki/wiki/index.md` が生成されている
    - [x] `wiki/wiki/log.md` が生成されている
    - [x] generator から再生成できる
