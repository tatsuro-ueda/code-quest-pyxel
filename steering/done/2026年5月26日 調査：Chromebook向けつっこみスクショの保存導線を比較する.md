---
status: done
priority: high
scheduled: 2026-05-26T18:25:15+00:00
dateCreated: 2026-05-26T18:25:15+00:00
dateModified: 2026-05-26T18:55:45+00:00
tags:
  - task
  - research
  - screenshot
  - sharing
  - chromebook
  - save
  - web
  - ux
  - archived
---

# 2026年5月26日 調査：Chromebook向けつっこみスクショの保存導線を比較する

> 状態：✅ close
> 次のゲート：なし

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 子どもが `撮る -> 保存する -> あとで見せる` を自分で把握できる導線をつくる
> 補足：やらないこと 今回は実装着手や upload 機能の追加までは進めない
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 主な利用端末は Chromebook である
   2. 💦 つっこみスクショは絵文字スタンプ最大 50 個で始める
   3. 💦 `play.html -> iframe(pyxel.html)` の wrapper 構成は維持する
   4. 💦 既存調査で wrapper から PNG 化できる見込みは確認済みである

2. Before
   1. 💦 共有先が Chromebook では限定され、まずはローカル保存が現実的である
   2. 💦 自動 download だけだと保存場所が子どもに見えにくい
   3. ❌ 撮れたとしても、その後の行き先が分からず会話が止まりうる

3. After
   1. 💦 保存ファーストの導線候補が Chromebook 前提で整理される
   2. ✅ `Chrome Canvas 型 + Show in folder` が第1候補として残る
   3. ✅ 類似事例と trusted voices が tasknote に記録される
   4. ❤️ 次に実装へ進む前提がそろう

4. 例外
   1. File System Access API は secure context と user gesture が要る
   2. 端末や管理ポリシーにより file picker の挙動が変わることがある

5. 境界条件
   1. `Code Maker` を主役から外さない
   2. 第1段階では server upload を持たない
   3. capture と share を分け、まず save UX を成立させる

6. 委任度
   1. 🟢 全体として起票と初期設計までは CC が自走できる
   2. 🟢 CCのみで可: note 起票、初期 Gherkin、wrapper 起点の設計整理
   3. 🔴 人の判断: 保存後の見せ方や親の関与レベルは user 判断が要る

---

## 2) ユーザーストーリーマップ

> Gherkin の前に、今回の実装テーマと事例調査の順番だけをそろえる。
> 委任度：🟢 事例調査まではこの順でそのまま進められる
> 残る曖昧さ：どの事例パターンを主導線に寄せるかは user 相談が要る

### 事前確認

- [ ] tasknote確認済み
- [ ] skill・tool・MCP確認済み
  - [ ] `manage-tasknotes`
  - [ ] `manage-tasknotes-create`
  - [ ] `manage-tasknotes-rules-core`
  - [ ] `manage-tasknotes-rules-format`
  - [ ] `brainstorming`
- [ ] 永続的ドキュメント確認済み
  - [ ] `AGENTS.md`
  - [ ] `docs/architecture.md`
  - [ ] `docs/framework-rule.md`
  - [ ] `docs/customer-jobs.md`
  - [ ] `docs/customer-journeys.md`
  - [ ] `templates/wrapper.html`
  - [ ] `steering/done/2026年5月26日 調査：つっこみスクショ機能の技術選定を進める.md`

### 本体

#### 話題1：保存導線を Chromebook 前提に絞る

##### ユーザー：子どもに保存場所を分かりやすくしたい担当者

1. 当初計画
   1. 👀 主導線を `showSaveFilePicker` と `download` で比較する
   2. ✂️ 最初の実装を `保存ファースト` に固定する
   3. 📝 子どもに伝わる保存後メッセージの要件を残す
2. 追加分
   1. 👀 Chromebook と子ども向け web editor の事例を集める
   2. ✂️ `ローカル保存` と `後から共有` の切り分け例を見る
   3. 📝 似ている保存 UX の型を 2〜3 個に整理する

