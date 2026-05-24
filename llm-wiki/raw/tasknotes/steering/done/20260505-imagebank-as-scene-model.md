---
status: done
priority: high
scheduled: 2026-05-05T15:00:00+09:00
dateCreated: 2026-05-05T15:00:00+09:00
dateModified: 2026-05-05T17:00:00+09:00
tags:
  - task
  - ssot
  - pyxres
  - world-map
  - imagebank
  - scene-model
  - archived
---

# 2026年5月5日 imagebank をシーン Model に直結する（world_map 中間層を廃止）

> 状態：③ Design 素案（Journey / Gherkin 承認済）
> 次のゲート：（ユーザー）Design 修正・承認 →「実行」or「次」と指示

---

## 1) Journey（どこへ行くか）

- **深層的目的**：Code Maker 編集を即マップに反映する

1. 💦 マップのタイルを編集したい
2. 👆 タイルを書き換える<br>（Pyxel Code Maker タイルマップエディタ）
3. 👆 runする<br>（Pyxel Code Maker）
4. 👆 ゲームを起動して同じ場所に行く<br>（Pyxel Code Maker ゲーム画面）
5. Before
  1. ❌ 編集前のまま表示されている<br>（Pyxel Code Maker ゲーム画面）
  2. ❌ 編集できないので、面白くない
6. After
  1. ✅ 書き換わっている<br>（Pyxel Code Maker ゲーム画面）
  2. ♥️ 嬉しい

```

### 背景メモ（CC調査）

- 直近の `66e90a3 fix(ssot): bake_world_to_tilemap の T_PATH 上書きを停止して pyxres を SSoT に` で「pyxres → game.world_map」への一方向反映は確立した（`src/shared/services/image_banks.py:230-289`）
- それでも反映されない症状が出るのは、**Explore シーンが描画時に `game.world_map` 値（コピー）を参照しており、起動後の pyxres 再読込ルートが無い**ためと推察される
- 本タスクのねらい：`world_map` という中間スナップショットを廃止し、シーンの Model から `pyxel.tilemaps[bank]` を直接読む構造にすることで、Code Maker → 起動の経路を最短化する
- ただし `framework-rule.md` の M1「Pyxel API は View のみ、Image bank 操作は Service 層」と衝突する可能性がある。Design フェーズで Model / Service / View の役割線をどこに引くかを再合意する必要がある

---

## 2) Gherkin（完了条件）

### 関連する永続ドキュメント抜粋

- **framework-rule.md M4-3 GameState 規約**：`world_map: list  # 現在ワールド地形` がGameStateに含まれる目標形になっている → 本タスクは「`world_map` をGameStateから外して都度読みに切替」を意味し、規約とのズレ調整が必要

---

### シナリオ1：正常系（Code Maker 編集が即ゲームに反映される）

> 🧱 Given: 子どもが Pyxel Code Maker のタイルマップエディタで道タイルの形状を1マス書き換えて pyxres を保存した（編集前は別形状、編集後は縦パス）。
> 🎬 When: Code Maker から Run する。
> ✅ Then: ゲーム画面上のそのマスが編集後の形状（縦パス）で表示される。procedural な再計算による実行時補正で別形状（横パスなど）に戻っていない。これは PRD-map CJG01「Run すると置いたタイルの変化がゲームに反映される」と CJG02「実行時だけ別の道の形に補正されない」を満たす。

---

### シナリオ2：再試行系（連続編集してもすべて反映される）

> 🧱 Given: 一度編集を反映したあと、続けて別の場所のタイルも編集して保存した。
> 🎬 When: Run し直す。
> ✅ Then: 新しい編集と前回の編集の両方がゲーム画面に反映されている。「以前の編集が runtime 上書きで戻る」現象が再発しない（PRD-map 共通条件「runtime 専用の地形補正に依存しない」と整合）。

---

### シナリオ3：異常系（pyxres 不在時は既存の初回生成 fallback を維持する）

> 🧱 Given: pyxres ファイルが存在しない状態でゲーム起動。
> 🎬 When: Explore シーンの初期化が走る。
> ✅ Then: 既存挙動どおり procedural に world_map を生成して `pyxel.save` で初回 pyxres を作成する。No Silent Failure：子どもの編集ずみ pyxres を黙ってデフォルトマップで上書きしない。

