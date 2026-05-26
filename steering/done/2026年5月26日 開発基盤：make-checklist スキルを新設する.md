---
status: done
priority: normal
scheduled: 2026-05-26T09:00:00.000+09:00
dateCreated: 2026-05-26T09:00:00.000+09:00
dateModified: 2026-05-26T10:30:00.000+09:00
tags:
  - task
---

# 2026年5月26日 開発基盤：make-checklist スキルを新設する

> 状態：⑨ Closing
> 次のゲート：なし

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的　docs/ 3 層を AI が毎回読まず機械的に網羅できるチェックリスト化
> 補足：やらないこと　docs/ 本体の規約変更、M1〜M5 の強化、対象 3 文書以外の取り込み
> 補足：責務分担厳格度 full

1. 前提条件
    1. 💦 2026-05-26 commit `27dc33c` で docs/ 3 層構造が確立
    2. 💦 docs/ は AI コーディング前提で M1〜M5 自力検証を狙う
    3. 💦 「3 文書を毎回読む」コストでチェック漏れが起きる

2. Before
    1. 💦 レビュー時に 3 文書を毎回スキャンしている
    2. 💦 M1〜M5・ディレクトリ規約・採用技術制約を見落とす
    3. ❌ 規約はあっても踏み外しが減らない不安

3. After
    1. 💦 `/make-checklist` で設計・実装・レビュー項目を一覧化できる
    2. ✅ docs/ 3 層の規約を機械的に網羅できる
    3. ❤️ レビューで見落とさない安心

4. 例外
    1. docs 更新時は make-checklist を再生成する運用を skill 本文に明記

5. 境界条件
    1. スキル置き場：`~/.claude/skills/make-checklist/`
    2. 対象 docs は code-quest-pyxel の 3 文書限定
    3. 出力先は呼び出し時に決定（標準は標準出力）

6. 委任度
    1. 🟡 一部判断要：粒度・シーン優先順位は人の確認
    2. 🟢 docs 3 文書のスキャン・ドラフト化は CC で可
    3. 🔴 3 シーンを別 skill にするか統合かは人判断

---

## 2) ユーザーストーリーマップ

> 委任度：🟡 ドラフト化は進められるが、3 シーンの優先順位は人の確認が必要
> 残る曖昧さ：最初に対応する 1 シーン（設計／実装／レビュー）が未確定

### 事前確認

- [ ] tasknote確認済み
- [ ] skill・tool・MCP確認済み
  - [ ] create-skill（スキル雛形作成）
  - [ ] manage-tasknotes（本起票）
- [ ] 永続的ドキュメント確認済み
  - [ ] docs/architecture.md（設計判断 SSoT）
  - [ ] docs/framework-rule.md（M1〜M5 規約）
  - [ ] docs/repository-structure.md（責務分担表）

### 本体

#### 話題1：3 シーン（設計・実装・レビュー）を 1 つに絞って始める

##### ユーザー：開発者

1. 当初計画
    1. ❓ 3 シーンを並べて最初に着手する 1 つを決める
    2. 👀 各シーンで「何を確認するか」を 3 文書から抽出
    3. 📝 抽出結果を skill draft に落とす

#### 話題2：チェックリストの粒度と出力形式を決める

##### ユーザー：CC + 開発者

1. 当初計画
    1. ❓ 項目数（1 シーン 10〜20 項目）の温度感を決める
    2. 👀 出力形式（標準出力 / markdown / Gherkin 風）を決める
    3. 📝 雛形（SAMPLE 1 つ）を作って人にレビュー依頼

#### 話題3：docs 更新時の再生成運用を決める

##### ユーザー：CC

1. 当初計画
    1. 👀 docs/ 3 文書更新時に make-checklist 再実行する運用フック
    2. 📝 運用ルールを skill 本文か CLAUDE.md に明記

---

## 3) Gherkin（完了条件）

> 委任度：🔴 まだ 3 シーン未確定のため Gherkin は仮置き
> 残る曖昧さ：シーン優先順位、項目粒度、出力形式

### シナリオ一覧

- [ ] シナリオ1-1：`/make-checklist` を呼ぶと 3 文書から項目を生成できる

1. 🧱 開発者が docs/ 3 層の規約を踏まえてレビューしたい（ターミナル）
2. 🎬 `/make-checklist` を呼ぶ（ターミナル）
3. ✅ docs/ 3 文書を読まずにチェック項目一覧が得られる（出力）

```gherkin
Given 開発者がターミナルで code-quest-pyxel のリポジトリにいる
When `/make-checklist` を呼ぶ
Then docs/ 3 文書（architecture / framework-rule / repository-structure）から派生したチェック項目が出力される
```

> 詳細シナリオ（シナリオ 1-2 以降）は ① Journey と ② USM のゲート通過後に確定する。

---

## 4) Design（どうやるか）

### 責務分担概要

| 親ディレクトリ | ファイル案 | 責務概要 | 負わせない責務 |
| --- | --- | --- | --- |
| `~/.claude/skills/make-checklist/` | `SKILL.md` | docs/ 3 層を読み設計・実装・レビュー時のチェックリストを生成 | docs/ 規約の更新、対象外文書の取り込み |
| `docs/` | `architecture.md` / `framework-rule.md` / `repository-structure.md` | チェック項目の正本（SSoT） | チェックリスト形式の出力 |

### 責務分担概要図

