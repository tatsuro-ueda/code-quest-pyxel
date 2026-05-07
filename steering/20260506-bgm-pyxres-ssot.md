---
status: done
priority: normal
scheduled: 2026-05-06T01:00:00.000+09:00
dateCreated: 2026-05-06T01:00:00.000+09:00
dateModified: 2026-05-06T01:00:00.000+09:00
tags:
  - task
---

# 2026年5月6日 BGM の責務分担を AI / 人が読める形に整える（CJ37 の BGM 面）

> 状態：① Journey 書き直し（CJ37 寄りに位置づけ直し）
> 次のゲート：（ユーザー）Journey/Gherkin/Design/Tasklist の妥当性を確認 →「実装」or「修正」と指示

---

## 1) Journey（どこへ行くか）

- **深層的目的**：BGM を「**シンプルで変更しやすい**」状態にする。複雑で高機能なプログラムは要らない。
- **やらないこと**：BGM の高機能化（フェード／クロスフェード／ランダム再生／プレイリスト切替）／**演出 ON/OFF 機能（個別 ON/OFF も `ぜんぶ` 一括 ON/OFF も提供しない）**。BGM・SFX・VFX は常に ON。設定画面に演出切替項目を **置かない**。
- **大方針（C+ 案・確定版）**：**シーンが BGM を持つ**。同一シーン内で複数曲を切り替えたい場合（例：通常戦闘 vs ボス戦闘、町 vs 野原 vs ダンジョン）は **View 内の小さな `if` 分岐**で対応する。AudioManager は撤去し、View が `pyxel.playm` を直接呼ぶ。
- **採用する 2 原則（2026-05-07 確認）**：
  - 原則 A：scene の View が `pyxel.playm(BGM_MUSIC_INDEX, loop=True)` を直接呼ぶ。住所も再生も View に集約。複数曲ある場合は View 内 `if` で選ぶ。
  - 原則 B：BGM の実体（音符）は pyxres = SSoT。Pyxel Code Maker で編集したものが起動後そのまま鳴る。

1. ❓ （子ども）町の BGM をもっと冒険っぽくしたい／戦闘の BGM を変えたい（ゲーム中）
2. 💦 （親）AI に「町の BGM を変えて」と頼む／または子どもが Pyxel Code Maker で曲をいじる（AI入力画面 / Code Maker）
3. Before
  1. AI
    1. ❌ 「町の BGM はどこに書いてあるんだろう？」と探しても、置き場が一箇所にまとまっておらず、関連箇所をあちこち追わないと答えが出ない（コードエディタ）
    2. ❌ 「ここを直すと別の場面の BGM も壊れるかもしれない」と影響範囲が読みきれず、自信を持って修正できない（コードエディタ）
    3. ❌ 「直したけれど他が壊れていないか確認してほしい」と親に返す → 親が出す前の検証コストが膨らむ（コードエディタ）
    4. ❌ 期待に応えられない
  2. 親
    1. ❌ AI に頼んでも「BGM が一発で届かない／場面が増えるたびに大ごとになる」→ 子どもの望みを返せない（生活）
    2. ❌ 子どもの期待に短時間で応えられない
  3. 子ども
    1. ❌ Pyxel Code Maker で BGM を編集しても、ゲームを起動するといつもの BGM に戻ってしまう（Code Maker、Web）
    2. ❌ 「変えたのに鳴らない……」とがっかりする → Code Maker は飾りに見え、編集する気が失せる（生活）
  4. 新しい場面の作り手
    1. ❌ BGM の住所をどこに書けばいいのか規約がなく、迷う（コードエディタ）
    2. ❌ 既存の AudioManager / `CHIPTUNE_TRACKS` / `choose_bgm_scene` を読み解かないと「自分の場面に BGM を付ける」ができない（コードエディタ）
4. After
  1. AI
    1. ✅ 「この場面の BGM はここ」とすぐ見つけられる。場面ごとの View ファイルに 1 行 `pyxel.playm(N, loop=True)` が並んでいる（コードエディタ）
    2. ✅ 「他の場面には影響しない」と確信して直せる。同じシーンの View だけ触ればよい（コードエディタ）
    3. ✅ 影響範囲がはっきり見える → 副作用なく直せる（CJ37 を満たす）
    4. ♥️ 期待に応えられる
  2. 親
    1. ✅ AI に頼んだ BGM の変更が一発で子どもに届く
    2. ✅ JIS（主体性支援）が回復し、好循環の音楽面が成立
    3. ♥️ 好循環が回る
  3. 子ども
    1. ✅ Pyxel Code Maker で編集した BGM が、ゲーム本体を起動しても **そのまま鳴る**（Code Maker / Web）
    2. ♥️ 「変えたのが鳴った！もっといじりたい！」と次のサイクルに進む → JCR（クリエイター・表現）と Buy2 約束が回復（生活）
  4. 新しい場面の作り手
    1. ✅ 「View に `pyxel.playm(N, loop=True)` を 1 行書くだけ」と決まっており、迷わず置ける（コードエディタ）
    2. ✅ AudioManager / `CHIPTUNE_TRACKS` / `choose_bgm_scene` / `sync_audio` の数百行は **削除済**で読む必要がない（コードエディタ）
    3. ♥️ コードベースが軽くなり、後から触る人が安心できる
  
---

## 2) Gherkin（完了条件）

> Gherkin に入る前に、**ユーザーストーリーマップ**を 4 アクター別に並べる。
> 各表は時系列（上から下）。列：アクター視点の **行動・出来事**、その瞬間の **感情**、その行動を支える **機能**（コード／pyxres／規約／外部 Buy）。
> 凡例：❓気づき／💡ひらめき／💦不安・負荷／😊安心／👀目視／👆操作／🔍探す／🤔迷い／❌つまずき／✅うまくいく／♥️満たされる

### ユーザーストーリーマップ — 子ども

