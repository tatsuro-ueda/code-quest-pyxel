# コーディング原則

> **この文書の役割**: M1〜M5 メタルールの規約本体（詳細根拠）。
>
> **上位文書（最優先・自動 load）**: [../AGENTS.md](../AGENTS.md)（≤100 行、AI 用エントリポイント）
>
> **人用詳細リファレンス**: [architecture.md](architecture.md)（リポジトリ構造 + ディレクトリ規約）

## 1. 正本を一つにする（SSoT / Single Source of Truth）

データや状態の「正しい置き場所」を一つに決め、他は必ずそこを経由して参照する。

してはいけないこと：

- 生データを直接読む
- 複数箇所に同じ意味のデータを持つ
- 都合のよい方を場面ごとに参照する
- ユーザー編集より自動生成を優先する

## 2. 本番の通り道を必ず通す（Golden Path Test / End-to-End Smoke Test）

ユーザーが実際に使う主要操作を、本番に近い環境で最低一回は動かして確認する。

してはいけないこと：

- unit test green だけで安心する
- 起動・メニュー・店・戦闘など主要導線を省く
- dev環境だけで確認する
- bundleや実機確認を後回しにする

## 3. Migration Safety

リファクタ時は“古い呼び方が残っていないか”を機械的に検出する。

してはいけないこと：

- grepや目視だけで移行完了と判断する
- 旧APIや旧フィールド名を放置する
- 存在しないメソッド呼び出しを見逃す
- dataclass化後もdictアクセスを残す
- manifestや設定の追加を手作業記憶に頼る
- CIで禁止パターン検出や静的チェックを入れない

## 4. No Silent Failure

失敗したときに黙ってユーザーの成果物を壊さない

してはいけないこと：

- エラーを握りつぶしてfallbackに流す
- ユーザー編集データを無言で上書きする
- 読み込み失敗時にデフォルト生成で置き換える
- ログや警告を出さない
- 成功したように見せる
- 破壊的処理を確認なしで実行する
- 失敗条件をテストせず見過ごす

# Pyxel用MVP規約

この規約は、Pyxel で書かれた RPG を AI と一緒にメンテナンスするときの「どこに何を書くか」を **5 本のメタルール（M1〜M5）** に整理したものです。AI が読み飛ばさないよう、まずメタ 5 本だけを読めば全体像がつかめ、詳細が必要なときに子節に降りる構造にしています。

一文でまとめると：

**「入力は Presenter、状態は Model、描画は View、Pyxel は View だけ、共有状態は明示、曖昧な便利実装は禁止」**

5 本のメタルール：

- **M1. Pyxel API と入力は View と最外殻の 1 か所に閉じる**
- **M2. View は ViewModel しか見ない**
- **M3. Presenter は入力解釈・Scene 遷移・副作用指揮のみ**
- **M4. Model は dataclass 中心、共有状態は明示する**
- **M5. 層規約は AI が自力で検証できる形で可視化する**

---

# はじめに：依存方向と 1 フレームの流れ

## 依存方向

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

### 補足：学校の劇で例えると

| 役 | 役割 | プロジェクトでの名前 |
|---|---|---|
| 台本 | セリフや動きが書いてある | **Model**（状態とルール） |
| 演出担当 | 台本を読んで役者に指示を出す | **Presenter** |
| 役者 | 舞台の上で動くだけ（セリフは言われた通り） | **View** |
| 道具係 | 音響・照明・小道具を用意する | **Service**（外部のもの担当） |

この 4 人が **お互いをどれだけ知っていていいか** を決めたのが「依存方向」。

**「A → B」は「A が B を使う」という意味**：

- **View → なし** = 役者は誰のことも知らない。台本（Model）を直接読まない。道具係（Service）にも話しかけない。演出担当に「こう動いて」と言われた通りに動くだけ。
- **Presenter → Model / Service / View用DTO** = 演出担当は、台本を読み、道具係に指示し、役者に渡す「あなた用カンペ」を作る。全体を動かす人。
- **Model → なし** = 台本は誰のことも知らない。「自分が舞台で読まれてるか」も知らない。ただの紙。
- **Service → 外部資源・共通機能** = 道具係はお店から照明を借りたり CD を買ってきたりする。外の世界とやり取りする人。

