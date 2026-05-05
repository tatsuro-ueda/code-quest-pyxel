---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00.000+09:00
dateCreated: 2026-05-05T23:00:00.000+09:00
dateModified: 2026-05-05T23:00:00.000+09:00
tags:
  - task
---

# 2026年5月5日 build パイプラインから index.html を切り離して手書き正本化

> 状態：① Journey 起票完了
> 次のゲート：（ユーザー）Journey/Gherkin/Design/Tasklist の妥当性を確認 →「実装」or「修正」と指示

---

## 1) Journey（どこへ行くか）

- **深層的目的**：root `index.html` を hand-maintained 正本にする
- **やらないこと**：`production/play.html` / `production/pyxel.html` / `production/code-maker.zip` の生成は触らない（build 必要、現行通り）

### Before（現状）

- 😕 root `index.html` は **2 つの正本** を持っている：(1) 手で書いた kid-pixel リデザイン（commits `dfc4dbd / 84e054c / 9173552`、645 行、子ども向け UI）と、(2) `tools/render_release_selector.py::generate_top_selector` が `templates/selector.html` から自動生成する 111 行 selector。
- ❌ `make build` を走らせると (2) が (1) を **黙って上書き**する。今回 build 後に発覚し、`git checkout -- index.html` で復旧した（commit `0dc8df0` で本番には影響回避済み）が、次回 build でも同じ regression が再発する。
- 😕 dev/prod 分離廃止（Phase 3）と本番一本化で「複数選択肢の selector」という generate_top_selector の存在意義が薄い。template の差分（preview card / hint block / changes list）は本番一本では空になる。
- 😕 `top_changes.json` は generate_top_selector からのみ参照されている。selector を切り離せば孤児になる。

### After（達成状態）

- 🙂 root `index.html` は **手書き正本**。`make build` を走らせても上書きされない（`git diff index.html` が空）。
- 🙂 `tools/build_web_release.py` から index.html 生成 + `shutil.copy2(selector_path, index_path)` の 4 行ブロックを削除。
- 🙂 `tools/render_release_selector.py::generate_top_selector` は **死関数**。本タスクで関数 + `load_top_page_changes` + `top_changes.json` をまとめて削除（dead code 撤去）。
- 🙂 `templates/selector.html` も generate_top_selector 専用テンプレートだったので削除（`generate_wrapper` は `templates/wrapper.html` を使うので残す）。
- 🙂 `make build` 後も `pytest test/ -q` が緑、`production/` 配下は再生成され、`index.html` だけ無変更。
- 🙂 子ども向け UI（kid-pixel リデザイン）が将来の build 実行で消えなくなり、自動生成 selector への意図せぬ巻き戻りが構造的に起き得ない。

---

## 2) Gherkin（完了条件）

### シナリオ 1：build 後に index.html が変わらない

- 🧱 Given：working tree clean、root `index.html` が kid-pixel リデザイン版（645 行）
- 🎬 When：`make build` を実行
- ✅ Then：`git diff index.html` が空。`production/pyxel.html / pyxel.pyxapp / code-maker.zip` のみ更新される。

### シナリオ 2：dead code が消える

- 🧱 Given：実装後の repo
- 🎬 When：`grep -rn "generate_top_selector\|load_top_page_changes\|TOP_CHANGES_FILE\|top_changes\.json\|templates/selector\.html" src/ tools/ test/ --include='*.py'` を実行
- ✅ Then：定義側 1 箇所も呼び出し側 1 箇所も 0 件。`top_changes.json` / `templates/selector.html` ファイル自体も repo から消えている。

### シナリオ 3：build / pytest が緑のまま

- 🧱 Given：作業前 `pytest test/ -q` = 718 passed
- 🎬 When：build パイプライン改修後
- ✅ Then：`pytest test/ -q` が 718 passed のまま。`make build` も完走（gen → test → build_web_release）。

### シナリオ 4：root index.html がプレイ導線を保持している（リスク確認）

- 🧱 Given：手書き正本の `index.html`
- 🎬 When：`grep -nE "production/play\.html|production/code-maker\.zip" index.html`
- ✅ Then：「あそんでみる」リンクが `production/play.html` を、Code Maker zip ダウンロードが `production/code-maker.zip` を指している（kid-pixel リデザインで既に書かれている）。GitHub Pages から開いて壊れない。

### シナリオ 5：将来の同一 regression を防ぐ静的ガード

- 🧱 Given：実装完了後、将来の開発者が generate_top_selector を復活させて build で index.html を上書きする可能性
- 🎬 When：`test_cjg_framework_rule_guards.py` などに「`tools/build_web_release.py` 内で `index.html` を出力する shutil.copy2/write_text が無いこと」を assert する grep ガードを 1 件追加
- ✅ Then：再侵入が pytest で即 fail。kid-pixel リデザインの保護を将来も維持できる。

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：Read / Edit / Bash / pytest。MCP 不要。

### 構成図

```text
インプット                                処理                              アウトプット
─────────                                ─────                             ─────────
tools/build_web_release.py L123-130 ┐                                  ┌→ build_web_release.py から削除
tools/render_release_selector.py    ├→ dead code 特定 → 一括削除 ─→  ├→ render_release_selector.py から削除
templates/selector.html             │   pytest 緑確認 → commit          ├→ ファイル削除
top_changes.json                    ┘                                   ├→ ファイル削除
                                                                        └→ 静的 guard 追加
```