| # | 行動・出来事 | 感情 | 機能 |
|---|---|---|---|
| 1 | プレイ中に「町の BGM 飽きたな、もっと冒険っぽい曲がいいな」と感じる | ❓ | ゲーム本体 |
| 2 | 親に「町の BGM を変えて」と頼む。または自分で Pyxel Code Maker を開く | 💡 | Pyxel Code Maker（Buy2） |
| 3 | Code Maker で町の musics スロットを編集する | 👆 | pyxres = SSoT、Code Maker の Music エディタ |
| 4 | Code Maker 内で Run → その場で新しい BGM が鳴る | ✅ | Code Maker の即時反映 |
| 5 | ゲーム本体を起動して町に入る | 👆 | ゲーム本体 + 起動時 `pyxel.load(pyxres)` |
| 6 | **編集した BGM がそのまま鳴る** | ✅ | `AudioManager._load_tracks` の `_music_has_data` ガード（pyxres SSoT 尊重） |
| 7 | 「変えたのが鳴った！もっといじりたい！」と次のサイクルへ | ♥️ | （体験） |

### ユーザーストーリーマップ — 親

| # | 行動・出来事 | 感情 | 機能 |
|---|---|---|---|
| 1 | 子の「BGM 変えて」を受け取る | 😊 | 対面 |
| 2 | AI に「町の BGM を変えて」と頼む | 💦 | AI 入力画面（Buy3 vibe coding） |
| 3 | AI が「`src/scenes/town/view.py` の `pyxel.playm(N, loop=True)` の N を変えるだけ」とすぐ返す | ✅ | View 内 1 行直書き／`grep` 一発で見える構造 |
| 4 | 起動して動作確認、安心して子に渡す | 👀 | ゲーム本体 |
| 5 | 子が喜び、次のサイクルが回り出す | ♥️ | JIS（主体性支援）成立 |

### ユーザーストーリーマップ — AI

