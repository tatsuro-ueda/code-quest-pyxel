---
status: done
priority: low
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:45:00+09:00
dateModified: 2026-05-05T17:45:00+09:00
tags:
  - task
  - framework-rule
  - m5-3
  - docs
  - cleanup
  - archived
---

# 2026年5月5日 ARCHITECTURE.md 整備 vs AGENTS.md 単独運用の判定（M5-3）

> 状態：① Journey 略式
> 分離元：`steering/20260425-autonomous-rule-compliance-loop.md` 判断待ち「2026-04-25 19:05 — `ARCHITECTURE.md` 新設 vs `docs/repository-structure.md` リネーム（M5-3）」

---

## 1) Journey

- **深層的目的**：AI と開発者が古い情報を引かなくなり、規約改訂のサイクルが回せる
- **方針（ユーザー指定）**：
  - 文書を **AI 用（短い、最優先）** と **人用（補足、AI も必要時参照）** の 2 層に分ける
  - 優先順位は本タスクで Journey として固定する（Design では選択肢を扱わない）
  - **AI 用 = `AGENTS.md`**（既存・root・Claude Code が自動 load・**100 行以内**に圧縮）
  - **人用 = `docs/architecture.md`**（既存 `docs/repository-structure.md` をリネーム、AI 用の補足、AI も必要時に参照）
  - **規約本体 = `docs/framework-rule.md`**（M1〜M5 詳細、両者から参照される根拠）

1. 💦 （開発者・AI）機能を追加したりバグ修正したい（コードエディタ／AI 起動時 context）
2. 💦 （開発者・AI）どの規約文書を最初に読むか考える（コードエディタ／AI 起動時 context）
3. Before
  1. ❌ AI が古い指針（例：framework-rule.md M4-1 旧版）を引いて実装し、後で改訂版と矛盾する PR が出る（AI 起動時 context）
  2. ❌ 開発者が `docs/repository-structure.md` を読んで `framework-rule.md` の存在に気づかない（コードエディタ）
  3. ❌ AGENTS.md / repository-structure.md / framework-rule.md の優先順位が言語化されておらず、毎回迷う（コードエディタ）
4. After（ユーザー指定の優先順位で固定）
  1. ✅ AI も人も **まず `AGENTS.md` を読む**（最優先・100 行以内・自動 load）（AI 起動時 context／コードエディタ）
  2. ✅ 必要に応じて **`docs/architecture.md`** を読む（人用詳細・AI も必要時参照、既存 `repository-structure.md` をリネーム）（コードエディタ）
  3. ✅ 規約の詳細根拠は **`docs/framework-rule.md`**（M1〜M5）にあり、AGENTS.md / architecture.md の両方から参照される（コードエディタ／AI 起動時 context）
  4. ✅ 各文書の冒頭に「この文書の役割」と「上位／下位／関連文書」が明記されている（コードエディタ）
  5. ♥️ （開発者・AI）「次に何を読めばよいか」で迷わなくなり、AI が古い指針を引いて矛盾 PR を出す確率が下がる

## 2) Gherkin

### シナリオ1：AGENTS.md が 100 行以内の AI 用最優先文書になる
> 🧱 Given: 現在の `AGENTS.md`（既存、root）。🎬 When: 100 行以内に圧縮し、冒頭に「AI 用最優先・自動 load」「補足は `docs/architecture.md`」「規約詳細は `docs/framework-rule.md`」のリンクを置く。✅ Then: `wc -l AGENTS.md` ≤ 100。AI が起動 context として読み切れるサイズで、必要時は次の文書へ辿れる。

### シナリオ2：`docs/repository-structure.md` が `docs/architecture.md` にリネームされる
> 🧱 Given: 既存 `docs/repository-structure.md` (15KB)。🎬 When: `docs/architecture.md` にリネームし、冒頭に「人用詳細・AI 用 AGENTS.md の補足・規約詳細は framework-rule.md」のリンクを置く。✅ Then: `git mv` 完了、リネーム後のファイルが「リポジトリのアーキテクチャ全体像 + ディレクトリ規約」を兼ねる文書として位置付けられている。

### シナリオ3：framework-rule.md が両者から参照される根拠文書として明記される
> 🧱 Given: 既存 `docs/framework-rule.md`。🎬 When: 冒頭に「規約本体（M1〜M5 詳細）」「上位は AGENTS.md と docs/architecture.md」のリンクを追加。✅ Then: framework-rule.md がどこから参照される位置付けかが冒頭で明確になっている。

### シナリオ4：M5-3 検証目安が「2 層構造」と整合する文言に改訂される
> 🧱 Given: 改訂前 framework-rule.md M5-3「ARCHITECTURE.md / AGENTS.md に本規約のサマリが取り込まれている」の曖昧表現。🎬 When: 「AI 用 AGENTS.md（最優先・100 行以内）と人用 docs/architecture.md（補足）の 2 層構造で、両者から framework-rule.md（規約本体）に到達できる」と改訂。✅ Then: 文言が Journey で固定された 2 層構造と一致する。AND/OR の解釈余地が消える。

