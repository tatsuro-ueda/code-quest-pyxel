---
status: latest
dateCreated: 2026-05-26
dateModified: 2026-05-26
---

# Development Checklist

> 生成元：`make-development-checklist` skill（`~/.claude/skills/make-development-checklist/SKILL.md`）
> 根拠 docs：`docs/architecture.md` / `docs/repository-structure.md` / `docs/framework-rule.md` / `docs/ux-policy.md`
> 用途：設計・実装・レビュー時の網羅チェック（3 シーン統合版）
> 更新方針：上記 4 文書のいずれかが変わったら `/make-development-checklist save` で再生成し、`dateCreated` を更新する

## A 章：アーキテクチャ・採用技術（24 項目、根拠：docs/architecture.md）

### A1. 製品の前提

- [ ] `.pyxres` を AI / runtime が直接編集していない（根拠：1 章「子どもが正本を編集する」）
- [ ] AI が自力で発見・検証できる規約配置を維持している（根拠：1 章 / M5）
- [ ] 中央集権クラスや一時 UI を新規追加していない（根拠：1 章・CJ44）

### A2. 採用技術と役割

- [ ] Pyxel API は `src/runtime/` / `src/scenes/*/view.py` / build 系に閉じている（根拠：2 章）
- [ ] Python 3 ゲーム本体が `src/` 配下に書かれている（根拠：2 章）
- [ ] ブラウザ実行は `dist/pyxel.html`（`pyxel app2html` 生成）経由のみ（根拠：2 章）
- [ ] save / Code Maker import は `save_store.py` / `browser_resource_override.py` の JS bridge 経由（根拠：2 章）
- [ ] Web プレイ記録は `play_session_logging.py` の sqlite3 のみが扱う（根拠：2 章）
- [ ] テストは `test/` 配下、pytest 実行（根拠：2 章）
- [ ] 配布 HTML の互換確認は Playwright（`tools/test_web_compat.py`）が行う（根拠：2 章）
- [ ] YAML 編集は `assets/*.yaml`、`src/generated/` は手で触らない(根拠：2 章・3.4）
- [ ] 開発環境は exe.dev VM、HTTPS proxy 経由（根拠：2 章・5 章）
- [ ] exe.dev VM の undocumented local endpoint を使用していない（根拠：5 章）

### A3. 採用技術から導かれる制約

- [ ] `pyxel.*` 描画 API が View / 最外殻だけで呼ばれている（根拠：4 章 / M1-1）
- [ ] 入力はフレーム冒頭で snapshot 化し Presenter は `InputStateTracker` 経由（根拠：4 章 / M1-2）
- [ ] 単一 main.py 制約に対し bundler で concat（手 inlined 維持禁止）（根拠：4 章）
- [ ] `pyxres` = SSoT、runtime は読み取りのみ（根拠：4 章）
- [ ] `SaveStore` Protocol で 3 実装（InMemory / File / LocalStorage）切替（根拠：4 章）
- [ ] dev / prod artifact 分離なし、`dist/` 一本化（根拠：4 章 / single_distribution_policy）
- [ ] `tools/test_headless.py` / `test_web_compat.py` を build gate に配置（根拠：4 章）
- [ ] `tools/hooks/*.sh` + `.claude/settings.json` の 2 系統 guardrail が機能（根拠：4 章 / M5-3）
- [ ] AGENTS.md ≤100 行が保たれている（根拠：4 章 / static guard）
- [ ] 子ども向け UI はひらがな表記・iframe 全画面・ボタンフェードアウト（根拠：4 章 / ui_policy）
- [ ] `src/` モジュール冒頭に関数・クラスを箇条書きする日本語 docstring（根拠：4 章 / module_docstring_policy）

## B 章：リポジトリ構造・責務分担（33 項目、根拠：docs/repository-structure.md）

### B1. 構造上の規約

- [ ] `src/` と `assets/` が source of truth、`dist/` は配布物のみ（根拠：構造 2 章）
- [ ] root `main.py` は 8 行 wrapper、runtime 本体は `src/runtime/app.py`（根拠：構造 2 章）
- [ ] runtime monolith の inlined コピーは bundler 自動生成（手で維持しない）（根拠：構造 2 章）
- [ ] Scene は MVP パターン（model / view / presenter / scene）（根拠：構造 2 章）
- [ ] scene 横断 state は `GameState` に集約して DI（根拠：構造 2 章）

### B2. ディレクトリ別責務

- [ ] `src/runtime/app.py::Game` にドメインロジックを書かない（根拠：構造 7 章）
- [ ] `Game.__init__` で deprecated field を直接初期化しない（@property forward のみ）（根拠：構造 4.1 / 7 章）
- [ ] `src/game_data.py` 経由でのみ YAML 生成物が runtime に供給される（根拠：構造 4.2）
- [ ] `src/scenes/*/model.py` で `pyxel.blt()` 等の描画系を呼ばない（根拠：構造 7 章）
- [ ] `src/scenes/*/view.py` に save / logging / build を書かない（根拠：構造 7 章）
- [ ] `src/scenes/*/presenter.py` で scene 外の永続化を行わない（根拠：構造 7 章）
- [ ] `src/shared/services/` が単一 scene の scene-local state を持たない（根拠：構造 7 章）
- [ ] `image_banks.py` が pyxres / pyxel.tilemaps の **読み取り**を担わない（根拠：構造 4.5 / 7 章）
- [ ] `world_generation.py` の戻り値を runtime / scene が snapshot で持たない（根拠：構造 7 章）
- [ ] `audio_system.py` にメロディ / SE 定義の正本を置かない（根拠：構造 4.5 / 7 章）
- [ ] `codemaker_resource_store.py` が「どの場面でどの音を鳴らすか」を決めない（根拠：構造 7 章）
- [ ] `assets/` に build 済みファイルを置かない（根拠：構造 7 章）
- [ ] `templates/` に完成 HTML を置かない（根拠：構造 5.4 / 7 章）
- [ ] `dist/` に source を置かない（根拠：構造 5.5 / 7 章）
- [ ] `GameState` がサービスインスタンスを持たない（dataclass values のみ）（根拠：構造 4.5 / 6.2）

### B3. レイヤー依存と循環防止

- [ ] `shared/services/` が `scenes/` / `runtime/` を import しない（根拠：構造 6.1）
- [ ] `shared/ui/` が `shared/services/` を import しない（根拠：構造 6.1）
- [ ] `shared/services/scene_manager.py` が Scene オブジェクトを保持しない（根拠：構造 4.5 / 6.1）
- [ ] scene 同士が直接 import しない（根拠：構造 6.1）

### B4. build / test / guardrail 運用

- [ ] BGM / pyxres / view / scene 変更時は `PYTHONPATH=. python tools/build_web_release.py` を実行（根拠：構造 3.5.2 / 3.5.3）
- [ ] bundle 内に旧シンボル（`AudioManager` / `SettingsScene` 等）が残っていない（根拠：構造 3.5.3）
- [ ] Code Maker zip の編集結果は `assets/blockquest.pyxres` を直接 SSoT として更新（根拠：構造 3.5.4）
- [ ] **preview / current 昇格 flow は使わない**（2026-05 廃止、`--promote` 禁止）（根拠：構造 3.5.4）
- [ ] `tools/hooks/*.sh` が `src/generated` 手書き・`.pyxres` 不正書換えを止める（根拠：構造 5.2）
- [ ] `test_architecture_layout.py` と `test_cjg_framework_rule_guards.py` が green（根拠：構造 5.3）

### B5. observability lane

- [ ] `play_session_logging.py` が Web プレイ記録 + IP / UA / browser を sqlite に集計（根拠：構造 5.2 後）
- [ ] `tools/web_runtime_server.py` が実公開 lane の server 入口として動く（根拠：構造 5.2 後）
- [ ] `tools/report_play_sessions.py` が人間可読レポートを生成する（根拠：構造 5.2 後）

## C 章：コーディング規約 M1〜M5（47 項目、根拠：docs/framework-rule.md）

### C1. SSoT（4 項目）

- [ ] 生データを直接読まない（M0 SSoT）
- [ ] 同じ意味のデータを複数箇所に持たない（M0 SSoT）
- [ ] ユーザー編集より自動生成を優先しない（M0 SSoT）
- [ ] dialogue は `assets/dialogue.yaml → gen_data → src/generated/dialogue.py → game_data.py` の一方向（M0 SSoT 一方向経路）

### C2. Golden Path（3 項目）

- [ ] 起動・メニュー・店・戦闘の主要導線を最低 1 回通す（M0 Golden Path）
- [ ] bundle や実機確認を後回しにしない（M0 Golden Path）
- [ ] **Code Maker zip も headless 起動（`Game()` 初期化 + 1 フレーム描画）まで通す**（M0 Golden Path）

### C3. M1：Pyxel API と入力は View / 最外殻だけ（7 項目）

- [ ] 描画系 API が許可リスト内（views / 最外殻 / shared/ui / audio_system / image_banks）だけで呼ばれる（M1-1）
- [ ] Model / Presenter / 許可外 services / shared/state で描画系を呼ばない（M1-1）
- [ ] Model からの読み取り系（`tilemaps[n].pget` / `images[n].pget`）は DB レイヤとして適切（M1-1）
- [ ] 入力（`pyxel.btn` / `btnp`）が View で読まれない（M1-2）
- [ ] 入力が Model / Presenter / Service / shared/state で読まれない（M1-2）
- [ ] Presenter は `InputStateTracker` snapshot 経由で入力を見る（M1-2）
- [ ] View で許可される描画は `cls / text / rect / rectb / blt / bltm` 中心（M1-3）

### C4. M2：View は ViewModel しか見ない（5 項目）

- [ ] View のシグネチャが `vm: *ViewModel`、GameState / Model 直渡しなし（M2-2）
- [ ] ViewModel に「解釈前」フィールド（`is_poisoned` / `*_ratio` 等）がない（M2-2）
- [ ] ViewModel は描画用データ（文字列・色・座標・ID・flag・選択・ゲージ）だけ（M2-2）
- [ ] View で `if hp_ratio < 0.3:` のような判断ロジックを書かない（M2-1）
- [ ] View で入力 / GameState 変更 / セーブ / 戦闘進行 / 遷移 / Service 直利用なし（M2-1）

### C5. M3：Presenter は入力解釈・Scene 遷移・副作用指揮のみ（10 項目）

- [ ] Presenter で `pyxel.*` の直接描画なし（M3-1）
- [ ] Presenter で生の座標計算を大量に書かない（M3-1）
- [ ] Presenter に長大なゲームルールを埋め込まない（M3-1）
- [ ] Presenter が scene-local state を勝手に複製しない（M3-1）
- [ ] 不要な shared state を増やさない（M3-1）
- [ ] Scene 間遷移の決定は Presenter 配下のみ（M3-2）
- [ ] Scene は配線に留まり、ルール / 描画 / Service ロジックを書かない（M3-2）
- [ ] Scene interface が統一されている（M3-2）
- [ ] 副作用が command として返される（M3-3）
- [ ] Presenter テストで状態変更と発行コマンドを分けて assertion（M3-3）

### C6. M4：Model は dataclass 中心、共有状態は明示（18 項目）

- [ ] Model が `pyxel.*` を呼ばない（読み取り系は許可）（M4-1）
- [ ] Model が音を鳴らさない（M4-1）
- [ ] Model が画面遷移を実行しない（M4-1）
- [ ] Model が保存処理を直接呼ばない（M4-1）
- [ ] Model がメッセージを画面表示しない（M4-1）
- [ ] Model に `sleep` や時刻依存を直接書かない（M4-1）
- [ ] Model が他 Scene の内部状態を直接触らない（M4-1）
- [ ] 新規 state は `dataclass`（`dict` 新規導入禁止）（M4-1）
- [ ] ミュータブルなネスト構造を最小限に抑える（M4-1）
- [ ] Service が A:Infrastructure / B:Domain Support / C:UI Support に分類されている（M4-2）
- [ ] Service の状態は「外部資源キャッシュ / UI 演出進行 / 入力履歴 / 保存対象外」のみ（M4-2）
- [ ] セーブ対象のゲーム進行は Model / GameState 側（M4-2）
- [ ] GameState に scene 横断＋保存価値のあるものが入っている（M4-3）
- [ ] GameState に一時 UI / アニメ途中値 / VFX タイマー / 一時入力履歴を入れない（M4-3）
- [ ] `Game.current_town / debug_mode / debug_seq / state / prev_state` を Game に直接初期化しない（M4-3）
- [ ] `world_map / dungeon_map / dungeon_rooms` を復活させない（M4-3）
- [ ] PlayerModel が `apply_damage / heal / use_item / gain_exp / can_use_spell` を保持（M4-4）
- [ ] `player[...]` の dict アクセスが残っていない（M4-4）

## D 章：UX 方針（27 項目、根拠：docs/ux-policy.md）

### D1. 子どもが読める表記（3 項目）

- [ ] せりふ / メニュー / エラー文言はひらがな中心（D1）
- [ ] 漢字を使うときは文脈だけで意味が取れるかを先に確認（D1）
- [ ] 子ども向け表示で英語や内部用語をそのまま出さない（D1）

### D2. いま選んでいる操作だけを見せる（5 項目）

- [ ] 画面上で競合する案内を同時に重ねない（D2）
- [ ] 前の操作結果メッセージが次の選択 UI を隠さない（D2）
- [ ] 会話 UI では現在ページだけを表示し、前ページが残らない（D2）
- [ ] ガイドは次の一歩を示すが、答えを全部は表示しない（D2）
- [ ] 「次に踏む場所が見て分かる」目印（最奥キャラ等）を口頭説明の代替にする（D2）

### D3. 押した実感を返す（3 項目）

- [ ] ボタン / 選択肢は、押した直後に見た目か音で変化を返す（D3）
- [ ] 画面遷移は CJ44 方針で即時切替を優先（複雑なフェードより）（D3）
- [ ] 進行不能 / エラー時は子どもが次に何をすべきかを短く返す（D3）

### D4. 危険操作は無言で通さない（4 項目）

- [ ] 保存上書き / データ削除 / 子どもの変更を失う操作には確認を入れる（D4）
- [ ] 子どもの編集面である Code Maker を内部都合で脇役化しない（D4）
- [ ] AI 側の都合で `.pyxres` や Code Maker 編集内容（効果音・音楽・画像）を勝手に置き換えない（D4）
- [ ] **Code Maker import UI は zip 内 code を採用せず、絵・音・タイルマップなど resource だけを戻す**（D4）

### D5. Web 共有は見せやすさを優先（5 項目）

- [ ] URL を開いたらすぐ遊べることを優先（D5）
- [ ] スマホで全画面プレイできる導線を保つ（D5）
- [ ] 共有導線を壊す変更は公開 URL 相当の実物確認まで done にしない（D5）
- [ ] **selector page で `あそんでみる` を dead link にしない**（D5）
- [ ] **preview source が無いときは古い card を見せず、card 自体を出さない**（D5）

### D6. 親は補助者であり、決定者ではない（3 項目）

- [ ] フィードバックをどう反映するかの最終判断は子どもが持つ（D6）
- [ ] 親向けの補助 UI / ログは子どもの体験を邪魔しない位置づけ（D6）
- [ ] 子どもが「自分たちのゲーム」と言える流れを崩さない（D6）

### D7. 小さな迷いを溜めない（具体事例、4 項目）

- [ ] 宿屋のコストを「とまる？」の前に見せる（D7）
- [ ] 店の `所持` バッジは clipping せず短く読める表記にする（D7）
- [ ] HP / MP 満タンの宿屋利用はスキップして gold を減らさない（D7）
- [ ] Code Maker 版 status bar の zone 名描画で未定義エラーを出さない（D7）

---

**合計：A 24 + B 33 + C 47 + D 27 = 131 項目**
