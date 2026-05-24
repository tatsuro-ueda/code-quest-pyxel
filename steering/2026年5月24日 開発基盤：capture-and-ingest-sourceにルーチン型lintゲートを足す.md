---
status: open
priority: high
scheduled: 2026-05-24T08:03:54.000+00:00
dateCreated: 2026-05-24T08:03:54.000+00:00
dateModified: 2026-05-24T08:03:54.000+00:00
tags:
  - task
  - llm-wiki
  - ingest
  - skill
  - lint
  - routine
---

# 2026年5月24日 開発基盤：capture-and-ingest-sourceにルーチン型lintゲートを足す

> 状態：② ユーザーストーリーマップ
> 次のゲート：（ユーザー）話題3：どこまで routine 型へ寄せるか

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 ingest skill の停止点を人にも lint にも読める形へ寄せる
> 補足：やらないこと 今回は ingest 本体の挙動変更や wiki 内容追加まで広げない
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 `capture-and-ingest-source` は user skill として運用中である
   2. 💦 dotfiles には routine-skill lint の spec と runner がある
   3. 💦 いまはこの skill が lint target に入っていない

2. Before
   1. 💦 要約確認や continue mode は本文にあるが lint では見えない
   2. 💦 gated profile は `状態` `次のゲート` と `Public API` を求める
   3. 💦 今の skill 本文はその shape にまだ寄っていない
   4. ❌ 迷う

3. After
   1. 💦 どの rule と profile で gate を付けるか決まる
   2. ✅ skill 更新時に停止点の崩れを lint で止められる
   3. ✅ `textlint` と呼んでいた gate の実体も repo 基準でそろう
   4. ❤️ 安心

4. 例外
   1. full rewrite が重ければ lighter profile を選んでもよい
   2. 呼び名が `textlint` でも実装は custom runner でよい

5. 境界条件
   1. scope は skill 文書と lint 設定までに絞る
   2. raw ingest の logic や wiki 更新は今回触らない
   3. tasknote 起票を先に行い実装は次ゲート後に回す

6. 委任度
   1. 🟡 調査は固まったが format 方針だけ人の確認が要る
   2. 🟢 CCのみで可：現状差分の整理と tasknote 起票
   3. 🟡 一部判断要：full rewrite か軽量拡張かの選択
   4. 🟢 CCのみで可：方針確定後の skill と lint の実装

---

## 2) ユーザーストーリーマップ

> 今回は調査結果を、現状把握、差分整理、方針選択の 3 話題に分ける。
> 委任度：🟡 調査は終わったが、実装方式の確定だけ人の確認が要る
> 残る曖昧さ：`capture-and-ingest-source` を gated routine 本文へ寄せ切るか未確定

### 事前確認

- [x] tasknote確認済み
- [x] skill・tool・MCP確認済み
  - [x] `manage-tasknotes`
  - [x] `research`
- [x] skill・tool・MCP
  - [x] `manage-tasknotes`
  - [x] `research`
- [x] 永続的ドキュメント確認済み
  - [x] `AGENTS.md`
  - [x] `~/dotfiles/claude/.claude/skills/manage-tasknotes/TEMPLATE.md`
  - [x] `~/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`
  - [x] `~/dotfiles/shared/linter/specs/routine-skill/routine_skill_rules.yml`
  - [x] `~/dotfiles/shared/linter/coding-rules/routine-skill/run_skill_lint.mjs`
  - [x] `~/dotfiles/shared/linter/coding-rules/routine-skill/batch_gate.mjs`
  - [x] `~/dotfiles/shared/linter/coding-rules/routine-skill/doc_fields.mjs`

#### 話題1：いまある routine-skill lint を確認する

##### ユーザー：この repo の skill 運用者（現状確認）

1. 当初計画
    1. 👀 spec の profile と target を確認する
    2. 👀 runner が target 未登録なら skip することを確認する
    3. 👀 `batch_gate` と `doc_fields` の必須形を抜き出す

#### 話題2：capture-and-ingest-source の現状差分を出す

##### ユーザー：この repo の skill 運用者（差分整理）

1. 当初計画
    1. 👀 skill 内の preview、review、continue gate を拾う
    2. ✂️ `状態` `次のゲート` `Public API` の欠けを整理する
    3. 📝 lint target 未登録も差分として固定する

