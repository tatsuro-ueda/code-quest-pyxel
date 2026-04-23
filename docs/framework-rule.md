## Point

あなたの状況なら、**Pyxel向けMVPは「一般論のMVP」ではなく、かなり厳しめの“実装規約つきMVP”にした方がうまく回ります。**
理由は3つです。

1. **1万行RPG**は、自由度が高いとすぐ崩れる
2. **PyxelはAPIが低レベル**なので、油断すると描画・入力・状態変更が混ざりやすい
3. **テスト超重要**なら、「どこで何をしてよいか」を機械的に決める方が強い

なので、今回は
**「Pyxel用MVP規約」**
として、かなりパッキリした形を提案します。

---

## Reason

### 1. なぜ普通のMVPでは足りないのか

MVPは本来、

* Model = 状態とルール
* View = 表示
* Presenter = 仲介

という考え方です。
ただし、これだけだと**人によって解釈が広すぎる**です。

たとえば Presenter が

* 入力を見る
* 状態を変える
* 遷移も決める
* 描画命令も直接出す
* メッセージ表示も触る

というふうに太っていくと、見た目はMVPでも中身は再び密結合になります。

あなたはすでに

* `GameState`
* Service分離
* Scene-local Model
* グローバル変数なし

まで来ているので、次に必要なのは
**「構造」より「交通ルール」**です。

---

### 2. なぜ厳しい規約が向いているのか

あなたは

* 拡張前提
* テスト重視
* AIに実装を触らせたい
* 規約がパッキリしている方が考えやすい

という条件です。
この場合、柔らかい設計よりも、**禁止事項が明確な設計**の方が強いです。

特にAIは、曖昧な設計だとすぐに

* Viewで状態変更
* Presenterで直接 `pyxel.blt`
* Modelから音を鳴らす
* Serviceをどこからでも触る

をやります。
つまり、**AIガードレールとして規約を使う**べきです。

---

### 3. Pyxelでは「描画APIを隔離する」のが重要

Pyxelは便利ですが、`pyxel.text()` や `pyxel.blt()` をどこからでも呼べるので、
少しでも油断すると**表示ロジックがゲームロジックに侵入**します。

だから、極端なくらいでちょうどよいです。
あなたの言う

> viewはpyxel.cls()、pyxel.text()、pyxel.rect()、pyxel.blt() だけ！

この方向はかなり正しいです。
厳密には `line`, `circ`, `clip`, `camera` などを使う場面はあるでしょうが、思想としては非常によいです。

---

## Example

以下、**Pyxel RPG向けMVP規約 v1**として提案します。

---

# 1. 最上位原則

## 1-1. 依存方向

依存は必ず次の向きです。

**View → なし**
**Presenter → Model / Service / View用DTO生成**
**Model → なし**
**Service → 外部資源・共通機能**

さらに厳密に言うと、

* **View は Model を知らない**
* **Model は Pyxel を知らない**
* **Model は Scene を知らない**
* **Scene 間遷移の決定権は Presenter にある**
* **Pyxel API を直接呼んでよいのは View 層だけ**

---

## 1-2. 1フレームの流れ

1フレームの処理順を固定します。

1. `input snapshot` を取得
2. Presenter が入力を解釈
3. Model を更新
4. Presenter が描画用データを作る
5. View が描画する

つまり：

**input → update → present → render**

これを崩さないことです。

---

# 2. 層ごとの責務

## 2-1. Model 規約

### Modelの役割

* 状態を持つ
* ルールを持つ
* 計算する
* 遷移条件を持つ

### Modelでやってよいこと

* HP計算
* レベルアップ判定
* 戦闘進行
* アイテム増減
* 位置更新
* フラグ更新
* メニュー選択状態更新

### Modelで禁止すること

* `pyxel.*` を呼ぶ
* 音を鳴らす
* 画面遷移を実行する
* 保存処理を直接呼ぶ
* メッセージを画面表示する
* `sleep` や時刻依存を直接持つ
* 他Sceneの内部状態を直接触る

