---
status: in-progress
priority: normal
scheduled: 2026-05-05T20:00:00.000+09:00
dateCreated: 2026-05-05T20:00:00.000+09:00
dateModified: 2026-05-05T20:00:00.000+09:00
tags:
  - task
---

# 2026年5月5日 AGENTS.md / docs/ を最近の steering 改訂に追従させる

> 状態：④ Tasklist 実行中
> 次のゲート：（CC）architecture.md の stale 記述（L31/L57/L68/L103/L107/L120/L165/L211-216）を一括差し替え

---

## 1) Journey（どこへ行くか）

- **深層的目的**：docs と code のズレを潰す
- **やらないこと**：規約そのものの再設計、ナビ構造の変更（M5-3 で確定済み）

### Before（現状）

- 😕 AI が `docs/architecture.md` を開くと **`BlockQuestApp` が窓口**と書いてある。実体は `src/runtime/app.py::Game` であり、`src/app.py::BlockQuestApp` は test/Phase 1 残骸の薄い shell として併存している。
- 😕 `core/scene_manager.py` を Scene/SceneManager の場所と書いてあるが、M4-3 で **`shared/services/scene_manager.py` に新 SceneManager** が増えた（current/previous 2 値の state holder）。古い方は test 専用の Scene Protocol として残っているだけ。
- 😕 `GameState は 19 フィールド` と書いてあるが、`world_map` / `dungeon_map` / `dungeon_rooms` 撤去で **実際は 13 フィールド前後**。`current_town` が新しく入っている。
- 😕 `image_banks.py` の責務に SSoT 反転（`bake_world_to_tilemap` → `regenerate_world_tilemap_fallback` rename, pyxres = SSoT）が反映されていない。
- 😕 `services は 16` と書いてあるが、`debug_service.py` / 新 `scene_manager.py` 追加で **実際は 18**。
- 😕 `app.py 263 行` だが property forward 追加で **326 行**に増えている。
- 😕 docs/ の自己参照が `repository-structure.md` のまま（既に `architecture.md` にリネーム済）／`AGENTS.md` の存在が触れられていない。
- 😕 `framework-rule.md` L528 に旧名 `bake_world_to_tilemap` が残っている。
- 😕 README は OK（既に AGENTS.md→architecture.md→framework-rule.md ナビあり）。

### After（達成状態）

- 🙂 architecture.md L31/L57: `Game クラス本体 (src/runtime/app.py)` を窓口として記述。`BlockQuestApp` は legacy shell として 1 行で言及（または完全に削除）。
- 🙂 architecture.md L68: `core/scene_manager.py` は **Scene Protocol 用** と明記、`shared/services/scene_manager.py` を新 state holder として L97 以降の services 表に追加。
- 🙂 architecture.md L103: `GameState` のフィールド数を実態（13 前後）に更新、`world_map / dungeon_map` 撤去理由を 1 行で書く。
- 🙂 architecture.md L107: `image_banks.py` 責務を「pyxres ロード／初期化／fallback 焼き戻し（pyxres 不在時のみ）／pyxres 保存」に書き換え。**読み取りは Model 直読**を明記。
- 🙂 architecture.md L110: `player_state.py` を「PlayerModel が SSoT、player_state は legacy shim（M4-4 で `dump_snapshot/restore_snapshot/exp_for_level/stats_for_level` のみ残存）」と更新。
- 🙂 architecture.md services 表に `debug_service.py`（DebugService、UUDD 検出含む）と `shared/services/scene_manager.py`（SceneManager state holder）を追加。
- 🙂 architecture.md `Game クラス本体` 行を 326 行に更新、property forward 4 種（current_town/debug_mode/state/prev_state）の存在を 1 行で言及。
- 🙂 architecture.md docs/ 表で自己参照を `architecture.md` に修正、`AGENTS.md` を「上位文書（≤100 行・自動 load）」として明示。
- 🙂 architecture.md `main_development_runtime.py` 行と Phase 3 残タスクを「**完了**」に更新（既に削除済）。
- 🙂 framework-rule.md L528 の旧 API 名を新名に置換し、dungeon 側 fallback も併記。
- 🙂 framework-rule.md L593 `BlockQuestApp` → `Game` クラス（または Service）に更新。
- 🙂 AGENTS.md の `runtime 入口` 説明に DebugService / SceneManager の存在をひとこと足す（≤100 行制約は維持）。
- 🙂 全変更後、`pytest test/ -q` 緑＋ `test_cjg_framework_rule_guards.py` の AGENTS≤100行 / architecture存在ガード緑。