**細かいルールの意味**：

- **View は Model を知らない** — 役者は台本を直接読まない。演出担当がまとめた「あなた用カンペ」だけ見る。役者が台本を全部読めるとアドリブで余計なことをする。
- **Model は Pyxel を知らない** — 台本に「ここで BGM を流す」「ここで画面を赤くする」と書かない。台本は「HP が 10 減った」という**事実だけ**を扱う。Pyxel なしでもテストできるようにするため。
- **Model は Scene を知らない** — 台本は「今は戦闘シーン」「今はお店シーン」を知らない。知ってしまうと台本の中に分岐が入り、太って壊れやすくなる。
- **Scene 間遷移の決定権は Presenter** — 「次は戦闘シーンに切り替える」と決めるのは演出担当だけ。役者も台本も勝手にシーンを切り替えられない。指揮者を 1 人に絞る。
- **Pyxel API を直接呼んでよいのは View だけ** — `pyxel.text()` / `pyxel.blt()` を使える人は役者だけ。描く場所を 1 か所に決めれば、見た目を直したいときは View だけ直せば済む。

**一言でまとめると**：

**「役者・台本・演出・道具係、それぞれ自分の仕事だけして、他人の仕事に口を出さない」**

これが守られていると、AI やうっかりした未来の自分がコードを直しても、他の場所まで壊さない——これが一番の狙い。

## 1 フレームの流れ

1 フレームの処理順を固定します。

1. `input snapshot` を取得
2. Presenter が入力を解釈
3. Model を更新
4. Presenter が描画用データを作る
5. View が描画する

つまり：

**input → update → present → render**

これを崩さないことです。

---

# M1. Pyxel 描画 API と入力は View と最外殻の 1 か所に閉じる

**Rule**: Pyxel の **描画系 API**（`pyxel.blt / bltm / text / line / rect / rectb / circ / circb / cls / pset` 等）と **入力取得**（`pyxel.btn / btnp`）は、**View 層と最外殻（`src/platform/pyxel_runtime.py` 相当）** に閉じ込める。Model / Presenter / Service / shared/state では呼ばない。
**ただし読み取り系 API**（`pyxel.tilemaps[n].pget`, `pyxel.images[n].pget`）は **Model から直接呼んでよい**。これは ImageBank / Tilemap を **DB レイヤ** として読み取るための例外規定（2026-05-05 改訂）。

**Why**: 描画 / 入力呼び出しが散ると、テスト時に差し替えが効かず Model がヘッドレスで動かせなくなる。1 か所に絞れば、見た目や入力仕様を直したいときにその 1 か所だけ直せば済む。
読み取り系 API を Model に解禁する理由：ImageBank（pyxres）が SSoT である以上、Model がそれを直接読まないと Code Maker 編集が即反映されない（中間スナップショットが古いまま残る）。読み取りは副作用がなく、テストでも `pyxel.tilemaps[n].pget` をモック差し替えできる。

## M1-1. Pyxel API 使用規約

### 描画系 API（`blt / bltm / text / line / rect / rectb / circ / circb / cls / pset` 等）

#### 許可

* `src/.../views/*.py`
* `src/platform/pyxel_runtime.py` のような最外殻
* `src/shared/ui/*.py`（**View と同等扱い**：UI 部品は views の延長として `shared/ui/` に置く。HUD / status_bar / message_window / vfx_overlay / text_renderer 等。2026-05-06 明文化）
* `src/shared/services/audio_system.py`（**Audio ラッパ**：BGM / SE / 効果音の Pyxel 連携。`pyxel.playm / play / sounds / musics`）
* `src/shared/services/image_banks.py`（**Resource ラッパ**：pyxres ロード/保存、image bank / tilemap の **書き込み・初期化のみ**。`pyxel.load / save / images / tilemaps[0].pset`。読み取りは Model 直読へ移管済 2026-05-05）

#### 禁止

* `models`（描画系は View または最外殻へ）
* `presenters`（同上）
* `services`（同上。ただし Audio ラッパ / Resource ラッパは上記許可リストの通り例外）
* `shared/state`（同上）

#### 検証 grep の例

