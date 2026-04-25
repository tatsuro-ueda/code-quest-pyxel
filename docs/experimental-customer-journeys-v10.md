# 実験案 v10：カスタマージャーニー ── v1 × v2 ハイブリッド

> 実験ラベル：**v10 / v1 × v2 ハイブリッド**
> 作成日：2026-04-25
> 視点：Before に**競合プロダクトでの人格別欠落**を 2-3 個並列、After に**CQP での人格遷移**で描く。「競合では人格 X が起動しない／置換される → CQP では人格 X が**この遷移の中で**生きる」を可視化する。
> 根拠：[`experimental-customer-jobs-v10.md`](./experimental-customer-jobs-v10.md)

---

## 凡例（v10 固有）

- **subgraph 構造**：
  - `Before-A` `Before-B`：競合プロダクトでの体験（その人格に何が起きるか）
  - `After`：CQP での人格遷移（人格ごとに色分け）
- ノード形式：`[（人格）絵文字 文（タッチポイント）]`
- 人格カラー：`子=黄` / `親=青` / `友達=赤` / `ビルド/AI=灰`
- 各ジャーニー末尾に「**この瞬間の人格 × 競合差別化**」を 1 行

---

## 代表ジャーニー 8 本（v1×v2 ハイブリッド版）

---

### CJ08-v10: 敵が強すぎる（人格遷移 × 競合欠落）

**主役の人格遷移**：`子(プレイヤー) → 親(観察者) → 親(翻訳者) → 親(セーフティネット) → 子(批評家) → 子(プレイヤー)`
**競合の欠落構造**：Scratch では子(プレイヤー)が直したいと思っても親の翻訳がない／Roblox/RPG Maker では親(翻訳者)が「先生」化する／vibe coding では親(セーフティネット)が機構化されていない

```mermaid
flowchart LR
    subgraph BeforeA["Before-A: Scratch"]
        BA1[子(プレイヤー)<br/>💢「敵強すぎ！」（Scratch プロジェクト）]
        BA1 --> BA2[子(クリエイター)<br/>💦HP 変数を独力で書き換え（Scratch エディタ）]
        BA2 --> BA3[子(批評家)<br/>❌親の翻訳・観察・セーフティネットがない（対面）]
    end
    subgraph BeforeB["Before-B: vibe coding 単体"]
        BB1[子(プレイヤー)<br/>💢「敵強すぎ！」（ゲーム中）]
        BB1 --> BB2[親<br/>👆AI に直接依頼（AI入力画面）]
        BB2 --> BB3[子(プレイヤー)<br/>❌壊れた版が届いて集中が切れる（ゲーム中）]
    end
    subgraph After["After: CQP の人格リレー"]
        P1[子(プレイヤー)<br/>💢「敵強すぎ！」（ゲーム中）]
        P1 --> P2[親(観察者)<br/>👀今日の集中度を見て受け止める（対面）]
        P2 --> P3[親(翻訳者)<br/>👆AI に「HP 50→30」（AI入力画面）]
        P3 --> P4[親(セーフティネット)<br/>👀ヘッドレス検証通過 → 開発版反映（承認キュー）]
        P4 --> P5[子(批評家)<br/>👀開発版で 2 かい／本番で 4 かい体感差（ゲーム中）]
        P5 --> P6[子(批評家)<br/>❤️「開発版のほう！」承認（選択ページ）]
        P6 --> P7[子(プレイヤー)<br/>❤️続きを楽しめる（ゲーム中）]
    end

    classDef child fill:#fff3cd,stroke:#856404,color:#000000;
    classDef parent fill:#d1ecf1,stroke:#0c5460,color:#000000;
    classDef bad fill:#f8d7da,stroke:#721c24,color:#000000;

    class P1,P5,P6,P7 child;
    class P2,P3,P4 parent;
    class BA1,BA2,BA3,BB1,BB3 child;
    class BB2 parent;
```

