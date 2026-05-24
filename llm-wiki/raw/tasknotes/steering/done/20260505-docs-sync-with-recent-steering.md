---
status: done
priority: normal
scheduled: 2026-05-05T20:00:00.000+09:00
dateCreated: 2026-05-05T20:00:00.000+09:00
dateModified: 2026-05-05T21:30:00.000+09:00
tags:
  - task
  - archived
---

# 2026年5月5日 AGENTS.md / docs/ を最近の steering 改訂に追従させる

> 状態：⑥ Discussion 完了（done）
> 次のゲート：なし

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
- [x] （CC）`docs/architecture.md` を Edit で更新
  - [x] L31 / L57-59：`BlockQuestApp` 説明 → `Game クラス本体 (src/runtime/app.py)` に置換
  - [x] L33 / L68-71：`core/scene_manager.py` を Scene Protocol 専用と明記、`shared/services/scene_manager.py` を services 表へ追加
  - [x] L97-118：services 表に `debug_service.py` と新 SceneManager を追記、`image_banks.py` 責務更新、`player_state.py` を M4-4 後の状態に更新
  - [x] L103：GameState フィールド数を実態（13 フィールド、`world_map / dungeon_map / dungeon_rooms` 撤去後）へ
  - [x] L120-121：DI list に DebugService / SceneManager を追加
  - [x] L162-166：`app.py` 行数（263 → 326）と property forward 4 種を追記
  - [x] L208-216：docs/ 表を `architecture.md`（自身）+ `AGENTS.md` 上位文書として再編
  - [x] L274-281：Phase 3 完了状態を反映、`main_development*.py` を削除済として記述
- [x] （CC）`docs/framework-rule.md` を Edit で微修正
  - [x] L528：`bake_world_to_tilemap` → `regenerate_world_tilemap_fallback`／dungeon 版併記
  - [x] L593：`BlockQuestApp` → `Game` クラス（M4-3 段階移行と整合）
- [x] （CC）`AGENTS.md` を Edit で微修正
  - [x] 「実装の事実」節に DebugService / SceneManager / Game クラス位置を追記、ちょうど 100 行を維持
- [x] （CC）`pytest test/test_cjg_framework_rule_guards.py -q` を実行（17 passed）
- [x] （CC）`pytest test/ -q` で全体 regression 確認（717 passed, 2 skipped）
- [x] （CC）`git add docs/ AGENTS.md` → commit `c63eaca`
- [x] （CC）Gherkin 6 シナリオを CoVe（下記 Result）
- [x] （CC）Result セクションに作業ログ、Discussion に保留点・指針・要約を記入
- [x] （CC）steering/done/ へ移動

### 作業記録

> Observe → Think → Act を刻む。

#### 2026-05-05 20:00（着手）

**Observe**：直前 commit `2d07caf docs(steering): pyxres SSoT note を done に更新` まで完了。worktree clean。`refactor/2026-05-05-m4-m5-cleanup` ブランチ上。
**Think**：架空のリネームではなく、既に実装済みの change を文書側で追従させるだけの低リスクタスク。コード変更ゼロで進める。
**Act**：本タスクノートを起票し Journey/Gherkin/Design/Tasklist を書いた。次は architecture.md を Edit で順次差し替える。

---

## 5) Result（成果物）

### 変更ファイル

- `docs/architecture.md`（+78 / −53）
- `docs/framework-rule.md`（+2 / −2）
- `AGENTS.md`（+8 / −4）

### 主な差分

| ファイル | 内容 |
|---|---|
| architecture.md L17 | `main_development.py` の Phase 3 廃止を明記 |
| architecture.md L26-50 | ツリー全体を更新（services 16→18、shared/state 追加、test 36→102 ファイル、main_development_runtime 行を削除） |
| architecture.md L55-77 | 4.1 を `src/runtime/app.py::Game`（窓口）に格上げ、4.2 を `BlockQuestApp` legacy shell として再定義、4.4 を `core/scene_manager.py` test 互換のみと明記 |
| architecture.md L97-126 | 4.6 services 表を 18 サービスに更新（debug_service / 新 scene_manager 追加、image_banks 責務を fallback 専用に書換、player_state を M4-4 後の legacy snapshot helper に更新、`browser_resource_override` を削除）。4.6.1 として `shared/state/` 節を新設し PlayerModel を記載 |
| architecture.md L162-180 | 4.11 runtime/ から `main_development_runtime.py` 行を削除、`app.py` を 263→326 行・property forward 4 種を明記 |
| architecture.md L196 | 5.3 test を `102 ファイル / 717 tests` に更新、`test_cjg_framework_rule_guards.py` の役割を追記 |
| architecture.md L208-220 | 5.6 docs/ 表を 2 層文書ナビ前提に再編（AGENTS.md を上位文書として明記、self-reference を `architecture.md` に修正） |
| architecture.md L221-244 | 6.1 レイヤー依存図を `runtime/app.py (Game)` 起点に変更、`shared/state` を追加、6.1 禁止項目に「`shared/services/scene_manager.py` が Scene オブジェクトを保持しない」を追加 |
| architecture.md L248-266 | 7. 責務の線引きに M4-3 deprecated field 復活防止 / image_banks 読み取り禁止 / world_generation 結果の snapshot 禁止を追加 |
| architecture.md L289-315 | 9. 現状と残タスクを M4-3 / M4-4 / M5-3 / Phase 2-3 の完了状況に更新、残タスクを再列挙 |
| framework-rule.md L528 | ImageBanks 責務記述で `bake_world_to_tilemap` → `regenerate_world_tilemap_fallback` / dungeon 版併記、旧名を rename 履歴として残置 |
| framework-rule.md L593 | M4-3 「Game クラス削除方針」に段階移行で property forward 化済の事実を追記 |
| AGENTS.md 「実装の事実」節 | runtime 入口チェーン、共有 state 4 種、M4-3 property forward の static guard、`src/app.py::BlockQuestApp` の legacy 位置付け、pyxres = SSoT、配布物一本化を 1〜2 行ずつで明記 |

