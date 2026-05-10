---
status: done
priority: normal
scheduled: 2026-05-09T00:00:00.000+09:00
dateCreated: 2026-05-09T00:00:00.000+09:00
dateModified: 2026-05-09T00:00:00.000+09:00
tags:
  - task
  - architecture
  - yaml
  - docs
  - checker
---

# 2026年5月9日 architecture_rules の `label_ja` 追加

> 状態：⑥ Discussion（実装完了 / 検証済み）
> 完了条件：`docs/architecture_rules.yml` の主要 `id` 群に日本語ラベルが付き、checker / fixer がそれを壊さず、現在の `guardian_autofix` 差分とも両立して検証が通ること

---

## 1) Journey

- **深層的目的**：英語 id を追わなくても YAML を読めるようにする
- **やらないこと**：`id` 自体を日本語へ置き換えて機械キーを壊すこと

**Before（現状）**：
- 💦 `docs/architecture_rules.yml` は `id` が主見出しのように見え、日本語で読みたい場面で視線が止まりやすい
- 💦 現在のワークツリーでは `coverage.guardian_autofix` への途中変更があり、architecture checker 系の focused verify がそのままでは赤い
- 💦 fixer の runtime entry 正規化は extra key を落とすため、`label_ja` を後から消す危険がある

**After（達成状態）**：
- ❤️ `facts.principles` / `flows` / `entry_points` / `runbooks` / `codemaker_bundle_contracts` / `migration_notes` / `validation_rules` に `label_ja` があり、人は日本語ラベルで読める
- ❤️ checker は `guardian_autofix` を受け入れ、focused verify が clean に戻る
- ❤️ fixer は runtime entry chain の `label_ja` を消さない

---

## 2) Gherkin

### シナリオ1：主要 rule/fact を日本語ラベルで読める

🧱 Given：AI や開発者が `docs/architecture_rules.yml` を目視で読む  
🎬 When：主要な `id` 付きブロックを見る  
✅ Then：`label_ja` があり、英語 id を読まなくても意味を追える

### シナリオ2：checker は現在の coverage key 変更と両立する

🧱 Given：ワークツリーの YAML では `coverage.guardian_autofix` が使われている  
🎬 When：`python -m pytest test/test_architecture_rules_checker.py -q` と checker CLI を実行する  
✅ Then：coverage key mismatch で落ちず、JSON を返せる

### シナリオ3：fixer を通しても `label_ja` が消えない

🧱 Given：runtime entry chain に `label_ja` がある  
🎬 When：runtime entry chain の fixer が YAML を正規化する  
✅ Then：canonical field を直しても `label_ja` は残る

---

## 3) Design

- `id` は機械キーとして維持し、主要ブロックだけに `label_ja` を追加する
- checker は coverage metadata の内部キーを `guardian_autofix` へ寄せつつ、fixture helper / focused test も合わせて更新する
- fixer は runtime entry chain の canonicalization で extra key を消さないようにし、`label_ja` を保持する
- 実装順は TDD で、まず focused test に「`label_ja` が必要」「coverage key mismatch を許さない」を書いて red を確認する

---

## 4) Tasklist

- [x] plan を `docs/superpowers/plans/2026-05-09-architecture-rules-label-ja.md` に保存した
- [x] red：`label_ja` 必須ブロックと `guardian_autofix` 両立の focused test を追加した
- [x] green：checker / fixer を更新して focused test を通した
- [x] green：`docs/architecture_rules.yml` に `label_ja` を追加した
- [x] verify：focused test と関連 CLI を通し、result / discussion を更新した

### 作業記録

#### 2026年5月9日（起票）

**Observe**：`id` は機械キーとして必要だが、人間の見出しとしては読みにくい。加えて現ワークツリーには `guardian_autofix` への途中変更があり、focused verify が赤い。  
**Think**：今回の変更は docs 追記だけでは足りず、checker / fixer が `label_ja` を落とさないことまで含めて固定する必要がある。  
**Act**：Journey / Gherkin / Design / Tasklist を固定し、plan と focused test から着手する。

#### 2026年5月9日（red）

**Observe**：`test/test_architecture_rules_checker.py` と `test/test_fix_architecture_rules.py` に `label_ja` 契約を足すと、`repair_autofix` 固定と runtime entry canonicalization が赤く出た。  
**Think**：今回の本当の変更単位は docs だけではなく、「current YAML schema を tooling が受け止めること」と「fixer が追加メタデータを消さないこと」の 2 つだった。  
**Act**：`guardian_autofix` を期待する helper / focused test と、runtime entry fixer の preservation test を追加した。

