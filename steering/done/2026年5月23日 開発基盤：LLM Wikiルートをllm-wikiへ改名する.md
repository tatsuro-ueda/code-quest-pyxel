---
status: done
priority: high
scheduled: 2026-05-23T09:58:52+00:00
dateCreated: 2026-05-23T09:58:52+00:00
dateModified: 2026-05-23T10:05:34+00:00
tags:
  - task
  - llm-wiki
  - rename
  - wiki
  - tooling
---

# 2026年5月23日 開発基盤：LLM Wikiルートをllm-wikiへ改名する

> 状態：⑧ Closing
> 次のゲート：（CC）なし

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 repo-local LLM Wiki の入口名を実体に合わせ、`wiki/wiki/` の認知負荷を消す
> 補足：やらないこと historical tasknote の旧 path 文字列を一括で書き換えない

1. 前提条件
   1. 💦 repo-local LLM Wiki の root は今 `wiki/` である
   2. 💦 generated artifact は `wiki/raw/` と `wiki/wiki/` に分かれている
   3. 💦 `tools/gen_wiki.py` と `test/test_gen_wiki.py` は `wiki/` 前提で動く

2. Before
   1. 💦 path を説明するたびに `wiki/wiki/` が混乱を生む
   2. 💦 active docs と generated nav も旧 root を前提にしている
   3. ❌ もどかしい

3. After
   1. 💦 root 名が `llm-wiki/` になり用途が一目で分かる
   2. ✅ code と docs と artifact が新 root にそろう
   3. ❤️ スッキリ

4. 例外
   1. historical `steering/done/*.md` は当時の記録として旧 path を残してよい
   2. 互換用の `wiki/` stub は今回作らない

5. 境界条件
   1. `raw/` `wiki/` `checklists/` の内部構造は変えない
   2. rename 対象は active docs と code と tests と現 artifact に絞る

6. 委任度
   1. 🟢 全体として CC 単独で進められる：影響範囲は repo 内の path 更新で閉じる
   2. 🟢 CCのみで可：rename、generator 更新、test 更新、verify
   3. 🔴 人の判断：旧 `wiki/` 互換 stub を残す案は今回は採らない

---

## 2) ユーザーストーリーマップ

> Gherkin の前に、今回の仕事をどの順番で進めるかだけをそろえる。
> 委任度：🟢 rename 実装と検証までは CC が進められる
> 残る曖昧さ：なし

### 話題一覧

#### 話題1：repo-local root を明示名へ変える

##### ユーザー：私

1. 当初計画
    1. 👀 旧 root を前提にした current surface を洗う
    2. ✂️ `wiki/` を `llm-wiki/` へ移す
    3. 📝 active docs の案内文を新 root に合わせる

#### 話題2：generator と test を新 root にそろえる

##### ユーザー：私

1. 当初計画
    1. 👀 `tools/gen_wiki.py` の default root と説明文を直す
    2. 🧪 `test/test_gen_wiki.py` の fixture と期待 path を直す
    3. ✅ pytest と spot check で rename 後の整合を確かめる

#### 話題3：歴史資料は歴史資料として残す

##### ユーザー：私

1. 当初計画
    1. 👀 old path が残る file を active docs と historical note に分ける
    2. ✂️ current operation に必要な file だけを書き換える
    3. 🧭 done note 本文の一括改変はしない

---

## 3) Gherkin（完了条件）

> 委任度：🟢 実装から verify まで CC が進められる
> 残る曖昧さ：なし

### シナリオ一覧

- [x] シナリオ1：repo-local LLM Wiki の root が `llm-wiki/` になる

1. 🧱 repo には `wiki/` root とその配下 artifact がある
2. 🎬 current surface を更新して root を `llm-wiki/` に改名する
3. ✅ active docs と generated nav は `llm-wiki/` を入口として案内する

- [x] シナリオ2：generator と tests が新 root 前提で通る

1. 🧱 `tools/gen_wiki.py` と `test/test_gen_wiki.py` は旧 `wiki/` root を前提にしている
2. 🎬 default root と fixture path を `llm-wiki/` へ更新する
3. ✅ `python -m pytest test/test_gen_wiki.py -q` と `python -m pytest test/ -q` が通る

- [x] シナリオ3：historical tasknote は当時の記録として残る