```bash
# services から pyxel 描画系直呼びを検出（Audio / Resource ラッパは除外）
grep -nE 'pyxel\.(blt|bltm|text|line|rect|rectb|circ|circb|cls|pset|tri|trib|clip|camera)' \
  src/shared/services/*.py | grep -vE '(audio_system|image_banks)\.py'
# → 0 件であること
```

### 読み取り系 API（`pyxel.tilemaps[n].pget`, `pyxel.images[n].pget`）

#### 許可

* `src/scenes/*/model.py`（**ImageBank を DB として読むため、2026-05-05 解禁**）
* `src/.../views/*.py`
* 最外殻 / Service 層

### 入力系 API（`pyxel.btn / btnp`）

#### 許可

* `src/.../views/*.py` 内では **読まない**（View は ViewModel だけ見る）
* 最外殻と `InputStateTracker` の中だけ

#### 禁止

* `models` / `presenters` / `services` / `shared/state`（Presenter は `InputStateTracker` スナップショット経由）

### 描画命令の制限

最初はかなり狭く始めるのがおすすめです。

**View で基本許可するもの**：

* `pyxel.cls`
* `pyxel.text`
* `pyxel.rect`
* `pyxel.rectb`
* `pyxel.blt`
* `pyxel.bltm`

**条件付き許可**：

* `pyxel.line`
* `pyxel.circ`
* `pyxel.circb`
* `pyxel.clip`
* `pyxel.camera`

**原則禁止**：

* View 以外での全 `pyxel.*`（View／最外殻でのみ呼ぶ）

これを **lint 的な規約** として明文化しておくと良いです。

## M1-2. 入力規約

入力は必ず `InputStateTracker` などで **フレーム冒頭にスナップショット化** します。

例：

* `pressed`
* `just_pressed`
* `just_released`

Presenter はそのスナップショットだけを見る。

### 禁止

* Presenter 内で直接 `pyxel.btnp()` を呼ぶ（Presenter は InputStateTracker のスナップショット経由）
* View で入力を見る（Presenter）
* Model で入力を見る（Presenter）

#### 理由

入力取得が散ると、再現性とテスト性が一気に落ちます。

## M1-3. View の描画範囲

View でやってよいこと：

* `pyxel.cls`
* `pyxel.text`
* `pyxel.rect`
* `pyxel.blt`
* 必要最小限の `pyxel.line`, `pyxel.rectb`, `pyxel.bltm`

それ以外の Pyxel API を View で使う前に、**本当に描画に必要か** を確認する。

## 検証の目安

- `grep -nE 'pyxel\.(blt|bltm|text|line|rect|rectb|circ|circb|cls|pset|tri|trib|clip|camera)' src/scenes/*/model.py src/scenes/*/presenter.py src/shared/state/*.py` が 0 件（描画系は Model / Presenter / state では 0 件）
- `grep -nE 'pyxel\.(btnp|btn)\b' src/scenes/*/presenter.py src/scenes/*/model.py src/shared/state/*.py` が 0 件
- Model 内の `pyxel.tilemaps[n].pget` / `pyxel.images[n].pget` は **許可**（DB 読み取り）

---

# M2. View は ViewModel しか見ない

**Rule**: View には `GameState` や `BattleModel` を直接渡さず、**ViewModel / RenderData** を渡す。ViewModel の中身は **描画に必要な、解釈済みの値だけ**。

**Why**: View が Model に直接触ると、少しずつ知識を持ち始める。「敵 HP が 30% 未満だから怒り状態っぽく赤字にする」のような判断を View に書き始めると、やがて View が「賢いテンプレート」に退化し、見た目を直すつもりが判断ロジックも直さねばならなくなる。View は「愚直な描画機械」に留める。

## M2-1. View 責務

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

* 入力取得（Presenter: InputStateTracker 経由）
* GameState 変更（Presenter / Model）
* 分岐だらけのゲームロジック（Model）
* セーブロード（Service: SaveStore、トリガは Presenter）
* 戦闘進行（Model）
* 遷移判断（Presenter）
* Service 直接利用（Presenter）（例外は描画専用アセット参照だけ）

### Viewの原則

**View は「賢いテンプレート」ではなく「愚直な描画機械」にする。**

つまり：

* View は「敵 HP が 30% 未満だから怒り状態っぽく赤字にする」などを判断しない
* そういう判断は Presenter 側で済ませる
* View は `color=8` を受け取ったらそのまま描くだけ

