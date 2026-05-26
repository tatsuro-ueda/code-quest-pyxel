---
status: in-progress
priority: high
scheduled: 2026-05-26T18:25:15+00:00
dateCreated: 2026-05-26T18:25:15+00:00
dateModified: 2026-05-26T18:48:14+00:00
tags:
  - task
  - screenshot
  - sharing
  - chromebook
  - save
  - web
  - ux
---

# 2026年5月26日 共有：Chromebook向けつっこみスクショを保存ファーストで始める

> 状態：⑥ 作業ログ
> 次のゲート：（user）`Chrome Canvas 型 + Show in folder` を採るか判断する

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 子どもが `撮る -> 保存する -> あとで見せる` を自分で把握できる導線をつくる
> 補足：やらないこと 今回は HP へのアップロードやコメント返却までは進めない
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
   1. 💦 保存ファーストの導線が Chromebook 前提で定まる
   2. ✅ 主導線を `保存ダイアログあり` にするかどうかが決まる
   3. ✅ 非対応時の fallback と説明文が決まる
   4. ❤️ 子どもが `ここに保存した` を自分で言える

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

#### 話題2：wrapper 側の最小責務を決める

##### ユーザー：Pyxel 本体を汚さずに始めたい担当者

1. 当初計画
   1. 👀 capture と stamp overlay と save UI を wrapper に寄せる
   2. ✂️ Pyxel 側は必要なら `postMessage` 通知だけに留める
   3. 📝 build 入口と smoke 手順を note に残す

#### 話題3：fallback と説明文を切り分ける

##### ユーザー：非対応時でも迷わせたくない担当者

1. 当初計画
   1. 👀 file picker 非対応時だけ download へ落とす
   2. 👀 保存先が見えにくい場合の補助文を決める
   3. 📝 子ども向け文言と親向け文言を混ぜない

---

## 3) Gherkin（完了条件）

> 委任度：🟢 この仕様線までなら CC が自走できる
> 残る曖昧さ：なし

### シナリオ一覧

- [ ] シナリオ1：保存ボタンから保存ダイアログを開ける

1. 🧱 子どもが wrapper 上のスクショ画面を見ている（play.html）
2. 🎬 `ほぞん` ボタンを押す（play.html）
3. ✅ 保存ダイアログが開き、保存先とファイル名を選べる（OS UI）

```gherkin
Given 子どもが Chromebook 上でつっこみスクショの保存画面を開いている
When 子どもが `ほぞん` ボタンを押す
Then 保存ダイアログが開く
And 子どもは保存先とファイル名を自分で選べる
```

- [ ] シナリオ2：保存後に結果がその場で分かる

1. 🧱 子どもが保存ダイアログで保存先を選んでいる（OS UI）
2. 🎬 保存を完了する（OS UI）
3. ✅ wrapper 上に保存完了メッセージが出る（play.html）

```gherkin
Given 子どもが保存ダイアログを開いている
When 子どもが保存先を選び PNG を保存する
Then wrapper 上に保存できたことを示すメッセージが出る
And 子どもは `ここに保存した` と把握できる
```

- [ ] シナリオ3：file picker が使えない環境でも保存を諦めない

1. 🧱 ブラウザが `showSaveFilePicker` を提供していない（play.html）
2. 🎬 子どもが `ほぞん` ボタンを押す（play.html）
3. ✅ download fallback と補助文で保存へ進める（play.html）

```gherkin
Given ブラウザが `showSaveFilePicker` を提供していない
When 子どもが `ほぞん` ボタンを押す
Then PNG は download fallback で保存できる
And どこを見ればよいかの補助文が表示される
```

---

## 4) Design（どうやるか）

### 責務分担概要

- root cause は `Chromebook での保存導線が未実装で、保存先の理解も設計されていない` である
- 正本は `docs/customer-jobs.md` `docs/customer-journeys.md` と wrapper 構成の実体に置く
- 修正入口は `templates/wrapper.html` とその生成元 `tools/render_release_selector.py` に閉じる
- 実装時は `capture -> annotate -> save` を wrapper で完結させ、Pyxel 側は必要最小限に留める