1. 🧱 `steering/done/*.md` には旧 path を含む記録がある
2. 🎬 rename 実装時に active docs と現 artifact のみに変更を絞る
3. ✅ 過去 note を一括改変せず current operation だけが新 root を向く

---

## 4) Design（どうやるか）

### 【参照】

- Spec: `docs/superpowers/specs/2026-05-23-llm-wiki-root-rename-design.md`
- Runtime Tooling: `tools/gen_wiki.py`
- Test: `test/test_gen_wiki.py`
- Active Doc: `llm-wiki/README.md`
- Steering: `steering/done/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す.md`

### 変更範囲

- やること:
  - `wiki/` を `llm-wiki/` へ改名する
  - generator の default root と説明文を更新する
  - tests と active docs と generated navigation を新 root に合わせる
- やらないこと:
  - `raw/` `wiki/` `checklists/` の内部構造変更
  - historical `steering/done/*.md` の一括置換
  - 互換用 `wiki/` stub の追加

### 検証

- 検証コマンド:
  - `python -m pytest test/test_gen_wiki.py -q`
  - `python -m pytest test/ -q`
  - `find llm-wiki -maxdepth 3 -type d | sort`
  - `rg -n "wiki/wiki|wiki/raw|wiki/checklists" llm-wiki tools test docs steering`
- 成功条件:
  - generator と test が新 root 前提で通る
  - `llm-wiki/` 配下に expected layout がある
  - active docs と generated nav の入口が新 root を向く
- 未実施時の扱い:
  - verify 未実施なら rename 完了扱いにしない

---

## 5) Tasklist

- [x] rename 方針を spec に固定する
- [x] `wiki/` を `llm-wiki/` へ改名する
- [x] `tools/gen_wiki.py` の default root と path 文言を更新する
- [x] `test/test_gen_wiki.py` の fixture と expected path を更新する
- [x] active docs と generated navigation を新 root にそろえる
- [x] verify を実行して結果を Result に記録する

---

## 6) Result

- `wiki/` を `llm-wiki/` へ改名し、内部 layout は `raw/` `wiki/` `checklists/` のまま維持した
- `tools/gen_wiki.py` の default root を `<repo>/llm-wiki` に更新し、`llm-wiki/checklists/...` を checklist source として扱えるようにした
- `test/test_gen_wiki.py` に default root と query README 文言の期待を追加し、`python -m pytest test/test_gen_wiki.py -q` を `4 passed` で通した
- `llm-wiki/README.md`、`llm-wiki/wiki/query/README.md`、`llm-wiki/wiki/query/spot-check.md` を新 root 名に合わせて更新した
- `python -m pytest test/ -q` を 2 回通し、どちらも `747 passed, 2 skipped, 14233 subtests passed` だった
- `find llm-wiki -maxdepth 3 -type d | sort` で `llm-wiki/raw`、`llm-wiki/wiki`、`llm-wiki/checklists` の存在を確認した

---

## 7) Discussion

### 2026年5月23日 09:58 UTC（起票）

**Observe**：repo-local LLM Wiki は `wiki/` root 配下にあり、artifact の実態は `wiki/raw/`, `wiki/wiki/`, `wiki/checklists/` に分かれている。  
**Think**：今回の主問題は内部構造ではなく root 名の分かりにくさなので、`wiki/` を `llm-wiki/` へ改名し、generator と tests と active docs を合わせるのが最小差分である。  
**Act**：spec を tasknote に落とし、historical note は書き換えない前提で rename 実装タスクを起票した。

### 2026年5月23日 10:05 UTC（完了）

**Observe**：failing test は default root、checklist source path、query README の旧 root 文言で落ちた。`llm-wiki/raw/tasknotes/...` に入った historical note も旧 path を多数含むが、これは source snapshot として残す対象だった。  
**Think**：generator の責務は root 名と checklist source 正規化だけ直せば十分で、historical note の本文一括置換はやはりノイズが大きい。active docs と query 入口だけを新 root に寄せれば current operation はそろう。  
**Act**：`tools/gen_wiki.py` と `test/test_gen_wiki.py` を更新して GREEN に戻し、tree を `llm-wiki/` へ移動し、active docs を更新して full pytest まで通した。

---

## 8) Closing

- 状態: done
- 次のゲート: なし
- close 条件:
    - [x] `llm-wiki/` root ができている
    - [x] generator と tests が新 root 前提で通っている
    - [x] verify 結果が Result に記録されている