> **この瞬間の人格 × 競合差別化**：Scratch では親(観察者)・親(翻訳者)・親(セーフティネット) が**3 つとも欠落**。vibe coding では親(セーフティネット) が**機構化されていない**。CQP では 3 つの親人格が**この順序で**作動して、子(プレイヤー)→子(批評家)→子(プレイヤー) の人格往復を支える。

---

### CJ31-v10: 子どもが変更を承認する

**主役の人格遷移**：`親(翻訳者) → 親(セーフティネット) → 子(批評家)（×複数）→ 子(プレイヤー)`
**競合の欠落構造**：Scratch では親が触れない／RPG Maker では親が直接編集して子(批評家) が外部化される／vibe coding では AI のおすすめが子(批評家) を置換する

```mermaid
flowchart LR
    subgraph BeforeA["Before-A: RPG Maker（親が直接編集）"]
        BA1[親<br/>👆データベースで HP 50→30（RPG Maker）]
        BA1 --> BA2[子<br/>❓「30 ってどのくらい？」（対面）]
        BA2 --> BA3[親<br/>❌「弱くなるってことだよ」と説明 → 子は親の理屈で決める（対面）]
    end
    subgraph BeforeB["Before-B: vibe coding（AI が判断者）"]
        BB1[親<br/>👆AI に「最適な HP に」（AI入力画面）]
        BB1 --> BB2[AI<br/>👆「推奨：HP=35」（AI出力画面）]
        BB2 --> BB3[子<br/>❌AI のおすすめを選ぶ → 自分で決めた感覚なし（対面）]
    end
    subgraph After["After: CQP の批評家中心ジャーニー"]
        A1[親(翻訳者)<br/>👆AI に依頼 → 開発版反映（承認キュー）]
        A1 --> A2[親(セーフティネット)<br/>👀ビルド検証通過（ビルドログ）]
        A2 --> A3[子(批評家)<br/>👀開発版で HP=30 → 2 かいで たおせる（ゲーム中）]
        A3 --> A4[子(批評家)<br/>👀本番で HP=50 → 4 かい かかる（ゲーム中）]
        A4 --> A5[子(批評家)<br/>❤️体感差で「開発版のほう！」（選択ページ）]
        A5 --> A6[子(プレイヤー)<br/>❤️新バランスで遊び続ける（ゲーム中）]
    end

    classDef child fill:#fff3cd,stroke:#856404,color:#000000;
    classDef parent fill:#d1ecf1,stroke:#0c5460,color:#000000;
    classDef ai fill:#e2e3f1,stroke:#3949ab,color:#000000;

    class A3,A4,A5,A6 child;
    class A1,A2 parent;
    class BA2,BA3,BB3 child;
    class BA1,BB1 parent;
    class BB2 ai;
```

> **この瞬間の人格 × 競合差別化**：競合のどれも**子(批評家) が体感で判断する経路**を持たない。RPG Maker は親の理屈、vibe coding は AI の推奨が judge を置き換える。CQP では子(批評家) が**遊び比べて二度判断**できる。

---

### CJ22-v10: 友達のフィードバックを反映する

**主役の人格遷移**：`友達 → 子(社会人) → 親(観察者) → 子(社会人) → 親(翻訳者) → 親(セーフティネット) → 子(批評家) → 子(社会人) → 友達`
**競合の欠落構造**：Scratch ではコメント文化で友達がスマホで来ない／Roblox は社会圧で家族の枠が壊れる／自前配信は反映が数日遅れる