### シナリオ5：AI 起動 context での「最初に読むべきファイル」が一意になる
> 🧱 Given: AI 起動時の自動 context 注入（Claude Code が AGENTS.md を読む）。🎬 When: AI が「ある機能を追加する」起点で文書を辿る。✅ Then: AGENTS.md → 必要なら docs/architecture.md → 必要なら docs/framework-rule.md の順に 3 ホップ以内で到達。古い指針を引いて矛盾 PR を出す確率が下がる（Journey Before の (1) 解消）。

### シナリオ6：開発者が GitHub で repo を開いた経路でも迷わない
> 🧱 Given: 新規開発者が GitHub で repo を開き、README.md を読む。🎬 When: README.md の冒頭リンクから「規約に従って実装するには？」を辿る。✅ Then: README.md → AGENTS.md（最優先）→ docs/architecture.md（人用詳細）→ docs/framework-rule.md（規約本体）の流れが明示されており、人にとっても AGENTS.md が最初のエントリポイントになっている（Journey で固定された優先順位どおり）。

### シナリオ7：再侵入を防ぐ静的ガード
> 🧱 Given: 改修完了後、将来「AGENTS.md が 100 行を超える」「docs/architecture.md が消える」などの逸脱懸念。🎬 When: `test_cjg_framework_rule_guards.py` に「`wc -l AGENTS.md` ≤ 100」「`docs/architecture.md` の存在」を assert する小ガードを追加。✅ Then: 逸脱が pytest で即 fail。Journey で固定した 2 層構造が維持される。

## 3) Design

### Journey で確定済みの方針（Design では選択肢を扱わない）

ユーザー指定により、優先順位と文書配置は Journey で固定済：
- **AI 用（最優先・100 行以内）**：`AGENTS.md`（root、自動 load）
- **人用（補足、AI も必要時参照）**：`docs/architecture.md`（既存 `docs/repository-structure.md` をリネーム）
- **規約本体（詳細根拠）**：`docs/framework-rule.md`

Design はこの方針に沿った実装手順だけを扱う。

## 4) Tasklist

### 事前調査
- [ ] 現 `AGENTS.md` の行数と内容構造を把握
- [ ] 現 `docs/repository-structure.md` の行数と内容構造を把握
- [ ] `docs/framework-rule.md` M5-3 セクションの現状文言を確認

### commit A: docs/repository-structure.md → docs/architecture.md リネーム
- [ ] `git mv docs/repository-structure.md docs/architecture.md`
- [ ] 冒頭に「人用詳細・AI 用 AGENTS.md の補足・規約詳細は framework-rule.md」のリンクブロック追加
- [ ] repo 内の `docs/repository-structure.md` 参照を `docs/architecture.md` に置換（grep で全件確認）
- [ ] commit `docs(architecture): docs/repository-structure.md → docs/architecture.md リネーム`

### commit B: AGENTS.md を ≤100 行に圧縮
- [ ] 既存 AGENTS.md の必須情報を選別、100 行以内に収める
- [ ] 冒頭に「AI 用最優先・自動 load」「補足は docs/architecture.md」「規約詳細は docs/framework-rule.md」リンクブロック追加
- [ ] `wc -l AGENTS.md` ≤100 を確認
- [ ] commit `docs(agents): AGENTS.md を ≤100 行に圧縮 + 2 層構造リンク追加`

### commit C: framework-rule.md M5-3 改訂
- [ ] M5-3「ARCHITECTURE.md / AGENTS.md に本規約のサマリが取り込まれている」を「AI 用 AGENTS.md（最優先・100 行以内）と人用 docs/architecture.md（補足）の 2 層構造で、両者から framework-rule.md（規約本体）に到達できる」に改訂
- [ ] framework-rule.md 冒頭に「規約本体（M1〜M5 詳細）」「上位は AGENTS.md と docs/architecture.md」リンク追加
- [ ] commit `docs(framework-rule): M5-3 を 2 層文書構造に整合させて改訂`

### commit D: README.md 更新
- [ ] README.md 冒頭に「規約に従って実装するには？」セクション追加：AGENTS.md（最優先）→ docs/architecture.md（人用詳細）→ docs/framework-rule.md（規約本体）の流れ明示
- [ ] commit `docs(readme): 文書ナビゲーション (AGENTS → architecture → framework-rule) 追加`

### commit E: 静的ガード追加
- [ ] `test/test_cjg_framework_rule_guards.py` に：(a)`wc -l AGENTS.md` ≤100、(b)`docs/architecture.md` の存在、を assert する 2 ケース追加
- [ ] `pytest -q test/test_cjg_framework_rule_guards.py` green
- [ ] commit `test(framework-rule): AGENTS.md ≤100 行 / docs/architecture.md 存在の static guard`

### 仕上げ
- [ ] tasknote status `done`、`archived` タグ追加、`steering/done/` へ移動

## 5) Result 


## 6) Discussion

（着手時に追記）