#### 2026年5月9日（green）

**Observe**：tooling 側を直すと、focused pytest は `label_ja` 未投入だけが赤として残った。  
**Think**：この段階で red が docs 欠落の 1 点に絞れたので、YAML 本体へ安全に `label_ja` を追加できる。  
**Act**：checker は `guardian_autofix` を正として受け、legacy `repair_autofix` も読めるようにし、fixer は runtime entry chain の extra key を保持するよう更新した。

#### 2026年5月9日（verify）

**Observe**：`label_ja` 追加後、focused pytest・checker CLI・fix CLI・repair test まで通った。  
**Think**：これで 3 つの Gherkin はすべて repo 内の test / CLI で確認でき、task を完了扱いにしてよい。  
**Act**：Result / Discussion を更新し、この note を done へ移す。

---

## 5) Result

### 実施内容

- `docs/architecture_rules.yml` の主要ブロックに `label_ja` を追加した
  - `facts.principles` 5 件
  - `facts.flows` 3 件
  - `facts.entry_points` 1 件 + `nodes` 3 件
  - `facts.runbooks` 3 件
  - `facts.codemaker_bundle_contracts` 1 件
  - `facts.migration_notes` 3 件
  - `validation_rules` 9 件
- `tools/architecture_rules/check_architecture_rules.py` を更新し、`guardian_autofix` を正として受け、legacy `repair_autofix` も互換で読めるようにした
- `tools/architecture_rules/fix_architecture_rules.py` を更新し、runtime entry chain 正規化時に `label_ja` などの extra key を保持するようにした
- `test/test_architecture_rules_checker.py` に major section `label_ja` 契約と `guardian_autofix` 前提を追加した
- `test/test_fix_architecture_rules.py` に runtime entry fixer の `label_ja` preservation test を追加した
- `docs/superpowers/plans/2026-05-09-architecture-rules-label-ja.md` に writing-plans 由来の plan を保存した

### Gherkin 確認結果

- シナリオ1：主要 rule/fact を日本語ラベルで読める
  - `facts.principles` / `flows` / `entry_points` / `runbooks` / `codemaker_bundle_contracts` / `migration_notes` / `validation_rules` の `label_ja` を focused test で確認した
- シナリオ2：checker は現在の coverage key 変更と両立する
  - `guardian_autofix` を含む real YAML で checker CLI と pytest が通ることを確認した
- シナリオ3：fixer を通しても `label_ja` が消えない
  - runtime entry fixer の unit test で `label_ja` 保持を確認し、real repo でも `python tools/fix_architecture_rules.py --rule-id runtime_entry_chain` が `OK` を返すことを確認した

### 検証結果

```text
$ python -m pytest test/test_architecture_rules_checker.py test/test_fix_architecture_rules.py -q
19 passed in 1.74s

$ python tools/check_architecture_rules.py
run_ok: true, has_warnings: false

$ python tools/fix_architecture_rules.py --rule-id runtime_entry_chain
status: OK

$ python -m pytest test/test_architecture_rules_checker.py test/test_fix_architecture_rules.py test/test_repair_architecture_rules.py -q
23 passed in 2.10s
```

### 変更ファイル

- `docs/architecture_rules.yml`
- `tools/architecture_rules/check_architecture_rules.py`
- `tools/architecture_rules/fix_architecture_rules.py`
- `test/test_architecture_rules_checker.py`
- `test/test_fix_architecture_rules.py`
- `docs/superpowers/plans/2026-05-09-architecture-rules-label-ja.md`

---

## 6) Discussion

- **結論**：`id` は機械キーのまま維持しつつ、主要ブロックへ `label_ja` を足す方針で readability 改善は完了した。checker/fixer も current YAML に追随し、今回の docs 追加を壊さない。
- **懸念点**：今回 `label_ja` を付けたのは主要ブロックだけで、`facts.tree` 内の大量の個別 node までは広げていない。tree node レベルでも日本語ラベルが必要なら別 task として切る方が安全。
- **懸念点**：coverage key は `guardian_autofix` へ寄せたが、checker JSON の集計フィールド名はまだ `repair_candidate_rule_ids` / `repair_implemented_rule_ids` のまま。外部互換を保つため今回は据え置いた。
- **次に起票すべきタスクノート**：
  - `architecture_rules tree node label_ja 拡張`
  - `coverage_review の repair_* 集計名を guardian_* へ整理`

---

### 反省とルール化

- 次にやること：`label_ja` は「主要ブロックから先に」入れ、fixer が触る経路では preservation test を先に置く
