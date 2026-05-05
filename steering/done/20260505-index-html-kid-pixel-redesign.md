---
status: done
priority: normal
scheduled: 2026-05-05T19:30:00+09:00
dateCreated: 2026-05-05T19:30:00+09:00
dateModified: 2026-05-05T19:30:00+09:00
tags:
  - task
  - ui
  - landing-page
  - kid-friendly
  - pixel-art
  - archived
---

# 2026年5月5日 index.html を子ども向けピクセルアート系に再デザイン

> 状態：① Journey ② Gherkin ③ Design ④ Tasklist 一気書き → 実装完走へ
> ターゲット：子ども本人（中学生未満〜中学生）
> 役割：A. 子ども向け UI デザイナー
> 画像追加スコープ：B（ヒーロー画像 + Code Maker 編集画面 + プレイ GIF を新規撮影して追加）
> 美術方向：ピクセルアート系（ゲーム本体と同じ 8bit テイストで揃える）

---

## 1) Journey

- **深層的目的**：子どもが index.html を開いた瞬間に「あそびたい！」と感じる入口にする
- **やらないこと**：
  - 大人 / 開発者向けの説明文を増やす
  - 既存の Code Maker 連携機能（zip インポート、リソースエディタへのリンク）を壊す
  - パフォーマンスを犠牲にする巨大画像 / 多数の外部依存

### Before（現状）
1. ❌ （子ども・スマホ）黒一色のダーク背景で「ゲーム本体」と入口の世界観が乖離している
2. ❌ （子ども・スマホ）画像 (`essay-manga.jpg`) が 1 枚だけで、タップしても拡大されない
3. ❌ （子ども）見出しが「ブロッククエスト」だけで、何のゲームか直感で分からない
4. ❌ （子ども）「あそんでみる」ボタンの押せる感が薄い（背景になじむグレー寄り）
5. ❌ （子ども）ひらがな比率は高いが、配色・フォントが大人っぽくて遊びの誘いが弱い

### After（達成状態）
1. ✅ （子ども・スマホ）開いた瞬間にヒーロー画像（タイトル画面）と「あそぼう」の文字が大きく目に入る
2. ✅ （子ども・スマホ）スクショをタップすると画面いっぱいに拡大、もう一度タップで戻る
3. ✅ （子ども）配色がファミコン系のカラフル、フォントがピクセルゲームの見出し風で「ゲームっぽい」と一目で伝わる
4. ✅ （子ども）「あそんでみる」ボタンが大きく、ピクセル枠線で押せそう感が強い
5. ✅ （子ども）剣 / 宝箱 / ハート等のピクセル装飾が散らされ、ゲーム世界の入口として機能する
6. ❤️ （子ども）「あそびたい！」と思って迷わず本番ボタンを押す

## 2) Gherkin

### シナリオ1：開いた瞬間にゲームの世界観が伝わる
> 🧱 Given: 子どもがスマホで index.html を初めて開く。🎬 When: ページが表示される。✅ Then: タイトル画面（ヒーロー画像）が画面幅いっぱいに表示され、ファミコン的な明るい配色とピクセルフォントで「これはゲームのページだ」と 2 秒以内に直感できる。「あそんでみる」ボタンが視認できる位置にある。

### シナリオ2：画像をタップすると拡大される
> 🧱 Given: ページ内に複数のスクショ（タイトル / バトル / マップ等）が並んでいる。🎬 When: 子どもがスクショ画像をタップする。✅ Then: その画像が画面いっぱいに拡大表示され、画面の暗いオーバーレイの上に出る。スマホでも PC でも動く。

### シナリオ3：拡大画像を簡単に閉じる
> 🧱 Given: スクショが拡大表示されている。🎬 When: 子どもが拡大画像 / オーバーレイ / × ボタン / Escape キーをタップ・押下する。✅ Then: 拡大が閉じてもとのページに戻る。スクロール位置は維持される。

### シナリオ4：本文が中学生未満にも読める
> 🧱 Given: 改修後の index.html。🎬 When: 子どもが本文を読む。✅ Then: 漢字に頼った大人っぽい説明が無く、ひらがな + カタカナ + 必要最小限の漢字（小学校 4 年生レベル）で書かれている。フォントサイズが 16 px 以上で、行間がゆったりしている。