## M2-2. ViewModel / RenderData 規約

### View は Model を直接受け取らない

View には `GameState` や `BattleModel` を直接渡さず、**ViewModel / RenderData** を渡します。

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

### RenderData は「解釈済み」にする

悪い例：

* `enemy_hp_ratio` を渡す
* `is_poisoned`
* `is_boss_phase_2`

良い例：

* `hp_gauge_width=18`
* `name_color=8`
* `status_icons=[...]`
* `portrait_variant="angry"`

つまり、**見た目の判断は Presenter で済ませる**です。

## 検証の目安

- View の関数シグネチャが `vm: *ViewModel` を取る形になっている（Model や GameState を直接引数に取っていない）
- ViewModel の中に `is_poisoned` / `*_ratio` のような「解釈前」のフィールドが無い

---

# M3. Presenter は入力解釈・Scene 遷移・副作用指揮のみ

**Rule**: Presenter は **入力解釈 / Model 更新指揮 / Service 利用 / 画面遷移の決定 / ViewModel 組立て** を担う。直接描画せず、長大なゲームルールを埋めず、副作用は command として返す。Scene は Presenter を束ねる「入れ物」にとどめる。

**Why**: Presenter は太りやすい層。MVP が崩れる最大原因はだいたい Presenter 肥大です。「副作用はコマンド化」を入れると、テスト時に *状態変更* と *発行コマンド* を分けて検証できるため、AI ガードレールとしても強い。

## M3-1. Presenter 責務

### Presenterの役割

* 入力を解釈する
* Model 更新を指揮する
* Service を使う
* 画面遷移を決める
* View に渡す描画用データを組み立てる

### Presenterでやってよいこと

* `if input.up_pressed: menu.move_up()`
* `if battle.is_finished(): router.to_field()`
* `message_service.enqueue(...)`
* `audio_requests.append("cursor")`
* ViewModel / RenderData の生成

### Presenterで禁止すること

* `pyxel.text()` など直接描画（View）
* 生の座標計算を大量に書く（shared/ui レイアウト helper）
* 長大なゲームルールを埋め込む（Model）
* Scene-local state を勝手に複製して持つ（Scene-local Model）
* "なんとなく便利だから" と shared state を増やす（GameState / Service に明示）

### Presenterの分割

1 万行 RPG なら、1 Scene 1 Presenter でも太ります。
なので Presenter の内部をさらに分けます。

例：

* `BattleInputHandler`
* `BattleFlowController`
* `BattleRenderAssembler`

ただし外からは `BattlePresenter` だけ見せる形にします。

## M3-2. Scene 規約

### Scene の責務

Scene は「入れ物」です。責務は次だけ。

* Scene-local Model を持つ
* Presenter を持つ
* View を持つ
* `update()` と `draw()` の入口になる

### Sceneで禁止

* ルール本体を書く（Model）
* 直接描画を書く（View）
* Service ロジックを書く（Service）

### つまり

Scene は **配線** だけに寄せます。本プロジェクトでは、Scene を薄い配線すら持たず、**Presenter が `update` / `draw` の入口を兼ねる**ところまで縮退してよい。

### Scene interface を統一

すべての Scene は同じ形にします。

例：

* `enter(context)`
* `update(input_state)`
* `build_view_model()`
* `draw(view_model)`
* `exit()`

またはさらに単純に：

* `update(input_state) -> SceneCommand`
* `present() -> ViewModel`

この統一が重要です。AI は入口が統一されているほど壊しにくいです。

## M3-3. コマンド規約

Presenter がいろいろ直接実行するとテストが面倒になります。
なので、**副作用はコマンド化** がおすすめです。

例：

* `PlaySfx("cursor")`
* `ShowMessage("...")`
* `ChangeScene("battle")`
* `SaveGame(slot=1)`

Presenter はこれらを返す。実際の実行はアプリ層で行う。

### 理由

これでテスト時に

* 状態変更
* 発行コマンド

を分けて検証できます。AI ガードレールとしても強いです。

## 検証の目安

