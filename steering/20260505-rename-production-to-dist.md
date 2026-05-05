---
status: open
priority: normal
scheduled: 2026-05-06T10:00:00.000+09:00
dateCreated: 2026-05-05T22:00:00.000+09:00
dateModified: 2026-05-05T22:00:00.000+09:00
tags:
  - task
---

# 2026年5月5日 production/ → dist/ にリネーム（dev/prod 一本化の名残整理）

> 状態：① Journey 起票完了、ユーザー承認待ち
> 次のゲート：（ユーザー）Journey/Gherkin/Design/Tasklist の妥当性を確認 →「実装」or「修正」と指示

---

## 1) Journey（どこへ行くか）

- **深層的目的**：「本番一本化」の名残を消す
- **やらないこと**：build script のロジック書き換え、配布物の構造変更、CDN 切替

### Before（現状）

- 😕 `dev/prod 分離` を Phase 3 で廃止して 1 artifact 化したのに、フォルダ名は **`production/`** のまま。「production があるなら development もあるのか？」と読み手に誤解を与える名残。
- 😕 `development/` フォルダは既に削除済（実体ゼロ）。`production/` だけ残っているのは命名として一貫性がない。
- 😕 README L65-67 に `development/...` への stale リンクが 3 行残っている（実体ゼロ）。
- 😕 `production/` を参照している場所が散在：`index.html`（2 箇所）、`README.md`（5 箇所）、`AGENTS.md`（1 箇所）、`docs/architecture.md`（6 箇所）、`docs/product-requirements-platform.md`、`docs/product-requirements-guardrails.md`、`infra/autostart/README.md`、`tools/build_codemaker.py`、`tools/build_web_release.py`、`tools/build_release_artifacts.py`、`tools/render_release_selector.py`、`tools/test_web_compat.py`、`tools/web_runtime_server.py`、`test/test_web_runtime_server.py` ほか複数 test。

### After（達成状態）

- 🙂 配布物フォルダは **`dist/`** に統一（業界標準的な命名で「ここが配布物だ」と即わかる）。
- 🙂 README から `development/...` 行を削除し、`dist/...` で書き直す。
- 🙂 全 source（`*.py / *.md / *.html`）の `production/` 参照が `dist/` に置換され、`grep -rn "production/" src/ tools/ test/ docs/ AGENTS.md README.md index.html` が 0 件（または history note のみ）。
- 🙂 build script (`tools/build_*.py`) が `dist/` を出力先として動き、`pytest test/` が 100% 緑のまま。
- 🙂 root `index.html` を開くと、ボタンから `dist/play.html` が起動して動く（ローカル `web_runtime_server` 実機確認）。
- 🙂 GitHub Pages の公開 URL は `https://tatsuro-ueda.github.io/code-quest-pyxel/` を入口に維持される（root `index.html` 経由なので透過）。直 URL `production/play.html` を bookmark している人がいる場合は壊れるが、root 入口経由をデフォルトとして許容する。

---

## 2) Gherkin（完了条件）

### シナリオ 1：正常系（リネーム後にローカル起動できる）

- 🧱 Given：`production/` を `dist/` にリネーム＋全参照を置換した直後
- 🎬 When：`python tools/web_runtime_server.py`（or 等価） で root `index.html` を開く
- ✅ Then：「あそんでみる」ボタンから `dist/play.html` が起動し、ゲームが正常にプレイできる。Code Maker zip ダウンロードリンクも `dist/code-maker.zip` を指している。

### シナリオ 2：build 経路が dist/ を出す

- 🧱 Given：`tools/build_web_release.py` / `tools/build_codemaker.py` 等の build script
- 🎬 When：それぞれを実行
- ✅ Then：`dist/` 配下に `pyxel.html / pyxel.pyxapp / code-maker.zip / play.html / index.html` が生成される。`production/` は再生成されない。

### シナリオ 3：テストが 100% 緑のまま

- 🧱 Given：作業前 `pytest test/ -q` = 717 passed
- 🎬 When：リネーム＋参照置換完了後
- ✅ Then：作業後も 717 passed（test 内の `production/` リテラル参照も dist/ に置換済）。

### シナリオ 4：docs に stale な `production/` 記述が残らない

- 🧱 Given：全 docs (`docs/*.md`, `README.md`, `AGENTS.md`)
- 🎬 When：`grep -nE "production/" docs/ README.md AGENTS.md`
- ✅ Then：0 件（または「旧名 `production/` から rename」と明示した history note のみ）。`development/` も同様に 0 件。

### シナリオ 5：GitHub Pages 入口が壊れない（リスク確認）

- 🧱 Given：root `index.html` が GitHub Pages のエントリ
- 🎬 When：`https://tatsuro-ueda.github.io/code-quest-pyxel/` を開く
- ✅ Then：root `index.html` 経由のプレイ導線は `dist/play.html` を指して動く。**直 URL `production/play.html` は 404 になる**ことを Discussion に記録し、Twitter/Discord 等の告知で旧 URL を貼っていないかをユーザーが確認する宿題として残す（人作業）。

### シナリオ 6：infra autostart の参照も追従する