```mermaid
flowchart LR
    subgraph BeforeA["Before-A: Scratch"]
        BA1[友達<br/>💡コメント欄に「ここ難しい」（Scratch サイト）]
        BA1 --> BA2[子(クリエイター)<br/>👆ブロック書き換え（Scratch エディタ）]
        BA2 --> BA3[友達<br/>❌PC 前提で再アクセスしない（対面）]
    end
    subgraph BeforeB["Before-B: 自前配信ゲーム"]
        BB1[友達<br/>💡対面で「ここ難しい」（対面）]
        BB1 --> BB2[親<br/>💦数日後に修正 → zip 再送（コードエディタ）]
        BB2 --> BB3[友達<br/>❌もう熱が冷めている（対面）]
    end
    subgraph After["After: CQP の友達ループ × 人格リレー"]
        F1[友達<br/>💡「ここ難しい」（スマホブラウザ）]
        F1 --> S1[子(社会人)<br/>👂受け止める（対面）]
        S1 --> O1[親(観察者)<br/>👀子の状態を察する（対面）]
        O1 --> S2[子(社会人)<br/>👆「パパ直して！」と判断（対面）]
        S2 --> T1[親(翻訳者)<br/>👆AI に翻訳（AI入力画面）]
        T1 --> N1[親(セーフティネット)<br/>👀検証通過 → 開発版（承認キュー）]
        N1 --> C1[子(批評家)<br/>👀遊び比べて承認（選択ページ）]
        C1 --> S3[子(社会人)<br/>👆URL 再送（LINE）]
        S3 --> F2[友達<br/>❤️「お、いい感じ！」（スマホブラウザ）]
    end

    classDef child fill:#fff3cd,stroke:#856404,color:#000000;
    classDef parent fill:#d1ecf1,stroke:#0c5460,color:#000000;
    classDef friend fill:#f8d7da,stroke:#721c24,color:#000000;

    class S1,S2,S3,C1 child;
    class O1,T1,N1 parent;
    class F1,F2 friend;
    class BA1,BB1,BA3,BB3 friend;
    class BA2 child;
    class BB2 parent;
```

> **この瞬間の人格 × 競合差別化**：Scratch は友達が PC でしか来られない／自前配信は反映の遅れで友達が消える。CQP では**9 人格を経由するリレー**が**数分のうちに**完結する。子(社会人) が起点と終点に二度立つ点が独自。

---

### CJ01-v10: はじめてのタイル配置

**主役の人格遷移**：`子(クリエイター) → 子(プレイヤー) → 子(社会人 or 親(観察者))`
**競合の欠落構造**：Scratch では子(クリエイター)は触れるが親の関与が立たない／Roblox は子(クリエイター)が Lua の壁にあたる／親が main.py を直すパターンでは子(クリエイター)が起動しない

```mermaid
flowchart LR
    subgraph BeforeA["Before-A: Roblox Studio"]
        BA1[子(クリエイター)<br/>💡「マップ変えたい」（Roblox Studio）]
        BA1 --> BA2[子(クリエイター)<br/>💦Lua とパーツの壁（Roblox Studio）]
        BA2 --> BA3[子(クリエイター)<br/>❌80% 未完成の壁にぶつかる（Roblox Studio）]
    end
    subgraph BeforeB["Before-B: 親が main.py を直す"]
        BB1[子<br/>💡「マップ変えたい」（ゲーム中）]
        BB1 --> BB2[親<br/>💦ソースコードを書き換える（コードエディタ）]
        BB2 --> BB3[子<br/>❌見てるだけ → 子(クリエイター)が起動しない（対面）]
    end
    subgraph After["After: CQP のクリエイター人格起動"]
        A1[子(クリエイター)<br/>💡「マップ変えたい」（ゲーム中）]
        A1 --> A2[子(クリエイター)<br/>👆タイルを直接配置（リソースエディター）]
        A2 --> A3[子(プレイヤー)<br/>👀Run → キャラがその場所を歩く（ゲーム中）]
        A3 --> A4[子(社会人)<br/>❤️「できた！見てみて！」親(観察者)に披露（対面）]
    end

    classDef child fill:#fff3cd,stroke:#856404,color:#000000;
    classDef parent fill:#d1ecf1,stroke:#0c5460,color:#000000;

    class A1,A2,A3,A4 child;
    class BA1,BA2,BA3,BB1,BB3 child;
    class BB2 parent;
```

