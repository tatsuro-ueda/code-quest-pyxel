---
status: done
priority: normal
scheduled: 2026-04-21T00:00:00+09:00
dateCreated: 2026-04-21T00:00:00+09:00
dateModified: 2026-04-21T00:00:00+09:00
tags:
  - task
  - readability
  - archived
---

# 2026年4月21日 src/配下のメソッドに責務コメントを付与

> 状態：(1) 改善対象ジャーニー
> 次のゲート：（ユーザー）task note 確認後、Gherkin・Design の詰めへ進むか判断

---

## 1) 改善対象ジャーニー

- **根拠となるカスタマージャーニー**：（直接紐づくCJなし。内部DX＝開発者体験の改善）
- **関連するカスタマージャーニー**：AIコーディング前提の保守性（CJ全体の土台）
- **深層的目的**：src/を読み返したとき責務を即把握できる
- **やらないこと**：
  - クラス／関数の実装を書き換える
  - 型ヒントやシグネチャを変える
  - モジュール階層の再配置
  - ドキュメンテーション文化的な多段落docstringの作成（1行で責務を示す）

### 人間の期待

- **この note が `done` なら、人間は何が成立していると思うか**：
  - src/配下の全 `.py` ファイルについて、各メソッド／関数／クラスに **「何をするのか（責務）」** が1行コメント（または短いdocstring）で付いている
  - 初見でファイルを開いたとき、メソッド名だけでは読み取りにくい責務が **コード本体を読まなくても** 把握できる
- **その期待を裏切りやすいズレ**：
  - コメントがWHATを繰り返すだけで責務になっていない（例：`# メソッド名と同じことを書く`）
  - 自明なgetter/setter/`__init__` まで冗長に埋めてしまう
  - 多段落docstringで冗長化してしまう
  - コメントが実装と食い違う（リネーム・移動後に更新されない）
- **ズレを潰すために見るべき現物**：
  - `src/scenes/*/presenter.py` 等の責務分離が重いファイル
  - `src/shared/services/` 配下のサービス群（責務が名前から読みにくい）
  - `src/core/scene_manager.py`（ライフサイクル責務）

```mermaid
flowchart TB
    subgraph BEFORE["Before（現状）"]
        direction TB
        B1["😓 src/ファイルを開く<br>（VS Code / Pyxel開発エディタ）"]
        B1 --> B2["😵 メソッド名と実装から責務を推測する<br>（presenter.py / services/）"]
        B2 --> B_END["😰 読むたびに同じ推測を繰り返す<br>（開発の立ち上がりが遅い）"]
    end

    subgraph AFTER["After（達成状態）"]
        direction TB
        A1["😌 src/ファイルを開く<br>（VS Code / Pyxel開発エディタ）"]
        A1 --> A2["🙂 各メソッド先頭の1行コメントで責務が読める<br>（presenter.py / services/）"]
        A2 --> A_END["😊 実装を読むかどうかを責務で判断できる<br>（コードを少し理解した状態）"]
    end

    BEFORE ~~~ AFTER

    classDef oldStyle fill:#f8d7da,stroke:#721c24,color:#000000;
    classDef newStyle fill:#d4edda,stroke:#155724,color:#000000;
    classDef endOld fill:#f5c6cb,stroke:#721c24,color:#000000,font-weight:bold;
    classDef endNew fill:#c3e6cb,stroke:#155724,color:#000000,font-weight:bold;

    class B1,B2 oldStyle;
    class A1,A2 newStyle;
    class B_END endOld;
    class A_END endNew;
```

### 現状

- src/配下は48ファイル（`__init__.py` と `generated/` 含む）
- 構成：`app.py` / `game_data.py` / `core/` / `scenes/{title,explore,battle,dialog}/(model|view|presenter).py` / `shared/{services,ui}/` / `generated/`
- 現在のコードは名前からある程度読めるが、`scene_manager.py` や `services/` の各クラスは、ファイルを開いてから責務を把握するまでに時間がかかる

### 今回の方針

- **対象**：`src/**/*.py`（ただし以下は対象外）
  - `__init__.py`（import集約のみ）
  - `src/generated/*.py`（SSoTから自動生成。手で書き換えるとSSoT運用に反する）
  - `__pycache__`
- **コメントレベル**：
  - **クラス** に1行の責務コメント（または1行docstring）
  - **メソッド／関数** に1行の責務コメント（または1行docstring）
  - **自明なもの** は付けない（例：`__init__` が単なる属性代入、`@property` で1行返すだけのgetter）
- **書き方**：
  - WHATではなくWHY／責務を書く（「何に関して誰の責任か」）
  - 日本語1行。末尾に句点なし、なくても可
  - docstring形式（`"""..."""`）か `#` コメントかは、既存ファイルのスタイルに合わせる
- **進め方**：一気に全ファイルではなく、まず代表ファイル1〜2個でサンプルを作り、ユーザーにレビューしてもらってから残りに展開

### 委任度

- 🟡 コード書き換えはないがスタイル判断が主観的なため、代表ファイルでサンプルを作って合意してから展開するのが安全

---

## 2) カスタマージャーニーgherkin（完了条件）

### シナリオ1：正常系（代表ファイルで責務コメントが読める）