#### 話題3：どこまで routine 型へ寄せるか

##### ユーザー：この repo の skill 運用者（方針選択）

1. 当初計画
    1. 🅰️ 既存 `skill_procedural_gated` に乗るよう本文を再構成する
    2. 🅱️ 現行構成を残して専用 profile や rule を足す
    3. 📌 第一案は A、重すぎるときだけ B に落とす

---

## 3) Gherkin（完了条件）

> 委任度：🟡 受け入れ条件は書けるが、A/B 確定前に実装は始めない
> 残る曖昧さ：A/B のどちらを採るか

### シナリオ一覧

- [ ] シナリオ1：capture-and-ingest-source が routine lint の target として解決される

1. 🧱 routine-skill spec と runner がある
2. 🎬 `capture-and-ingest-source` の path を lint 対象へ登録する
3. ✅ `run_skill_lint` がこの skill を skip せず評価する

```gherkin
Given routine-skill spec と runner が dotfiles にある
When `capture-and-ingest-source` の path を target に登録する
Then `run_skill_lint` はこの skill を skip しない
And 適用された profile 群が結果から分かる
```

- [ ] シナリオ2：選んだ方式で gate が機械的に読める

1. 🧱 skill の gate 位置を本文で表現している
2. 🎬 A または B の方式で lint rule を適用する
3. ✅ `状態` と `次のゲート` 相当の停止点ずれを検出できる

```gherkin
Given skill に preview review continue などの gate がある
When 選んだ profile と rule で lint を実行する
Then gate の開始位置と次の停止点が機械的に読める
And 本文とのずれがあれば lint finding として返る
```

- [ ] シナリオ3：skill の読みやすさを落とさず gate を追加できる

1. 🧱 skill は user invocable な長い運用手順を持つ
2. 🎬 本文再構成または専用 profile 追加を行う
3. ✅ summary draft と continue mode の流れが今より読みにくくならない

```gherkin
Given `capture-and-ingest-source` は summary draft と continue mode を含む
When skill 本文または lint profile を更新する
Then user は preview review finalize の流れを追える
And lint のためだけの不自然な構造増殖は起きない
```

---

## 4) Design（どうやるか）

### 責務分担概要

- 第一案は `capture-and-ingest-source` を routine 型の shape へ寄せる
- その場合は既存 `skill_procedural_gated` を再利用し target 追加で済ませる
- 本文の可読性が大きく落ちるなら、現行構成を保った専用 profile を足す
- どちらでも `run_skill_lint` と markdownlint の両方で止める

### 責務分担概要図

```mermaid
flowchart TD
    A[現行 skill] --> B{方式選択}
    B -->|A| C[SKILL本文を routine 型へ再構成]
    B -->|B| D[専用 profile と target を追加]
    C --> E[spec に target を登録]
    D --> E
    E --> F[run_skill_lint]
    F --> G[markdownlint と sync check]
```

```mermaid
flowchart TD
    D1[① 現状調査] --> D2[② tasknote 起票]
    D2 -->|ゲート1: ユーザー| D3[③ 方式A/B確定]
    D3 --> D4[④ skill と spec 修正]
    D4 --> D5[⑤ lint 実行]
    D5 --> D6[⑥ 結果共有]
```

### 責務分担詳細

- `steering/2026年5月24日 開発基盤：capture-and-ingest-sourceにルーチン型lintゲートを足す.md`
  （➕：今回の調査結果と方式分岐を固定する）
- `~/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`
  （✏️：routine 型へ寄せるか現行 shape を残すかの主対象）
- `~/dotfiles/shared/linter/specs/routine-skill/routine_skill_rules.yml`
  （✏️：target と profile を登録する正本）
- `~/dotfiles/shared/linter/coding-rules/routine-skill/run_skill_lint.mjs`
  （➕：target 解決の動作確認に使う runner）
- `~/dotfiles/shared/linter/coding-rules/routine-skill/batch_gate.mjs`
  （➕：既存 gate rule の要件確認に使う）
- `~/dotfiles/shared/linter/coding-rules/routine-skill/doc_fields.mjs`
  （➕：`Public API` block 要件の確認に使う）

### 調査結果