> **この瞬間の人格 × 競合差別化**：Roblox は子(クリエイター)を起動するが**完成までいかない**。親が main.py を直す場合は**子(クリエイター)が初動から起動しない**。CQP では子(クリエイター)→子(プレイヤー)→子(社会人) の**人格 3 連発**が数十秒で起きる。

---

### CJ26-v10:「自分たちのゲーム」と言えるようになる

**主役の人格遷移**：`子(クリエイター) ↔ 親(翻訳者) ×複数 → 親(観察者) → 子(社会人) → 子(プレイヤー)`
**競合の欠落構造**：Scratch は表層がスクラッチ感／SMM2 はマリオ感／vibe coding は「親と AI が作ったやつ」感

```mermaid
flowchart LR
    subgraph BeforeA["Before-A: SMM2"]
        BA1[子(クリエイター)<br/>👆コースを作る（SMM2）]
        BA1 --> BA2[友達<br/>❓「マリオのコースね」とカテゴライズ（対面）]
        BA2 --> BA3[子(社会人)<br/>❌「自分たちのゲーム」とは言いにくい（対面）]
    end
    subgraph BeforeB["Before-B: vibe coding"]
        BB1[親<br/>👆AI に「RPG 作って」（AI入力画面）]
        BB1 --> BB2[AI<br/>👆全部生成（コードエディタ）]
        BB2 --> BB3[子<br/>❌「親と AI が作ったやつ」感（対面）]
    end
    subgraph After["After: CQP のオリジナル積層"]
        A1[子(クリエイター)<br/>👆Tilemap でマップを書き換え（リソースエディター）]
        A1 --> A2[親(翻訳者)<br/>👆AI に「敵やセリフ追加」（AI入力画面）]
        A2 --> A3[子(クリエイター)<br/>👆Sprite/Sound を Code Maker で触る（Pyxel Code Maker）]
        A3 --> A4[親(翻訳者)<br/>👆AI に「BGM 取り込み」（AI入力画面）]
        A4 --> A5[親(観察者)<br/>👀オリジナル比率が半分超え（履歴UI）]
        A5 --> A6[子(社会人)<br/>👆「友達に見せたい！」（対面）]
        A6 --> A7[子(プレイヤー)<br/>❤️Run →「ぼくたちのゲーム」（ゲーム中）]
    end

    classDef child fill:#fff3cd,stroke:#856404,color:#000000;
    classDef parent fill:#d1ecf1,stroke:#0c5460,color:#000000;
    classDef ai fill:#e2e3f1,stroke:#3949ab,color:#000000;

    class A1,A3,A6,A7 child;
    class A2,A4,A5 parent;
    class BA1,BA3,BB3 child;
    class BB1 parent;
    class BB2 ai;
```

> **この瞬間の人格 × 競合差別化**：SMM2 は表層を変えられないので子(社会人) が「自分たちのゲーム」と言いにくい。vibe coding は子(クリエイター) が AI に置換される。CQP は子(クリエイター)↔親(翻訳者) の**往復**で表層・中身ともに親子の手が入る。

---

### CJ35-v10: AI で修正したらエラーが出て動かない

**主役の人格遷移**：`子(プレイヤー) → 親(翻訳者) → 親(セーフティネット)（強烈に作動）→ 子(プレイヤー)`
**競合の欠落構造**：vibe coding 単体／RPG Maker のプラグイン／Roblox Lua のいずれもセーフティネット人格を**機構化していない**

