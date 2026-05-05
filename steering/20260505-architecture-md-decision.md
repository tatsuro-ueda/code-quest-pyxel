---
status: open
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
---

# 2026年5月5日 ARCHITECTURE.md 整備 vs AGENTS.md 単独運用の判定（M5-3）

> 状態：① Journey 略式
> 分離元：`steering/20260425-autonomous-rule-compliance-loop.md` 判断待ち「2026-04-25 19:05 — `ARCHITECTURE.md` 新設 vs `docs/repository-structure.md` リネーム（M5-3）」

---

## 1) Journey

- **深層的目的**：人と AI のどちらがリポジトリを開いても「次にどの規約文書を読めばよいか」で迷わない状態を作る

1. 💦 （開発者・AI）機能を追加したりバグ修正したい（コードエディタ／AI 起動時 context）
2. 💦 （開発者・AI）どの規約文書を最初に読むか考える（コードエディタ／AI 起動時 context）
3. Before
  1. ❌ AI が古い指針（例：framework-rule.md M4-1 旧版）を引いて実装し、後で改訂版と矛盾する PR が出る（AI 起動時 context）
  2. ❌ 開発者が repository-structure.md を読んで framework-rule.md の存在に気づかない（コードエディタ）
  3. ❌ AGENTS.md / ARCHITECTURE.md / repository-structure.md / framework-rule.md の優先順位が言語化されておらず、毎回迷う（コードエディタ）
4. After
  1. ✅ 各文書の冒頭に「この文書の役割」と「上位／関連文書」が明記されている（コードエディタ）
  2. ✅ 人にとっての最優先文書 と AI にとっての最優先文書 がそれぞれ確定している（同じか別かを問わず明示されている）（コードエディタ／AI 起動時 context）
  3. ✅ ARCHITECTURE.md を作る／作らないが決まっている（保留状態が解消）（コードエディタ）
  4. ♥️ （開発者・AI）「次に何を読めばよいか」で迷わなくなる

## 2) Gherkin

### シナリオ1：M5-3 検証目安の文言解釈が確定する
> 🧱 Given: framework-rule.md M5-3 検証目安「ARCHITECTURE.md / AGENTS.md に本規約のサマリが取り込まれている」の AND/OR が現状曖昧。🎬 When: 文言を改訂する。✅ Then: 「両方必要 / どちらか一方で可 / 役割を分けて両方持つ」のいずれかが文中で明示され、解釈の余地が残らない。

### シナリオ2：人にとって最優先 / AI にとって最優先 が分けて記述される
> 🧱 Given: 改修後の repo。🎬 When: 開発者が GitHub で repo を開く（README.md 起点）/ AI が起動して context を読む（AGENTS.md 起点）の 2 経路を辿る。✅ Then: それぞれの起点文書から「次に読むべき文書」が一意に辿れる。AI 起点と人起点で最優先が違っても、その違いが意図的であることが文中で明示されている。

### シナリオ3：各文書の冒頭に役割と上位／関連文書が書かれている
> 🧱 Given: 改修後の `AGENTS.md` / `docs/framework-rule.md` / `docs/repository-structure.md` / （新設するなら）`ARCHITECTURE.md`。🎬 When: 各ファイルの冒頭 5〜10 行を読む。✅ Then: 「この文書の役割」と「上位／関連文書（リンク付き）」が必ず書かれている。読み手は冒頭だけで「これが正しい入口か / 別を読むべきか」を判断できる。

### シナリオ4：ARCHITECTURE.md の存否が確定する
> 🧱 Given: 現状 ARCHITECTURE.md は不在、`docs/repository-structure.md` (15KB) が事実上の構造文書。🎬 When: Design の (A)〜(D) のいずれかを採用する。✅ Then: 「作る／作らない」が決まっており、「（作った方が良ければ）」のような保留状態が消えている。

### シナリオ5：開発者・AI のどちらがリポジトリを開いても迷わない
> 🧱 Given: 上記 4 シナリオ完了後の repo。🎬 When: 新規開発者 or 新規 AI session が「ある機能を追加する」起点で文書を辿る。✅ Then: 3 ホップ以内に必要な規約（M1〜M5、ディレクトリ規約、AI 実装ルール）に到達する。古い指針を引いて改訂版と矛盾する PR を出す確率が下がる。

## 3) Design

### 確定すべき判断 3 件

本タスクは複数の判断が絡む。Design ではそれぞれの選択肢を提示し、ユーザー判断を仰ぐ。