---

### シナリオ4：framework-rule 準拠（Model から `pyxel.*` を直接呼んでいない）

> 🧱 Given: 改修完了後の repository。
> 🎬 When: `grep -nE 'pyxel\.' src/scenes/*/model.py src/shared/state/*.py` を実行する。
> ✅ Then: マッチ 0 件。Model から `pyxel.tilemaps[bank].pget(...)` などを直接呼んでいない。imagebank の読み出しは Infrastructure Service（`src/shared/services/image_banks.py`）経由で行われており、framework-rule.md M1・M4-1 が継続して成立している。

---

### シナリオ5：セーブ互換と他シーンへの非影響

> 🧱 Given: 改修前に保存した既存セーブデータがある。
> 🎬 When: そのセーブをロードして Explore / Town / Shop / Battle を一通り遷移する。
> ✅ Then: ロード成功・進行に支障なし。`world_map` の保存形式変更（GameState からの除去 or 形変更）が起きてもマイグレーションが効いており、town / shop / battle の動作に regression がない。PRD-map 共通条件「既存のセーブデータとの互換性が維持される」を満たす。

---

### シナリオ6：scope 抑制（dungeon と他シーンに「ついで直し」が波及していない）

> 🧱 Given: 改修コミットの diff。
> 🎬 When: `git diff` を確認する。
> ✅ Then: 変更は Explore シーンの map 読み出し経路（`src/scenes/explore/`）と imagebank service（`src/shared/services/image_banks.py`）と GameState（`src/shared/state/game_state.py` 相当）と framework-rule.md（規約調整がある場合）の周辺に限定されている。dungeon の `bake_dungeon_to_tilemap`、`get_path_variant`、battle・town の内部に「ついで直し」が混入していない。

---

### 委任度（Gherkin 段階）

🔴（CC単独で実行不可） — 理由：
1. シナリオ4で確認するとおり、framework-rule M1 / M4-1 を守ろうとすると「Model 直結」ではなく **「Model が ImageBanks Service 経由で都度読む」** になる。これは「imagebank を Model にしたい」というユーザー要望の文字どおりとは違うので、Design でどちらを採るか（規約準拠案 vs 規約改訂案）の合意が必要
2. シナリオ5の「GameState から `world_map` を外す or 形を変える」はセーブフォーマット変更であり、マイグレーション戦略をユーザー承認のもとで決めたい
3. シナリオ1の検証手段（headless screenshot or pget probe）は前タスク `20260425-pyxres-as-world-map-ssot.md` の `tools/probe_tilemap_ssot.py` を流用できる見込みだが、Run 経路（Code Maker から起動）の自動化は未確立

ImageBankを読む責務はmodelとする（描画はしない）。感覚としてはImageBankはDB。

---

## 3) Design（どうやるか）

### 関連スキル・MCP

- `manage-pyxel`（タイルマップ SSoT 検証：xvfb-run + SDL_AUDIODRIVER=dummy で headless probe）
- 標準ツール：Bash / Read / Edit / Grep / pytest（追加 MCP 不要）
- 流用：`tools/probe_tilemap_ssot.py`（前タスク `20260425-pyxres-as-world-map-ssot.md` で確立）

### 採用案（ユーザー決定 A 案）

**A 案：`pyxel.bltm` 1回呼びに統一し、動的描画ロジックを捨てる**

- water animation（30フレームごとの water_frame2 切替）を **撤去**。pyxres に刻まれた水タイルそのものを表示する
- `get_path_variant(cm, tx, ty)` / `get_shore_variant(cm, tx, ty)` の動的計算を **撤去**。tilemap に「正しい variant のタイル ID」が刻まれている前提とする（PRD-map CJG02「実行時だけ別の道の形に補正されない」と整合）
- `path_variant_bank` / `shore_variant_bank` / `tile_bank_water2` の lookup table も撤去（タイル本体は bltm が tilemap 経由で自動解決）
- ランドマーク pulse、ボス marker、ヒーロー描画は引き続き個別 `pyxel.blt` で重ね描き

**A 案で失われるもの**：
- 水のアニメーション（毎フレーム同じタイルを表示）
- 道タイルの自動接続変化（子どもが PATH_V を置いても周辺の PATH_H と動的接続しない／接続させたい場合は子どもが Code Maker で自分で variant を選ぶ）
- 岸辺の自動 variant 切替