| # | 行動・出来事 | 感情 | 機能 |
|---|---|---|---|
| 1 | 親から「町の BGM を変えて」を受け取る | 🔍 | （依頼） |
| 2 | `grep -rnE 'pyxel\.playm\(' src/scenes/` で全シーンの BGM 呼び出しが 1 行ずつ見える | ✅ | scene/*/view.py の直書き規約 |
| 3 | 該当シーン（town）の View だけを編集する | ✅ | scene = BGM の 1:1 マッピング |
| 4 | 他シーンの View には触らない。**影響範囲が物理的に同じファイルに閉じている** | ✅ | scene 単位の独立性 |
| 5 | 自信を持って「直しました」と親に返す | ✅ | CJ37（責務が読める）達成 |

### ユーザーストーリーマップ — 新しい場面の作り手

| # | 行動・出来事 | 感情 | 機能 |
|---|---|---|---|
| 1 | 新しいシーン（例：「城」）を作ろうとする | 💡 | M5-1 scene 構造規約 |
| 2 | `docs/framework-rule.md` M5-1 を読んで「BGM は View に `pyxel.playm(N, loop=True)` 1 行と書く」と分かる | 😊 | M5-1 改訂で BGM の置き場が明文化 |
| 3 | pyxres の musics 空き番号 N を確認する | 👆 | Pyxel Code Maker |
| 4 | 新しい View に 1 行 `pyxel.playm(N, loop=True)` を追加する | 👆 | View 直書き規約 |
| 5 | テストプレイ → 新しい場面で曲が鳴る | ✅ | シーン切替時の自動切替（次節 Design 参照） |
| 6 | 「規約に従うだけで迷わない、AudioManager の数百行を読まずに済んだ」 | ♥️ | AudioManager 撤去の効果 |

---

### Customer Journey と PRD への変更案（C+ 案・確定版）

> 最重要は **customer-jobs.md の Job**（JIS / JCR / JPA / JCT）。Job が満たされる限り、Journey と PRD の細部は **シンプルさ優先で書き換えてよい**（ユーザー方針 2026-05-07）。
> 確定版：View 内 1 行 `pyxel.playm` + 必要なら View 内 `if` 分岐。**設定画面の演出 ON/OFF は全廃**。AudioManager 撤去。

#### 改訂 1：CJ15「フィールド BGM をゾーンごとに付ける」

- **現状 After**：「Run → ゾーンが変わると曲が変わる」（zone を `choose_bgm_scene` の純粋関数で動的切替）
- **変更後 After**：表現は同じ。切替の所在を **ExploreView 内の小さな `if`**（`if in_dungeon: pyxel.playm(dungeon) elif zone >= 1: pyxel.playm(overworld) else: pyxel.playm(town)`）に移すだけ。
- **理由**：機能維持、`choose_bgm_scene` / `sync_audio` の中央集権撤去で AI は当該 View 1 ファイルだけ読めばよい。

#### 改訂 2：CJ16「戦闘 BGM を付ける」

- **現状 After**：「うわ、戦闘っぽい！ボス戦はもっとかっこよく」（`battle / boss / victory` の 3 種を `choose_bgm_scene` で切替）
- **変更後 After**：そのまま維持。boss / victory / 通常戦闘の切替は **BattleView 内の小さな `if`** に移す。
- **理由**：CJ16 のボス戦特別曲は維持できる。BattleView 1 ファイルに閉じている限り、CJ37（責務が読める）も壊れない。

#### 改訂 3：CJ20「演出の有無でゲームの印象が変わることを体験する」

- **本来の趣旨（再解釈）**：CJ20 が指す「演出」とは、**敵から攻撃を受けたときに画面を赤く光らせる／効果音を鳴らす／ダメージ数値が飛ぶ**といった "演出そのものの設計" のこと。プレイヤー設定でリアルタイム ON/OFF する機能の話ではない。
- **現状 After**：「音と光をオフにして遊んでみて」「ON に戻す → 全然違う！」と書かれており、**設定 ON/OFF 機構を前提**にしている。
- **変更後 After**：「演出（赤フラッシュ・SFX・ダメージ表示）を **作り込む前と後で見比べる**。Code Maker で SFX を空 slot に差し替えれば一時的に消せるので、それでも比較体験は成立する」と書き換える。設定画面の ON/OFF は **削除**。
- **理由**：ON/OFF UI は子の "ゲーム中の主体的選択" を増やすが、本プロダクトの主体性は **Code Maker での編集**で十分（Buy2 / JCR）。実装の複雑さを増やしてまで設定 UI で再現する必要はない（CJ44 シンプルさ優先）。
- **影響**：Job「JCT 批評家・自己判断」は Code Maker で空 pyxres を作って差し替える経路で代替可能。

#### 改訂 4：PRD `docs/product-requirements-platform.md` L57

- **現状（実装済みとして記載）**：「`せってい` の `ぜんぶ` で BGM/SFX/VFX をまとめて ON/OFF できる」
- **変更後**：**この行を削除**。`ぜんぶ` 一括機能は撤去。
- **理由**：個別 ON/OFF も含めて演出切替機能をすべて廃止するため、上位の `ぜんぶ` は意味を持たない。

#### 改訂 5：PRD `docs/product-requirements-platform.md` L58

- **現状（実装済みとして記載）**：「BGM/SFX/VFX を個別にも ON/OFF でき、切り替えはその場で反映される」
- **変更後**：**この行も削除**。BGM/SFX/VFX の個別 ON/OFF 機能を **持たない**。
- **理由**：個別 ON/OFF を維持するためだけに各 View に `if not game.bgm_enabled: return` を入れ、`game.bgm_enabled` フラグや設定 UI を保守するコストはシンプルさを損なう。BGM・SFX・VFX は **常に ON**。

#### 改訂 6：設定画面（タイトル / ゲーム内メニュー）の演出切替項目を全削除

- **現状**：設定画面に `ぜんぶ` / `BGM` / `SFX` / `VFX` の 4 項目（または同等）があり、トグル ON/OFF できる
- **変更後**：**これら 4 項目をすべて削除**。設定画面に演出関連の項目は残さない。
- **理由**：演出切替機能を撤去したので、UI も合わせて消す。設定画面はその他の項目（セーブ／ロード／タイトルへ戻る等）のみになる。

#### 改訂 7（新設）：「シンプルさは変更速度の前提条件」を CJ44 として追加

- **追加先**：`docs/customer-journeys.md` の「ガードレール」群（CJ35-CJ41 の並び）に **CJ44** を新設
- **タイトル案**：「**機能を増やしすぎず、シンプルさを保つ（変更速度の前提）**」
- **感情**：❌複雑で重く、変えるたびに時間がかかる → ❤️シンプルで素早く変更できる
- **本文要旨**：
  - AI コーディング前提のこのプロダクトでは、**変更速度 = 子の望みが届く速度**。複雑な実装は変更速度を下げ、JIS（主体性支援）と CJ08-14（デバッグループ）を直接損なう。
  - 「便利そうな機能」「将来必要そうな抽象」を足す前に、**「これを足すと変更が遅くなる」を判定する**。トレードオフは常に「機能 vs 変更速度」で、本プロダクトは **変更速度を優先**する。
  - 例：`AudioManager` の中央集権・演出個別 ON/OFF UI などは機能を提供したが、変更速度を犠牲にしていた。確定版では機能の一部（フェード／プレイリスト／演出 ON/OFF）を削り、View 1 行に降ろすことで変更速度を取り戻す。
- **`customer-jobs.md` への波及**：JIS 定義文に既に「実装による具現化」を追記済（2026-05-07）。シンプルさは JIS の "具現化" を「速い」状態に保つ前提条件として、CJ44 が JIS を支える形で位置付ける。
- **PRD `product-requirements-guardrails.md` への波及**：「複雑性を増やす変更は変更速度の検証を必須にする」を Rule として追記する（CJG44 として登録）。

---

### Gherkin（検収可能な完了条件）

> 各シナリオは AI が実装中に CoVe で自力検証できる粒度。`[Phase]` は実装段階：
> **P1** = pyxres SSoT ガード（最小差分・既存 AudioManager の `_load_tracks` だけ修正）
> **P2** = AudioManager 撤去 + View 直書き（`pyxel.playm` を View に移し、複数曲は View 内 `if` で）
> **P3** = 設定画面の演出切替項目（`ぜんぶ` / BGM / SFX / VFX）を全削除、関連フラグも全撤去
> **P4** = CJ / PRD ドキュメント改訂（CJ15/CJ16/CJ20 修正、PRD L57+L58 削除、CJ44 新設）

#### シナリオ 1：pyxres ロード済の musics / sounds を起動時に上書きしない  `[P1]`

- 🧱 Given：`pyxel.musics[i]` と `pyxel.sounds[j]` のスタブを用意し、各 slot に **非ゼロのプレースホルダ**（pyxres 由来データ相当）を事前注入する
- 🎬 When：P1 段階の fallback ガード関数を実行する
- ✅ Then：`pyxel.musics[i].set(...)` と `pyxel.sounds[j].set(...)` の `MagicMock.call_count == 0`

#### シナリオ 2：pyxres 不在 / 空 slot 時のみ fallback 書き込みが走る  `[P1]`

- 🧱 Given：`pyxel.musics[i]` と `pyxel.sounds[j]` のスタブを **空（空 note 列）** で用意
- 🎬 When：P1 段階の fallback ガード関数を実行
- ✅ Then：すべての対象 slot に対して `set(...)` が呼ばれている（`call_count > 0`）

#### シナリオ 3：BGM を持つ各シーンの View に `pyxel.playm(` がある  `[P2]`

- 🧱 Given：実装後の `src/scenes/*/view.py`
- 🎬 When：`grep -rnE 'pyxel\.playm\(' src/scenes/ --include='*.py'` を実行
- ✅ Then：BGM を持つ全シーン（少なくとも `title / town / battle / dungeon / shop / ending`）から、各ファイルに **1 行以上** マッチが返る。複数曲を持つシーン（`battle` や `explore`）は複数行マッチでよい

#### シナリオ 4：シーン切替時に前 BGM を止めて新シーン BGM を流す  `[P2]`

- 🧱 Given：`game.current_bgm` が町 BGM の index を保持し、TownView が `pyxel.playm(town)` を呼んだ直後
- 🎬 When：`game.state` が `"battle"` に変わり、BattleView の `draw()` が呼ばれる
- ✅ Then：BattleView は冒頭で「自分の BGM が再生中でない」ことを検知し、`pyxel.stop()` → `pyxel.playm(battle, loop=True)` を 1 回だけ発火する。`game.current_bgm` が更新される

#### シナリオ 5：冪等性（同フレーム / 連続フレームで重複再生しない）  `[P2]`

- 🧱 Given：BattleView が `pyxel.playm(battle)` を発火済みで `game.current_bgm == battle`
- 🎬 When：BattleView の `draw()` を 100 フレーム連続で呼ぶ
- ✅ Then：`pyxel.playm` の呼び出し回数は **1 回のみ**、`pyxel.stop` も 1 回のみ。冪等性を `MagicMock.call_count == 1` で検証

#### シナリオ 6：BattleView が boss/通常/勝利を View 内 `if` で切替できる  `[P2]`

- 🧱 Given：BattleView の model が `is_boss=True, phase="menu", enemy_hp=10`
- 🎬 When：BattleView の `draw()` が呼ばれる
- ✅ Then：`pyxel.playm` の引数が **boss BGM の index** で発火する。次に model を `phase="result", enemy_hp=0` に変えて再度呼ぶと `pyxel.playm` が **victory BGM の index** で発火。通常戦闘（is_boss=False, phase="menu"）なら通常 BGM が発火。3 ケースをユニットテストで検証

#### シナリオ 7：ExploreView が in_dungeon / zone を View 内 `if` で切替できる  `[P2]`

- 🧱 Given：`player_model.in_dungeon=True`
- 🎬 When：ExploreView の `draw()` が呼ばれる
- ✅ Then：`pyxel.playm` の引数が **dungeon BGM の index**。次に `in_dungeon=False, zone=2` で呼ぶと **overworld BGM の index**、`zone=0` だと **town BGM の index**。3 ケースをユニットテストで検証

#### シナリオ 8：AudioManager / `CHIPTUNE_TRACKS` / `choose_bgm_scene` / `sync_audio` が削除されている  `[P2]`

- 🧱 Given：実装後の `src/shared/services/audio_system.py` および `src/runtime/app.py`
- 🎬 When：`grep -nE 'class AudioManager|^CHIPTUNE_TRACKS|def choose_bgm_scene|def sync_audio' src/shared/services/audio_system.py src/runtime/app.py` を実行
- ✅ Then：マッチ 0 件。`audio_system.py` は `SfxSystem` と P1 の fallback ガード関数のみを残す薄いファイルになっている

#### シナリオ 9：framework-rule M5-1 に View での BGM 直書き規約が明文化されている  `[P2]`

- 🧱 Given：実装後の `docs/framework-rule.md`
- 🎬 When：`grep -nE 'pyxel\.playm|BGM' docs/framework-rule.md` を実行
- ✅ Then：M5-1（scene 構造規約）に「**BGM はそのシーンの `view.py` 冒頭で `pyxel.playm(N, loop=True)` を直接呼ぶ。複数曲ある場合は同 View 内の小さな `if` 分岐で選ぶ**。シーン切替時に前 BGM の `pyxel.stop` を発火する責務も同 View が持つ。**演出 ON/OFF 機構は持たない**（CJ44）」と明文化された一文がある

#### シナリオ 10：再侵入を防ぐ静的 guard  `[P2+P3]`

- 🧱 Given：実装後の `test/test_cjg_framework_rule_guards.py`
- 🎬 When：`pytest test/test_cjg_framework_rule_guards.py -q` を実行
- ✅ Then：以下の guard が緑：
  - **G1**：`audio_system.py` に `class AudioManager` `^CHIPTUNE_TRACKS` `def choose_bgm_scene` `def sync_audio` のいずれも存在しない
  - **G2**：`src/scenes/*/view.py` のうち BGM を持つシーンには `pyxel.playm(` 呼び出しが 1 件以上ある
  - **G3**：`src/scenes/*/view.py` 以外（`model.py / presenter.py / scene.py`）には `pyxel.playm(` がない
  - **G4**：`src/` 全域に `bgm_enabled` `sfx_enabled` `vfx_enabled` のいずれの代入文・参照も存在しない（演出 ON/OFF フラグの再侵入防止）

#### シナリオ 11：設定画面から演出切替項目（`ぜんぶ` / BGM / SFX / VFX）が全削除されている  `[P3]`

- 🧱 Given：実装後のタイトル設定画面 / ゲーム内メニュー設定画面のコード（`src/scenes/settings/` または `src/scenes/title/` 等）
- 🎬 When：`grep -rnE 'ぜんぶ|BGM\|SFX\|VFX|bgm_enabled|sfx_enabled|vfx_enabled|toggle_bgm|toggle_sfx|toggle_vfx' src/ --include='*.py'` を実行
- ✅ Then：演出切替に該当する文字列・関数名・属性が **0 件**。設定画面のメニュー項目から `ぜんぶ / BGM / SFX / VFX` の 4 つが消えている（コード grep + 設定項目リストの長さで検証）

#### シナリオ 12：演出関連フラグが全撤去されている（Game / PlayerModel）  `[P3]`

- 🧱 Given：実装後の `src/runtime/app.py::Game` および `src/shared/state/player_model.py::PlayerModel`
- 🎬 When：AST で両クラスのフィールドを列挙する
- ✅ Then：`bgm_enabled / sfx_enabled / vfx_enabled` のいずれの属性も **存在しない**。`set_enabled` 等のメソッドも存在しない。BGM・SFX・VFX は **常に ON** の前提でコード全体が書かれている

#### シナリオ 13：CJ / PRD の改訂が反映されている  `[P4]`

- 🧱 Given：実装後の `docs/customer-journeys.md` と `docs/product-requirements-platform.md`
- 🎬 When：以下を grep
  - `grep -nE '^- `実装済み`: ' docs/product-requirements-platform.md | grep -E 'BGM/SFX/VFX|ぜんぶ'`
  - `grep -n 'CJ44' docs/customer-journeys.md`
  - `grep -n '音と光をオフ' docs/customer-journeys.md`
- ✅ Then：（a）PRD platform.md L57 の「`ぜんぶ` で BGM/SFX/VFX をまとめて ON/OFF」と L58 の「個別にも ON/OFF」の **2 行が削除**。（b）`CJ44` が customer-journeys.md の「ガードレール」群に新設。（c）CJ20 の本文から「音と光をオフにして遊んで」が削除または **作り込み比較体験**の表現に置換。（d）CJ15 の After は表現維持・実装が View 内 `if` であることを補足。（e）CJ16 の本文は維持

#### シナリオ 14：実機で Pyxel Code Maker 編集 BGM が鳴る（人作業）  `[P1]`

- 🧱 Given：P1 実装後、Pyxel Code Maker で町 BGM の melody を改編して pyxres を保存
- 🎬 When：`python main.py` 起動 → タイトル → 町
- ✅ Then：**改編した melody が鳴る**。CC 環境では headless で再生確認できないため、最終目視確認は人作業

#### シナリオ 15：既存テストが緑のまま  `[P1+P2+P3+P4]`

- 🧱 Given：作業前 `pytest test/ -q` = 733 passed
- 🎬 When：全フェーズ完了後に再実行
- ✅ Then：（a）AudioManager / sync_audio / choose_bgm_scene / 演出 ON/OFF を直接テストしている既存 test は撤去または書き換え。（b）新 guard G1-G4 + View 単体 test 数件追加。（c）pytest コマンドは緑

---

## Design

### 大まかな責任分担

> 各役者が「何の SoT を持つか」「何を撤去するか」を上から順に固定する。
> Phase 番号は Gherkin と整合：**P1** = pyxres SSoT ガード（最小差分）／**P2** = AudioManager 撤去 + View 直書き／**P3** = 設定画面演出切替の全撤去／**P4** = CJ / PRD / CJ44 ドキュメント改訂。

#### 採用した 2 つの原則（ユーザー確認済 2026-05-07）

- **原則 A（責務分業）**：scene の `view.py` が `pyxel.playm(BGM_MUSIC_INDEX, loop=True)` を **直接呼ぶ**。住所も再生制御も View に集約する。複数曲があるシーン（戦闘の boss / 通常 / 勝利、探索の dungeon / overworld / town 等）は **View 内の小さな `if` 分岐** で選ぶ。
- **原則 B（pyxres = SSoT）**：BGM の実体（音符・リズム・音色）は `assets/blockquest.pyxres` が SSoT。Pyxel Code Maker で編集して保存したものが、ゲーム起動時の `pyxel.load` でそのまま反映される。ランタイム側からは **書き戻さない**。

#### 残す役者（C+ 確定版で生き残るもの）

1. **pyxres（`assets/blockquest.pyxres`）**
   1. BGM 実データ（musics / sounds）の SSoT
   2. Pyxel Code Maker からも、ゲーム起動時の `pyxel.load` からも読まれる
   3. ロード後はランタイム側から **書き戻さない**（ImageBanks の方針と対称）

2. **Pyxel Code Maker（外部 Buy2）**
   1. pyxres を編集する唯一の "編集 UI"
   2. 子どもが BGM の音符を直接いじる場
   3. 保存した pyxres が、次回ゲーム起動時の load 経由で反映される

3. **各 scene の `view.py` — 原則 A の主役**
   1. その scene の BGM の **住所**（`pyxel.musics[N]` の N）と **再生制御**を 1 ファイルに集約する
   2. `draw()` 冒頭で「自分の BGM が再生中でなければ `pyxel.stop()` → `pyxel.playm(N, loop=True)`」を呼ぶ（冪等）
   3. 複数曲を持つシーンは View 内の **小さな `if` 分岐** で選ぶ：
      1. `BattleView`：`is_boss / battle_phase / enemy_hp` で boss / 通常 / 勝利を選択
      2. `ExploreView`：`in_dungeon / zone` で dungeon / overworld / town を選択
   4. `grep -rnE 'pyxel\.playm\(' src/scenes/` で「どの scene にどの BGM が紐づくか」が一覧できる

4. **`Game.current_bgm: int | None` 属性 — 冪等性の単一状態**
   1. 「現在 `pyxel.playm` で発火中の music index」を保持する 1 個のフィールド
   2. 各 View が `draw()` で `if game.current_bgm != target_bgm: ...` の比較に使う
   3. View が新 BGM を発火したらここを更新する
   4. `bgm_enabled` 等の ON/OFF フラグは **持たない**（撤去対象、後述）

5. **`audio_system.py` の P1 fallback ガード関数 — 原則 B の番人**
   1. 「pyxres 不在 / 空 slot のときだけ procedural データで埋める」という責務だけに縮小して残す
   2. 関数シグネチャ例：`def ensure_music_slots(pyxel, fallback_tracks): ...`（クラスではなく関数）
   3. 中身は `_slot_has_sound` / `_music_has_data` のガードを通った slot に対してのみ `pyxel.musics[i].set(...)` / `pyxel.sounds[j].set(...)` を呼ぶ
   4. SfxSystem と対称（SFX 側は既に `_slot_has_sound` 実装済）

6. **`SfxSystem`（`audio_system.py` 内、既存）**
   1. SFX 専用の薄い service。**変更なし**
   2. `_slot_has_sound` で pyxres 尊重済（C+ 案でも維持）
   3. View からは `game.sfx.play(slot)` 等で呼ぶ既存 API を維持

7. **`docs/framework-rule.md` — 規約の SoT**
   1. **M4-2 改訂（P2）**：`AudioManager` 行を削除し、「BGM 制御は scene の `view.py` に集約」を明記
   2. **M5-1 改訂（P2）**：scene 構造規約に「**BGM はそのシーンの `view.py` 冒頭で `pyxel.playm(N, loop=True)` を直接呼ぶ。複数曲ある場合は View 内の小さな `if` 分岐で選ぶ。シーン切替時に前 BGM の `pyxel.stop` を発火する責務も同 View が持つ。演出 ON/OFF 機構は持たない（CJ44）**」を明文化

8. **`test/test_cjg_framework_rule_guards.py` — 再侵入防止 guard**
   1. **G1**：`audio_system.py` に `class AudioManager` `^CHIPTUNE_TRACKS` `def choose_bgm_scene` `def sync_audio` のいずれも存在しない（撤去確認）
   2. **G2**：`src/scenes/*/view.py` のうち BGM を持つシーンに `pyxel.playm(` が 1 件以上ある（住所宣言確認）
   3. **G3**：`src/scenes/*/{model,presenter,scene}.py` に `pyxel.playm(` がない（誤侵入防止）
   4. **G4**：`src/` 全域に `bgm_enabled` `sfx_enabled` `vfx_enabled` のいずれの代入文・参照も存在しない（演出 ON/OFF フラグの再侵入防止）

#### 撤去する役者（C+ 確定版で消えるもの）

9. **`class AudioManager`** — `audio_system.py` から **完全削除**（P2）
   1. `_load_tracks` の責務は P1 の fallback ガード関数（役者 5）に降格・移植
   2. `play_scene` / `set_enabled` / `current_scene` 状態は不要（View が直接 `pyxel.playm` を呼び、`Game.current_bgm` で冪等性確保するため）

10. **`CHIPTUNE_TRACKS` モジュール定数** — `audio_system.py` から **完全削除**（P2）
    1. scene 名 → BGM データの中央集権 dict は無くす
    2. 各 scene 固有の procedural データは fallback ガード関数の引数として渡せる軽い形に圧縮（または各 scene module 側に分散）。**ただし pyxres 経由が正規ルートで、procedural は本当に pyxres が空の時だけ**
    3. `gain` 設定は title scene の View が起動直後に 1 回だけ `pyxel.channels[*].gain = ...` を設定する形に降ろす

11. **`choose_bgm_scene` / `sync_audio` 関数** — `audio_system.py` から **完全削除**（P2）
    1. scene 横断の BGM 決定ロジック（`in_dungeon → dungeon`、`battle_phase + is_boss → boss/victory` 等）は ExploreView / BattleView 内の `if` 分岐に移植
    2. `Game.update()` 末尾の `_sync_audio_fn(self)` 呼び出しも削除（役者 12）

12. **`src/runtime/app.py::Game.update()` の `_sync_audio_fn` 呼び出し**（P2）
    1. 毎フレームの BGM 同期は不要になる（View が `draw()` で自分の BGM を冪等に発火するため）
    2. 該当行を削除し、`Game.__init__` の `_sync_audio_fn(self)` 初回呼び出しも削除

13. **演出 ON/OFF フラグ** `Game.bgm_enabled / sfx_enabled / vfx_enabled` および `PlayerModel.vfx_enabled`（P3）
    1. **すべて撤去**。BGM・SFX・VFX は常に ON
    2. 関連する `set_enabled` 等のメソッドも撤去

14. **設定画面の演出切替項目**（P3）
    1. タイトル設定 / ゲーム内メニュー設定の **`ぜんぶ` / `BGM` / `SFX` / `VFX` の 4 項目をすべて削除**
    2. 設定画面に演出関連の項目は残らない（その他の項目：セーブ・ロード・タイトルへ戻る等は維持）

15. **撤去されるテスト** — `test/test_audio_system.py` のうち AudioManager / sync_audio / choose_bgm_scene / 演出 ON/OFF を直接テストしているケース（P2/P3）
    1. 該当 test を削除または「View が `pyxel.playm` を呼ぶ」test に書き換え
    2. 新規追加：シナリオ 6（BattleView 切替）/ シナリオ 7（ExploreView 切替）/ シナリオ 5（冪等性）の View 単体 test

#### 補足：CJ / PRD / CJ44 ドキュメント改訂（P4）

- `docs/customer-journeys.md` の CJ15 / CJ16 / CJ20 を C+ 確定版に整合
- `docs/customer-journeys.md` ガードレール群に **CJ44「シンプルさは変更速度の前提条件」** を新設
- `docs/product-requirements-platform.md` L57 + L58 を削除（演出 ON/OFF を実装済として記載した行が消える）
- `docs/product-requirements-guardrails.md` に CJG44 として「複雑性を増やす変更は変更速度の検証を必須にする」を追記

#### 詳細責任分担表（ディレクトリ × ファイル × メソッド × Phase）

> 実装着手時に「どこを触るか／触らないか」を一覧化。新規行は Phase 列の P1-P4 が touch する範囲を示す。

| ディレクトリ | ファイル | 担う責務（C+ 確定版） | 主要メソッド／関数 | Phase |
|---|---|---|---|---|
| `src/runtime/` | `app.py::Game` | runtime 殻。`current_bgm: int \| None = None` 属性を保持。`AudioManager` の生成と `_sync_audio_fn` 呼び出しを撤去 | `Game.__init__`、`Game.update` の末尾、`run()` 直前 | P2 |
| `src/scenes/title/` | `view.py::TitleView` | title BGM の直接再生 + 起動時に `pyxel.channels[*].gain` を設定（旧 AudioManager の責務を引き受け） | `TitleView.draw()` 冒頭 | P2 |
| `src/scenes/title/` | `presenter.py::TitlePresenter` | save_data 復元時の `bgm_enabled / sfx_enabled / vfx_enabled` コピーを削除 | `apply_save_data` 周辺の 3 行 | P3 |
| `src/scenes/town/` | `view.py::TownView` | town BGM の直接再生 | `TownView.draw()` 冒頭 | P2 |
| `src/scenes/explore/` | `view.py::ExploreView` | 探索 BGM の `if` 分岐：`in_dungeon → dungeon`、`zone >= 1 → overworld`、それ以外 `town` | `ExploreView.draw()` 冒頭 | P2 |
| `src/scenes/battle/` | `view.py::BattleView` | 戦闘 BGM の `if` 分岐：`phase == "result" and hp <= 0 → victory`、`is_boss → boss`、それ以外 `battle` | `BattleView.draw()` 冒頭 | P2 |
| `src/scenes/ending/` | `view.py::EndingView` | ending BGM の直接再生 | `EndingView.draw()` 冒頭 | P2 |
| `src/scenes/settings/` | `model.py / presenter.py / view.py / view_model.py / scene.py` | **シーン全体を撤去するか、`back` 項目だけ残す薄い構造に縮小**。演出切替 4 項目（ぜんぶ / BGM / SFX / VFX）をすべて削除 | `_rows`, `_toggle`, `apply_av`, `build_view_model` | P3 |
| `src/scenes/menu/` | `presenter.py` 等 | settings シーンへの遷移を残すなら scene を縮小、撤去するなら遷移コードも削除 | settings 遷移箇所 | P3 |
| `src/shared/services/` | `audio_system.py` | **`AudioManager` / `CHIPTUNE_TRACKS` / `TRACK_ORDER` / `melody_slot` / `bass_slot` / `drum_slot` / `music_index` / `track_slot` / `choose_bgm_scene` / `sync_audio` を全削除**。`SfxSystem` のみ残す。`SfxSystem.set_enabled` も削除（常に ON） | （撤去対象の関数群） | P2 / P3 |
| `src/shared/services/` | `vfx.py::VfxSystem` | `player_model.vfx_enabled` チェックを削除（常に発火）。判定ロジックは `timer / VFX_FLASH cfg` のみに | `start`, `draw_overlay` | P3 |
| `src/shared/services/` | `player_state.py` | `bgm_enabled / sfx_enabled / vfx_enabled` の save / load を全削除 | `_normalize_player_data`, `serialize`, `setdefault` 群 | P3 |
| `src/shared/state/` | `player_model.py::PlayerModel` | `bgm_enabled / sfx_enabled / vfx_enabled` 3 フィールドを削除。`__slots__` 等にあれば併せて削除 | クラス定義、`__slots__` 群 | P3 |
| `docs/` | `framework-rule.md` | **M4-2 改訂**：`AudioManager` 行を削除、「BGM 制御は scene の `view.py` に集約」と注記。**M5-1 改訂**：「BGM は `view.py` 冒頭で `pyxel.playm(N, loop=True)` を直接呼ぶ。複数曲は View 内 `if`。シーン切替時 `pyxel.stop` を発火。演出 ON/OFF は持たない（CJ44）」を明文化 | M4-2 / M5-1 節 | P4 |
| `docs/` | `customer-journeys.md` | CJ15 / CJ16 / CJ20 の Before/After を C+ 確定版に整合。**CJ44「シンプルさは変更速度の前提条件」** をガードレール群に新設。一覧表（L38-82 周辺）にも CJ44 を追加 | CJ15 / CJ16 / CJ20 / 一覧表 / CJ44 新規 | P4 |
| `docs/` | `customer-jobs.md` | JIS の定義文に「実装による具現化」既追記済（2026-05-07）→ そのまま | （変更なし） | — |
| `docs/` | `product-requirements-platform.md` | L57 「`ぜんぶ` で BGM/SFX/VFX をまとめて ON/OFF」L58「個別にも ON/OFF」を削除。Gherkin 例にある演出 ON/OFF も削除 | L55-90 周辺 | P4 |
| `docs/` | `product-requirements-guardrails.md` | **CJG44**「複雑性を増やす変更は変更速度の検証を必須にする」を追記 | 末尾の Guardrail 一覧 | P4 |
| `docs/` | `architecture.md` | AudioManager / sync_audio への参照箇所を整理（あれば） | grep 結果次第 | P4 |
| `test/` | `test_cjg_framework_rule_guards.py` | **新クラス `AudioBoundaryGuardTest`** を追加：G1（AudioManager 等の不在）/ G2（View に playm 1 件以上）/ G3（model/presenter/scene に playm 0 件）/ G4（bgm_enabled 等の代入・参照 0 件） | 新規 4 メソッド | P2 / P3 |
| `test/` | `test_audio_system.py` | `test_play_scene_*` `test_set_enabled_*` `test_load_tracks_*` 等の AudioManager 関連 test を撤去または「View 直書き」test に書き換え | （該当 test 群） | P2 |
| `test/` | `test_player_state.py` 系 | `bgm_enabled / sfx_enabled / vfx_enabled` を assert している test を削除 | （該当 test 群） | P3 |
| `test/` | `test_settings_*.py` 系 | 設定画面の演出切替 test を削除（または撤去された scene の代替 test に） | （該当 test 群） | P3 |
| `test/` | `test_audio_pyxres_ssot.py` （新規） | シナリオ 1 / 2 / 6 / 7 / 8 をユニットテストとして追加 | 新規 5-7 メソッド | P1 / P2 |

---



---

## 4) Tasklist


### 作業記録

> Observe → Think → Act を刻む。

#### 2026-05-06 01:00（起票）

**Observe**：直前会話で「pyxel.bltm が 1 か所だけのわりに shared/services にマップ系コードが多い」を整理した流れで、ユーザーから「音楽や効果音は pyxres から直読みしているか？」と問い。grep で `AudioManager._load_tracks` が無条件 `.set()` を打つことを発見。SFX 側には `_slot_has_sound` ガードがあって対称が崩れている。
**Think**：BGM 側に同じガードを入れれば SFX と完全対称になり、最小差分で「Code Maker 編集が runtime に反映」が成立。`_music_has_data` は pyxel.Music API の属性名を複数 try する防御的な実装で FakeMusic 互換も担保。framework-rule.md M4-2 と image_banks.py docstring も同改訂で揃える。
**Act**：本タスクノートを起票し Journey/Gherkin/Design/Tasklist を書いた。実装単位は最小（audio_system.py への 2 ヘルパ追加 + `_load_tracks` のガード化 + docstring 3 か所）。ユーザー承認後に実装へ進む。

---

## 5) Result（成果物）

### P1: pyxres SSoT ガード（事前タスクで実施済み）

- `bake_world_to_tilemap` の `T_PATH` 上書きを停止して pyxres を SSoT に
- `world_map_ssot` failing test と probe を追加・解消（commit 2d07caf, 9e57930, 66e90a3, 5bffd21, 4f5cf52）

### P2: AudioManager 撤去 + View 直書き

- `src/shared/services/audio_system.py`: AudioManager / CHIPTUNE_TRACKS / TRACK_ORDER /
  choose_bgm_scene / sync_audio / MELODY_CHANNEL / BASS_CHANNEL / DRUM_CHANNEL / BGM_CHANNEL を撤去
- `src/scenes/{title,explore,battle,ending}/view.py` に `play_bgm()` と BGM_INDEX 定数を追加
- `src/scenes/{title,explore,battle,ending}/scene.py::draw()` で `_play_*_bgm(game)` を呼び出し
- `src/runtime/app.py`: `self.audio` 撤去、`current_bgm: int | None` 追加、`_sync_audio_fn` 撤去
- `src/runtime/main_runtime.py` shim から `sync_audio` import を撤去
- 削除テスト: test_cjg_audio_manager_behavior / test_audio_system / test_cjg_audio_bgm_sfx /
  test_cjg_sync_audio_player_model / test_cjg20_av_toggle
- 更新テスト: test_dialogue_integration / test_architecture_layout / test_cjg_game_init_smoke

### P3: 演出 ON/OFF フラグ + 設定画面項目を撤去

- `src/shared/state/player_model.py`: `bgm_enabled` / `sfx_enabled` / `vfx_enabled` を撤去
- `src/shared/services/player_state.py`: 同上、`SAVED_PLAYER_KEYS` から AV キー除去、
  `restore_snapshot` は legacy AV キーを `pop` で無視
- `src/shared/services/vfx.py`: `vfx_enabled` チェックを撤去（VFX 常時 ON）
- `src/shared/services/audio_system.py`: `SfxSystem.set_enabled` も撤去（SFX 常時 ON）
- `src/scenes/title/{model,presenter,scene,view}.py`: 「せってい」項目と `settings_open` を撤去、
  メニューを 2 項目（はじめから / つづきから）に縮小
- `src/scenes/menu/presenter.py`: 「せってい/SETTINGS」を撤去、メニューを 5 項目に縮小
- `src/scenes/settings/` ディレクトリ全体を git rm（model.py / view_model.py / view.py /
  presenter.py / scene.py / __init__.py）
- `src/runtime/app.py`: `SettingsScene` import / `self.settings_scene` / state == "settings"
  分岐 / `apply_av` 呼び出しをすべて撤去
- `src/runtime/main_runtime.py` shim から `SettingsScene` import を撤去
- `tools/codemaker_manifest.txt` から `src/scenes/settings/*.py` 5 行を削除
- 削除テスト: test_cjg_settings_scene_navigation / test_game_settings
- 更新テスト: test_cjg_title_scene_behavior / test_cjg_menu_navigation /
  test_player_factory / test_player_snapshot / test_player_model /
  test_cjg_save_round_trip / test_cjg_vfx_system / test_damage_vfx /
  test_scene_responsibilities / test_cjg_game_init_smoke

### P4: CJ / PRD / CJ44 ドキュメント改訂

- `docs/customer-journeys.md`: CJ20 の意味を「演出 ON/OFF UI で比較する」から「演出を実際に
  当てて違いを体験する」に改訂、CJ44「シンプルさは変更速度の前提条件」を新設（一覧表 + 詳細節）
- `docs/product-requirements-av.md`: 冒頭に CJ44 確定版の改訂概要を追加、CJG15/16/19/20/24 の
  実装状況を更新、CJG20 と CJG44 の節を新設、共通条件から ON/OFF 関連 Rule を撤去
- `docs/product-requirements-platform.md`: CJG20 を AV PRD に移管（旧 ON/OFF UI 内容は撤去）、
  CJG26 の `Sound / Music` 実装状況を「pyxres SSoT」に更新
- `docs/product-requirements-guardrails.md`: AudioManager / SfxSystem の上書き禁止 Rule を
  「pyxres = SSoT」基準に書き換え、Scenario 名を `pyxres の Sound / Music が runtime audio の正本になる` に改訂
- `docs/framework-rule.md`: AudioManager 言及を「View が pyxel.playm を直接呼ぶ」に書き換え、
  Infrastructure Service 一覧から AudioManager を撤去（SfxSystem に置換）
- `docs/architecture.md`: Game.__init__ の DI 一覧と Scene 表（11→10）を更新、audio_system.py
  の責務を「SFX 再生のみ」に書き換え

### 詳細責任分担表（P4 補足、タスクノート 3) Design に追記済）

directory × file × method × Phase の網羅表を Design セクションに追加。各 view.py の
play_bgm() / scene.py の _play_*_bgm 呼び出し / audio_system.py の SfxSystem を確認可能。

### テスト結果

最終 pytest: **674 passed, 2 skipped** （6.05s）。失敗なし。

---

## 6) Discussion（反省）

### 設計判断の振り返り

**最も大きな判断は「中央集権の AudioManager を撤去して View が pyxel.playm を直接呼ぶ」。**
M1（View だけが Pyxel に触れる）の例外として明示的に View からの BGM 発火を許可したが、
代わりに「scene 横断の BGM ステートマシン」が消えるので変更速度が劇的に上がった。

副作用として、scene を増やすたびに view.py に play_bgm() を書く必要がある。
これは「コピペ 5 行」なので CJ44 シンプルさ優先の判断と整合する（抽象化したくなったら
それは複雑度の負債）。`_INITIAL_GAIN_APPLIED` を title/view.py だけに置く判断も同様：
gain 設定は「最初に 1 度だけ」なので、最初に開く scene が責任を持つだけで足りる。

### 副次的な気づき

1. **「便利な設定画面」は子どもにも親にも実は不要だった**。BGM/SFX/VFX 個別 ON/OFF UI
   が無くなっても誰も困らない。なぜなら「うるさい→OFF にする」は親の都合であり、
   子の「こうしたい」を実装する力にはならない。撤去で得たもの（コードの単純さ）の方が
   遥かに大きい。

2. **「PlayerModel に AV フラグを置く」は典型的な over-design だった**。設定値は
   セーブに含まれるべきものではなく、起動時のデフォルトでよい。撤去によりセーブデータの
   フォーマット変更も最小化された（古いセーブは AV キーを持っていても無視される）。

3. **テストを「機能のあるなし」ではなく「ユーザーストーリー」で書く重要性**。
   `test_play_while_disabled_is_noop` のような実装詳細テストは、機能撤去時に削除コストが
   高い。CJ44 を docs に書いて行動指針にしたことで、今後この種のテストを書きにくくなる。

### 残課題（次タスクノートで対応）

- **production bundle 再ビルド**：本変更は Code Maker 互換 bundle に影響するため、
  `tools/build_codemaker.py` を再実行して dist/ を更新する必要がある。
  → 別タスクノートで実施（自動委任可）。
- **古いセーブの互換確認**：`bgm_enabled` / `sfx_enabled` / `vfx_enabled` を含むセーブの
  ロード経路は `restore_snapshot` で `pop` するためテスト上はカバー済み。
  実機で v1 セーブからのロードを 1 回だけ確認しておきたい（自動化困難なので親の手作業）。
- **CJG19 フェード演出の再評価**：今回 wont 扱いにしたが、もし子どもから「町に入るときに
  ふわっとして欲しい」要望が出たら CJ44 の判断軸に従って再検討する。

### 反省

- **「途中確認禁止」指示を受けて自走できた**。8 件のテスト失敗を順に潰して P3 を完遂し、
  ドキュメント 6 ファイルの整合も自分で取れた。逆に、ユーザーが介入したくなる箇所
  （Journey / Gherkin の文言など）を最初に固めてから委任に入るスタイルが効いた。
- **manifest 修正・bundle 再ビルドの「忘れがちな後処理」もチェックリスト化が必要**。
  今回は `tools/codemaker_manifest.txt` を test 経由で機械的にチェックできたので問題なかった。

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：bundle 再ビルド（別タスクノート）
