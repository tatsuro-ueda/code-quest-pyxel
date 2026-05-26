---
status: open
priority: normal
scheduled: 2026-05-26T13:26:44.000+09:00
dateCreated: 2026-05-26T13:26:44.000+09:00
dateModified: 2026-05-26T13:26:44.000+09:00
tags:
  - task
  - skill
  - checklist
  - docs
---

# 2026年5月26日 開発基盤：make-development-checklist を .tasknote-paths.yml 対応にする

> 状態：① Journey
> 次のゲート：（CC）対象 skill の path 解決仕様と fallback 方針を Design に固める

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的　repo ごとの docs 配置差分を skill から切り離し、設定を repo 側へ戻す
> 補足：やらないこと　checklist 項目自体の再設計、docs 本文の改変、`llm-wiki-update-docs` の仕様変更
> 補足：責務分担厳格度 full

1. 前提条件
    1. 💦 skill は docs 4 文書を固定 path で見ている
    2. 💦 repo root に `/.tasknote-paths.yml` がある
    3. 💦 user は repo 設定を使わせたい

2. Before
    1. 💦 `docs/` 直書き前提がある
    2. 💦 repo ごとの差分を宣言しにくい
    3. ❌ repo 設定が path 解決に使われない

3. After
    1. 💦 skill は repo config を先に見る
    2. ✅ `docs_root` から参照 doc を解決できる
    3. ✅ repo 側の設定だけで差分を表現できる
    4. ❤️ skill から project 依存を減らせる

4. 例外
    1. `/.tasknote-paths.yml` が無い repo の扱いを決める
    2. 不足キー時の fallback 順を決める

5. 境界条件
    1. 主対象は `make-development-checklist/SKILL.md`
    2. repo 側の正本は `/.tasknote-paths.yml`
    3. 出力文面の改稿は今回の主題ではない

6. 委任度
    1. 🟡 全体として fallback 方針だけ確認余地がある
    2. 🟢 CCのみで可: 現状差分と変更案を note 化できる
    3. 🔴 人の判断: stop か部分 fallback かを決める

---

## 2) ユーザーストーリーマップ

> 委任度：🟢 起票と初期 scope 固定までは CC が進められる
> 残る曖昧さ：`/.tasknote-paths.yml` 未設定時の fallback 方針

### 事前確認

- [x] tasknote確認済み
- [x] skill・tool・MCP確認済み
  - [x] `manage-tasknotes`
  - [x] `make-development-checklist`
- [x] 永続的ドキュメント確認済み
  - [x] `AGENTS.md`
  - [x] `README.md`
  - [x] `/.tasknote-paths.yml`
  - [x] `~/dotfiles/claude/.claude/skills/make-development-checklist/SKILL.md`
  - [x] `steering/done/2026年5月26日 開発基盤：make-checklist を汎用化してリネームする.md`

### 本体

#### 話題1：repo 設定から docs 解決する入口を 1 本にそろえる

##### ユーザー：この repo の運用者

1. 当初計画
    1. 👀 現状の固定 `docs/` 前提と repo 側設定の差分を洗い出す
    2. 🔗 `docs_root` と target doc 名の対応を skill から読める形に整理する
    3. 📝 fallback 方針を Gherkin と Design に固定する

#### 話題2：repo 固有前提を skill 本体から外す

##### ユーザー：skill 保守者

1. 当初計画
    1. ✂️ `docs/` 直書き前提を見直す
    2. 🧭 `/.tasknote-paths.yml` を優先参照するルールを定める
    3. ✅ config が無い repo でも壊れない最小動作を残す

---

## 3) Gherkin（完了条件）

> 委任度：🟢 初期シナリオの固定までは CC が進められる
> 残る曖昧さ：config 不備時の stop / fallback の境界

### シナリオ一覧

- [ ] シナリオ1：repo に `/.tasknote-paths.yml` がある場合はそこから docs を解決できる

1. 🧱 開発者が `docs_root` と target doc 対応を持つ repo にいる（repo root）
2. 🎬 `make-development-checklist` を呼ぶ（skill）
3. ✅ skill は repo 設定に従って参照 doc を決める（出力）

```gherkin
Given repo root に `/.tasknote-paths.yml` があり `docs_root` と target docs が定義されている
When `make-development-checklist` を呼ぶ
Then skill は固定 `docs/` 前提ではなく repo 設定から参照 path を解決する
And 解決した文書だけを根拠に checklist を生成する
```

- [ ] シナリオ2：repo に設定が無い場合も扱いが明示されている

1. 🧱 開発者が `/.tasknote-paths.yml` を持たない repo にいる（repo root）
2. 🎬 `make-development-checklist` を呼ぶ（skill）
3. ✅ default か warning stop のどちらか一貫した挙動で止まらず判断できる（出力）

```gherkin
Given repo root に `/.tasknote-paths.yml` が存在しない
When `make-development-checklist` を呼ぶ
Then skill は事前に定めた fallback 方針どおりに動く
And user から見て参照先が曖昧なまま silently 進まない
```

---

## 4) Design（どうやるか）

### 責務分担概要

| 親ディレクトリ | ファイル案 | 責務概要 | 負わせない責務 |
| --- | --- | --- | --- |
| `~/dotfiles/claude/.claude/skills/make-development-checklist/` | `SKILL.md` | repo config 優先の docs 解決と fallback ルールを持つ | repo 固有 path を直書きする |
| `./` | `.tasknote-paths.yml` | `docs_root` と対象 doc 名の正本を置く | skill 本体の分岐を直接持つ |
| `steering/done/` | `2026年5月26日 開発基盤：make-checklist を汎用化してリネームする.md` | 旧判断の経緯を参照する | 実装の正本になる |