- `grep -nE 'pyxel\.(text|rect|rectb|blt|bltm|cls|line|circ)' src/scenes/*/presenter.py` が 0 件
- Scene 間遷移の代入（`game.state =` / `game_state.state =` 相当）が Presenter 配下のみで検出される（Model / View には出ない）
- 副作用コマンドを返すパスが存在し、Presenter テストがそれを assertion している（または `未実装` として note に記録）

---

# M4. Model は dataclass 中心、共有状態は明示する

**Rule**: Model は Pyxel / Scene / 副作用を知らず、状態・ルール・計算・遷移条件だけを持つ。新規状態は `@dataclass` で宣言し、dict 新規導入を禁止する。共有は `GameState` / 引数 / Command で **明示** し、他 Scene の内部状態を直接触らない。

**Why**: 「なんとなく便利な dict」と「他 scene の内部のぞき込み」が、改修時のデグレ源として最大。`@dataclass` による型と補完とテスト、`GameState` による明示的な共有境界があって初めて、AI が参照範囲を追える。

## M4-1. Model 責務

台本・指示者・役者・道具係の内の台本。
台本は誰のことも知らない。「自分が舞台で読まれてるか」も知らない。ただの紙。
台本に「ここで BGM を流す」「ここで画面を赤くする」と書かない。台本は「HP が 10 減った」という事実だけを扱う。Pyxel なしでもテストできるようにするため。

### Modelの役割

* 状態を持つ
* ルールを持つ
* 計算する
* 遷移条件を持つ

### Modelでやってよいこと

* HP 計算
* レベルアップ判定
* 戦闘進行
* アイテム増減
* 位置更新
* フラグ更新
* メニュー選択状態更新

### Modelで禁止すること

* `pyxel.*` を呼ぶ（View）
* 音を鳴らす（Service: AudioManager）
* 画面遷移を実行する（Presenter）
* 保存処理を直接呼ぶ（Service: SaveStore）
* メッセージを画面表示する（Service: MessageDisplay → View）
* `sleep` や時刻依存を直接持つ（Service／最外殻）
* 他 Scene の内部状態を直接触る（共有は GameState、切替は Presenter）

### Modelの形

* `dataclass` を原則
* `dict` は縮小方針
* ミュータブルなネスト構造は最小限
* 可能なら `player` も段階的に `PlayerState dataclass` へ移行

#### 理由

`player` が dict のままだと、AI や将来の自分がキー文字列を雑に増やしやすいからです。
型・補完・テストの観点で弱いです。
歴史的事情があるのは自然ですが、**最優先の漸進改善候補** です。

## M4-2. Service 規約

台本・指示者・役者・道具係の内の道具係。

### Service の分類を分ける

Service が便利すぎると何でも入って壊れます。なので種類を分けます。

#### A. Infrastructure Service

外部依存を扱う

* SaveStore
* AudioManager
* ImageBanks（**書き込み・初期化のみ**：pyxres ロード / `setup_world_tilemap` / `regenerate_world_tilemap_fallback` / `regenerate_dungeon_tilemap_fallback`（いずれも pyxres 不在時の fallback のみ）/ `pyxel.save`。**読み取りは Model 直読**（`pyxel.tilemaps[0]` / `pyxel.images[n]`）へ移管、2026-05-05 改訂。旧名 `bake_world_to_tilemap` / `bake_dungeon_to_tilemap` は同改訂でリネーム）

#### B. Domain Support Service

ゲーム共通の補助

* DamageCalculator
* EncounterResolver
* LootTableResolver

#### C. UI Support Service

表示補助

* MessageDisplay
* VFX

この分類を明文化してください。

### Service に状態を持たせる基準

状態を持ってよいのは、

* 外部資源のキャッシュ
* UI 演出の内部進行
* 入力履歴
* 保存対象ではない補助情報

だけです。

逆に、**セーブに入るべきゲーム進行状態は Model / GameState へ** です。

## M4-3. GameState 規約

### GameState に入れるもの

Scene 横断で、かつ保存価値があるもの。

例：

* プレイヤー成長
* 所持金
* 所持品
* 進行フラグ
* 現在マップ
* 位置
* 最終町座標
* 世界進行状態

### GameState に入れないもの

* 一時 UI 状態
* 画面アニメ途中値
* メッセージ送りの index
* フレーム単位の VFX タイマー
* 一時入力履歴

### `Game` クラス削除方針

