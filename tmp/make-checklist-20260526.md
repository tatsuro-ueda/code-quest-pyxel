# make-checklist 出力（2026-05-26）

> 生成元：`~/.claude/skills/make-checklist/SKILL.md`
> 根拠 docs：`docs/architecture.md` / `docs/repository-structure.md` / `docs/framework-rule.md`
> 用途：設計・実装・レビュー時の網羅チェック（3 シーン統合版、100 項目）

---

## A. アーキテクチャ・採用技術（25 項目、根拠：docs/architecture.md）

### A1. 製品の前提（3 項目）

- [ ] `.pyxres` を AI / runtime が直接編集していない（根拠：架空 1 章）
- [ ] AI が自力で発見・検証できる規約配置を維持している（根拠：架空 1 章 / M5）
- [ ] 中央集権クラスや一時 UI を新規追加していない（根拠：架空 1 章・CJ44）

### A2. 採用技術と役割（10 項目）

- [ ] Pyxel API の使用箇所が `src/runtime/` / `src/scenes/*/view.py` / build 系に閉じている（根拠：架空 2 章）
- [ ] Python ゲーム本体は `src/` 配下に書かれている（根拠：架空 2 章）
- [ ] ブラウザ実行は `dist/pyxel.html`（`pyxel app2html` 生成）経由のみ（根拠：架空 2 章）
- [ ] save / Code Maker import は `save_store.py` / `browser_resource_override.py` の JS bridge 経由（根拠：架空 2 章）
- [ ] Web プレイ記録は `play_session_logging.py` の sqlite3 のみが扱う（根拠：架空 2 章）
- [ ] テストは `test/` 配下、pytest 実行(根拠：架空 2 章）
- [ ] 配布 HTML の互換確認は Playwright（`tools/test_web_compat.py`）が行う（根拠：架空 2 章）
- [ ] YAML 編集は `assets/*.yaml`、`src/generated/` は自動生成物として直接編集していない（根拠：架空 2 章・3.4）
- [ ] 開発環境は exe.dev VM、HTTPS proxy 経由でブラウザ確認（根拠：架空 2 章・5 章）
- [ ] exe.dev VM の undocumented local endpoint を使用していない（根拠：架空 5 章）

### A3. 採用技術から導かれる制約（12 項目）

- [ ] `pyxel.*` 描画 API が View / 最外殻だけで呼ばれている（根拠：架空 4 章 / framework M1-1）
- [ ] 入力（`pyxel.btn` / `btnp`）はフレーム冒頭で snapshot 化し Presenter は `InputStateTracker` 経由（根拠：架空 4 章 / framework M1-2）
- [ ] 単一 main.py 制約に対し bundler で concat（手 inlined 維持禁止）（根拠：架空 4 章）
- [ ] `pyxres` = SSoT、runtime は読み取りのみ（ImageBanks は書き込み・初期化・fallback のみ）（根拠：架空 4 章 / M4-2）
- [ ] `SaveStore` Protocol で 3 実装（InMemory / File / LocalStorage）を切替（根拠：架空 4 章）
- [ ] dev / prod artifact 分離なし、`dist/` 一本化（根拠：架空 4 章 / single_distribution_policy）
- [ ] YAML 直読禁止、`src/generated/` 直書き禁止（根拠：架空 4 章）
- [ ] `tools/test_headless.py` / `test_web_compat.py` が build gate に組み込まれている（根拠：架空 4 章）
- [ ] `tools/hooks/*.sh` + `.claude/settings.json` の 2 系統 guardrail が機能している（根拠：架空 4 章 / M5-3）
- [ ] `AGENTS.md` ≤100 行が保たれている（根拠：架空 4 章 / static guard）
- [ ] 子ども向け UI はひらがな表記・iframe 全画面・ボタンフェードアウト（根拠：架空 4 章 / ui_policy）
- [ ] `src/` モジュール冒頭に関数・クラスを箇条書きする日本語 docstring（`from __future__` より前）（根拠：架空 4 章 / module_docstring_policy）

---

## B. リポジトリ構造・責務分担（30 項目、根拠：docs/repository-structure.md）

### B1. 構造上の規約（5 項目）

- [ ] `src/` と `assets/` が source of truth、`dist/` は配布物のみ（source なし）（根拠：構造 2 章）
- [ ] root `main.py` は 8 行 wrapper、runtime 本体は `src/runtime/app.py`（根拠：構造 2 章）
- [ ] Scene は MVP パターン（model / view / presenter / scene）（根拠：構造 2 章）
- [ ] scene 横断 state は `GameState` に集約して DI（根拠：構造 2 章）
- [ ] runtime monolith の inlined コピーは bundler 自動生成（手で維持しない）（根拠：構造 2 章 / 7 章）

### B2. ディレクトリ別責務（15 項目）

- [ ] `src/runtime/app.py::Game` に戦闘ロジック等のドメイン責務が書かれていない（根拠：構造 7 章）
- [ ] `Game.__init__` で deprecated field（`current_town` 等）を直接初期化していない（@property forward のみ）（根拠：構造 4.1 / 7 章）
- [ ] `src/game_data.py` 経由でのみ YAML 生成物が runtime に供給されている（根拠：構造 4.2）
- [ ] `src/scenes/*/model.py` で `pyxel.blt()` 等の描画系を呼んでいない（根拠：構造 7 章）
- [ ] `src/scenes/*/view.py` に save / logging / build が書かれていない（根拠：構造 7 章）
- [ ] `src/scenes/*/presenter.py` で scene 外の永続化を行っていない（根拠：構造 7 章）
- [ ] `src/shared/services/` が単一 scene の scene-local state を持っていない（根拠：構造 7 章）
- [ ] `image_banks.py` が pyxres / pyxel.tilemaps の **読み取り**を担っていない（読み取りは Model 直読）（根拠：構造 4.5 / 7 章）
- [ ] `world_generation.py` の戻り値を runtime / scene が snapshot で持っていない（pyxres = SSoT）（根拠：構造 7 章）
- [ ] `audio_system.py` にメロディ / SE 定義の正本を置いていない（根拠：構造 4.5 / 7 章）
- [ ] `codemaker_resource_store.py` が「どの場面でどの音を鳴らすか」を決めていない（根拠：構造 7 章）
- [ ] `assets/` に build 済みファイルを置いていない（根拠：構造 7 章）
- [ ] `templates/` に完成 HTML を置いていない（根拠：構造 5.4 / 7 章）
- [ ] `dist/` に source を置いていない（根拠：構造 5.5 / 7 章）
- [ ] `GameState` がサービスインスタンスを持っていない（dataclass values のみ）（根拠：構造 4.5 / 6.2）

### B3. レイヤー依存と循環防止（4 項目）

- [ ] `shared/services/` が `scenes/` / `runtime/` を import していない（根拠：構造 6.1）
- [ ] `shared/ui/` が `shared/services/` を import していない（ui は座標計算のみ）（根拠：構造 6.1）
- [ ] `shared/services/scene_manager.py` が Scene オブジェクトを保持していない（state holder のみ）（根拠：構造 4.5 / 6.1）
- [ ] scene 同士が直接 import していない（共有は GameState / services 経由）（根拠：構造 6.1）

### B4. build runbook（4 項目）

- [ ] BGM / pyxres / view / scene 変更時は `PYTHONPATH=. python tools/build_web_release.py` を実行（根拠：構造 3.5.2 / 3.5.3）
- [ ] bundle 内に旧シンボル（`AudioManager` / `SettingsScene` 等）が残っていないことを 3.5.3 の自己検査で確認（根拠：構造 3.5.3 / 3.5.4）
- [ ] `dist/code-maker.zip` の編集結果は `assets/blockquest.pyxres` を直接 SSoT として更新（根拠：構造 3.5.4）
- [ ] `python tools/build_release_artifacts.py` を直接叩かず `PYTHONPATH=. python tools/build_web_release.py` を使う（根拠：構造 3.5.4）

### B5. test と guardrail（2 項目）

- [ ] `test_architecture_layout.py` と `test_cjg_framework_rule_guards.py` が green（根拠：構造 5.3）
- [ ] `tools/hooks/*.sh` が `src/generated` 手書き・`.pyxres` 不正書換えを止める運用（根拠：構造 5.2）

---

## C. コーディング規約 M1〜M5（45 項目、根拠：docs/framework-rule.md）

### C1. M1：Pyxel API と入力は View / 最外殻だけ（7 項目）

- [ ] 描画系 API（`blt` / `bltm` / `text` / `line` / `rect` / `rectb` / `circ` / `circb` / `cls` / `pset`）が `views/` / 最外殻 / `shared/ui/` / `audio_system.py` / `image_banks.py` の許可リスト内だけで呼ばれている（M1-1）
- [ ] `models` / `presenters` / `services`（許可リスト除く）/ `shared/state` で描画系を呼んでいない（M1-1）
- [ ] Model からの読み取り系（`tilemaps[n].pget` / `images[n].pget`）は DB レイヤとして適切（M1-1）
- [ ] 入力（`pyxel.btn` / `btnp`）が View で読まれていない（View は ViewModel のみ）（M1-2）
- [ ] 入力が Model / Presenter / Service / shared/state で読まれていない（最外殻と InputStateTracker のみ）（M1-2）
- [ ] Presenter は `InputStateTracker` の snapshot（`pressed` / `just_pressed` / `just_released`）経由で入力を見る（M1-2）
- [ ] View で許可される描画は `cls` / `text` / `rect` / `rectb` / `blt` / `bltm`、条件付きで `line` / `circ` / `circb` / `clip` / `camera`（M1-3）

### C2. M2：View は ViewModel しか見ない（5 項目）

- [ ] View 関数のシグネチャが `vm: *ViewModel` で GameState / Model を直接受け取っていない（M2-2）
- [ ] ViewModel に `is_poisoned` / `*_ratio` のような「解釈前」フィールドが含まれていない（M2-2）
- [ ] ViewModel が描画用データ（文字列・色・座標・スプライト ID・可視 flag・選択位置・ゲージ長）だけを持つ（M2-2）
- [ ] View で `if hp_ratio < 0.3:` のような判断ロジックを書いていない（Presenter で済ませる）（M2-1）
- [ ] View で入力取得 / GameState 変更 / セーブロード / 戦闘進行 / 遷移判断 / Service 直接利用を行っていない（M2-1）

### C3. M3：Presenter は入力解釈・Scene 遷移・副作用指揮のみ（10 項目）

- [ ] Presenter で `pyxel.text` 等の直接描画を行っていない（M3-1）
- [ ] Presenter で生の座標計算を大量に書いていない（shared/ui レイアウト helper 経由）（M3-1）
- [ ] Presenter に長大なゲームルールを埋め込んでいない（Model 側）（M3-1）
- [ ] Presenter が scene-local state を勝手に複製していない（M3-1）
- [ ] 不要な shared state を増やしていない（GameState / Service に明示）（M3-1）
- [ ] Scene 間遷移の決定が Presenter 配下のみで行われている（M3-2）
- [ ] Scene は配線（Scene-local Model / Presenter / View / `update` / `draw` 入口）に留まり、ルール / 描画 / Service ロジックを書いていない（M3-2）
- [ ] Scene interface が統一されている（`update(input_state)` / `present()` または同等）（M3-2）
- [ ] 副作用が command（`PlaySfx` / `ShowMessage` / `ChangeScene` / `SaveGame`）として返されている（M3-3）
- [ ] Presenter テストで「状態変更」と「発行コマンド」を分けて assertion している（M3-3）

### C4. M4：Model は dataclass 中心、共有状態は明示（18 項目）

- [ ] Model が `pyxel.*` を呼んでいない（読み取り系は許可）（M4-1）
- [ ] Model が音を鳴らしていない（View が `pyxel.playm` 担当）（M4-1）
- [ ] Model が画面遷移を実行していない（Presenter 担当）（M4-1）
- [ ] Model が保存処理を直接呼んでいない（SaveStore 経由、Presenter トリガ）（M4-1）
- [ ] Model がメッセージを画面表示していない（MessageDisplay → View）（M4-1）
- [ ] Model に `sleep` や時刻依存が直接書かれていない（M4-1）
- [ ] Model が他 Scene の内部状態を直接触っていない（M4-1）
- [ ] 新規 state が `dataclass` で宣言されている（`dict` 新規導入禁止）（M4-1）
- [ ] ミュータブルなネスト構造を最小限に抑えている（M4-1）
- [ ] Service が A:Infrastructure / B:Domain Support / C:UI Support に分類されている（M4-2）
- [ ] Service の状態が「外部資源キャッシュ / UI 演出進行 / 入力履歴 / 保存対象外」のいずれか（M4-2）
- [ ] セーブ対象のゲーム進行は Model / GameState 側に置かれている（M4-2）
- [ ] GameState に scene 横断＋保存価値のあるもの（player / 所持金 / 進行 flag / 現在マップ / 位置）が入っている（M4-3）
- [ ] GameState に一時 UI / アニメ途中値 / VFX タイマー / 一時入力履歴を入れていない（M4-3）
- [ ] `Game.current_town / debug_mode / debug_seq / state / prev_state` を Game に直接初期化していない（@property forward のみ）（M4-3）
- [ ] `world_map / dungeon_map / dungeon_rooms` を復活させていない（撤去済み）（M4-3）
- [ ] PlayerModel が `apply_damage` / `heal` / `use_item` / `gain_exp` / `can_use_spell` のルールを保持（M4-4）
- [ ] `player[...]` の dict アクセスが残っていない（PlayerModel 経由）（M4-4）

### C5. M5：層規約は検証可能な形で可視化（5 項目）

- [ ] Scene が `src/scenes/<scene>/{model,presenter,view,view_model?,scene}.py` の階層（M5-1）
- [ ] クラス命名が `<Scene>Model` / `<Scene>Presenter` / `<Scene>View` / `<Scene>ViewModel`（M5-1）
- [ ] テスト優先順位 1〜6（Model 単体 → Presenter → Scene 結合 → View smoke → headless → 実機）を踏まえている（M5-2）
- [ ] Pyxel 描画結果に強く依存するテストや fragile な frame 依存テストを書いていない（M5-2）
- [ ] `docs/architecture.md` / `docs/repository-structure.md` / `docs/framework-rule.md` の 3 層が AGENTS.md から到達できる構造（M5-3）

---

合計：A 25 + B 30 + C 45 = **100 項目**
