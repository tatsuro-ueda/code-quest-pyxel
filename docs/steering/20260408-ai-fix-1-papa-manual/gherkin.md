# 受け入れ条件: 段階1 — papa-manual（紙プロトタイプ）

> この段階は **実装ゼロ**。受け入れ条件は「子ども・パパ・既存ゲーム」の3者の振る舞いとして書く。各シナリオは `flowchart TD` 1枚 + 1行サマリー Gherkin。詳細は [`./journey.md`](./journey.md) を参照。

## プロダクト判断の合意事項

| # | 論点 | 決定 | 理由 |
|---|---|---|---|
| M1 | 実装スコープ | **実装ゼロ**。既存ゲーム＋紙＋パパの手作業のみ | 体験の核を実装の前に紙で検証する |
| M2 | パパが ＡＩ役 | パパが Claude（または他のAI）に手動で「3つの案を出して」と聞く | 自動化の前にプロンプトの感触をパパが掴む |
| M3 | 候補数 | 必ず **3つ**。1つや2つでは出さない | 「比べて選ぶ」体験を成立させるため |
| M4 | 候補の見せ方 | 紙・ノート・口頭・画面メモ など。**仮名・カタカナ主体**で書く | A5（必須UIに漢字を使わない）の練習も兼ねる |
| M5 | 候補に必ず数値を含める | 「HP1.2倍」「2倍」「5倍」など、効果量を一目で分かるように書く | 段階2以降の Q5（候補の表示）の根拠を作る |
| M6 | 「バージョン」という言葉 | 「あたらしいばーじょんだよ」「もとのばーじょんにもどそう」と意識的に使う | 子どもにこの言葉が伝わるか検証する |
| M7 | 子どもが選ぶ | 必ず子どもが選ぶ。パパが代わりに選ばない | 「子どもが主役」の体験を確認 |
| M8 | もとに戻すは無料 | 何度戻してもパパは嫌がらない／「もう一回やってみよう」と促す | 「こわしてもこわくない」の検証 |
| M9 | 観察記録 | パパは作業時間と子どもの反応を **メモする** | 段階2以降の設計の根拠データ |
| M10 | 失敗してOK | 候補のコードが動かなくても、子どもを責めない／「ＡＩがちょっとまちがえたね」で済ませる | 失敗の心理コストを低く保つ |

---

## シナリオ1：詰まった子どもがパパに頼む

> **シナリオ1**：戦闘で詰まった子ども が パパに「ボスがつよすぎる」と伝える と パパが「3つの直し方を考えて見せてあげるね」と応じる

```mermaid
flowchart TD
    S1[子どもが詰まる] --> S2["子: 『ボスがつよすぎる！』"]
    S2 --> S3["パパ: 『じゃあ3つの<br/>なおしかたを かんがえるね』"]
    S3 --> SOK[✓ 「ＡＩにたのむ」体験の入り口が成立]

    classDef child fill:#dbeafe,stroke:#1d4ed8;
    classDef papa fill:#f3e8ff,stroke:#7c3aed;
    classDef ok fill:#d4edda,stroke:#155724;
    class S1,S2 child;
    class S3 papa;
    class SOK ok;
```

---

## シナリオ2：パパが Claude に手動で頼む

> **シナリオ2**：依頼を受けたパパ が 別のデバイスで Claude に「ボスを少し弱くする3案」を聞く と 数分以内に3つの実装案を受け取れる

```mermaid
flowchart TD
    P1[パパ: スマホ/PCで Claude を開く] --> P2["『ブロッククエストのボスを<br/>少し弱くする3案を出して。<br/>HP1.2倍・2倍・5倍など<br/>段階的なバリエーションで』"]
    P2 --> P3[Claude が3案を返す]
    P3 --> P4{3案そろってる?}
    P4 -->|いいえ| P5[もう一度聞き直す]
    P5 --> P3
    P4 -->|はい| POK[✓ パパが3候補を持っている状態]

    classDef papa fill:#f3e8ff,stroke:#7c3aed;
    classDef ai fill:#fde2e2,stroke:#dc2626;
    classDef gate fill:#e2e3f1,stroke:#3949ab;
    classDef ok fill:#d4edda,stroke:#155724;
    class P1,P2,P5 papa;
    class P3 ai;
    class P4 gate;
    class POK ok;
```