### 責務分担概要図

```mermaid
flowchart TD
    A[iframe 内 canvas から PNG を作る] --> B[絵文字スタンプを焼き込む]
    B --> C[save picker を開く]
    C --> D[保存完了か fallback を表示する]
```

### 責務分担詳細

- `templates/wrapper.html` （✏️：保存ボタン、スタンプ overlay、save UI を持たせる）
- `tools/render_release_selector.py` （✏️：wrapper 生成に必要な placeholder を保つ）
- `dist/play.html` （❌：生成物のため直接編集しない）
- `src/runtime/app.py` （❌：第1段階では保存 UI を持たせない）

### 関連スキル・MCP

- `manage-tasknotes`
- `brainstorming`
- `playwright`

### 【参照】

- Steering: `steering/done/2026年5月26日 調査：つっこみスクショ機能の技術選定を進める.md`
- Architecture: `docs/architecture.md`
- UXPolicy: `docs/customer-jobs.md` / `docs/customer-journeys.md`

### 変更範囲

- やること: wrapper の保存導線、保存結果メッセージ、fallback 文言の実装
- やらないこと: server upload、コメント機能、Pyxel scene への大規模 UI 追加

### 検証

- 検証コマンド: `python -m pytest test/ -q` と local browser smoke を回す
- 成功条件: save picker 主導線と download fallback の両方が確認できる
- 未実施時の扱い: 実機未確認は未確認として残し、desktop smoke と分けて記録する

---

## 5) Tasklist

```mermaid
flowchart TD
    T0[類似事例を調査する] --> T1[保存ファーストの最小仕様を固める]
    T1 --> T2[wrapper の保存導線を実装する]
    T2 --> T3[fallback 文言を入れる]
    T3 --> T4[local browser smoke と pytest を回す]
    T4 --> T5[Development Checklist を /tmp へコピーしてレビューする]

    classDef done fill:#d4edda,stroke:#155724,color:#000000;
    classDef wip fill:#fff3cd,stroke:#856404,color:#000000;
    classDef todo fill:#e2e3f1,stroke:#3949ab,color:#000000;

    class T0 done;
    class T1,T2,T3,T4,T5 todo;
```

> 必ず上から順に実施。CCがCoVeで自力検証しながら進める。

- [x] （CC）類似事例を調査する
- [ ] （CC）保存ファーストの最小仕様を固める
- [ ] （CC）wrapper の保存導線を実装する
- [ ] （CC）fallback 文言を入れる → **作業ログに事実を記録** → **Discussionに判断を記録**
- [ ] （CC）local browser smoke と `python -m pytest test/ -q` を回す
- [ ] （CC）Development Checklist を `/tmp` へコピーしてレビューする

### 記録の分け方

#### 作業ログ に書く

- 変更したファイルや差分
- 実行した確認コマンドと結果
- file picker / download fallback の成否

#### Discussion に書く

- なぜ保存ダイアログを主導線にしたか
- 非対応時の説明文をどう決めたか
- 次に共有や upload を足すなら何を守るか

### レビュー

- 原本 checklist: `docs/development-checklist.md`
- /tmp コピー: `/tmp/development-checklist-20260526-1825.md`
- レビュー結果: 未実施
- 未通過時の扱い: fail があれば修正して再レビューし、全部通るまで Close しない

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

> 評価：🟡 類似事例の調査まで完了

### 成果物

- `steering/2026年5月26日 共有：Chromebook向けつっこみスクショを保存ファーストで始める.md` （保存ファースト実装の起票）

---

## 8) Discussion

### 反省とルール化

- 記入先：manage-tasknotes
- 次にやること：事例比較と trusted voices を見て主導線の型を 1 本に決める

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
- 次のゲート: （user）`Chrome Canvas 型 + Show in folder` を採るか判断する
- close 条件:
  - [ ] 保存主導線と fallback が実装される
  - [ ] local browser smoke と pytest の結果が記録される
  - [ ] Development Checklist のレビュー結果が残る

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