---

## 2) Gherkin（完了条件）

### シナリオ 1：AI が architecture.md を読んで現状の窓口クラスにたどり着く

- 🧱 Given：AI が `docs/architecture.md` を開く
- 🎬 When：「アプリの起動エントリ／Game ループはどこ？」と問う
- ✅ Then：`src/runtime/app.py::Game` クラス本体（pyxel 初期化＋全 Scene/Service 組み立て＋update/draw dispatcher）に到達できる。`src/app.py::BlockQuestApp` は legacy shell として注釈付きで残っているか、完全削除されているかが明示されている。

### シナリオ 2：services 一覧の数とメンバが実態と一致する

- 🧱 Given：AI が architecture.md L4.5 services 表を見る
- 🎬 When：`ls src/shared/services/*.py` の結果と表を突き合わせる
- ✅ Then：18 services（既存 16 + DebugService + 新 SceneManager）すべてが表に載っており、`image_banks.py` 責務は **pyxres ロード／fallback 焼き戻し／pyxres 保存** と明記されている。

### シナリオ 3：GameState 圧縮の最新形が反映されている

- 🧱 Given：AI が architecture.md / framework-rule.md の GameState 記述を読む
- 🎬 When：実際の `GameState` dataclass（`src/shared/services/game_state.py`）と比較
- ✅ Then：`world_map` が無いこと、`current_town` が入っていること、`@property in_dungeon / glitch_lord_defeated` が PlayerModel 経由であることが、文書からも読み取れる（フィールド数 19 のような具体数字 stale が無い）。

### シナリオ 4：旧 API 名が文書から消えている

- 🧱 Given：`grep -nE 'bake_world_to_tilemap|bake_dungeon_to_tilemap|main_development_runtime' docs/ AGENTS.md README.md`
- 🎬 When：実行する
- ✅ Then：0 件（または「旧名」と明示した履歴記述のみ）。

### シナリオ 5：2 層文書ナビが両方向に通っている（リスク確認）

- 🧱 Given：AGENTS.md / architecture.md / framework-rule.md を順に読む
- 🎬 When：相互リンクをたどる
- ✅ Then：AGENTS → architecture → framework-rule の往復、および framework-rule から AGENTS / architecture への戻り、すべてのリンクが既存ファイルを指している（架空 URL なし）。`test_cjg_framework_rule_guards.py::test_agents_md_under_100_lines` と `test_architecture_md_exists` が緑。

### シナリオ 6：本番テストスイートに regression が出ない

- 🧱 Given：作業前 `pytest test/ -q` が 100% 緑（102 ファイル / 717 tests）
- 🎬 When：文書のみ更新（コードは変更しない）
- ✅ Then：作業後も 100% 緑のまま。コード変更ゼロのため当然の前提だが CoVe で確認する。

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：manage-tasknotes（自身の起票/更新）、Read/Edit（docs 編集）、Bash（pytest / grep）。MCP 不要。

### 構成図

```text
インプット                   処理                          アウトプット
─────────                   ─────                         ─────────
docs/architecture.md  ┐                                  ┌→ docs/architecture.md (更新)
docs/framework-rule.md├→ stale 検出 → 既存実装と突合 → ├→ docs/framework-rule.md (微修正)
AGENTS.md             ┘    ↓ Edit で差分書き込み         └→ AGENTS.md (微修正)
                        pytest + 文書ガードで検証
                        commit
```

### 手順フロー