```mermaid
flowchart LR
    subgraph BeforeA["Before-A: vibe coding 単体"]
        BA1[子(プレイヤー)<br/>💢「新しい技ほしい！」（対面）]
        BA1 --> BA2[親<br/>👆AI に依頼（AI入力画面）]
        BA2 --> BA3[子(プレイヤー)<br/>❌Run → 黒い画面 → 集中が切れる（ゲーム中）]
    end
    subgraph BeforeB["Before-B: Roblox Lua"]
        BB1[親<br/>👆Lua を修正（Roblox Studio）]
        BB1 --> BB2[テスト弱い<br/>💦不安定なまま公開（Roblox）]
        BB2 --> BB3[子(プレイヤー)<br/>❌Roblox 上でクラッシュ（Roblox）]
    end
    subgraph After["After: CQP のセーフティネット人格作動"]
        A1[子(プレイヤー)<br/>💡「新しい技ほしい！」（対面）]
        A1 --> A2[親(翻訳者)<br/>👆AI に依頼（AI入力画面）]
        A2 --> A3[親(セーフティネット)<br/>👀ヘッドレス検証 NG → 開発版を出さず親にエラー要約（ビルドログ）]
        A3 --> A4[親(翻訳者)<br/>👆AI に再依頼（AI入力画面）]
        A4 --> A5[親(セーフティネット)<br/>👆OK → 開発版カードに反映（選択ページ）]
        A5 --> A6[子(プレイヤー)<br/>❤️常に動くゲームだけが届く（ゲーム中）]
    end

    classDef child fill:#fff3cd,stroke:#856404,color:#000000;
    classDef parent fill:#d1ecf1,stroke:#0c5460,color:#000000;

    class A1,A6 child;
    class A2,A3,A4,A5 parent;
    class BA1,BA3,BB3 child;
    class BA2,BB1,BB2 parent;
```

> **この瞬間の人格 × 競合差別化**：vibe coding/Roblox いずれも**親(セーフティネット) を機構化していない**ため、壊れた版が子(プレイヤー) に届く。CQP のヘッドレス検証＋承認キューが**親(セーフティネット) を機構化した世界唯一の構造**。

---

### CJ43-v10: 実公開で遊ばれた記録が見える

**主役の人格遷移**：`子(社会人) → 友達 → 親(観察者)`
**競合の欠落構造**：Scratch のビュー数は誰が遊んだか不明／Roblox 統計はプラットフォーム指標で家族の判断に使えない／自前配信は記録なし

```mermaid
flowchart LR
    subgraph BeforeA["Before-A: Scratch"]
        BA1[親<br/>👀Scratch のプロジェクト View 数（Scratch サイト）]
        BA1 --> BA2[親(観察者)<br/>❓誰が遊んだか不明 → 勘で判断（対面）]
    end
    subgraph BeforeB["Before-B: Roblox"]
        BB1[親<br/>👀Roblox 統計（Roblox Studio）]
        BB1 --> BB2[親(観察者)<br/>❓Roblox 指標は家族の判断に直結しない（対面）]
    end
    subgraph BeforeC["Before-C: 自前配信"]
        BC1[親<br/>👆URL を送る（LINE）]
        BC1 --> BC2[親(観察者)<br/>❌アクセス記録なし → 勘で判断（対面）]
    end
    subgraph After["After: CQP の実公開ログ × 観察者人格"]
        A1[子(社会人)<br/>👆URL を送る（LINE）]
        A1 --> A2[友達<br/>👆実公開 URL を開いて遊ぶ（スマホブラウザ）]
        A2 --> A3[親(観察者)<br/>👀日別・ページ別ログを確認（実公開アクセスログ）]
        A3 --> A4[親(観察者)<br/>❤️遊ばれていれば嬉しい／届かなければ公開経路を見直す（対面）]
    end

    classDef child fill:#fff3cd,stroke:#856404,color:#000000;
    classDef parent fill:#d1ecf1,stroke:#0c5460,color:#000000;
    classDef friend fill:#f8d7da,stroke:#721c24,color:#000000;

    class A1 child;
    class A3,A4 parent;
    class A2 friend;
    class BA2,BB2,BC2 parent;
    class BA1,BB1,BC1 parent;
```