#### 話題2：Chromebook らしい保存後体験を調べる

##### ユーザー：保存後に迷わせたくない担当者

1. 当初計画
   1. 👀 `Downloads` `Select folder` `Show in folder` の導線を確認する
   2. ✂️ 保存後に再発見しやすい UX 要素を抜き出す
   3. 📝 子どもが理解しやすい補助導線を note に残す

#### 話題3：誰の視点で判断するかを整理する

##### ユーザー：調査結果の筋を確かめたい担当者

1. 当初計画
   1. 👀 trusted voices を creative learning と product で分けて探す
   2. 👀 何をどの人の視点で判断するかを整理する
   3. 📝 次の相談相手候補を note に残す

---

## 3) Gherkin（完了条件）

> 委任度：🟢 調査結果の整理と保存までなら CC が自走できる
> 残る曖昧さ：なし

### シナリオ一覧

- [x] シナリオ1：類似事例の保存 UX 型が比較できる

1. 🧱 Chromebook と子ども向け制作ツールの保存事例を調べている（調査）
2. 🎬 似ている保存導線を比較する（調査）
3. ✅ 保存 UX の型が 2〜4 個に整理される（tasknote）

```gherkin
Given Chromebook と子ども向け web editor の保存事例を調べている
When 類似する保存導線を比較する
Then 保存 UX の型を 2〜4 個に整理できる
And 第1候補と補助候補を言語化できる
```

- [x] シナリオ2：Chromebook らしい保存後導線が明記される

1. 🧱 Chromebook の保存先と再発見導線を調べている（調査）
2. 🎬 `Downloads` `Select folder` `Show in folder` を確認する（調査）
3. ✅ 保存後に迷いにくい補助導線が tasknote に残る（tasknote）

```gherkin
Given Chromebook の保存先と再発見導線を調べている
When 保存後の行方が分かる要素を比較する
Then 保存後に迷いにくい補助導線を tasknote に残せる
And `Show in folder` を補助線として評価できる
```

- [x] シナリオ3：trusted voices が判断材料として整理される

1. 🧱 子どもの創作 UX に詳しい発信者を探している（調査）
2. 🎬 creative learning と product の両軸で整理する（調査）
3. ✅ 次の相談相手候補が tasknote に残る（tasknote）

```gherkin
Given 子どもの創作 UX に詳しい発信者を探している
When creative learning と product の両軸で候補を整理する
Then 次の相談相手候補を tasknote に残せる
And どの人の視点をどの判断に使うかを明記できる
```

---

## 4) Design（どうやるか）

### 責務分担概要

- root cause は `Chromebook 向け保存導線の前例と判断材料が未整理だった` である
- 正本は `docs/customer-jobs.md` `docs/customer-journeys.md` と公式ヘルプ記事に置く
- 今回の入口は tasknote と公式資料の比較であり、コード実装には入らない
- 調査対象は `類似事例` `Chromebook 保存導線` `trusted voices` の 3 本に分ける

### 責務分担概要図

```mermaid
flowchart TD
    A[類似事例を集める] --> B[Chromebook の保存後導線を比べる]
    B --> C[trusted voices を整理する]
    C --> D[第1候補の型を tasknote に残す]
```

### 責務分担詳細

- `docs/customer-jobs.md` （👀：子どもの job との整合を見る）
- `docs/customer-journeys.md` （👀：共有・保存の連続体験の要求を見る）
- `Chromebook Help / Chrome Canvas / Piskel / Pixilart` （👀：保存 UX の前例を見る）
- `tasknote` （✏️：調査結果と候補整理を記録する）

### 関連スキル・MCP

- `manage-tasknotes`
- `brainstorming`
- `research`
- `find-trusted-voices`

### 【参照】

- Steering: `steering/done/2026年5月26日 調査：つっこみスクショ機能の技術選定を進める.md`
- Architecture: `docs/architecture.md`
- UXPolicy: `docs/customer-jobs.md` / `docs/customer-journeys.md`

### 変更範囲

