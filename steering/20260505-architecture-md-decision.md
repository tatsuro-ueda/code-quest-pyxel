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

- **深層的目的**：framework-rule.md M5-3 検証目安「ARCHITECTURE.md / AGENTS.md に本規約のサマリが取り込まれている」の文言の解釈を確定し、文書整理を完了させる
- **やらないこと**：
  - framework-rule.md の本体規約（M1〜M5）の再編
  - `docs/repository-structure.md` の内容自体の書き換え

## 2) Gherkin

- M5-3 検証目安の文言が「AGENTS.md か ARCHITECTURE.md のどちらか」と読めるか「両方必要」と読めるかが framework-rule.md 上で明確化されている
- 上記判定に応じて、ARCHITECTURE.md を新設する／しないの方針が決まる
- `grep -nE 'M[1-5]-[0-9]\|framework-rule' AGENTS.md ARCHITECTURE.md 2>/dev/null` で必要な参照件数が一意に確定

## 3) Design

### 想定選択肢
1. **(A) ARCHITECTURE.md を新設**：framework-rule.md の M1〜M5 セクション要約を repo root に。AGENTS.md と役割重複の懸念
2. **(B) `docs/repository-structure.md` を `ARCHITECTURE.md` にリネーム**して root に。既存内容（ディレクトリ規約）と framework-rule の規約は別レイヤーなので、リネームだけで M5-3 検証目安を満たすかは解釈次第
3. **(C) 現状維持** + framework-rule.md に「`docs/repository-structure.md` を ARCHITECTURE.md と読み替える」regulations を追記。scope 0
4. **(D) AGENTS.md 単独運用**：本日 (`ea04cdf`) の M1〜M5 サマリ追加で M5-3 検証目安を充足したと宣言。framework-rule.md M5-3 文言を「AGENTS.md があれば ARCHITECTURE.md は省略可」と明文化

### 推奨方針
（D）が現状最小コストで意義を満たす。本タスクの実体は **framework-rule.md M5-3 の文言を 1〜2 行追記する** だけで終わる可能性が高い。

### 委任度
🟢 高：docs 1 ファイルの数行追記で完了見込み

## 4) Tasklist

- [ ] (D) を採る場合：`docs/framework-rule.md` M5-3 の検証目安に「AGENTS.md がサマリを保持していれば ARCHITECTURE.md は省略可」を追記
- [ ] (A)/(B) を採る場合：ARCHITECTURE.md を作成 / リネーム
- [ ] AGENTS.md からの参照リンクを最新化
- [ ] autonomous-rule-compliance-loop.md の該当エントリを「→ 本ノートに分離」更新

## 5) Result / 6) Discussion

（着手時に追記）