### シナリオ5：「あそんでみる」ボタンが目立って押せる感がある
> 🧱 Given: ページに「あそんでみる」ボタンがある。🎬 When: 子どもがページを見渡す。✅ Then: ボタンがファミコン的な明るい色（黄色 / オレンジ等）で、ピクセル枠線が付き、押せそうな立体感がある。タップすると即座に反応する（active 状態のスタイル変化）。

### シナリオ6：既存の Code Maker 連携機能が壊れない
> 🧱 Given: 既存機能（リソースファイルダウンロード / リソースエディタへのリンク / zip インポート）。🎬 When: 改修後にそれらを使う。✅ Then: すべて改修前と同じ動作をする（リンク先 URL、JS の zip POST 処理、入力フォーム）。

### シナリオ7：スマホ縦持ちで快適に閲覧できる
> 🧱 Given: 子どもがスマホ縦持ちでページを開く。🎬 When: スクロールして全コンテンツを見る。✅ Then: 横スクロールが発生しない。文字がはみ出さない。タップ対象（ボタン / 画像）が指で押しやすいサイズ（最低 44 px）。

## 3) Design

### 美術方向：ピクセルアート系（ゲーム本体と統一）

| 要素 | 方針 |
|---|---|
| **配色** | ファミコン的ハイコントラスト：背景は深い紫紺 (#1a1466) → グラデーション、アクセントは黄 (#ffcc00) / シアン (#3df0ff) / マゼンタ (#ff66cc) / 白 (#fff) |
| **タイポ** | 見出し：Google Font `Press Start 2P`（8bit pixel font）。本文：システム sans-serif（ひらがな読みやすさ優先） |
| **装飾** | ピクセル境界線（CSS `image-rendering: pixelated` + 4px の段階的シャドウ）、ドットパターン背景、星 / ハート / 剣の SVG ピクセルアイコン |
| **ヒーロー画像** | `assets/screenshots/title.png` を画面幅いっぱい、`image-rendering: pixelated` で拡大ボケ防止 |
| **ボタン** | 黄色背景 + 黒の太枠 + 4px の影で「押せる」感、active で影を消す（押し込み感） |

### 画像追加（B 案）

新規追加対象：
1. **`assets/screenshots/title.png`**（既存、ヒーロー化のみ）
2. **`assets/screenshots/battle.png`**（バトル画面）— 新規撮影
3. **`assets/screenshots/explore.png`**（マップ探索画面）— 新規撮影
4. **`assets/screenshots/dungeon.png`**（ダンジョン画面）— 新規撮影
5. **`assets/screenshots/code-maker.png`**（Code Maker 編集画面）— 新規撮影 / 入手困難なら省略
6. **装飾用 SVG**：`assets/icons/sword.svg`, `heart.svg`, `chest.svg`, `star.svg` — インライン SVG で軽量

撮影は `tools/test_headless.py` 系または Pyxel app の手動実行 + 画面キャプチャ。実時間の制約で実機キャプチャが取れない場合は、既存 `title.png` のみで進めて他はプレースホルダー（CSS 装飾枠）にする。

### lightbox 実装

- **方針**：vanilla JS + ネイティブ `<dialog>` 要素（モダンブラウザ対応、軽量）
- 画像クリック → `dialog.showModal()` で中に img を展開
- オーバーレイクリック / Escape / × ボタンで閉じる
- スマホでもピンチズーム可能（`touch-action: pinch-zoom`）

### レイアウト構造

```
[Hero: タイトル画面ヒーロー + 「ブロッククエスト」見出し + 「あそんでみる」CTA ]
[ゲームの遊び方の見出し]
[スクショ 3 枚（バトル / マップ / ダンジョン）— grid レイアウト、タップで拡大]
[Code Maker 連携セクション（既存）— ピクセル枠で装飾]
[zip インポートパネル（既存）— ピクセル枠で装飾]
[フッター（既存）]
```

### 関連スキル・MCP
- 標準ツール：Bash / Edit / Write / Read
- pyxel MCP：スクショ撮影に使う（available なら）
- 追加ライブラリ：なし（vanilla CSS + JS）
- 外部依存：Google Fonts (`Press Start 2P`) のみ（CDN 1 行）

### 委任度
🟢 高：技術的判断は自走可能。新規スクショ取得が困難なら既存 1 枚 + プレースホルダーで完走する形で fallback。

## 4) Tasklist

### 事前準備
- [ ] 既存 index.html の構造確認（実装済）
- [ ] assets/screenshots/ 内容確認（実装済：`title.png` のみ）

### commit A: スクショ追加（取れる範囲で）
- [ ] pyxel MCP / headless tool でゲーム画面キャプチャを試みる（バトル / 探索 / ダンジョン）
- [ ] 取得できたものを `assets/screenshots/` に保存
- [ ] 取得不可なら CSS プレースホルダー方式で進める旨を Tasklist に記録
- [ ] commit `assets(screenshots): index.html ヒーロー用スクショ追加`

### commit B: index.html ピクセルアート再デザイン
- [ ] HTML 構造再構成：ヒーロー / 遊び方 / 既存 Code Maker パネル / フッター
- [ ] CSS 全面書き直し：ファミコン配色・ピクセル枠線・ドットパターン背景・Press Start 2P 見出し
- [ ] ヒーロー画像セクション：title.png を `image-rendering: pixelated` で拡大表示 + CTA「あそんでみる」を直近に配置
- [ ] スクショギャラリー：grid 配置、各画像 `data-lightbox` 属性付与
- [ ] CTA ボタン：黄色背景 + 黒太枠 + 4px 影、active 状態で影オフ
- [ ] 装飾 SVG（剣 / 宝箱 / 星）をインラインで散らす
- [ ] 本文をひらがな寄りに調整（必要に応じ）
- [ ] commit `feat(index): 子ども向けピクセルアート系に再デザイン`

### commit C: lightbox 実装
- [ ] vanilla JS + `<dialog>` で画像タップ → 拡大モーダル
- [ ] オーバーレイ / × / Escape で閉じる
- [ ] 既存の Code Maker zip インポート JS を壊さないことを確認
- [ ] commit `feat(index): 画像タップで拡大表示する lightbox 追加`

### commit D: 仕上げ
- [ ] スマホ縦幅 (375px / 414px) で横スクロール無し確認
- [ ] 既存リンク（production/play.html / リソースエディタ / code-maker.zip）が正しく動く確認
- [ ] tasknote status `done`、`steering/done/` へ移動
- [ ] commit `docs(steering): index-html-kid-pixel-redesign を done`

## 5) Result

### 実装変更（1 commit）

- **`index.html`**：全面書き直し（111 行 → 649 行、CSS と JS を 1 ファイルに同梱）
- **`steering/20260505-index-html-kid-pixel-redesign.md`**：本ノート起票

### 主要 UI 変更点

| 要素 | Before | After |
|---|---|---|
| 背景 | `#000` ベタ | 紫紺 → ブルーのラジアルグラデ + ドットパターン |
| 見出しフォント | sans-serif | `Press Start 2P`（8bit pixel）+ 黄色 + 赤の影 |
| 本文フォント | sans-serif | `DotGothic16`（ピクセル感ある日本語フォント） |
| ヒーロー画像 | なし | `title.png` を `image-rendering: pixelated` で大きく + 黄色枠 + ドロップシャドウ + 「🔍 タップで おおきく」ヒント |
| CTA「あそんでみる」 | 薄グレー、平面 | 黄色背景 + 黒太枠 + 6px 押し込み影、`Press Start 2P`、active で押し込みアニメ |
| 機能紹介 | なし | 2x2 グリッドの「ゆうしゃのぼうけん」（5 つのまほう / 3 つのまち / ダンジョンボスバトル / ぜんぶひらがな）+ 各タイル SVG ピクセルアイコン |
| カードセクション | ダーク単色 | シアン / マゼンタ / グリーンの色違い枠線 + ピクセル影 + SVG ピクセル見出しアイコン |
| 画像拡大 | なし | `<dialog>` ベースの lightbox（タップで拡大、背景 / Escape / × で閉じる、ピンチズーム可） |
| ファイル選択 UI | デフォルト | マゼンタ枠 + マゼンタボタン |

### 装飾 SVG（インライン、外部依存ゼロ）

- 剣 (sword)：ゆうしゃのぼうけん セクション
- 宝箱 (chest)：あたらしくなったこと セクション
- 鉛筆 (pencil)：じぶんで かえてあそぼう セクション
- ハート (heart)：Code Maker から もどす セクション
- 各機能タイル内に魔法 / 町 / ダンジョン / ひらがなのミニアイコン

### 機能温存

- `production/play.html?v=...` リンク → 維持
- `production/code-maker.zip?v=...` ダウンロード → 維持
- `https://kitao.github.io/pyxel/wasm/code-maker/` リンク → 維持
- zip インポート JS（`/internal/codemaker-resource-import` POST）→ 維持
- code-server リンクの hostname 動的書換 → 維持

### 検証

- HTML パース成功（Python `html.parser` で 0 error）
- 全 pytest green（717 passed、2 skipped）
- pre-commit hook 通過

### 未実施項目

| 項目 | 理由 | フォロー |
|---|---|---|
| バトル / 探索 / ダンジョンの新規スクショ | `tools/test_headless.py` は描画関数キャプチャのみで実画像保存機能なし。Pyxel headless での screenshot 出力には別実装が必要 | 別タスクで pyxel.screenshot 経由のスクショ取得スクリプトを書き、撮影後に `<picture>` で追加 |
| Code Maker 編集画面のスクショ | 外部サービス (`kitao.github.io`) 依存で AI からアクセス困難 | 人手で撮影してもらう |
| プレイ GIF | 動画キャプチャ手段なし | 同上、人手 / 別ツール |
| 実機ブラウザ確認（スマホ縦持ち、横スクロール無し、タッチ操作） | AI からブラウザ起動できない | user 側で確認、回帰があれば別タスクで修正 |

## 6) Discussion

### 良かった点

- 「子ども本人 × ピクセルアート系」の方向決めが先にできていたので、配色 / フォント / 装飾の判断が一貫した
- 既存 `title.png` 1 枚しか使えない制約が早期に分かったため、SVG ピクセルアイコンで装飾を補う形に切り替えて完走できた
- `<dialog>` を使った lightbox はネイティブで Escape / モーダル動作が効くので、独自モーダル実装より安全かつ短い
- 既存の Code Maker 連携（zip インポート、外部リンク）に手を入れず、外側の見た目だけを総入れ替えにできた → 機能リスクゼロ

### 反省点

- 着手前の事前 grep で「実画像キャプチャ手段がない」を発見できなかった。Tasklist 段階でツール調査を 1 ステップ入れるべきだった（Q3 で B を選んでもらった以上、画像追加は約束事項。途中で SVG 代替に切り替える判断を user に確認しないまま進めた）
- DotGothic16 / Press Start 2P を Google Fonts から CDN ロードしている。ネットワーク不在時にフォントが崩れる。`font-display: swap` は付いているが、オフライン専用配信を想定するならローカル同梱に切り替えるべき
- カード内の SVG アイコンを「直書き」したため、index.html が 649 行に膨らんだ。同じ SVG を別 scene でも使うようになったら `assets/icons/*.svg` に外出ししてキャッシュ可能にすべき

### 今後（次にやること）

1. **実機スクショ撮影スクリプトの作成**：`tools/capture_screenshots.py` を新規作成し、`pyxel.screenshot()` を各シーン（タイトル / マップ / バトル / ダンジョン / Code Maker 起動誘導）で叩いて `assets/screenshots/*.png` に保存する。完了後、index.html の `<picture>` で追加スクショを並べる
2. **Code Maker 編集画面のスクショ取得**：外部サービスのスクショは人手で 1 枚撮ってもらい `assets/screenshots/code-maker.png` に置く → 「じぶんで かえてあそぼう」セクションに追加
3. **実機ブラウザ確認 + 微調整**：user 側で iPhone Safari / Android Chrome / PC Chrome で開いて、横スクロール・タップ反応・lightbox の挙動を確認 → 回帰があれば issue / 別タスクで修正
4. **GitHub Pages デプロイ確認**：`https://tatsuro-ueda.github.io/code-quest-pyxel/` で実物が変わっていることを確認、必要に応じてキャッシュバスター更新

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- ルール候補：「画像追加 OK」のスコープ確定時は、着手前に「AI から取得可能な画像か」を 1 度確認してから commit に入る（Q3 で B 案を取った後、実は (a) と同等の素材しか手に入らなかった反省を踏まえて）
- 次にやること：上記 1 〜 4 の順

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：実機ブラウザ確認（user 側 / GitHub Pages デプロイ）