- やること: 類似事例調査、trusted voices 整理、推奨方針の記録
- やらないこと: 実装着手、server upload、Pyxel scene への UI 追加

### 検証

- 検証コマンド: tasknote lint と `python -m pytest test/ -q` を回す
- 成功条件: 調査結果が tasknote に残り、lint が通る
- 未実施時の扱い: pytest の既存 fail は原因を分けて記録する

---

## 5) Tasklist

```mermaid
flowchart TD
    T1[類似事例を調査する] --> T2[Chromebook 保存導線を整理する]
    T2 --> T3[trusted voices を整理する]
    T3 --> T4[推奨方針を tasknote に残す]
    T4 --> T5[lint と pytest の結果を記録する]

    classDef done fill:#d4edda,stroke:#155724,color:#000000;
    classDef wip fill:#fff3cd,stroke:#856404,color:#000000;
    classDef todo fill:#e2e3f1,stroke:#3949ab,color:#000000;

    class T1,T2,T3,T4,T5 done;
```

> 必ず上から順に実施。CCがCoVeで自力検証しながら進める。

- [x] （CC）類似事例を調査する
- [x] （CC）Chromebook 保存導線を整理する
- [x] （CC）trusted voices を整理する → **作業ログに事実を記録** → **Discussionに判断を記録**
- [x] （CC）推奨方針を tasknote に残す
- [x] （CC）lint と `python -m pytest test/ -q` の結果を記録する

### 記録の分け方

#### 作業ログ に書く

- 変更したファイルや差分
- 実行した確認コマンドと結果
- 参照した事例と trusted voices

#### Discussion に書く

- なぜその事例を近いとみなしたか
- どの発信者の視点を何の判断に使うか
- 次に実装 note を切るなら何を固定して始めるか

---

## 6) 作業ログ

- 起票方針を決めた
  - Chromebook 前提では `保存ファースト` が最小実装と判断した
  - 自動 download より `保存ダイアログあり` を主導線に置く方針にした
- 類似事例を調査した
  - Google `Chrome Canvas` は Chromebook 上で絵をローカル保存でき、
    `画像として保存` のあと `フォルダで表示` を案内している
  - Chromebook 標準のスクリーンショットは `Downloads` へ保存され、
    保存先フォルダを変えられる
  - Chromebook shelf / Tote には recent screenshot preview が出て、
    `Show in folder` や `Copy image` がある
  - `Piskel For Kids` は子ども向けに social 機能を削り、
    browser 上で安全に export する方針を取っている
  - `Pixilart` は `Download .PNG` と `Upload Drawing` を UI で分け、
    upload には login を要求している
- 検証コマンドを回した
  - tasknote lint は通過した
  - `python -m pytest test/ -q` は既存 3 fail のままで、
    `docs/architecture_rules.yml`
    と `docs/stakeholder_voices.yml` 欠落が原因だった
- 信頼できる発信者を追加で整理した
  - `Mitchel Resnick` は child agency と creative learning の原理を見る軸
  - `Ricarose Roque` は family creative learning と関係性設計を見る軸
  - `Andrés Monroy-Hernández` は `つくる + 共有する` の設計を見る軸
  - `Björn Jeffery` は子ども向けデジタルトイの感覚を見る軸
  - `Karen Brennan` と `Yasmin Kafai` は Scratch 周辺の補助線になる

---

## 7) 評価と成果物

> 評価：🟢 調査完了

### 成果物

- `steering/done/2026年5月26日 調査：Chromebook向けつっこみスクショの保存導線を比較する.md` （保存導線の調査記録）

---

## 8) Discussion

### 反省とルール化

- 記入先：manage-tasknotes
- 次にやること：実装へ進めるなら別 note で最小仕様を切る

### 判断メモ

1. `Chrome Canvas 型`
   - 最も Chromebook に近い
   - `保存する` と `保存先を見る` が連続している
   - 今回はこの型が第1候補である

2. `Chromebook screenshot 型`
   - `Downloads` と `Select folder` が前提にある
   - 保存後に shelf / Tote から再発見できる
   - `保存後の行方が分からない` 問題への補助線として強い

