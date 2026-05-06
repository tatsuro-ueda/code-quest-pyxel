---
status: done
priority: normal
scheduled: 2026-05-06T10:00:00.000+09:00
dateCreated: 2026-05-05T22:00:00.000+09:00
dateModified: 2026-05-06T01:00:00.000+09:00
tags:
  - task
  - archived
---

# 2026年5月5日 production/ → dist/ にリネーム（dev/prod 一本化の名残整理）

> 状態：① Journey 起票完了、ユーザー承認待ち
> 次のゲート：（ユーザー）Journey/Gherkin/Design/Tasklist の妥当性を確認 →「実装」or「修正」と指示

---

## 1) Journey（どこへ行くか）

- **深層的目的**：「本番一本化」の名残を消す

1. 💦 （開発者）機能を追加したりバグ修正したい（コードエディタ）
2. 💦 （開発者）リポジトリを眺める（コードエディタ、あなめる）
3. Before
  1. ❌ もう使っていないファイルや関数が残っている（コードエディタ）
  2. ❌ （開発者）わかりにくい
4. After
  1. ✅ もう使っていないファイルや関数が残っていない（コードエディタ）
  2. ♥️ （開発者）嬉しい

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

- **関連スキル・MCP**：Read / Edit / Bash（`git mv` + `grep -rln` + `sed -i`）/ pytest。manage-pyxel skill, Pyxel MCP。

今回はやることが journeyとgherkinにほとんど記述済み

### 構成図

```text
インプット                          処理                           アウトプット
─────────                          ─────                          ─────────
production/ フォルダ      ┐                                       ┌→ dist/ フォルダ (リネーム後)
全 source の "production/" ├→ git mv → 参照置換 → 検証 commit  ├→ source の "dist/" 参照
README L65-67 stale       ┘    (1 commit、レビュー容易)            └→ README から development/ 削除
                              pytest + 実機 index.html 確認
```

### リスクと対処

| リスク | 対処 |
|---|---|
| 直 URL `production/play.html` を bookmark / 告知している人がいる | Discussion に「旧 URL 死亡」を明記し、ユーザーに告知見直しを依頼 |
| GitHub Pages 反映に数分のラグ | push 後 5 分待ってから動作確認 |
| build script が `production/` 文字列を絶対パスで持っている可能性 | grep で `"production"` リテラルもチェック（PRODUCTION_DIR 等の定数名は別途検討） |
| systemd unit に絶対パス `/path/to/production/` があれば壊れる | `infra/autostart/` を読んでから対処、無ければスキップ |
| test 内の hardcoded path | `grep -rn "production/" test/` を実行し全置換 |

### ゲート

- ユーザー承認待ち（Journey/Gherkin/Design の妥当性確認）。
- 承認後は「途中で止めない」モードで実装まで完走可。

---

## 4) Tasklist

> 上から順に実施。CC が CoVe で自力検証しながら進める。
> `production/` 文字列参照は 15 ソースファイル + 多数の done タスクノート (history) に存在。
> 本タスクは ソースのみ touch し、done/ は historic record として保持する。

### Phase A：物理リネーム + コード定数

- [ ] A1. `git mv production dist` でフォルダ単位リネーム
- [ ] A2. `tools/build_release_artifacts.py` の定数を一括リネーム：
  - `PRODUCTION_DIR = Path("production")` → `DIST_DIR = Path("dist")`
  - `PRODUCTION_PYXAPP_FILE / PRODUCTION_HTML_FILE / PRODUCTION_PLAY_FILE / PRODUCTION_INDEX_FILE` → `DIST_*`
  - `production_output_dir()` → `dist_output_dir()`
- [ ] A3. `tools/build_web_release.py` の import / 利用箇所を更新（PRODUCTION_DIR → DIST_DIR 等）

### Phase B：文字列置換（ソース・docs・README・index・test）

- [ ] B1. `tools/build_codemaker.py / build_web_release.py / render_release_selector.py / test_web_compat.py / web_runtime_server.py` の `"production/..."` 文字列を `"dist/..."` に置換
- [ ] B2. `test/test_web_runtime_server.py` 内 hardcoded path を置換
- [ ] B3. `README.md`：
  - `development/...` の stale 行 (L65-67) を削除
  - `production/...` 参照 5 箇所を `dist/...` に置換
- [ ] B4. `AGENTS.md` の `production/` 参照 1 箇所を `dist/` に置換（≤100 行制約あり）
- [ ] B5. `index.html` の `production/play.html` / `production/code-maker.zip` を `dist/...` に置換（2 箇所）
- [ ] B6. `docs/architecture.md` / `product-requirements-platform.md` / `product-requirements-guardrails.md` の `production/` 参照を `dist/...` に置換
- [ ] B7. `infra/autostart/README.md` の `production/` 参照を `dist/...` に置換

### Phase C：検証