### 検証ログ（CoVe）

```
$ python -m pytest test/test_cjg_framework_rule_guards.py -q
17 passed, 22 subtests passed in 0.11s

$ python -m pytest test/ -q
717 passed, 2 skipped, 14460 subtests passed in 6.13s

$ git commit ...
pre-commit: All tests passed.
[refactor/2026-05-05-m4-m5-cleanup c63eaca] docs(sync): AGENTS / architecture / framework-rule を最近の steering 改訂に追従
 3 files changed, 102 insertions(+), 67 deletions(-)
```

### Gherkin CoVe

| シナリオ | 結果 | 根拠 |
|---|---|---|
| 1. Game クラスへの到達 | ✅ | architecture.md 4.1 が `src/runtime/app.py::Game` を窓口として明示、4.2 で `BlockQuestApp` を legacy shell と注記 |
| 2. services 表の実態一致 | ✅ | `ls src/shared/services/*.py` = 18、表も 18 行（+ shared/state 節）、image_banks 責務に「pyxres ロード／fallback 焼き戻し／pyxres 保存」明記 |
| 3. GameState 圧縮反映 | ✅ | architecture.md L103 の `GameState` 説明に `world_map / dungeon_map / dungeon_rooms` 撤去・`current_town` 追加・PlayerModel 経由を明記。具体数字 stale (19) を全削除 |
| 4. 旧 API 名の文書消去 | ✅ | grep 結果は「rename した」「Phase 3 で削除済」の履歴記述のみ。stale な現状記述ゼロ |
| 5. 2 層文書ナビ往復 | ✅ | architecture.md L208-220 が AGENTS.md を上位文書として明示、framework-rule.md L1-7 / L783 が両方への戻りリンクあり、`test_agents_md_is_within_100_lines` / `test_docs_architecture_md_exists` 緑 |
| 6. テスト regression | ✅ | 717 passed (作業前と同数)、コード変更ゼロ |

---

## 6) Discussion（反省）

### 要約

最近 1 日で進んだ 5 本のリファクタ（dungeon-map-removal / game-class-shrink-m43 / imagebank-direct-cleanup / player-state-shim-removal / index-html-kid-pixel-redesign）と、それに伴う `core/scene_manager.py` の役割縮退、`shared/services/scene_manager.py` / `debug_service.py` の新設、`bake_world_to_tilemap` → `regenerate_world_tilemap_fallback` rename、Phase 3 の dev/prod 分離廃止、AGENTS.md 100 行化、`docs/repository-structure.md` → `docs/architecture.md` リネーム、を 3 ファイル（AGENTS.md / docs/architecture.md / docs/framework-rule.md）に追従させた。差分は 102 insertions / 67 deletions。コード変更ゼロ、テスト 717 全緑。

### 結論

- **docs と code の同時改修ペア化**を意識しないと、リファクタ commit のたびに docs 負債が積み上がる。今回はまとめて 1 commit で追従できたが、次回からは「コード rename / 削除をする commit と同じ commit に docs 修正を入れる」運用に切り替えるべき。
- AGENTS.md がちょうど 100 行に達した。`shared/state/` を加えたい・新しい実態を 1 行追記したい、という都度の追加圧力が効いており、今後 1 行入れるたびに古い行を 1 行削る zero-sum の編集を強制する閾値として機能している。

### 保留点（今後の指針）

| 保留 | 指針 |
|---|---|
| `src/app.py::BlockQuestApp` の最終整理 | M4-3 と M4-4 の進度を見て、test/Code Maker bundler 側を `Game` 直参照に切り替えてから削除する。Gherkin で「`BlockQuestApp` を import する箇所がゼロ」を完了条件にして別タスクで起票する |
| `src/core/scene_manager.py` の削除 | 上記と同じく test 側書き換えとセットで進める。新 `SceneManager` (state holder) と旧 `SceneManager` (Scene オブジェクト保持) が同名で並ぶ状態は、grep して名前混乱の温床になりうる |
| `item_use.py` / `player_state.py` 残存 | M4-4 後半タスクとして PlayerModel に吸収。`dump_snapshot / restore_snapshot` は save 互換のため最後まで残しても良い |
| docs 自動 stale 検出 | 「architecture.md 内の `行数` 数字を Lint する」「services 表の数を `ls src/shared/services/*.py | wc -l` と突合する」ような pre-commit を入れる案あり。費用対効果は次の docs 編集で再検討 |
| docs/customer-journeys.md の M4-3 反映 | CJ37 系の改訂で「責務が曖昧で直すほど別の所が壊れる」ガードレールに M4-3 / DebugService の事実が反映されていない可能性あり。次の CJ ブラッシュアップ時にチェック |

### 反省とルール化

- 記入先：CLAUDE.md／feedback memory
- ルール候補：「コード commit と docs commit を分けない（1 PR 1 機能 = 1 commit に docs 同梱）」を feedback memory に保存するか検討。今回はユーザー指示で文書のみ独立 commit したので、強制ルールにはしない。
- 次にやること：M4-4 後半（`item_use` / `player_state` の PlayerModel 吸収）を別タスクで起票する判断はユーザーに委ねる。`src/app.py::BlockQuestApp` の整理タスクも同様。