### Modelの形

* `dataclass` を原則
* `dict` は縮小方針
* ミュータブルなネスト構造は最小限
* 可能なら `player` も段階的に `PlayerState dataclass` へ移行

#### 理由

`player` がdictのままだと、AIや将来の自分がキー文字列を雑に増やしやすいからです。
型・補完・テストの観点で弱いです。
歴史的事情があるのは自然ですが、**最優先の漸進改善候補**です。

---

## 2-2. Presenter 規約

### Presenterの役割

* 入力を解釈する
* Model更新を指揮する
* Serviceを使う
* 画面遷移を決める
* Viewに渡す描画用データを組み立てる

### Presenterでやってよいこと

* `if input.up_pressed: menu.move_up()`
* `if battle.is_finished(): router.to_field()`
* `message_service.enqueue(...)`
* `audio_requests.append("cursor")`
* ViewModel / RenderData の生成

### Presenterで禁止すること

* `pyxel.text()` など直接描画
* 生の座標計算を大量に書く
* 長大なゲームルールを埋め込む
* Scene-local state を勝手に複製して持つ
* “なんとなく便利だから”と shared state を増やす

### Presenterの分割

1万行RPGなら、1 Scene 1 Presenter でも太ります。
なので Presenter の内部をさらに分けます。

例：

* `BattleInputHandler`
* `BattleFlowController`
* `BattleRenderAssembler`

ただし外からは `BattlePresenter` だけ見せる形にします。

#### 理由

Presenterは太りやすい層です。
MVPが崩れる最大原因はだいたいPresenter肥大です。

---

## 2-3. View 規約

### Viewの役割

* 受け取った描画用データをそのまま描く
* 画面に出すだけ

### Viewでやってよいこと

* `pyxel.cls`
* `pyxel.text`
* `pyxel.rect`
* `pyxel.blt`
* 必要最小限の `pyxel.line`, `pyxel.rectb`, `pyxel.bltm`

### Viewで禁止すること

* 入力取得
* GameState変更
* 分岐だらけのゲームロジック
* セーブロード
* 戦闘進行
* 遷移判断
* Service直接利用（例外は描画専用アセット参照だけ）

### Viewの原則

**Viewは「賢いテンプレート」ではなく「愚直な描画機械」にする。**

つまり：

* Viewは「敵HPが30%未満だから怒り状態っぽく赤字にする」などを判断しない
* そういう判断は Presenter 側で済ませる
* Viewは `color=8` を受け取ったらそのまま描くだけ

---

# 3. Pyxel API 使用規約

ここはかなり強く決めてよいです。

## 3-1. Pyxel API を呼んでよい場所

### 許可

* `src/.../views/*.py`
* `src/platform/pyxel_runtime.py` のような最外殻

### 禁止

* `models`
* `presenters`
* `services`（ただし Audio/Save のPyxel依存ラッパは別）
* `shared/state`

---

## 3-2. 描画命令の制限

最初はかなり狭く始めるのがおすすめです。

### Viewで基本許可するもの

* `pyxel.cls`
* `pyxel.text`
* `pyxel.rect`
* `pyxel.rectb`
* `pyxel.blt`
* `pyxel.bltm`

### 条件付き許可

* `pyxel.line`
* `pyxel.circ`
* `pyxel.circb`
* `pyxel.clip`
* `pyxel.camera`

### 原則禁止

* View以外での全 `pyxel.*`

これを**lint的な規約**として明文化しておくと良いです。

---

# 4. 入力規約

## 4-1. 入力取得は1か所

入力は必ず `InputStateTracker` などで**フレーム冒頭にスナップショット化**します。

例：

* `pressed`
* `just_pressed`
* `just_released`

Presenter はそのスナップショットだけを見る。

### 禁止

* Presenter内で直接 `pyxel.btnp()` を呼ぶ
* Viewで入力を見る
* Modelで入力を見る