これは進めてよいです。
**dispatcher 専用の薄い Game クラスが共有 state を少し持っている** のは、将来のノイズ源です。

方針は明快です。

* `Game` は最終的に **ランタイム殻** にする
* shared state は `GameState` / `SceneManager`（state holder）/ `DebugService` / その他 Service のいずれかへ整理（`src/app.py::BlockQuestApp` は Phase 1 由来の legacy shell。本体は `src/runtime/app.py::Game`）
* 「とりあえずここに置く」を禁止

つまり、`Game` は将来的に **`pyxel.run` につなぐだけの最外殻** にするのがよいです（M4-3 段階移行で `current_town / debug_mode / state / prev_state` などは @property forward に変換済）。

### M4-3 段階移行ステータス（2026-05-05 改訂）

5 ループの段階移行で以下の field が `Game` から移送済：

| Field | 移送先 | 互換 |
|---|---|---|
| `current_town` | `GameState.current_town` | `Game.current_town` を `@property` でフォワード |
| `cam_x` / `cam_y` | `ExploreModel` | 直接書換（Explore 専用） |
| `dungeon_rooms` | 撤去（dead code） | — |
| `dungeon_map` / `world_map` | 撤去（pyxres = SSoT、Model 直読） | static guard で復活防止 |
| `debug_mode` / `debug_seq` | `DebugService` | `@property` フォワード |
| `state` / `prev_state` | `SceneManager` | `@property` フォワード |

ガード：`test_cjg_framework_rule_guards.py::test_game_init_does_not_directly_initialize_deprecated_fields`
が `Game.__init__` の AST を解析し、上記 field が `self.X = ...` として
直接初期化されたら fail させる（@property 経由のフォワードは許可）。

## M4-4. PlayerModel と GameState 圧縮（本プロジェクト適用）

ルールは可能な限り Model に集める。ただし本プロジェクトでは Scene 横断の player state があるため、3 層で整理する。

### Level 1: scene-local Model にルールを引き上げる

現在 Presenter / Scene に散っている判定を、まず各 scene の Model へ：

- `BattleModel.apply_damage / can_use_spell / advance_phase`
- `MenuModel.move_cursor_up / confirm`
- `ShopModel.can_buy / deduct_gold`

### Level 2: `PlayerModel` を新設し、`player` dict を吸収する

player は複数 scene をまたぐので scene-local Model には置けない。**GameState が `player: PlayerModel` を保有** し、PlayerModel 自身がルールを持つ：

- `player.apply_damage(amount)`
- `player.heal(amount)`
- `player.use_item(item)` ← `src/shared/services/item_use.py` の中身を吸収
- `player.gain_exp(amount) -> bool`（true で level up）
- `player.can_use_spell(spell)`

これで `item_use.py` は消滅し、`player_state.py` の `exp_for_level / stats_for_level` も PlayerModel のメソッドへ移動する。

### Level 3: Scene 横断かつ player 以外のルールは Domain Support Service に残す

- `world_generation`（マップ生成＝ state 生成）
- `landmark_events`（座標判定）
- `audio_system.choose_bgm_scene`（純粋関数）
- `dialog_runner`（YAML ドリブンエンジン）

優先順位は **Model 最優先 → player は PlayerModel → どうしても横断なら Service**。

### GameState の圧縮（目標形）

```python
@dataclass
class GameState:
    player: PlayerModel              # 成長・所持・位置・装備
    progress: ProgressFlags          # 進行フラグ 4 件を集約
    # world_map は削除（2026-05-05 改訂）：DB（pyxres / pyxel.tilemaps）が
    # SSoT であり、ExploreModel が必要時に直読する。中間スナップショットを
    # 共有 state に持たない。
    dungeon_map: list | None         # 現在ダンジョン地形（Code Maker 編集対象外なので当面残す）
    last_town_pos: tuple[int, int]
    world_return_x: int
    world_return_y: int
```

### GameState から出すもの

| 現フィールド | 理由 | 移し先 |
|---|---|---|
| `cam_x, cam_y` | 画面アニメ途中値 | `ExploreModel` か新 `ViewportService` |
| `state, prev_state` | scene 切替メタ | `SceneManager` |
| `debug_mode, debug_seq` | 保存対象でない補助情報 | 新 `DebugService` |
| `dungeon_template, dungeon_template_rooms, dungeon_rooms, dungeon_spawn` | 生成時の中間物（保存しない） | `WorldGenerationService` の結果 cache |

