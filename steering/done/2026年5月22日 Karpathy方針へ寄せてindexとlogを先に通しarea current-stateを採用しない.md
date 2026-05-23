---
status: done
priority: high
scheduled: 2026-05-22T21:10:00.000+09:00
dateCreated: 2026-05-22T21:10:00.000+09:00
dateModified: 2026-05-22T21:20:00.000+09:00
tags:
  - task
  - llm-wiki
  - karpathy
  - index
  - log
---

# 2026年5月22日 Karpathy方針へ寄せてindexとlogを先に通しarea current-stateを採用しない

> 状態：⑧ Closing 完了
> 次のゲート：（CC）`wiki/wiki/index.md` と `wiki/wiki/log.md` の最小形を tasknote に落とし、`tools/gen_wiki.py` でどこまで自動生成するかを決める

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 shared package の一般論より repo 固有ローカル設計が先に立ちすぎるのを防ぎ、Karpathy gist の抽象度に近い安全な最小形へ戻す
> 補足：やらないこと この note では `battle` / `guardrails` のような repo 固有 area 分類を current-state ページへ展開しない

1. 前提条件
   1. 💦 Karpathy の gist は `index.md` と `log.md` を明示しているが、repo 固有の area current-state 分類は明示していない
   2. 💦 `code-quest-pyxel` では `docs/` と `steering/done/` の source がまだ少数しか wiki 化されておらず、早すぎる area 設計は過剰化しやすい
   3. 💦 ユーザーは「Karpathy の考え方に寄せる方が安全」と明示している

2. Before
   1. 💦 次の実作業は child `05` の repo 固有解釈として `raw tasknotes index` と `area current-state` を作る前提になっていた
   2. 💦 これは shared package の一般案を repo 側で強く具体化しすぎており、Karpathy の最小パターンから一段離れていた
   3. ❌ 迷う

3. After
   1. 💦 次のゲートは `index.md` と `log.md` を先に通す Karpathy 寄りの路線へ差し替わる
   2. ✅ `area current-state` は evidence が薄い local extension として保留扱いになる
   3. ❤️ 安心

4. 例外
   1. 将来 source 数や summary 数が増えて `index.md` だけでは探索がつらくなったときは、その時点で area 切りを再検討してよい
   2. ただし再検討しても、まずは query の痛みや search の不足を根拠としてから導入する

5. 境界条件
   1. 今回の修正対象は repo 側 current-date tasknotes と `wiki/README.md` に限定する
   2. `steering/llm-wiki/` の shared package mirror 自体は書き換えない

6. 委任度
   1. 🟢 全体として CC 単独で進められる：repo 側 orchestration と README の更新で足りる
   2. 🟢 CCのみで可：child `05` 方向の next gate を Karpathy 寄りへ差し替える
   3. 🟡 後で人の判断があり得る：`index.md` と `log.md` を generator に寄せるか、最初は手動で作るか

---

## 2) ユーザーストーリーマップ

> Gherkin の前に、今回の仕事をどの順番で進めるかだけをそろえる。
> 委任度：🟢 repo 側 next gate の差し替えまでは CC が進められる
> 残る曖昧さ：`index.md` と `log.md` の自動生成責務は次ノートで確定する

### 話題一覧

#### 話題1：Karpathy の明示項目へ戻す

##### ユーザー：私

1. 当初計画
    1. 👀 gist の `Indexing and logging` を根拠にする
    2. 🧭 `index.md` と `log.md` を次の最小ゴールにする
    3. ✂️ `area current-state` は次ゲートから外す

#### 話題2：repo 側の current-date notes だけを修正する

##### ユーザー：私

1. 当初計画
    1. 📝 child `04` の Closing と親 orchestration note の next gate を差し替える
    2. 📝 `wiki/README.md` に「areas は current rollout では未採用」と書く
    3. 🔗 新しい repo-local note に判断理由を残す

---