1. **stale 検出（既に完了）**: grep で `BlockQuestApp / core/ / 19 フィールド / 16 サービス / 263 行 / repository-structure / bake_world_to_tilemap / main_development` を抽出。
2. **architecture.md を一括書換**：影響行は L31/L33/L57-59/L68-71/L103/L107/L110/L120-121/L165/L211-216/L274-281。Edit で 1 ファイル 1 セッションで終わらせる（半端コミットを避ける）。
3. **framework-rule.md 微修正**：L528 の旧 API 名置換、L593 の `BlockQuestApp` 言及を見直し、必要なら 1〜2 行追記。
4. **AGENTS.md 微修正**：「実装の事実」節に DebugService / SceneManager / Game クラス位置を 1〜2 行追記。≤100 行を維持。
5. **検証**：`pytest test/test_cjg_framework_rule_guards.py -q` → `pytest test/ -q`。
6. **commit**：`docs(sync): AGENTS / architecture / framework-rule を最近の steering に追従`（複数 commit に分割しない、文書のみ）。
7. **Result / Discussion 記入** → steering/done/ 移動。

### ゲート

- 計画の妥当性は本タスクノート Tasklist セクションで自己 CoVe（Gherkin 6 シナリオすべて満たすか）。
- ユーザー指示「途中で止めない」モードのため、実装後に Result/Discussion へ進む。

---

## 4) Tasklist

> 上から順に実施。CC が CoVe で自力検証しながら進める。

- [x] （CC）stale 検出 grep（完了：本ノートの Journey で結果列挙）
- [ ] （CC）`docs/architecture.md` を Edit で更新
  - [ ] L31 / L57-59：`BlockQuestApp` 説明 → `Game クラス本体 (src/runtime/app.py)` に置換
  - [ ] L33 / L68-71：`core/scene_manager.py` を Scene Protocol 専用と明記、`shared/services/scene_manager.py` を services 表へ追加
  - [ ] L97-118：services 表に `debug_service.py` と新 SceneManager を追記、`image_banks.py` 責務更新、`player_state.py` を M4-4 後の状態に更新
  - [ ] L103：GameState フィールド数を実態（`world_map / dungeon_map / dungeon_rooms` 撤去後）へ
  - [ ] L120-121：DI list に DebugService / SceneManager を追加
  - [ ] L162-166：`app.py` 行数（263 → 326）と property forward 4 種を追記
  - [ ] L208-216：docs/ 表を `architecture.md`（自身）+ `AGENTS.md` 上位文書として再編
  - [ ] L274-281：Phase 3 完了状態を反映、`main_development*.py` を削除済として記述
- [ ] （CC）`docs/framework-rule.md` を Edit で微修正
  - [ ] L528：`bake_world_to_tilemap` → `regenerate_world_tilemap_fallback`／dungeon 版併記
  - [ ] L593：`BlockQuestApp` → `Game` クラス（M4-3 段階移行と整合）
- [ ] （CC）`AGENTS.md` を Edit で微修正
  - [ ] 「実装の事実」節に DebugService / SceneManager / Game クラス位置を追記、≤100 行を維持
- [ ] （CC）`pytest test/test_cjg_framework_rule_guards.py -q` を実行
- [ ] （CC）`pytest test/ -q` で全体 regression 確認
- [ ] （CC）`git add docs/ AGENTS.md steering/...` → commit
- [ ] （CC）Gherkin 6 シナリオを CoVe
- [ ] （CC）Result セクションに作業ログ、Discussion に保留点・指針・要約を記入
- [ ] （CC）steering/done/ へ移動

### 作業記録

> Observe → Think → Act を刻む。

#### 2026-05-05 20:00（着手）

**Observe**：直前 commit `2d07caf docs(steering): pyxres SSoT note を done に更新` まで完了。worktree clean。`refactor/2026-05-05-m4-m5-cleanup` ブランチ上。
**Think**：架空のリネームではなく、既に実装済みの change を文書側で追従させるだけの低リスクタスク。コード変更ゼロで進める。
**Act**：本タスクノートを起票し Journey/Gherkin/Design/Tasklist を書いた。次は architecture.md を Edit で順次差し替える。

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