## 検証の目安

- `grep -rnE 'player\[.?["\x27]' src/` が 0 件（PlayerModel 経由になっている。既存コードの段階的移行は `未実装` として note に明示）
- `grep -nE 'pyxel\.(blt|bltm|text|line|rect|rectb|circ|circb|cls|pset|tri|trib|clip|camera)' src/scenes/*/model.py src/shared/state/*.py` が 0 件（描画系の禁止）
- Model 内で `pyxel.tilemaps[n].pget` / `pyxel.images[n].pget` は許可（DB 読み取り）
- `grep -nE '[a-z_]+_scene\.(model|_)' src/scenes/` が対象 scene 以外で 0 件（他 scene の内部を直接読んでいない）

---

# M5. 層規約は AI が自力で検証できる形で可視化する

**Rule**: ファイル命名・テスト優先順位・AI 向けガードレール文面を明文化し、PRD / ARCHITECTURE.md / AGENTS.md に取り込む。AI が自力で **「この規約が存在する」** と発見できる状態にする。

**Why**: 規約は書いただけでは機能しない。AI が次の改修で自然に見つけられる場所に置き、検証コマンドまで書いて初めて、層規約が実際に守られる。

## M5-1. 命名規約

### ファイル命名

Scene は **ディレクトリ階層** で並びを固定する（本プロジェクトの現行構造）。

```
src/scenes/<scene>/
├── __init__.py
├── model.py        # SceneModel
├── presenter.py    # ScenePresenter
├── view.py         # SceneView
├── view_model.py   # SceneViewModel（導入後）
└── scene.py        # Scene（束ね。本プロジェクトでは Presenter が入口兼務まで縮退可）
```

例：`src/scenes/battle/{model,presenter,view,scene}.py`。
Scene 名を prefix に付けたフラット配置（`battle_model.py` 等）は採用しない。

### クラス命名

* `BattleModel`
* `BattlePresenter`
* `BattleView`
* `BattleViewModel`

Support 分割するときは

* `BattleFlowController`
* `BattleRenderAssembler`

### メソッド命名

Presenter では

* `handle_input()`
* `update_model()`
* `build_view_model()`

View では

* `render(vm)`

Model では

* `apply_damage()`
* `can_use_skill()`
* `move_cursor_up()`

## M5-2. テスト規約

### 一番大事な優先順位

テストの優先順位はこうです。

1. **Model 単体テスト**
2. **Presenter テスト**
3. **Scene 結合テスト**
4. **View スモークテスト**
5. **Pyxel 実機確認**

### Presenter テストで見るもの

Presenter テストでは

* 入力
* 初期 Model
* Service スタブ
* 出力コマンド
* 更新後 Model
* 生成 ViewModel

を見るようにします。これでかなり壊れにくくなります。

### 禁止テスト

* Pyxel 描画結果そのものに強く依存するテスト
* フレーム数にべったり依存する fragile test
* 内部実装にしか意味のない private 状態確認

## M5-3. AI 向けガードレール文面

これは実際にリポジトリ規約として置く価値があります。

### AI 実装ルール例

* View 以外で `pyxel.*` を呼ばない
* Model で副作用を起こさない
* Presenter で直接描画しない
* View は Model を参照しない
* 新しい共有状態を追加する前に `GameState / SceneModel / ServiceState` のどれかを明示する
* `dict` を新規導入しない。新規状態は `dataclass`
* 副作用は command / request として返す
* 1 つの PR で Scene 構造とゲームルールを同時に大改造しない

このへんは `AGENTS.md` (≤100 行・自動 load) と `docs/architecture.md` (人用詳細) に書くと効きます。両者から本ファイル `docs/framework-rule.md` (規約本体) に到達できる 2 層構造を維持します。

### 文書 2 層構造（2026-05-05 改訂）

| 文書 | 役割 | サイズ |
|---|---|---|
| `AGENTS.md` | AI 用最優先・自動 load・エントリポイント | ≤100 行 |
| `docs/architecture.md` | 人用詳細（補足リファレンス、AI も必要時参照） | 制限なし |
| `docs/framework-rule.md` (本ファイル) | 規約本体（M1〜M5 詳細根拠） | 制限なし |