## 3) Gherkin（完了条件）

> 委任度：🟢 設計差し替えまでは CC が完走できる
> 残る曖昧さ：なし

### シナリオ一覧

- [x] シナリオ1：repo 側 next gate が area current-state から index/log へ変わる

1. 🧱 current-date notes は child `05` の local area 設計へ進む形になっている
2. 🎬 次の実作業を `index.md` / `log.md` 先行へ差し替える
3. ✅ 未来のセッションは Karpathy 寄りの最小パターンから再開できる

- [x] シナリオ2：shared package と repo ローカル判断の境界が残る

1. 🧱 shared package には `areas/current-state` がある
2. 🎬 repo 側では mirror を保ったまま current-date notes だけで逸脱を明記する
3. ✅ shared package 更新を壊さずに repo ローカル判断だけ差し替えられる

---

## 4) Design（どうやるか）

### 責務分担概要

- shared package は参考として残す
- repo 側 current-date notes が「この repo はどこまで採るか」を決める
- 次ノートでは `index.md` と `log.md` を最小で通し、area current-state は保留にする

### 【参照】

- Steering: `steering/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する.md`
- Steering: `steering/done/2026年5月22日 練習用プロジェクトでminimal ingestとsummariesを通す.md`
- Steering: `steering/llm-wiki/child-tasknotes/05-練習用プロジェクトでraw tasknotes indexとarea current-stateを通す.md`
- External: Andrej Karpathy `LLM Wiki` gist

### 変更範囲

- やること:
  - repo 側 current-date note の next gate を差し替える
  - `wiki/README.md` に current rollout の方針を追記する
  - この判断を steering note に残す
- やらないこと:
  - shared package mirror の書き換え
  - `index.md` / `log.md` の本実装
  - `area current-state` の実装

### 検証

- 検証コマンド:
  - `rg -n "area current-state|index.md|log.md" steering/2026年5月22日*.md wiki/README.md`
- 成功条件:
  - repo 側 next gate が `index.md` / `log.md` 先行に差し替わっている
  - `area current-state` は current rollout で未採用と読める
- 未実施時の扱い:
  - 次の自律再開点が古いまま残るので未完了扱いにする

---

## 5) Tasklist

- [x] current-date child `04` の Closing を差し替えた
- [x] parent orchestration note の next gate を差し替えた
- [x] `wiki/README.md` に current rollout 方針を追記した
- [x] この note 自身に判断理由を残した

---

## 6) Result（成果物）

- repo 側 next gate を `raw tasknotes index / area current-state` から `index.md / log.md` 先行へ差し替えた
- `steering/done/2026年5月22日 練習用プロジェクトでminimal ingestとsummariesを通す.md` と親 orchestration note の次ゲート文言を更新した
- `wiki/README.md` に「current rollout は Karpathy の最小パターンへ寄せる」「areas は reserved/optional」と明記した
- shared package mirror 自体は変更せず、repo 側 current-date notes だけでローカル判断を上書きした

---

## 7) Discussion（残課題の起票）

### 残課題メモ

- `index.md` と `log.md` の生成責務を `tools/gen_wiki.py` にどこまで持たせるかはまだ未確定
- shared package 側の child `05` は残るので、今後も repo ローカル判断との差を current-date notes 側で管理する必要がある
- 別tasknoteにした場合のタイトル or パス：`steering/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す.md`

### 反省とルール化

- 記入先：`wiki/README.md`, `steering/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する.md`
- 次にやること：`index.md` と `log.md` を先に通し、それでも navigation が足りないと判明した場合だけ local extension を足す

---

## 8) Closing

- 状態: done
- 次のゲート: `steering/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す.md` を開き、`index.md` / `log.md` の実生成へ進む
- close 条件:
    - [x] repo 側 next gate を差し替えた
    - [x] shared package mirror はそのまま保った
    - [x] `wiki/README.md` に current rollout 方針を追記した