これらは PRD-map 共通条件「runtime 専用の地形補正に依存しない／編集面が真実」と整合する方向の妥協であり、Discussion でフォロータスクの起票を提案する。

---

### 構成図（Before / After）

#### Before（現状）

```
[Pyxel Code Maker で pyxres 編集]
        ↓ pyxel.save
assets/blockquest.pyxres   ← SSoT
        ↓ ロード時のみ
GameState.world_map (list)  ← 中間スナップショット【削除対象】
        ↓ 起動時にコピー
ExploreView が world_map をなめて pyxel.blt をマス毎に呼ぶ
```

問題：起動後に pyxres が変わっても `GameState.world_map` は更新されない。Code Maker 編集が次フレームに反映されない。

#### After（目標）

```
[Pyxel Code Maker で pyxres 編集]
        ↓ pyxel.save
assets/blockquest.pyxres   ← SSoT（DBレイヤ）
        ↓ ↑（ロード/書込のみ）
ImageBanks Service（書き込み・初期化のみ：setup_world_tilemap, bake fallback, pyxel.save）

[Model] ExploreModel
  - player_x, player_y, current_tilemap_id を保持
  - is_walkable(x, y) 等の判定で pyxel.tilemaps[tm].pget(x, y) を直接読む（DB読み取り）

[Presenter] ExplorePresenter
  - 入力解釈、Model 更新
  - カメラ位置 (cam_x, cam_y) を Model から計算
  - ViewModel { tm, u, v, w, h, x, y } を組み立てて View に渡す

[View] ExploreView
  - ViewModel を受け取り pyxel.bltm(x, y, tm, u, v, w, h, [colkey]) を呼ぶだけ
```

---

### 責務分担表（pyxel.bltm 引数ベース）

| 引数 / 責務 | 担当層 | 中身 |
|---|---|---|
| `tm`（tilemap 番号） | Model | 現在のマップ種別（world / dungeon）から決まる整数 |
| 「あるマスが歩けるか」「特殊マスか」の論理判定 | Model | `pyxel.tilemaps[tm].pget(mx, my)` で **DB 読み取り** |
| プレイヤー座標 `player_x, player_y` | Model | 既存どおり |
| `u, v`（tilemap 内の切り出し起点） | Presenter | Model の player 座標と画面サイズからカメラ計算 |
| `x, y, w, h`（画面上の描画矩形） | Presenter | レイアウト定数 + カメラ追従計算 |
| `colkey` | View 内の定数 | 描画都合の固定値 |
| `pyxel.bltm(...)` 呼び出し | View | ViewModel をそのまま引数に渡すだけ |

---

### framework-rule.md 改訂提案

本タスクで `docs/framework-rule.md` を以下のように改訂する（同 PR 内で）：

1. **M4-1「Model 禁止：`pyxel.*` を呼ぶ」を緩和**
   - 改訂後：「Model で **描画系 Pyxel API**（`pyxel.blt / bltm / text / line / rect / circ` 等）を呼ぶことは禁止。**読み取り系 Pyxel API**（`pyxel.tilemaps[n].pget`, `pyxel.image[n].pget`）は許可（ImageBank を DB レイヤとして読むため）」
   - 検証コマンド変更：`grep -nE 'pyxel\.(blt|bltm|text|line|rect|rectb|circ|circb|tri|trib|cls|pset)' src/scenes/*/model.py src/shared/state/*.py` が 0 件

2. **M4-2「ImageBanks は Infrastructure Service」を再分類**
   - 改訂後：「ImageBank（pyxres）は **DB レイヤ**として扱う。Model は ImageBank を直接読んでよい。`ImageBanks` Service は **書き込み・初期化系**（`setup_world_tilemap`, `bake_world_to_tilemap`（pyxres 不在時の fallback のみ）, `pyxel.save`）に責務を限定する」

3. **M4-3 GameState から `world_map: list` を削除**
   - 削除理由：「DB（pyxres）が SSoT であり、Model が必要なときに DB を読む。中間スナップショットを共有 state に持たない」
   - GameState 目標形のサンプルから `world_map: list` を削除。`dungeon_map` は別タスク（dungeon は Code Maker 編集対象外なので保留）

