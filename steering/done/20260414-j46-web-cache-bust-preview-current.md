---
status: done
priority: high
scheduled: 2026-04-14T13:45:00+00:00
dateCreated: 2026-04-14T13:45:00+00:00
dateModified: 2026-04-14T13:56:00+00:00
tags:
  - task
  - j46
  - preview
  - runtime
  - cache
---

# 2026年4月14日 J46 preview/current の古い配信物をブラウザに使わせない

> 状態：(5) Discussion
> 次のゲート：（ユーザー）preview を開き直して挙動を確認する

---

## 1) 改善対象ジャーニー

- **根拠となるカスタマージャーニー**：`docs/customer-journeys.md` の `CJ31: 子どもが変更を承認する`
- **関連するカスタマージャーニー**：`docs/customer-journeys.md` の `CJ33: 子どもが変更を選んで適用する`
- **深層的目的**：preview を更新したら、子どもがブラウザで開く `おためしばん` が本当にその更新内容になる
- **やらないこと**：今回の note でゲームロジックそのものを再設計すること

### 人間の期待

- **この note が `done` なら、人間は何が成立していると思うか**：build 後に `おためしばん` / `もとのままばん` を開き直すと、その時点の最新配信物が表示される
- **その期待を裏切りやすいズレ**：`pyxel.html` / `pyxel-preview.html` の URL が毎回同じで、ブラウザが古い html を再利用する
- **ズレを潰すために見るべき現物**：`index.html`、`play.html`、`play-preview.html`、`tools/build_web_release.py`

## 2) カスタマージャーニーgherkin（完了条件）

### シナリオ1：正常系

> {build 後の selector を開く} で {おためしばん / もとのままばんへ進む} と {wrapper と pyxel html の URL に build token が付き古い html を流用しない}

### シナリオ2：回帰確認

> {preview source がない通常 build} で {selector を生成する} と {stale preview を隠す既存挙動を壊さない}

### 対応するカスタマージャーニーgherkin

- `docs/cj-gherkin-platform.md`
  `CJG31`
  `Scenario: 親がAIに頼んだ変更はまずおためし版に入る`
- `docs/cj-gherkin-platform.md`
  `CJG31`
  `Scenario: 選択ページの変更説明が実際の配信内容と一致する`

## 3) Design（どうやるか）

- `selector.html` の href に build token を付ける
- `wrapper.html` の iframe src に build token を付ける
- token は current / preview の依存ファイルから作る
- 既存の stale preview pruning と freshness check は壊さない

## 4) Tasklist

- [x] task note を起票する
- [x] versioned URL の failing test を書く
- [x] build token を実装する
- [x] `python -m pytest test/test_build_web_release.py -q`
- [x] `python -m pytest test/ -q`

## 5) Discussion（記録・反省）

### 2026年4月14日 13:45（起票）

**Observe**：preview 用 `main.py` にはノイズガーディアン除外が入っていたが、ユーザー観測では preview でもランダム遭遇していた。`selector -> play-preview.html -> pyxel-preview.html` は毎回同じ URL で、ブラウザが古い html を掴む余地がある。
**Think**：通常遭遇ロジックをいじる前に、web 配信が常に最新 artifact を読む形に直すべき。build token を query string として流せば、静的配信のまま cache bust ができる。
**Act**：J46 を起票し、まず build テストで versioned URL を固定してから `tools/build_web_release.py` と wrapper / selector を直す。

### 2026年4月14日 13:56（修正・検証完了）

**Observe**：`test/test_build_web_release.py` に build 出力の URL 期待値を追加すると、`index.html` は `play.html` / `play-preview.html` の固定 URL を出し、`play*.html` も `pyxel*.html` の固定 URL を iframe へ入れていた。これでは build 後もブラウザが同じ URL を再利用できる。
**Think**：`generate_selector()` / `generate_wrapper()` は引数文字列をそのまま埋めるだけなので、build 側で current / preview ごとの token を計算して渡せば最小修正で済む。token は依存ファイルの最新 revision timestamp を使えば、dirty worktree でも build 内容に追従する。
**Act**：`tools/build_web_release.py` に `build_cache_token()` と `versioned_asset_url()` を追加し、通常 build / preview build の両方で `play*.html?v=...` と `pyxel*.html?v=...` を生成するようにした。回帰は `python -m pytest test/test_build_web_release.py -q` で `22 passed`、全体は `python -m pytest test/ -q` で `163 passed, 2 skipped`。`python tools/build_web_release.py --preview` 後の実ファイルでは `index.html` が `play-preview.html?v=1776173657` と `play.html?v=1776171277` を返し、`play-preview.html` は `pyxel-preview.html?v=1776173657` を iframe に設定した。web 互換は `python tools/test_web_compat.py` で `OK: Web版テスト通過`、live runtime `http://127.0.0.1:8888/index.html` と `http://127.0.0.1:8888/play-preview.html` でも同じ token 付き URL を確認した。