#### 理由

入力取得が散ると、再現性とテスト性が一気に落ちます。

---

# 5. Scene 規約

## 5-1. Scene の責務

Scene は「入れ物」です。
責務は次だけ。

* Scene-local Model を持つ
* Presenter を持つ
* View を持つ
* `update()` と `draw()` の入口になる

### Sceneで禁止

* ルール本体を書く
* 直接描画を書く
* Serviceロジックを書く

### つまり

Scene は**配線**だけに寄せます。

---

## 5-2. Scene interface を統一

すべてのSceneは同じ形にします。

例：

* `enter(context)`
* `update(input_state)`
* `build_view_model()`
* `draw(view_model)`
* `exit()`

またはさらに単純に：

* `update(input_state) -> SceneCommand`
* `present() -> ViewModel`

この統一が重要です。
AIは入口が統一されているほど壊しにくいです。

---

# 6. ViewModel / RenderData 規約

これはかなり重要です。

## 6-1. ViewはModelを直接受け取らない

Viewには `GameState` や `BattleModel` を直接渡さず、
**ViewModel / RenderData** を渡します。

例：

* `BattleViewModel`
* `TownViewModel`
* `MenuViewModel`

中身は

* 表示文字列
* 色
* 座標
* スプライトID
* 可視フラグ
* 選択位置
* ゲージ長

など、**描画に必要なものだけ**です。

#### 理由

ViewがModelに直接触ると、少しずつ知識を持ち始めます。
そこから崩れます。

---

## 6-2. RenderDataは「解釈済み」にする

悪い例：

* `enemy_hp_ratio` を渡す
* `is_poisoned`
* `is_boss_phase_2`

良い例：

* `hp_gauge_width=18`
* `name_color=8`
* `status_icons=[...]`
* `portrait_variant="angry"`

つまり、**見た目の判断はPresenterで済ませる**です。

---

# 7. Service 規約

## 7-1. Service の分類を分ける

Serviceが便利すぎると何でも入って壊れます。
なので種類を分けます。

### A. Infrastructure Service

外部依存を扱う

* SaveStore
* AudioManager
* ImageBanks

### B. Domain Support Service

ゲーム共通の補助

* DamageCalculator
* EncounterResolver
* LootTableResolver

### C. UI Support Service

表示補助

* MessageDisplay
* VFX

この分類を明文化してください。

---

## 7-2. Serviceに状態を持たせる基準

状態を持ってよいのは、

* 外部資源のキャッシュ
* UI演出の内部進行
* 入力履歴
* 保存対象ではない補助情報

だけです。

逆に、**セーブに入るべきゲーム進行状態はModel / GameStateへ**です。

---

# 8. GameState 規約

## 8-1. GameState に入れるもの

Scene横断で、かつ保存価値があるもの。

例：

* プレイヤー成長
* 所持金
* 所持品
* 進行フラグ
* 現在マップ
* 位置
* 最終町座標
* 世界進行状態

## 8-2. GameState に入れないもの

* 一時UI状態
* 画面アニメ途中値
* メッセージ送りのindex
* フレーム単位のVFXタイマー
* 一時入力履歴

---

## 8-3. `Game` クラス削除方針

これは進めてよいです。
**dispatcher専用の薄いGameクラスが共有stateを少し持っている**のは、将来のノイズ源です。

方針は明快です。

* `Game` は最終的に **ランタイム殻** にする
* shared state は `BlockQuestApp` / `GameState` / Service のいずれかへ整理
* 「とりあえずここに置く」を禁止

つまり、`Game` は将来的に
**pyxel.runにつなぐだけの最外殻**
にするのがよいです。

---

# 9. コマンド規約

Presenterがいろいろ直接実行するとテストが面倒になります。
なので、**副作用はコマンド化**がおすすめです。

例：

* `PlaySfx("cursor")`
* `ShowMessage("...")`
* `ChangeScene("battle")`
* `SaveGame(slot=1)`