### 削除対象の根拠

| 削除対象 | 根拠 |
|---|---|
| `tools/build_web_release.py` L123-130（`index_path = output_dir / "index.html"` から `shutil.copy2(...)` まで） | これが root index.html を黙って上書きする犯人 |
| `tools/render_release_selector.py::generate_top_selector` (L120-135) | 上記から呼ばれる唯一の関数。Phase 3 後は dev/preview 引数も既に削除済で、本番一本のカードを 1 枚出すだけの薄いラッパ |
| `tools/render_release_selector.py::load_top_page_changes` (L103-117) | generate_top_selector からのみ参照される |
| `tools/render_release_selector.py::TOP_CHANGES_FILE` / `TOP_CHANGE_LIST_FRESHNESS_DEPENDENCIES` 定数 (L9, L18-24) | load_top_page_changes 専用 |
| `tools/render_release_selector.py::generate_selector` (L55-100) | generate_top_selector からのみ呼ばれる |
| `templates/selector.html` | 上記 generate_selector 専用テンプレート |
| `top_changes.json` | 上記 load_top_page_changes 専用 |

`generate_wrapper`（L34-52、`templates/wrapper.html` ベース）は **`production/play.html` の生成に必要なので残す**（build_web_release.py L115-121 で利用）。

### 手順フロー

1. **影響範囲の最終 grep**（`generate_top_selector / load_top_page_changes / TOP_CHANGES_FILE / top_changes\.json / templates/selector\.html / generate_selector`）→ 想定 3 ファイル（build_web_release.py / render_release_selector.py / resolve_release_source_of_truth.py）。
2. **`tools/build_web_release.py` 編集**：L123-130 を削除、`generate_top_selector` の import も外す。
3. **`tools/render_release_selector.py` 編集**：`generate_top_selector / load_top_page_changes / generate_selector / TOP_CHANGES_FILE / TOP_CHANGE_LIST_FRESHNESS_DEPENDENCIES` を削除。`generate_wrapper` のみ残す。
4. **`tools/resolve_release_source_of_truth.py` 確認**：`validate_change_list_freshness` が他から呼ばれているか確認、孤児なら削除。
5. **ファイル削除**：`templates/selector.html`、`top_changes.json`。
6. **静的 guard 追加**：`test_cjg_framework_rule_guards.py` に「build_web_release.py が index.html に出力しない」テスト 1 件。
7. **検証**：`make build` → `git diff index.html` が空、`pytest test/ -q` 緑。
8. **commit**：`refactor(build): index.html を build パイプラインから切り離し dead code を撤去`。
9. **Result / Discussion 記入** → steering/done/ へ移動。

### リスクと対処

| リスク | 対処 |
|---|---|
| `validate_change_list_freshness` が他から使われていた | grep で確認、使われていれば残す |
| `generate_wrapper` が誤って削除される | テンプレ指定で混同しない、wrapper は触らない |
| `production/play.html` 生成が壊れる | `make build` 後に `production/play.html` の存在 + 中身を確認 |

### ゲート

- ユーザー承認待ち。承認後は途中で止めずに完走可。

---

## 4) Tasklist

> 上から順に実施。CC が CoVe で自力検証しながら進める。

- [ ] （CC）影響範囲の最終 grep（generate_top_selector / load_top_page_changes / templates/selector.html / top_changes.json / generate_selector / validate_change_list_freshness）
- [ ] （CC）`tools/build_web_release.py` から index.html 生成ブロック削除 + import 整理
- [ ] （CC）`tools/render_release_selector.py` から dead 関数 / 定数を削除（`generate_wrapper` のみ残す）
- [ ] （CC）`tools/resolve_release_source_of_truth.py` の `validate_change_list_freshness` 利用状況確認 → 孤児なら削除
- [ ] （CC）`templates/selector.html` / `top_changes.json` 削除
- [ ] （CC）`test_cjg_framework_rule_guards.py` に「build_web_release.py が index.html を出力しない」guard 追加
- [ ] （CC）`make build` 実行 → `git diff index.html` が空であることを確認
- [ ] （CC）`pytest test/ -q` 全緑確認（718 → 719 passed、新 guard +1）
- [ ] （CC）`git add -A` → commit `refactor(build): index.html を build パイプラインから切り離し dead code を撤去`
- [ ] （CC）Result セクションに作業ログ、Discussion に保留点・要約を記入
- [ ] （CC）steering/done/ へ移動

### 作業記録

> Observe → Think → Act を刻む。

#### 2026-05-05 23:00（起票）

**Observe**：本日 `make build` 実行直後に `index.html` が generate_top_selector で 645 行→111 行に上書きされる regression を発見。`git checkout -- index.html` で復旧、production artifact のみ commit (`0dc8df0`) して本番には影響回避済。
**Think**：dev/prod 分離廃止（Phase 3）後、selector は本番カード 1 枚を出すだけの薄いラッパで、子ども向け UI（kid-pixel リデザイン）に置き換えた今は完全に dead。手書き正本化が最小コストで構造的に regression を防げる。
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