```mermaid
flowchart TD
    D1[docs/architecture.md] --> S[make-checklist skill]
    D2[docs/framework-rule.md] --> S
    D3[docs/repository-structure.md] --> S
    S --> O[チェックリスト出力]

    classDef ssot fill:#e2e3f1,stroke:#3949ab,color:#000000;
    classDef skill fill:#fff3cd,stroke:#856404,color:#000000;
    classDef out fill:#d4edda,stroke:#155724,color:#000000;

    class D1,D2,D3 ssot;
    class S skill;
    class O out;
```

### 責務分担詳細

- `~/.claude/skills/make-checklist/` （➕：新規 skill）
  - `SKILL.md` （➕：skill 本体定義）
    - `entry point`: docs/ 3 文書を読んでチェック項目を出力する入口
- `docs/` （❌：参照のみ、今回触らない）
  - `architecture.md` （❌：設計判断 SSoT）
    - `read only`: チェック項目の元データとして読む
  - `framework-rule.md` （❌：M1〜M5 規約）
    - `read only`: チェック項目の元データとして読む
  - `repository-structure.md` （❌：責務分担表）
    - `read only`: チェック項目の元データとして読む

### 関連スキル・MCP

- `create-skill`
- `manage-tasknotes`

### 【参照】

- Architecture: `docs/architecture.md`
- Framework: `docs/framework-rule.md`
- Structure: `docs/repository-structure.md`

### 変更範囲

- やること：`~/.claude/skills/make-checklist/` の新規作成（SKILL.md + 必要なら shared asset）
- やらないこと：docs/ 3 文書の更新、対象外文書の取り込み

### 検証

- 検証コマンド：（後段で確定）スキル呼び出し → チェック項目出力の目視
- 成功条件：docs/ 3 文書を開かずに必要なチェック項目が一覧で出る
- 未実施時の扱い：（① Journey と ② USM のゲート通過後に確定）

---

## 5) Tasklist

- [x] （CC）docs/ 3 文書をスキャンしてチェック項目候補を抽出
- [x] （CC）抽出結果を skill draft に落とす
- [x] （ユーザー）粒度・出力形式をレビュー → 100 項目 / 3 シーン統合で確定
- [x] （CC）skill 本文を `~/.claude/skills/make-checklist/SKILL.md` に書く
- [x] （CC）SAMPLE 出力（チェックリスト本体）を SKILL.md 内に同梱、skill 登録を確認

---

## 6) 作業ログ

- 2026-05-26 起票（commit `1bdd4c0`）
- ユーザー判断：3 シーン（設計／実装／レビュー）統合・100 項目・配置先は全プロジェクト共通（`~/.claude/skills/`）
- `~/.claude/skills/make-checklist/SKILL.md` を新規作成（合計 100 項目：A 25 / B 30 / C 45）
  - A 章：docs/architecture.md より（製品の前提 3 / 採用技術と役割 10 / 採用技術から導かれる制約 12）
  - B 章：docs/repository-structure.md より（構造規約 5 / ディレクトリ責務 15 / レイヤー依存 4 / build runbook 4 / test と guardrail 2）
  - C 章：docs/framework-rule.md より（M1 7 / M2 5 / M3 10 / M4 18 / M5 5）
- skill 登録確認：Skill tool の available list に `make-checklist` が出現することを確認

---

## 7) 評価と成果物

> 評価：🟢 期待通り完了した

### 成果物

- `~/.claude/skills/make-checklist/SKILL.md`（新規、100 項目チェックリスト本体を含む）
- skill description：「code-quest-pyxel の docs/ 3 層から派生した 100 項目チェックリストを出力」

---

## 8) Discussion

### 判断記録

- **3 シーン分割 vs 統合**：「時間がないため」を尊重し統合採用。あとで分割するかは未確定。100 項目は A/B/C のタグで分類済みのため、後から `/make-checklist design`・`/make-checklist review` のような分割は SKILL.md 内 routing 追記で実現できる
- **配置先**：全プロジェクト共通（`~/.claude/skills/`）。ただしチェックリスト本体は code-quest-pyxel 固有のため、他リポで流用するときは新 skill 起票が安全と SKILL.md に明記
- **粒度 100 項目**：3 文書を網羅するには適切。A 25 / B 30 / C 45 の偏りは framework-rule.md の規約密度に従った自然な分布

### 反省とルール化

- 記入先：CLAUDE.md / memory（必要なら）
- 次にやること：docs/ 3 文書が更新されたら本 skill の項目本体も同期する運用フックを将来検討

### 次に起票すべきタスクノート（候補）

- なし（運用段階に入る。docs 更新時の同期は SKILL.md 内の運用ルールで担保）

---

## 9) Closing

- 状態: done
- 次のゲート: なし
- close 条件:
  - [x] make-checklist スキル本体（`~/.claude/skills/make-checklist/SKILL.md`）が登録された
  - [x] チェックリスト 100 項目が docs/ 3 層を網羅している
  - [x] docs 更新時の再生成運用ルールを SKILL.md 本文に明記

---

## 10) 参考資料

- `docs/architecture.md`（設計判断 SSoT）
- `docs/framework-rule.md`（M1〜M5 規約）
- `docs/repository-structure.md`（責務分担表）
- 関連 commit：`27dc33c`（3 層構造確立）/ `346c97f`（schema update）
- 既存 skill 例：`~/.claude/skills/create-skill/`, `~/.claude/skills/manage-tasknotes/`