AI / 人ともに `AGENTS.md` を最初に読み、必要に応じて `architecture.md`、最後に本ファイルへ降りる流れ。`AGENTS.md` が大きくなって自動 load の context を圧迫すると AI が起動時に読み切れなくなるため、100 行制限を `test_cjg_framework_rule_guards.py` の static guard で守る。

## 検証の目安

- `find src/scenes -maxdepth 2 -type f -name '*.py' | grep -vE '/(model|presenter|view|view_model|scene|__init__)\.py$'` が 0 件（命名規約）
- `test/test_player_model.py` / `test/test_*_presenter.py` 等の Model / Presenter 単体テストが存在している（または優先順位 1 位・2 位の項目として `未実装` と明示）
- AI 用 `AGENTS.md` が 100 行以内で自動 load される / 人用 `docs/architecture.md` が存在する 2 層構造で、両者から本ファイル `docs/framework-rule.md` に到達できる

---

# Proposal

以上を踏まえて、**あなた向けの結論** はこうです。

### 結論1

**Pyxel RPG の MVP は、「MVP 思想」ではなく「MVP 規約セット」として運用するべき** です。

### 結論2

特に強く固定すべきなのは次の 5 つ（本規約のメタ 5 本）です。

1. **Pyxel API と入力は View と最外殻の 1 か所に閉じる**（M1）
2. **View は ViewModel しか見ない**（M2）
3. **Presenter は入力解釈・Scene 遷移・副作用指揮のみ**（M3）
4. **Model は dataclass 中心、共有状態は明示する**（M4）
5. **層規約は AI が自力で検証できる形で可視化する**（M5）

### 結論3

Phase 1.5 では、まず次の順で進めると安定します。

1. `Game` クラスを最外殻へ縮退（M4-3）
2. `Scene interface` を統一（M3-2）
3. `ViewModel` を全 Scene に導入（M2-2）
4. `player dict` を `PlayerModel` 化する計画を切る（M4-4）
5. 副作用コマンドを導入（M3-3）

---

最後に、規約を一文で言うならこうです。

**「入力は Presenter、状態は Model、描画は View、Pyxel は View だけ、共有状態は明示、曖昧な便利実装は禁止」**

---

# 付録: 本プロジェクト適用メモ（2026-04-23 起案 / 2026-04-24 メタ構造化）

この規約を本リポジトリ（Block Quest Pyxel）に段階適用する際の、**未実施の方針メモ**。Phase 1.5 終了時点では着手していない。実装時はこの節を根拠資料として参照する。

## 進める順序

インパクト順：

1. **Level 2（`player` dict → `PlayerModel`）を最初に**（M4-4） — これが決まると `item_use` / `player_state` の消化と GameState 圧縮が一緒についてくる
2. Level 1（scene-local Model へのルール引き上げ）を scene 単位で進める（M4-1）
3. ViewModel 導入（M2-2）は scene.py を解体する過程で scene ごとに入れる
4. 副作用コマンド（M3-3）は Presenter テストを書くタイミングで段階導入

## 旧章番号との対応（本書き換え 2026-04-24 時点）

旧書式（1〜12 章）→ 新書式（M1〜M5 配下）の対応：

| 旧章 | 新位置 |
|---|---|
| 1-1 依存方向 | はじめに |
| 1-2 1フレームの流れ | はじめに |
| 2-1 Model 規約 | M4-1 |
| 2-2 Presenter 規約 | M3-1 |
| 2-3 View 規約 | M2-1 |
| 3 Pyxel API 使用規約 | M1-1 |
| 4 入力規約 | M1-2 |
| 5 Scene 規約 | M3-2 |
| 6 ViewModel / RenderData 規約 | M2-2 |
| 7 Service 規約 | M4-2 |
| 8 GameState 規約 | M4-3 |
| 9 コマンド規約 | M3-3 |
| 10 テスト規約 | M5-2 |
| 11 命名規約 | M5-1 |
| 12 AI 向けガードレール文面 | M5-3 |
| 付録 A Model への責務寄せ | M4-4 |
| 付録 B GameState の圧縮 | M4-4 |
| 付録 C 進める順序 | 付録（本節） |