- 🧱 Given：`infra/autostart/README.md`、`tools/web_runtime_server.py`
- 🎬 When：`production/` 参照を grep
- ✅ Then：すべて `dist/` に置換され、systemd unit / runtime server 起動が壊れない（unit ファイル自体に絶対パスがあれば手動修正の TODO を Discussion に記録）。

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：Read / Edit / Bash（`git mv` + `grep -rln` + `sed -i`）/ pytest。MCP 不要。

### 構成図

```text
インプット                          処理                           アウトプット
─────────                          ─────                          ─────────
production/ フォルダ      ┐                                       ┌→ dist/ フォルダ (リネーム後)
全 source の "production/" ├→ git mv → 参照置換 → 検証 commit  ├→ source の "dist/" 参照
README L65-67 stale       ┘    (1 commit、レビュー容易)            └→ README から development/ 削除
                              pytest + 実機 index.html 確認
```

### 手順フロー

1. **影響範囲の最終確認**：`grep -rln "production/" --include="*.py" --include="*.md" --include="*.html" --include="*.js" --include="*.json"` → 想定 16 ファイル前後。
2. **`git mv production dist`**：履歴保持で folder rename。
3. **source 一括置換**：`sed -i 's|production/|dist/|g'` を対象 16 ファイルに。ただし steering/done/ 配下の履歴記述は触らない（過去ログ）。
4. **README L65-67 の `development/...` 行を削除**、`dist/...` で 3 行に短縮。
5. **`pytest test/ -q`** で 717 全緑を確認。`tools/test_web_compat.py` は Playwright 必要なので可能なら個別実行、無ければ skip 確認。
6. **ローカル `index.html` 実機確認**：`python -m http.server 8000` 等で root を serve、`http://localhost:8000/` を開いて「あそんでみる」が動くか目視。
7. **commit**：`refactor(dist): production/ → dist/ にリネーム + 全参照置換`（1 commit）。
8. **GitHub Pages 動作確認**（push 後）：`https://tatsuro-ueda.github.io/code-quest-pyxel/` を開いて壊れていないか。
9. **Result / Discussion 記入** → steering/done/ へ移動。

### リスクと対処

| リスク | 対処 |
|---|---|
| 直 URL `production/play.html` を bookmark / 告知している人がいる | Discussion に「旧 URL 死亡」を明記し、ユーザーに告知見直しを依頼 |
| GitHub Pages 反映に数分のラグ | push 後 5 分待ってから動作確認 |
| build script が `production/` 文字列を絶対パスで持っている可能性 | grep で `"production"` リテラルもチェック（PRODUCTION_DIR 等の定数名は別途検討） |
| systemd unit に絶対パス `/path/to/production/` があれば壊れる | `infra/autostart/` を読んでから対処、無ければスキップ |
| test 内の hardcoded path | `grep -rn "production/" test/` を実行し全置換 |

### ゲート

- ユーザー承認待ち（Journey/Gherkin/Design/Tasklist の妥当性確認）。
- 承認後は「途中で止めない」モードで実装まで完走可。

---

## 4) Tasklist

> 上から順に実施。CC が CoVe で自力検証しながら進める。

- [ ] （CC）影響範囲の最終 grep（py / md / html / js / json）
- [ ] （CC）`git mv production dist` で folder rename
- [ ] （CC）source 一括置換：`sed -i 's|production/|dist/|g'`（steering/done/ 除外）
- [ ] （CC）`PRODUCTION_DIR` / `"production"` リテラル定数があれば手動見直し
- [ ] （CC）README L65-67 の `development/...` 行削除＋`dist/...` で書き直し
- [ ] （CC）AGENTS.md / docs/architecture.md の `production/` 表記を `dist/` に
- [ ] （CC）`pytest test/ -q` 全緑確認（717 passed 維持）
- [ ] （CC）ローカル `python -m http.server` で `index.html` を開いて「あそんでみる」動作確認
- [ ] （CC）`git add -A` → commit `refactor(dist): production/ → dist/ にリネーム + 全参照置換`
- [ ] （ユーザー）push 後、GitHub Pages で `https://tatsuro-ueda.github.io/code-quest-pyxel/` を開いて目視確認
- [ ] （CC）Result セクションに作業ログ、Discussion に保留点・直 URL 告知見直し依頼を記入
- [ ] （CC）steering/done/ へ移動

### 作業記録

> Observe → Think → Act を刻む。

#### 2026-05-05 22:00（起票）

**Observe**：`production/` 参照は 16 ファイル前後。`development/` は実体ゼロだが README に stale な行が 3 行ある。GitHub Pages は root `index.html` 経由なので、入口 URL は壊れない。直 URL bookmark のリスクのみ。
**Think**：「dev/prod 一本化」の意図が `production/` という命名で読み取りにくくなっている。`dist/` は業界標準的で「ここが配布物」と即わかる。1 commit で完結する低リスク refactor。
**Act**：本タスクノートを起票し Journey/Gherkin/Design/Tasklist を書いた。ユーザー承認後に実装へ進む。

---

## 5) Result（成果物）

実装後に作業ログを書く。

---

## 6) Discussion（反省）

実装後に保留点・指針・要約を書く。

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：