#### 判断 1: M5-3 検証目安「ARCHITECTURE.md / AGENTS.md」の AND/OR
- (1-A) どちらか一方でよい — `ea04cdf` の AGENTS.md 改修で充足
- (1-B) 役割を分けて両方持つ — AGENTS.md は AI 向け short summary、ARCHITECTURE.md は人向け詳述
- (1-C) AGENTS.md だけで足り、ARCHITECTURE.md は省略可と明文化

#### 判断 2: ARCHITECTURE.md を作る／作らない
- (2-A) **新設**：framework-rule.md の M1〜M5 セクション要約を repo root に。AGENTS.md と役割分離が前提
- (2-B) **`docs/repository-structure.md` を `ARCHITECTURE.md` にリネーム**して root に。既存内容（ディレクトリ規約）+ framework-rule への入口リンクを冒頭に追加
- (2-C) **作らない**：AGENTS.md 単独運用、判断 1 で (1-A) or (1-C)

#### 判断 3: 人にとっての最優先 と AI にとっての最優先 を分けるか
- (3-A) 同じ（最上位文書を共通で 1 つに集約） — シンプルだが、AI prompt context への自動注入を意識した文書（AGENTS.md）と、人が GitHub で読みたい文書（README.md / ARCHITECTURE.md）は粒度が違うので集約には書き直しが必要
- (3-B) 分ける（人は README.md / ARCHITECTURE.md 起点、AI は AGENTS.md 起点） — 現状に近い、両起点から同一の規約に辿れることを確認
- (3-C) AGENTS.md を共通の最上位として人にも読ませる — AI 自動注入仕様を流用、人は最初に AGENTS.md を読む運用

### 各文書の現状（事前整理）

| 文書 | 現在の場所 | 役割 | サイズ | 読み手 |
|---|---|---|---|---|
| `AGENTS.md` | repo root | AI 起動時の自動 context、M1〜M5 サマリ + 検証コマンド | small | AI |
| `README.md` | repo root | プロダクト紹介、起動手順 | medium | 人 |
| `docs/framework-rule.md` | docs/ | 規約本体（M1〜M5 詳細） | large | 人・AI |
| `docs/repository-structure.md` | docs/ | ディレクトリ規約 | 15KB | 人 |
| `ARCHITECTURE.md` | （不在） | — | — | — |

### 推奨案（CC 素案、ユーザー確定要）

判断 3 → **(3-B) 分ける**：人と AI で最適経路が違うことを明示するのが正直。
判断 2 → **(2-B) リネーム**：`docs/repository-structure.md` を `ARCHITECTURE.md` にリネームして root に置く。冒頭に「人向け入口、AI は AGENTS.md を参照」と書く。
判断 1 → **(1-B) 役割を分けて両方持つ**：AGENTS.md（AI 向け short）/ ARCHITECTURE.md（人向け詳述）として M5-3 検証目安を改訂

### 推奨案を採る場合の作業範囲

- `docs/framework-rule.md` M5-3 検証目安：「AGENTS.md（AI 向け）と ARCHITECTURE.md（人向け）で役割を分けて両方持つ。両者から framework-rule.md に到達できる」と明文化（数行）
- `docs/repository-structure.md` を `ARCHITECTURE.md` にリネーム + 冒頭 5〜10 行に「役割 / 人向け入口 / AI は AGENTS.md / framework-rule.md へのリンク」を追加
- `AGENTS.md` の冒頭 5〜10 行に「役割 / AI 自動 context / 人は ARCHITECTURE.md → README.md / framework-rule.md へのリンク」を追加
- `docs/framework-rule.md` の冒頭 5〜10 行に「役割 / 上位は AGENTS.md と ARCHITECTURE.md」を追加
- `README.md` の冒頭に ARCHITECTURE.md / AGENTS.md / framework-rule.md への入口リンクを追加

### 委任度
🟡 中：判断 3 件はユーザー確定が必要。確定後の作業（5 ファイルの冒頭加筆 + リネーム）は CC 自走可能

## 4) Tasklist

- [ ] 判断 1〜3 をユーザー確定（推奨案または別案を選ぶ）
- [ ] `docs/repository-structure.md` を `ARCHITECTURE.md` にリネームして root に移動（推奨案 (2-B) を採る場合）
- [ ] 各文書の冒頭に「役割 / 上位／関連文書」を追加：`AGENTS.md` / `ARCHITECTURE.md` / `docs/framework-rule.md` / `README.md`
- [ ] `docs/framework-rule.md` M5-3 検証目安を採用案に合わせて改訂
- [ ] `grep -nE 'M[1-5]-[0-9]\|framework-rule' AGENTS.md ARCHITECTURE.md` で参照件数を確認
- [ ] autonomous-rule-compliance-loop.md の該当エントリを「→ 本ノートに分離」更新（既に `b6f837f` で実施済）

## 5) Result / 6) Discussion

（着手時に追記）