3. `Piskel For Kids 型`
   - 子ども向けに `no ads` `no tracking` `no social features`
     を明示している
   - `まず export` して終える考え方は相性が良い
   - ただし Chromebook 固有の保存理解までは支えていない

4. `Pixilart 型`
   - `Download .PNG` と `Upload Drawing` を明確に分けている
   - 今回の `まず保存、upload は別機能` の考え方を後押しする
   - ただし子ども向け安全性は Piskel For Kids より弱い

### 参考にしたい個人発信者

1. `Mitchel Resnick`
   - URL: `https://www.media.mit.edu/people/mres/`
   - 理由: Scratch と 4P の原点で、`保存` を単機能でなく
     `Projects + Peers + Passion + Play` の流れで見られる
   - 注意: 原理は強いが、Chromebook 固有 UX の話は少ない

2. `Ricarose Roque`
   - URL: `https://www.ricarose.com/`
   - 理由: Family Creative Learning を直接持っており、
     `親子で保存物を介して関係をつくる` 視点が近い
   - 注意: product UI の細部より workshop / community 寄り

3. `Andrés Monroy-Hernández`
   - URL: `https://www.andresmh.com/`
   - 理由: Scratch website の設計に関わっており、
     `create and share programmable media` の橋渡しに近い
   - 注意: 現在は子ども専業ではなく social computing 全般へ広い

4. `Björn Jeffery`
   - URL: `https://www.bjornjeffery.com/`
   - 理由: Toca Boca 由来で、
     `子どもが迷わず触れて見せたくなる` 体験の感覚が強い
   - 注意: 学術原理より product / market 観点が中心

5. `Karen Brennan`
   - URL: `https://kbrennan.scholars.harvard.edu/`
   - 理由: ScratchEd と Creative Computing Lab から、
     `作る人を支える周辺導線` の視点を借りやすい
   - 注意: 教師支援の比重が高く、親子共有に直結しない部分もある

6. `Yasmin Kafai`
   - URL: `https://www.gse.upenn.edu/academics/faculty-directory/kafai`
   - 理由: `game design as learning` と Scratch 研究の基礎が深い
   - 注意: save UX の細部より learning design 全体を見る人

---

## 9) Closing

- 状態: open
- 次のゲート: なし
- close 条件:
  - [x] 類似事例が tasknote に記録される
  - [x] trusted voices が tasknote に記録される
  - [x] 推奨方針と pytest 結果が tasknote に記録される

---

## 10) 参考資料

- Local: `docs/architecture.md`
- Local: `docs/framework-rule.md`
- Local: `docs/customer-jobs.md`
- Local: `docs/customer-journeys.md`
- Local: `templates/wrapper.html`
- Local: `steering/done/2026年5月26日 調査：つっこみスクショ機能の技術選定を進める.md`
- Web: [Chrome 描画キャンバスで絵を描く - Chromebook ヘルプ](https://support.google.com/chromebook/answer/9200774?hl=ja)
- Web: [Take a screenshot or record your screen - Chromebook Help](https://support.google.com/chromebook/answer/10474268?hl=en-en)
- Web: [Customize your Chromebook's shelf - Chromebook Help](https://support.google.com/chromebook/answer/3113576?hl=en-en)
- Web: [Mitchel Resnick - MIT Media Lab](https://www.media.mit.edu/people/mres/)
- Web: [Ricarose Roque](https://www.ricarose.com/)
- Web: [Andrés Monroy-Hernández](https://www.andresmh.com/)
- Web: [Björn Jeffery](https://www.bjornjeffery.com/)
- Web: [Karen Brennan](https://kbrennan.scholars.harvard.edu/)
- Web: [Yasmin B. Kafai | Penn GSE](https://www.gse.upenn.edu/academics/faculty-directory/kafai)
- Web: [Piskel FAQ](https://www.piskelapp.com/faq/)
- Web: [Piskel Terms](https://www.piskelapp.com/terms/)
- Web: [Pixilart Editing Help](https://www.pixilart.com/draw/help-6a87c26067abf16)