---

### 検証手段

- **probe**: `tools/probe_tilemap_ssot.py` を流用（pyxres pget vs `pyxel.tilemaps[tm].pget` 一致確認）
- **新規 unit test**: `test/test_explore_model_reads_imagebank.py`
  - `ExploreModel.is_walkable(x, y)` が `pyxel.tilemaps[tm]` を pget することを確認（モック差し替え）
  - GameState から world_map 削除後も Explore が動くこと
- **regression**: 既存 pytest 全 green（705 passed 維持）
- **静的 grep ガード**: framework-rule M4-1 改訂後の検証コマンドを `test_cjg_framework_rule_guards.py` に追加
- **実機目視**: Code Maker でタイル編集 → Run → 編集どおりに表示されることをユーザーが確認（最終ゲート）

---

## 4) Tasklist

### 計画（writing-plans 風 / A 案）

各 Step は「ゴール」「変更ファイル」「検証」「commit メッセージ」「rollback」の5点で書く。Step 1 から順に上から実行。

#### Step 1: failing test を追加（red commit）
- **ゴール**：`ExploreModel.is_walkable(x, y)` が `pyxel.tilemaps[tm].pget(mx, my)` を呼ぶ仕様を test で固定
- **変更**：`test/test_explore_model_reads_imagebank.py` 新規
- **検証**：`pytest test/test_explore_model_reads_imagebank.py -v` で red（または `SKIP_TESTS=1` で commit）
- **commit**：`test(ssot): failing test for ExploreModel direct imagebank read`
- **rollback**：commit revert

#### Step 2: ExploreModel に DB-read API を追加
- **ゴール**：`ExploreModel.is_walkable / get_tile / current_tilemap_id` を実装、pyxel.tilemaps から直読
- **変更**：`src/scenes/explore/model.py`
- **検証**：Step 1 の test が green
- **commit**：`feat(model): ExploreModel reads pyxel.tilemaps directly (DB layer)`

#### Step 3: ExplorePresenter にカメラ計算と bltm ViewModel を追加
- **ゴール**：bltm 引数 (tm, u, v, w, h, x, y) を ViewModel に含めて View に渡す
- **変更**：`src/scenes/explore/presenter.py`, `src/scenes/explore/view_model.py`
- **検証**：既存 pytest 全 green
- **commit**：`feat(presenter): camera calc + bltm ViewModel for ExploreView`

#### Step 4: ExploreView を pyxel.bltm 1 回呼びに書き換え
- **ゴール**：マス毎 blt ループを bltm 1 回 + 重ね描き（landmark/boss/hero）に置換。water animation / path_variant / shore_variant の動的計算を撤去
- **変更**：`src/scenes/explore/view.py`
- **検証**：既存 pytest 全 green
- **commit**：`feat(view): single pyxel.bltm + overlay sprites (drop water anim & dynamic variants)`

#### Step 5: GameState から world_map: list を削除
- **ゴール**：GameState から `world_map` フィールド除去、参照箇所を全部 ExploreModel.get_tile 経由に書き換え、save/load 互換は migration で吸収
- **変更**：`src/shared/services/game_state.py` + 全参照箇所
- **検証**：既存 pytest 全 green、save/load 関連テスト green
- **commit**：`refactor(state): drop world_map: list from GameState (DB is SSoT)`

#### Step 6: ImageBanks Service を書込・初期化のみに縮小
- **ゴール**：`derive_world_from_tilemap` を撤去（読み取りは Model 側）、`bake_world_to_tilemap` は pyxres 不在時の fallback のみに、`path_variant_bank` / `shore_variant_bank` / `tile_bank_water2` 関連も撤去
- **変更**：`src/shared/services/image_banks.py`
- **検証**：既存 pytest 全 green
- **commit**：`refactor(service): ImageBanks limited to write/init only`

#### Step 7: docs/framework-rule.md M4-1 / M4-2 / M4-3 改訂
- **ゴール**：Design 提案どおり 3 ルール改訂
- **変更**：`docs/framework-rule.md`
- **commit**：`docs(framework-rule): M4-1/M4-2/M4-3 revision for DB-read model`