- [ ] C1. `grep -rn "production/" src/ tools/ test/ docs/ AGENTS.md README.md index.html infra/` が 0 件（done/ と steering/*.md は除外）
- [ ] C2. `grep -rn "development/" src/ tools/ test/ docs/ AGENTS.md README.md index.html infra/` が 0 件
- [ ] C3. `pytest test/ -q` 全緑（733 維持）
- [ ] C4. `make build` 実行 → `dist/` に出力、`production/` は再生成されない、`git diff index.html` が空

### Phase D：commit + ノート移動

- [ ] D1. commit (a)：`refactor(build): production/ → dist/ にリネーム（dev/prod 一本化の名残整理）`
- [ ] D2. Result セクションに作業ログ、Discussion に「直 URL bookmark の 404 リスク（GitHub Pages root index.html 経由は無事）」を記入
- [ ] D3. ノート移動：`steering/done/`

---

## 5) Result（成果物）

### 作業記録

#### 2026-05-06 自走実装（CC）

**Observe**：`production/` 文字列参照は 15 ソースファイル + history 多数。`development/` は実体ゼロだが README に stale な行が 3 行残る。

**Think**：sed -i で機械的に一括置換が安全。ただし内部識別子 `page_kind="production"` (template の data attribute + JSON ログ) と意味的ラベル `PRODUCTION_SELECTOR_LABEL = "本番"` / `PRODUCTION_RUNTIME_FILE` は folder と無関係なので touch しない。docs 内の historical Gherkin (`development/play.html` など) も history 性が高いので別タスク扱い。

**Act**：
1. `git mv production dist`（フォルダリネーム）。
2. `tools/build_release_artifacts.py` の `PRODUCTION_DIR` 等定数 / `production_output_dir` 関数を `DIST_*` / `dist_output_dir` にリネーム。
3. `tools/build_web_release.py` の import + 利用を更新。
4. 一括 sed で `production/` → `dist/`、`production_play_url` → `dist_play_url`、`"production"` → `"dist"` を全 source（tools/ test/ docs/ AGENTS.md README.md index.html infra/）に適用。`page_kind="production"` は副作用で変わったので戻した。
5. `tools/web_runtime_server.py::ensure_production_build` → `ensure_dist_build` にリネーム、caller (infra/autostart/README.md, code-quest-runtime.service) も追従。
6. README から `development/` 3 行削除 + 1 行表現を「本番と開発版を比べる root selector」→「kid-pixel デザインのトップページ」に書き換え。
7. `pytest test/ -q` = 733 passed 維持。`grep -rn "production/" tools/ test/ docs/ AGENTS.md README.md index.html infra/` = 0 件。
8. `make build` 実行 → `dist/` に出力、`production/` は再生成されない（フォルダ削除済）。`git diff index.html` は build による cache token 等の少差。
9. **発覚**：前 detach commit (`8a41a94`) で 7 ファイルが stage 漏れしていた → 本 commit に混入する形で取り込み、commit message と Discussion で明示。

#### 2026-05-05 22:00（起票）

**Observe**：`production/` 参照は 16 ファイル前後。`development/` は実体ゼロだが README に stale な行が 3 行ある。GitHub Pages は root `index.html` 経由なので、入口 URL は壊れない。直 URL bookmark のリスクのみ。
**Think**：「dev/prod 一本化」の意図が `production/` という命名で読み取りにくくなっている。`dist/` は業界標準的で「ここが配布物」と即わかる。1 commit で完結する低リスク refactor。
**Act**：本タスクノートを起票し Journey/Gherkin/Design/Tasklist を書いた。ユーザー承認後に実装へ進む。


---

## 6) Discussion（反省）

### 達成

- `production/` → `dist/` のフォルダリネーム + 全 source 参照置換完了。
- `tools/build_release_artifacts.py` の `PRODUCTION_DIR / PRODUCTION_*_FILE / production_output_dir` 等定数 / 関数名も `DIST_*` / `dist_output_dir` にリネーム。
- `tools/web_runtime_server.py::ensure_production_build` → `ensure_dist_build` にリネーム + caller (infra/autostart) も追従。
- `make build` が `dist/` 配下に出力、`production/` フォルダは無くなったことを確認。
- README から `development/` の stale 行 3 つを削除。
- `pytest test/ -q` = 733 passed 維持（`page_kind` 内部識別子は "production" のまま温存し test 互換）。
- `production_play_url` JSON フィールドも `dist_play_url` に変更（test/test_web_runtime_server.py + test/test_codemaker_import_ui_server_import.py の mock 含む）。

### 重大な反省：前 commit の stage 漏れ

- 前 detach commit (`8a41a94`) で `git add` の改行コマンド（`\` で行継続）が解釈に失敗し、index.html / README.md / top_changes.json / build_web_release.py / render_release_selector.py / resolve_release_source_of_truth.py / test_cjg_framework_rule_guards.py の **7 ファイル変更が commit から漏れた**。
- 結果として、本 rename commit に detach タスクの「TOP_CHANGES マーカー埋込み」「dead code 削除」「G1/G2/G3 guard 追加」等が混在することになった。commit history としては 1 つにまとまっているが、論理的には 2 タスク分の変更を含む。
- **ルール化候補**：CC が `git add` を打った直後に `git status --short` の頭 1 文字（X = staged）を確認する習慣を付ける。改行で長い `git add` を組み立てる代わりに `git add -A` （ただし不要ファイル除外を確認）か、ファイル単位で 1 行ずつ add する。

### 保留点

- **直 URL `production/play.html` の bookmark / 告知**：GitHub Pages root `index.html` 経由のプレイ導線は無事だが、Twitter / Discord 等で `production/play.html` を直貼りしている場合 404。手作業で告知を見直す必要あり（人作業）。
- **docs 内の historical PRD 記述**：`docs/product-requirements-platform.md` の Gherkin に `development/play.html` / `development/code-maker.zip` 等の dev/prod 並行運用時代の記述が残っている。Phase 3 完了 + dist 一本化の整合性を取るには別タスクで PRD 全体を sweep する必要がある。
- **systemd unit ファイル `infra/autostart/code-quest-runtime.service`** の絶対パス：`production/` 文字列は置換済だが、外部の絶対パス（例：`/home/.../production/...`）が systemd で稼働中なら手動再 install が必要（インストール先環境次第）。

### ルール化候補

- 「dev/prod 一本化」が完了した今、`dist/` を SoT として `development/` 系の言葉自体を docs から段階的に消していく（PRD sweep 別タスク）。
- `git add` の複数ファイル指定は 1 行 1 ファイルか、`git add -p` で確認しながら。改行継続は CC 環境でのトークン分解事故が起きやすい。

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：