### 責務分担概要図

```mermaid
flowchart TD
    A[repo root] --> B[/.tasknote-paths.yml]
    B --> C[make-development-checklist]
    C --> D[resolved docs paths]
    D --> E[development checklist]

    classDef io fill:#e2e3f1,stroke:#3949ab,color:#000000;
    classDef proc fill:#fff3cd,stroke:#856404,color:#000000;
    classDef out fill:#d4edda,stroke:#155724,color:#000000;

    class A,B io;
    class C,D proc;
    class E out;
```

### 責務分担詳細

- `~/dotfiles/claude/.claude/skills/make-development-checklist/` （✏️：skill 定義の置き場）
  - `SKILL.md`: repo config 優先の docs 解決と fallback ルールを書く
- `./` （✏️：repo 設定の正本置き場）
  - `.tasknote-paths.yml`: `docs_root` と対象 doc 名の正本を持つ
- `steering/done/` （❌：参照専用の履歴置き場）
  - `2026年5月26日 開発基盤：make-checklist を汎用化してリネームする.md`: 旧判断との差分を参照する

### 関連スキル・MCP

- `manage-tasknotes`
- `make-development-checklist`

### 【参照】

- Steering: `steering/done/2026年5月26日 開発基盤：make-checklist を汎用化してリネームする.md`
- Architecture: `docs/architecture.md`
- RepositoryStructure: `docs/repository-structure.md`
- FrameworkRule: `docs/framework-rule.md`
- RepoConfig: `/.tasknote-paths.yml`

### 変更範囲

- やること：skill の docs path 解決を repo config 優先へ寄せる設計と実装
- やらないこと：checklist 出力文面の全面改稿、repo docs 本文の仕様変更

### 検証

- 検証コマンド：実装時に `make-development-checklist` を code-quest-pyxel 上で呼び、参照 path が `/.tasknote-paths.yml` と一致することを確認する
- 成功条件：repo 設定経由で doc 解決ができ、固定 `docs/` 直書きに依存しない
- 未実施時の扱い：参照 path の現物確認が終わるまで close しない

---

## 5) Tasklist

```mermaid
flowchart TD
    T1[現状 skill の固定 path を洗い出す] --> T2[repo config の流用可否を確認する]
    T2 --> T3[fallback 方針を決める]
    T3 --> T4[skill 本文を更新する]
    T4 --> T5[code-quest-pyxel で参照 path を確認する]

    classDef todo fill:#e2e3f1,stroke:#3949ab,color:#000000;

    class T1,T2,T3,T4,T5 todo;
```

> 必ず上から順に実施。CC が現物確認を含めて前へ進める。

- [ ] （CC）現状 skill の固定 path と save 先の前提を洗い出す
- [ ] （CC）`/.tasknote-paths.yml` の既存 key で足りるかを確認する
- [ ] （ユーザー or CC）config 不備時の fallback 方針を決める
- [ ] （CC）`make-development-checklist` の本文を更新する
- [ ] （CC）code-quest-pyxel で repo 設定解決を確認する

### 記録の分け方

> 実行のたびに、事実は `作業ログ`、判断は `Discussion` に分けて残す。

#### 作業ログ に書く

- 変更した skill / config
- 確認した path と結果
- warning や fallback の実際の挙動

#### Discussion に書く

- fallback をどう決めたか
- `.tasknote-paths.yml` 既存 schema で足りるか
- 他 repo へ広げる時の制約

### レビュー（開発 task のときだけ）

- 原本 checklist: `docs/development-checklist.md`
- /tmp コピー: `/tmp/development-checklist-YYYYMMDD-HHMM.md`
- レビュー結果:
- 未通過時の扱い: fail があれば修正して再レビューし、全部通るまで Close しない

---

## 6) 作業ログ

- 2026-05-26 起票
- `make-development-checklist` 現状仕様と `/.tasknote-paths.yml` を確認し、repo config 対応を task として切り出した

---

## 7) 評価と成果物

> 評価：🟡 起票のみ完了

### 成果物

- `steering/2026年5月26日 開発基盤：make-development-checklist を .tasknote-paths.yml 対応にする.md`

---

## 8) Discussion

### 判断記録

- まずは repo 内の設定を正本に寄せる方針を note に固定し、実装前に fallback 境界を明示する

### 反省とルール化

- 記入先：必要なら `make-development-checklist` 側
- 次にやること：現状 skill の固定 path 解決箇所を洗い出して Design を前へ進める

---

## 9) Closing

- 状態: open
- 次のゲート: （CC）対象 skill の path 解決仕様と fallback 方針を Design に固める
- close 条件:
  - [ ] repo 設定優先の path 解決仕様が固まっている
  - [ ] `make-development-checklist` 側の修正が実装されている
  - [ ] code-quest-pyxel 上で設定解決の現物確認が済んでいる

---

## 10) 参考資料

- `AGENTS.md`
- `README.md`
- `/.tasknote-paths.yml`
- `docs/architecture.md`
- `docs/framework-rule.md`
- `docs/repository-structure.md`
- `~/dotfiles/claude/.claude/skills/make-development-checklist/SKILL.md`
- `steering/done/2026年5月26日 開発基盤：make-checklist を汎用化してリネームする.md`