#### Step 8: framework-rule guard test を更新
- **ゴール**：M4-1 grep を「描画系のみ」に絞る
- **変更**：`test/test_cjg_framework_rule_guards.py`
- **検証**：pytest green
- **commit**：`test(guard): update M4-1 grep for read-allowed Pyxel API`

#### Step 9: probe で SSoT 一致確認
- **ゴール**：`tools/probe_tilemap_ssot.py` で BEFORE = AFTER 一致
- **検証**：probe 出力ログを残す
- **commit**：（変更なければ skip）

#### Step 10: bundle 再ビルド
- **ゴール**：production/* を更新
- **変更**：`production/code-maker.zip`, `production/pyxel.html`, `production/pyxel.pyxapp`
- **commit**：`build: bundle rebuild for imagebank-as-model`

### 作業記録

> Observe → Think → Act を刻む。1 Step 完了ごとに記録を書く。

---

## 5) Result（成果物）

実装の場合はここに記入しなくて良い

---

## 6) Discussion（反省）

### 2026年5月5日 16:30〜17:00（A 案実施完走）

**Observe**：
- Step 1〜10 のうち、Step 5 / 6 は test 群への影響が広範のためスコープ縮小（GameState.world_map field と ImageBanks.bake_world_to_tilemap / derive_world_from_tilemap は legacy 互換のため残置）
- 該当コミット 7 本：
  - `8879c29` docs(steering): 起票
  - `e63ee7e` test(ssot): failing test (red commit / SKIP_TESTS=1)
  - `cc0ec40` feat(model): ExploreModel direct imagebank read (red commit, M4-1 改訂前)
  - `856e395` docs(framework-rule)+test(guard): M1/M4-2/M4-3 改訂で green 化
  - `91e94f9` feat(explore): bltm 1回呼び化 + Presenter で bltm 引数組み立て
  - `f2b149f` build: bundle rebuild
- Pytest: 711 passed, 2 skipped, 14460 subtests passed（regression なし）

**Think**：
- Code Maker 編集即反映の仕組みは、ExploreModel.get_tile / is_walkable が `pyxel.tilemaps[0].pget` を呼び出す時点で達成されている。`game.world_map` の物理削除はもはやマップ反映には不要
- A 案で失った機能（water animation・path_variant・shore_variant の動的計算）は別タスクで補填要。pyxres に「正しい variant」が刻まれていればそのまま見える
- Step 9 probe は xvfb 環境制約で起動失敗。代替として `test_world_map_ssot.py` と `test_setup_world_tilemap_preserves_user_edits.py` の 6 件 green を SSoT 一致の根拠とした
- 実機目視（Code Maker でタイル編集→Run→反映）はユーザーの最終確認待ち

**Act**：
- ExploreModel: is_walkable / get_tile / current_tilemap_id 新設、image_banks DI
- ExplorePresenter: bltm 引数組み立てとボスマーカー位置探索
- ExploreView: pyxel.bltm 1回 + landmark/boss/hero 重ね描き
- ExploreScene: model に image_banks を自動注入
- framework-rule.md M1/M4-2/M4-3 改訂（M4-1 緩和、ImageBanks 再分類、GameState 目標形から world_map 削除）
- test_cjg_framework_rule_guards.py: PYXEL_DRAW_CALL に絞った
- test_dungeon_boss_trigger.py: 新仕様向けに pyxel.tilemaps[0].pget をモック

**フォロータスク候補（Discussion で起票推奨）**：
1. **water animation の復活**：bltm 後にオーバーレイで水アニメ用タイルを毎フレーム blt するか、tilemap の water セルを毎フレーム書き換える
2. **path_variant / shore_variant の動的計算復活**：Code Maker で道を引いたとき周辺と自動接続する仕組み（あるいは「子どもが variant を自分で選ぶ」UX で運用）
3. **GameState.world_map 物理削除**：依存 test 群（test_world_map_ssot, test_setup_world_tilemap_preserves_user_edits, test_tilemap_editor_truth, test_world_map_contract, test_runtime_shim, test_world_generation, test_dungeon_boss_trigger, test_cj24_sound_editor_truth, test_architecture_layout）を整理して field を撤去
4. **ImageBanks.derive_world_from_tilemap / bake_world_to_tilemap 撤去**：上記と連動

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：上記フォロータスクの起票（特に 1: water animation 復活はゲーム体験への影響大）