---

## シナリオ3：パパが3候補を紙に書いて子どもに見せる

> **シナリオ3**：3案を持ったパパ が 仮名・カタカナ主体で **3つのカード** を書いて子どもに並べて見せる と 子どもが効果量を比べて自分で選べる

```mermaid
flowchart TD
    W1[パパ: 3つのカードを書く] --> W2["・1ばん：すこしよわい（HP1.2倍）<br/>・2ばん：ちょうどいい（HP2倍）<br/>・3ばん：すごくつよい（HP5倍）"]
    W2 --> W3[子どもの前に並べる]
    W3 --> W4[子: 3枚を見比べる]
    W4 --> W5[子: 「これにする！」]
    W5 --> WOK[✓ 「比べて選ぶ」体験が成立]

    classDef papa fill:#f3e8ff,stroke:#7c3aed;
    classDef child fill:#dbeafe,stroke:#1d4ed8;
    classDef ok fill:#d4edda,stroke:#155724;
    class W1,W2,W3 papa;
    class W4,W5 child;
    class WOK ok;
```

---

## シナリオ4：パパが手動でゲームを書き換えて見せる

> **シナリオ4**：選択を受けたパパ が `main.py` を書き換えてビルド・配信する と 子どもは「ばーじょんがかわった」体験を得られる

```mermaid
flowchart TD
    C1[子: 「2ばんがいい」] --> C2[パパ: main.pyの該当行を書き換え]
    C2 --> C3[パパ: ビルド & 配信]
    C3 --> C4[パパ: 「リロードしてね」と声をかける]
    C4 --> C5[子: ゲーム内セーブ]
    C5 --> C6[子: ブラウザリロード]
    C6 --> C7[新しいバージョンで戦闘再開]
    C7 --> COK[✓ 「ＡＩでしゅうせい」体験のフルサイクルが成立<br/>（手動だが）]

    classDef papa fill:#f3e8ff,stroke:#7c3aed;
    classDef child fill:#dbeafe,stroke:#1d4ed8;
    classDef ok fill:#d4edda,stroke:#155724;
    class C2,C3,C4 papa;
    class C1,C5,C6,C7 child;
    class COK ok;
```

---

## シナリオ5：気に入らなければ「もとにもどして」と頼める

> **シナリオ5**：新バージョンが気に入らなかった子ども が 「もとにもどして」と頼む と パパが嫌がらずに元のmain.pyに戻して再ビルドし、子どもは「こわれていない」と分かる

```mermaid
flowchart TD
    R1[子: 新バージョンを試したが微妙] --> R2["子: 『もとのにもどして』"]
    R2 --> R3["パパ: 『いいよ』と<br/>嫌がらない態度"]
    R3 --> R4[パパ: original の main.py を復元]
    R4 --> R5[パパ: ビルド & 配信]
    R5 --> R6[子: セーブ→リロード]
    R6 --> R7[もとのバージョンで遊べる]
    R7 --> ROK[✓ 「こわしてもこわくない」感覚が成立]
    ROK --> R8[「もういっかい たのもう」になる]

    classDef papa fill:#f3e8ff,stroke:#7c3aed;
    classDef child fill:#dbeafe,stroke:#1d4ed8;
    classDef ok fill:#d4edda,stroke:#155724;
    class R3,R4,R5 papa;
    class R1,R2,R6,R7,R8 child;
    class ROK ok;
```

---

## シナリオ6：「ばーじょん」という言葉が伝わるか検証

> **シナリオ6**：パパが意識して **「ばーじょん」** という言葉を使う と 子どもがその言葉を理解して使い始める／または「もっとわかりやすい言い方」を子どもの口から聞ける