- current skill は要約確認 gate を本文に持つが routine target ではない
- `skill_procedural_gated` は `doc_fields` と `batch_gate` を含む
- `batch_gate` は `> 状態` と `> 次のゲート` を本文見出しへ解決する
- `doc_fields` は `## Public API` 内の番号 block に `Goal` `Returns` `Policy` を求める
- つまり既存 gated profile をそのまま使うなら、skill 本文の shape をかなり寄せる必要がある

### 【参照】

- Steering: `steering/2026年5月24日 開発基盤：capture-and-ingest-sourceに要約確認ゲートを追加する.md`
- Steering: `steering/2026年5月24日 開発基盤：capture-and-ingest-sourceにrelated page更新とingest logを足す.md`
- Architecture: `AGENTS.md`
- Skill: `~/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`
- LintSpec: `~/dotfiles/shared/linter/specs/routine-skill/routine_skill_rules.yml`
- Runner: `~/dotfiles/shared/linter/coding-rules/routine-skill/run_skill_lint.mjs`

### 変更範囲

- やること:
  - routine lint と現行 skill の差分を 1 つの方針へ寄せる
  - 必要な target/profile/rule の追加または skill 本文の再構成を行う
  - gate 崩れを止める検証コマンドを残す
- やらないこと:
  - ingest の中身や wiki 反映の挙動を変えること
  - `entities/` や `concepts/` などの新構造を作ること
  - tasknote 起票と同時に実装まで完了扱いにすること

### 検証

- 検証コマンド:
  - `node /home/exedev/dotfiles/shared/linter/coding-rules/routine-skill/run_skill_lint.mjs /home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md --root /home/exedev/dotfiles`
  - `npx -y markdownlint-cli2 '/home/exedev/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md'`
  - `python3 /home/exedev/dotfiles/codex/.codex/scripts/sync_claude_skills_to_agents.py --check`
- 成功条件:
  - `capture-and-ingest-source` が lint target として評価される
  - gate の summary と本文ずれが lint で止まる
  - summary draft と continue mode の流れが still readable である
- 未実施時の扱い:
  - いずれか未実施なら gate 追加完了扱いにしない

---

## 5) Tasklist

- [x] 現状調査をして差分を整理する
- [x] tasknote を起票する
- [ ] 方式 A/B を確定する
- [ ] skill 本文または lint profile を更新する
- [ ] lint と sync check で検証する

---

## 6) 作業ログ

- `capture-and-ingest-source` は routine lint の target 未登録だった
- 既存 gated profile は `状態` `次のゲート` `Public API` を前提にしていた
- tasknote では、full rewrite と lighter profile の 2 案を比較できる形にした

---

## 7) 評価と成果物

- 調査対象:
  - `~/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`
  - `~/dotfiles/shared/linter/specs/routine-skill/routine_skill_rules.yml`
  - `~/dotfiles/shared/linter/coding-rules/routine-skill/run_skill_lint.mjs`
- 成果物:
  - `steering/2026年5月24日 開発基盤：capture-and-ingest-sourceにルーチン型lintゲートを足す.md`
- 評価:
  - current skill が lint target 外であることを特定できた
  - gated profile の必須 shape を実装前に固定できた

---

## 8) Discussion

- 第一案は A で、既存 infra を使い回す方が rule の増殖を防げる
- ただし `capture-and-ingest-source` は長い user skill なので、本文可読性を壊すなら B へ落とす
- つまり今回の確認点は「routine 型へどこまで本文を寄せてよいか」の 1 点に絞れる

---

## 9) Closing

- 今回は tasknote 起票まで
- 次のゲートは `話題3：どこまで routine 型へ寄せるか`
- 関連tasknote:
  - `steering/2026年5月24日 開発基盤：capture-and-ingest-sourceに要約確認ゲートを追加する.md`
  - `steering/2026年5月24日 開発基盤：capture-and-ingest-sourceにrelated page更新とingest logを足す.md`

---

## 10) 参考資料

- `~/dotfiles/claude/.claude/skills/capture-and-ingest-source/SKILL.md`
- `~/dotfiles/shared/linter/specs/routine-skill/routine_skill_rules.yml`
- `~/dotfiles/shared/linter/coding-rules/routine-skill/run_skill_lint.mjs`
- `~/dotfiles/shared/linter/coding-rules/routine-skill/batch_gate.mjs`
- `~/dotfiles/shared/linter/coding-rules/routine-skill/doc_fields.mjs`