Presenterはこれらを返す。
実際の実行はアプリ層で行う。

#### 理由

これでテスト時に

* 状態変更
* 発行コマンド
  を分けて検証できます。

AIガードレールとしても強いです。

---

# 10. テスト規約

## 10-1. 一番大事な優先順位

テストの優先順位はこうです。

1. **Model単体テスト**
2. **Presenterテスト**
3. **Scene結合テスト**
4. **Viewスモークテスト**
5. **Pyxel実機確認**

---

## 10-2. Presenterテストで見るもの

Presenterテストでは

* 入力
* 初期Model
* Serviceスタブ
* 出力コマンド
* 更新後Model
* 生成ViewModel

を見るようにします。

これでかなり壊れにくくなります。

---

## 10-3. 禁止テスト

* Pyxel描画結果そのものに強く依存するテスト
* フレーム数にべったり依存する fragile test
* 内部実装にしか意味のない private 状態確認

---

# 11. 命名規約

かなり大事です。

## 11-1. ファイル命名

Scene は **ディレクトリ階層** で並びを固定する（本プロジェクトの現行構造）。

```
src/scenes/<scene>/
├── __init__.py
├── model.py        # SceneModel
├── presenter.py    # ScenePresenter
├── view.py         # SceneView
├── view_model.py   # SceneViewModel（導入後）
└── scene.py        # Scene（束ね）
```

例：`src/scenes/battle/{model,presenter,view,scene}.py`。
Scene 名を prefix に付けたフラット配置（`battle_model.py` 等）は採用しない。

---

## 11-2. クラス命名

* `BattleModel`
* `BattlePresenter`
* `BattleView`
* `BattleViewModel`

Support分割するときは

* `BattleFlowController`
* `BattleRenderAssembler`

---

## 11-3. メソッド命名

Presenterでは

* `handle_input()`
* `update_model()`
* `build_view_model()`

Viewでは

* `render(vm)`

Modelでは

* `apply_damage()`
* `can_use_skill()`
* `move_cursor_up()`

---

# 12. AI向けガードレール文面

これは実際にリポジトリ規約として置く価値があります。

## 12-1. AI実装ルール例

* View以外で `pyxel.*` を呼ばない
* Modelで副作用を起こさない
* Presenterで直接描画しない
* ViewはModelを参照しない
* 新しい共有状態を追加する前に `GameState / SceneModel / ServiceState` のどれかを明示する
* `dict` を新規導入しない。新規状態は `dataclass`
* 副作用は command / request として返す
* 1つのPRで Scene構造とゲームルールを同時に大改造しない

このへんは `ARCHITECTURE.md` に書くと効きます。

---

## Proposal

以上を踏まえて、**あなた向けの結論**はこうです。

### 結論1

**Pyxel RPGのMVPは、「MVP思想」ではなく「MVP規約セット」として運用するべき**です。

### 結論2

特に強く固定すべきなのは次の4つです。

1. **Pyxel API は View のみ**
2. **View は ViewModel しか見ない**
3. **Presenter は入力解釈・遷移・副作用指揮のみ**
4. **Model は dataclass中心、dict新規禁止**

### 結論3

Phase 1.5では、まず次の順で進めると安定します。

1. `Game` クラスを最外殻へ縮退
2. `Scene interface` を統一
3. `ViewModel` を全Sceneに導入
4. `player dict` を dataclass 化する計画を切る
5. `副作用コマンド` を導入

---

最後に、規約を一文で言うならこうです。

**「入力はPresenter、状態はModel、描画はView、PyxelはViewだけ、共有状態は明示、曖昧な便利実装は禁止」**

---

# 付録: 本プロジェクト適用メモ（2026-04-23）

この規約を本リポジトリ（Block Quest Pyxel）に段階適用する際の、**未実施の方針メモ**。Phase 1.5 終了時点では着手していない。実装時はこの節を根拠資料として参照する。