```mermaid
flowchart TD
    L1["パパ: 『あたらしいばーじょんだよ』"] --> L2{子の反応は?}
    L2 -->|理解した| L3[子: 「ばーじょん」という言葉を使う]
    L2 -->|きょとん| L4[パパ: 別の言い方を試す<br/>例: 「あたらしい かたち」]
    L4 --> L5[子の反応をメモ]
    L3 --> LOK[✓ 「ばーじょん」が伝わる<br/>→ 段階2以降もこの言葉でOK]
    L5 --> LOK2[✓ より良い言葉が見つかる<br/>→ 段階2以降の文言を更新]

    classDef papa fill:#f3e8ff,stroke:#7c3aed;
    classDef child fill:#dbeafe,stroke:#1d4ed8;
    classDef gate fill:#e2e3f1,stroke:#3949ab;
    classDef ok fill:#d4edda,stroke:#155724;
    class L1,L4 papa;
    class L3,L5 child;
    class L2 gate;
    class LOK,LOK2 ok;
```

---

## シナリオ7：パパが作業時間を計測する

> **シナリオ7**：パパが 「Claudeに聞く」「main.py書き換え」「ビルド配信」「もとに戻す」 の4工程の所要時間をメモする と 段階2以降のシステム化優先順位を決めるデータが揃う

```mermaid
flowchart TD
    T1[1. Claudeに聞いて3案を得る] --> T1a[所要: ___ 分]
    T1a --> T2[2. main.pyを書き換える]
    T2 --> T2a[所要: ___ 分]
    T2a --> T3[3. ビルドして配信する]
    T3 --> T3a[所要: ___ 分]
    T3a --> T4[4. もとに戻す（必要なら）]
    T4 --> T4a[所要: ___ 分]
    T4a --> TOK[✓ 4工程の時間データが揃う<br/>→ 段階2以降の優先順位の根拠]

    classDef step fill:#f3e8ff,stroke:#7c3aed;
    classDef data fill:#fff3cd,stroke:#997404;
    classDef ok fill:#d4edda,stroke:#155724;
    class T1,T2,T3,T4 step;
    class T1a,T2a,T3a,T4a data;
    class TOK ok;
```

---

## シナリオ8：子どもの「言いたかった一言」を集める

> **シナリオ8**：1サイクル終わったあとパパが 「もしじぶんでＡＩにたのめたら、なんていう？」と聞く と 子どもの自然な言い回しが集まり、段階2の `window.prompt` の例文設計の根拠になる

```mermaid
flowchart TD
    Q1[1サイクル終了後] --> Q2["パパ: 『もしじぶんで<br/>ＡＩにたのめたら、なんていう？』"]
    Q2 --> Q3[子: 「てきをよわく」]
    Q2 --> Q4[子: 「もっとはやく うごきたい」]
    Q2 --> Q5[子: 「まほうをピンクにして」]
    Q3 --> Q6[パパ: メモする]
    Q4 --> Q6
    Q5 --> Q6
    Q6 --> QOK[✓ promptの例文設計に使える<br/>子どもの自然な言い回しコレクション]

    classDef papa fill:#f3e8ff,stroke:#7c3aed;
    classDef child fill:#dbeafe,stroke:#1d4ed8;
    classDef ok fill:#d4edda,stroke:#155724;
    class Q1,Q2,Q6 papa;
    class Q3,Q4,Q5 child;
    class QOK ok;
```

---

## この段階の完了条件

以下のすべてを満たしたら段階2へ進む：

- [ ] 少なくとも **3回** のフルサイクル（依頼→3候補→選択→反映→遊ぶ）を実施
- [ ] うち **1回以上** は「もとに戻す」を経験
- [ ] 「3つから選ぶ」が苦痛ではないことを確認
- [ ] 子どもが「**もういっかい！**」と言ったか観察
- [ ] パパが4工程の所要時間データを取った
- [ ] 子どもの自然な「一言」を **5個以上** 集めた
- [ ] 「ばーじょん」（または代替語）が伝わるか結論を出した

満たされなかった場合は **親 journey.md / gherkin.md を見直す**。段階2の実装に進む前に体験設計の問題を解決する。

---

## 関連ドキュメント

- [`./journey.md`](./journey.md) — この段階のジャーニー詳細
- [親 journey.md](../20260408-ai-fix-from-browser/journey.md) — 全体ビジョン
- [親 gherkin.md](../20260408-ai-fix-from-browser/gherkin.md) — 5段階マップ
- 後続: [`../20260408-ai-fix-2-system-suggests/`](../20260408-ai-fix-2-system-suggests/) — 段階2（後日作成）