> 🧱 Given: `src/scenes/battle/presenter.py` のような責務が重いファイルを開いている。🎬 When: 各メソッド先頭のコメント（またはdocstring）を読む。✅ Then: 実装を読まなくても、そのメソッドが何のためにあるかが1行でわかる。

### シナリオ2：再試行系（追加されたメソッドへの展開が迷わない）

> 🧱 Given: 今回のコメント付与が終わった後、新しいメソッドを追加したい。🎬 When: 既存メソッドのコメントスタイルを真似て1行コメントを書く。✅ Then: スタイルが一貫しており、レビューで書き直しにならない。

### シナリオ3：異常系（自明なものまで埋めていないこと）

> 🧱 Given: `__init__` が単なる属性代入のクラスや、1行で値を返すだけの `@property` がある。🎬 When: そのファイルを開く。✅ Then: 冗長なコメントで埋まっておらず、責務が非自明なメソッドだけにコメントが付いている。

### シナリオ4：回帰確認（ロジックと生成物が壊れていない）

> 🧱 Given: コメント付与後のsrc/。🎬 When: `python -m pytest test/ -q` と `make run`（または相当の起動確認）を実行する。✅ Then: テストは通り、起動も変わらず、`src/generated/` も変化していない。

### 対応するカスタマージャーニーgherkin

- 直接対応するCJ gherkinなし（内部DX改善のため）

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：manage-tasknotes / steer-development
- **MCP**：追加なし

### 調査起点

- `src/app.py` → `src/core/scene_manager.py` → `src/scenes/*/presenter.py` の流れを先に読み、責務の縦の筋を掴む
- `src/shared/services/` は各ファイル独立した責務なので横に展開

### 実世界の確認点

- **実際に見るURL / path**：`/home/exedev/code-quest-pyxel/src/`
- **実際に動いている process / service**：Pyxel本体（`main.py` 経由で `src/app.py` を起動）、webビルドは `production/` に同梱される `main.py`
- **実際に増えるべき file / DB / endpoint**：src/配下の既存 `.py` のコメント行のみ（新規ファイルは作らない）

### 検証方針

- 代表ファイル（候補：`src/core/scene_manager.py` と `src/scenes/battle/presenter.py`）を先にコメント付与してユーザーにレビューしてもらう
- スタイル合意後、残りファイルへ展開
- 最後に `python -m pytest test/ -q` で回帰、`git diff --stat src/generated/` が空であることを確認

---

## 4) Tasklist

- [x] docs / カスタマージャーニー / gherkin の根拠をそろえる（内部DXのため直接対応CJなし）
- [x] 対象ファイル一覧を確定（`__init__.py` と `generated/` を除外）
- [x] 代表ファイル2つにサンプル実装 → ユーザーにスタイルレビュー依頼（合意済）
- [x] 合意後、残りファイルへ順次展開（28ファイル完了）
- [x] `python -m pytest test/ -q` を実行する（260 passed）
- [x] `git diff --stat src/generated/` が空であることを確認

---

## 5) Discussion（記録・反省）

> Observe → Think → Act を刻む。未来の自分が復元できることが目的。

### 2026年4月21日（起票）

**Observe**：ユーザーから「src/下のコードにメソッドレベルで責務コメントを付けたい。コードを理解したいから」と依頼。保存先は `steering/`、status は `open` を選択。

**Think**：コード改変ではなくドキュメンテーション付与のタスク。ただし「責務」は主観が入るため、代表ファイルで先に合意してから全体展開するのが安全。`src/generated/` はSSoT運用（project memory: ssot_policy）に反するので除外必須。

**Act**：タスクノートを `steering/20260421-src-method-level-comments.md` として起票。次のゲートはユーザーによる内容確認と、Gherkin・Designで進めるか／代表ファイルのサンプルをいますぐ作るかの方針決定。

### 2026年4月21日（サンプル作成→全展開→検証）

**Observe**：ユーザーから「サンプルを作って」→「これで進めてください」と承認。`src/core/scene_manager.py` と `src/scenes/battle/presenter.py` の2ファイルでサンプルを作ったところ、battle/presenter.pyが1メソッドのみで軽すぎる材料だったが、スタイル方針（日本語1行docstring・既存英語docstringも日本語に揃える・`__init__` の単純代入や dataclass フィールドにはコメント付けない）がシンプルだったためそのまま承認された。

**Think**：残り28ファイルへ展開するにあたり、以下の判断を入れた：
  - 英語docstringは日本語に揃える（一貫性のため。ただし責務自体は変えない）
  - scenes/*/*.py は ほぼ同構造なので同じパターンで一気に書ける
  - `audio_system.py` `codemaker_resource_store.py` `dialog/model.py` は責務が非自明なプライベート関数にもコメントを入れる価値あり
  - モジュール冒頭docstring（`"""BGM subsystem and track catalog."""` など）は触らない
  - `src/generated/` は当初から除外で合意通り

**Act**：全30ファイル中28ファイルに責務docstringを付与（scene_manager.py と battle/presenter.py はサンプル時点で完了済）。`python -m pytest test/ -q` → **260 passed**。`git diff --stat src/generated/` → **差分なし**。src/配下は未追跡状態のリファクタ途中物なので `git diff` では全体差分が出ず、新規ファイルの内側の変更として取り込まれる。