## A. Model への責務寄せ（2-1 節への補足）

ルールは可能な限り Model に集める。ただし本プロジェクトでは Scene 横断の player state があるため、3 層で整理する。

**Level 1: scene-local Model にルールを引き上げる**

現在 Presenter / Scene に散っている判定を、まず各 scene の Model へ：

- `BattleModel.apply_damage / can_use_spell / advance_phase`
- `MenuModel.move_cursor_up / confirm`
- `ShopModel.can_buy / deduct_gold`

**Level 2: `PlayerModel` を新設し、`player` dict を吸収する**

player は複数 scene をまたぐので scene-local Model には置けない。**GameState が `player: PlayerModel` を保有**し、PlayerModel 自身がルールを持つ：

- `player.apply_damage(amount)`
- `player.heal(amount)`
- `player.use_item(item)` ← `src/shared/services/item_use.py` の中身を吸収
- `player.gain_exp(amount) -> bool`（true で level up）
- `player.can_use_spell(spell)`

これで `item_use.py` は消滅し、`player_state.py` の `exp_for_level / stats_for_level` も PlayerModel のメソッドへ移動。2-1 節の「HP計算／レベルアップ判定／アイテム増減／位置更新」が Model に集まる。

**Level 3: Scene 横断かつ player 以外のルールは Domain Support Service に残す**

- `world_generation`（マップ生成＝state 生成）
- `landmark_events`（座標判定）
- `audio_system.choose_bgm_scene`（純粋関数）
- `dialog_runner`（YAML ドリブンエンジン）

優先順位は **Model 最優先 → player は PlayerModel → どうしても横断なら Service**。

## B. `GameState` の圧縮（8-1 / 8-2 節への適用）

現在の 19 フィールドを規約に照らすと、セーブ価値のある 7 フィールド前後まで縮む。

### GameState に残すもの

```python
@dataclass
class GameState:
    player: PlayerModel              # 成長・所持・位置・装備
    progress: ProgressFlags          # 進行フラグ 4 件を集約
    world_map: list                  # 現在ワールド地形
    dungeon_map: list | None         # 現在ダンジョン地形
    last_town_pos: tuple[int, int]
    world_return_x: int
    world_return_y: int
```

`ProgressFlags` は `cave_unblock_shown / tree_cleared_shown / poison_step_counter / has_save` を束ねた dataclass。

### GameState から出すもの

| 現フィールド | 理由（8-2 節該当） | 移し先 |
|---|---|---|
| `cam_x, cam_y` | 画面アニメ途中値 | `ExploreModel` か新 `ViewportService` |
| `state, prev_state` | scene 切替メタ | `SceneManager` |
| `debug_mode, debug_seq` | 保存対象でない補助情報 | 新 `DebugService` |
| `dungeon_template, dungeon_template_rooms, dungeon_rooms, dungeon_spawn` | 生成時の中間物（保存しない） | `WorldGenerationService` の結果 cache |

### 波及する整理

- `save_store` の dump/restore は GameState と 1:1 対応になり、`test_save_compat.py` の対象がクリアになる
- `Game` クラス（`src/runtime/app.py`）が抱える `debug_mode / debug_seq / cam_x / cam_y` が別クラスへ移り、8-3 節の「最外殻」方針に近づく
- `state / prev_state` が SceneManager 側になると `BlockQuestApp.set_scene` が `GameState.state` を書かなくなり、6-1 節の「Scene 間遷移の決定権は Presenter」との整合が取りやすい

## C. 進める順序

インパクト順：

1. **Level 2（`player` dict → `PlayerModel`）を最初に** — これが決まると item_use / player_state の消化と GameState 圧縮が一緒についてくる
2. Level 1（scene-local Model へのルール引き上げ）を scene 単位で進める
3. ViewModel 導入（6 節）は scene.py を解体する過程で scene ごとに入れる
4. 副作用コマンド（9 節）は Presenter テストを書くタイミングで段階導入