> **この瞬間の人格 × 競合差別化**：競合のどこにも**親(観察者) のための家族意思決定ダッシュボード**がない。Scratch/Roblox は別の指標（プラットフォーム軸）。CQP の実公開ログは**親(観察者) のための事実情報**として設計されている。

---

### CJ34-v10: 承認したあとに「やっぱり」となる

**主役の人格遷移**：`子(批評家) → 子(プレイヤー) → 子(批評家)（再判断）→ 親(翻訳者) → 子(批評家)`
**競合の欠落構造**：Scratch/Roblox/RPG Maker のいずれも「**戻す権利**」を機構化していない

```mermaid
flowchart LR
    subgraph BeforeA["Before-A: Scratch（自分のブロックを巻き戻し）"]
        BA1[子(クリエイター)<br/>👆ブロックを書き戻す（Scratch エディタ）]
        BA1 --> BA2[子(批評家)<br/>❓元の状態が分からない（Scratch エディタ）]
    end
    subgraph BeforeB["Before-B: 親管理ゲーム"]
        BB1[子<br/>❓「やっぱり前のがよかった」（対面）]
        BB1 --> BB2[親<br/>💦戻し方を考える → 結局親が決める（コードエディタ）]
    end
    subgraph After["After: CQP の戻す権利"]
        A1[子(批評家)<br/>👆HP=30 を承認（選択ページ）]
        A1 --> A2[子(プレイヤー)<br/>👆しばらく遊ぶ（ゲーム中）]
        A2 --> A3[子(批評家)<br/>💡「やっぱり前のがよかった！」（対面）]
        A3 --> A4[親(翻訳者)<br/>👆「もどして」依頼を承認キューに（承認キュー）]
        A4 --> A5[子(批評家)<br/>❤️自分で承認して戻る（選択ページ）]
    end

    classDef child fill:#fff3cd,stroke:#856404,color:#000000;
    classDef parent fill:#d1ecf1,stroke:#0c5460,color:#000000;

    class A1,A2,A3,A5 child;
    class A4 parent;
    class BA1,BA2,BB1 child;
    class BB2 parent;
```

> **この瞬間の人格 × 競合差別化**：競合では「戻す」が**子(批評家) の権利として機構化されていない**。Scratch でも親管理ゲームでも、戻す行為は**子の自己効力感を伴わない**。CQP は子(批評家) が**二度判断する権利**を承認キューで保証する。

---

## 全 42 ジャーニーへの適用テンプレ

各ジャーニーで：

1. **主役の人格遷移**：3-5 個の人格をリスト
2. **競合の欠落構造**：1-3 個の競合で、どの人格がどう失敗するかを 1 行ずつ
3. **Before-A / Before-B**：2 つの競合体験を mermaid で（人格カラーで色分け）
4. **After**：CQP の人格遷移 mermaid（人格カラーで色分け）
5. **末尾コメント**：「この瞬間の人格 × 競合差別化」1 行

---

## このバージョンを採用するときに変わること

- 全 42 ジャーニーが**競合並列 × 人格遷移**の構造で書き直される
- 一覧表に「**主要人格**」「**競合の欠落**」の 2 列が追加
- マーケティング・コピーが**8 人格 × 主要競合**のマトリクスから書き出せる
- プロダクト・ロードマップが「**この人格を競合に対して立たせる**」観点で優先順位付け
- 親(観察者) ダッシュボードの設計が「**競合では監視寄りなものを観察に留める**」原則で進む
- セーフティネット機構（CJ35-CJ41）が「**競合のどこにもない世界唯一の機構**」として再ポジション

---

## 参照
- [`experimental-customer-jobs-v10.md`](./experimental-customer-jobs-v10.md)
- 元実験：[`experimental-customer-journeys-v1.md`](./experimental-customer-journeys-v1.md), [`experimental-customer-journeys-v2.md`](./experimental-customer-journeys-v2.md)
