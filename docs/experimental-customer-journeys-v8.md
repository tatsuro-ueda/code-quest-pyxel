# 実験案 v8：カスタマージャーニー ── 教育哲学軸

> 実験ラベル：**v8 / 教育哲学軸**
> 作成日：2026-04-25
> 視点：各ジャーニーが、**4 つの教育哲学**（Constructionism / SDT / PBL / モンテッソーリ）の**どの瞬間を体現しているか**を明示する。同じジャーニーが複数の哲学的瞬間を貫いて起きていることを示す。
> 根拠：[`experimental-customer-jobs-v8.md`](./experimental-customer-jobs-v8.md)

---

## 凡例（v8 固有）

- 各ノードに教育哲学のラベルを **`[C]` Constructionism / `[A]` Autonomy / `[CO]` Competence / `[R]` Relatedness / `[PBL]` Project / `[M]` モンテッソーリ** で付ける
- ノード形式：`[（主体）絵文字 文 [哲学ラベル]（タッチポイント）]`
- ジャーニー末尾に「**この瞬間に活性化した教育哲学**」サマリー

---

## 代表ジャーニー：教育哲学的に厚いもの 7 本

---

### CJ01-v8: はじめてのタイル配置（Constructionism の入り口）

**教育哲学的意味**：Papert の "child programs the computer" の現代版。リソースエディターは Logo の精神的後継。

```mermaid
flowchart LR
    subgraph Before["Before: instructionism 的"]
        B1[（子）❓「マップ変えたい」（ゲーム中）]
        B1 --> B2[（親）💦コードを子に説明する [反 C]（コードエディタ）]
        B2 --> B3[（子）❌教えられる側になる [反 A]（対面）]
    end
    subgraph After["After: constructionism 的"]
        A1[（子）💡「マップ変えたい」（ゲーム中）]
        A1 --> A2[（子）👆タイルを直接配置 [C: 子がコンピュータをプログラム]（リソースエディター）]
        A2 --> A3[（子）👀Run → 反映を見る [CO: 達成感]（ゲーム中）]
        A3 --> A4[（子）❤️「できた！」 [A: 自分でやった][CO: できた]（対面）]
    end
```

> **活性化した教育哲学**：[C] 構成主義（直接ものづくり）、[A] 自律性、[CO] 有能感

---

### CJ08-v8: 敵が強すぎる（SDT の Autonomy が試される瞬間）

**教育哲学的意味**：「親が直す」だと SDT の Autonomy が侵食される。承認キューによって Autonomy を回復させる構造。

```mermaid
flowchart LR
    subgraph Phase1["Phase 1: 子の問題提起"]
        A1[（子）💢「敵強すぎ！」 [PBL: 子が問題を発見]（ゲーム中）]
    end
    subgraph Phase2["Phase 2: 親(媒介者) の関与"]
        A2[（親）👆AIに翻訳 [C: 媒介者ロール]（AI入力画面）]
    end
    subgraph Phase3["Phase 3: 子の自律的判断"]
        A3[（ビルド）👀検証通過（ビルドログ）]
        A3 --> A4[（子）👀開発版／本番を遊び比べ [A: 体感での判断][M: 自己訂正]（ゲーム中）]
        A4 --> A5[（子）❤️承認 [A: 自分で決めた][CO: できた]（選択ページ）]
    end

    A1 --> A2
    A2 --> A3
```

> **活性化した教育哲学**：[A] 自律性、[CO] 有能感、[C] 媒介者、[M] 自己訂正、[PBL] 問題発見

---

### CJ22-v8: 友達のフィードバックを反映する（PBL の真正性）

**教育哲学的意味**：PBL の「真正性のあるプロジェクト」「公開された成果物」「学習者主導」が同時に作動する。

```mermaid
flowchart LR
    subgraph Authentic["真正性"]
        A1[（友達）💡スマホで遊んで「ここ難しい」 [PBL: 真正性ある反応]（スマホブラウザ）]
    end
    subgraph LearnerLed["学習者主導"]
        A2[（子）👆「直して！」と判断 [PBL: 学習者主導][A: 自律性]（対面）]
    end
    subgraph Mediator["媒介者"]
        A3[（親）👆AIに翻訳 [C: 媒介者]（AI入力画面）]
        A3 --> A4[（ビルド）👀検証通過（ビルドログ）]
    end
    subgraph Public["公開された成果物"]
        A5[（子）👆URL 再送 [PBL: 公開][R: 友達と繋がる]（LINE）]
        A5 --> A6[（友達）❤️「いい感じ！」 [R: 関係性][CO: 認められた]（スマホブラウザ）]
    end

    A1 --> A2
    A2 --> A3
    A4 --> A5
```

> **活性化した教育哲学**：[PBL] 真正性・学習者主導・公開、[A] 自律性、[C] 媒介者、[R] 関係性、[CO] 有能感

---

### CJ31-v8: 子どもが変更を承認する（SDT 3 欲求が同時に作動）

**教育哲学的意味**：Autonomy・Competence・Relatedness の 3 欲求がこのジャーニーで完備される。

```mermaid
flowchart TD
    A1[（親）👆AIに依頼 → 開発版に反映 [C: 媒介者]（承認キュー）]
    A1 --> A2[（子）👀開発版で 2 かい たおせる [CO: できた]（ゲーム中）]
    A2 --> A3[（子）👀本番で 4 かい かかる [M: 自己訂正]（ゲーム中）]
    A3 --> A4[（子）❤️「開発版のほう！」承認 [A: 自分で決めた]（選択ページ）]
    A4 --> A5[（家族）❤️判断が尊重される関係 [R: 関係性]（対面）]

    classDef autonomy fill:#fff3cd,stroke:#856404,color:#000000;
    classDef competence fill:#d4edda,stroke:#155724,color:#000000;
    classDef relatedness fill:#d1ecf1,stroke:#0c5460,color:#000000;

    class A4 autonomy;
    class A2 competence;
    class A5 relatedness;
```

> **活性化した教育哲学**：[A] 自律性、[CO] 有能感、[R] 関係性が同時作動。SDT 3 欲求の理想形。

---

### CJ20-v8: 演出 ON/OFF で違いを体験する（モンテッソーリ的「不介入の介入」）

**教育哲学的意味**：親が「教えず」「環境を準備する」だけで、子が自分で気づく構造。モンテッソーリの真髄。

```mermaid
flowchart LR
    subgraph Setup["環境を準備"]
        A1[（親）💡演出を口で説明しない [反 instructionism] [M: 不介入の介入]（対面）]
        A1 --> A2[（親）👆ON/OFF 切替を提示 [M: 準備された環境]（プロダクト）]
    end
    subgraph SelfDiscovery["自己発見"]
        A3[（子）👆OFF で遊ぶ → 寂しい [M: 自己訂正]（ゲーム中）]
        A3 --> A4[（子）👆ON に戻る → 違いに気づく [CO: 有能感]（ゲーム中）]
        A4 --> A5[（子）💡「演出って大事なんだ」と自分で発見 [C: 自分で構成]（対面）]
    end

    A2 --> A3
```

> **活性化した教育哲学**：[M] 不介入の介入・準備された環境・自己訂正、[C] 自己構成、[CO] 有能感

---

### CJ26-v8:「自分たちのゲーム」（家族版 SDT）

**教育哲学的意味**：個人の SDT を家族集団に拡張した姿。家族の Autonomy / Competence / Relatedness が同時に育つ。

```mermaid
flowchart TD
    A1[（家族）👆改造を重ねてオリジナル比率が半分超え [PBL: 過程][C: 構成]（履歴UI）]
    A1 --> A2[（家族）👆Code Maker で見た目・音まで触る [C: 直接ものづくり]（Pyxel Code Maker）]
    A2 --> A3[（家族）❤️「ぼくたちのゲーム」 [家族の A: 自分たちで決めた][家族の CO: 完成させた][家族の R: 一緒に作った]（対面）]

    classDef family fill:#ffd700,stroke:#856404,color:#000000;
    class A3 family;
```

> **活性化した教育哲学**：家族版 SDT 3 欲求の同時充足。Papert の powerful ideas に「家族で」触れる。

---

### CJ30-v8: エンディングを書く（PBL の完成形 + Papert の理想）

**教育哲学的意味**：PBL の「最終産物」と Papert の「powerful ideas を作品に込める」が一致する瞬間。

```mermaid
flowchart LR
    subgraph Process["過程"]
        A1[（家族）👆半年の積み重ね [PBL: 過程の評価]（履歴UI）]
    end
    subgraph Production["作品創造"]
        A2[（家族）👆セリフを考案 → AIが実装 [C: 媒介者][PBL: 真正性]（AI入力画面）]
        A2 --> A3[（家族）👆クレジットに子の名前 [PBL: オーナーシップ]（クレジット）]
    end
    subgraph Public["公開"]
        A4[（子）👆Run → エンディング到達 [CO: 完成]（ゲーム中）]
        A4 --> A5[（家族）❤️「ぼくたちが作った」 [家族版 A][家族版 CO][家族版 R]（対面）]
    end

    A1 --> A2
    A3 --> A4
```

> **活性化した教育哲学**：[PBL] 過程・真正性・オーナーシップ、[C] powerful ideas を作品化、家族版 SDT 充足

---

## 教育哲学的な「禁忌ジャーニー」（やってはいけない設計）

### 禁忌 1：教師化ジャーニー（v8 が拒否する）

```mermaid
flowchart LR
    subgraph Forbidden["禁忌：これをやらない"]
        F1[（プロダクト）❌「今日学んだ概念」を子に振り返らせる [反 SDT]（教育UI）]
        F1 --> F2[（プロダクト）❌「次に学ぶべき」を提案する [反 M: 介入]（教育UI）]
        F2 --> F3[（子）❌教えられる側になる [反 C]（対面）]
    end
```

> **アンチパターンとしての価値**：v6 のアンチジョブ AJ1 を教育哲学的に正当化する。

---

## このバージョンを採用するときに変わること

- ジャーニーに**教育哲学ラベル**が付く（マルチ・ラベル）
- 設計ガイドラインが「**この設計はどの哲学を活性化させるか／侵食するか**」で評価される
- マーケティング・教育機関向け資料が**学術的言語**で書ける
- 開発チームに「教育哲学リード」役割が誕生する可能性
- v6 アンチジョブが「SDT 外発的動機防止」「Papert 反 instructionism」として理論武装される
- 学校・教育機関・教育系投資家との対話が共通語彙で可能に

---

## 哲学ラベルの全ジャーニー集計

| 哲学 | 主に活性化するジャーニー |
|---|---|
| [C] Constructionism | CJ01-CJ07, CJ23-CJ24, CJ26（直接ものづくり） |
| [A] Autonomy | CJ31-CJ34（承認）、CJ22（friend feedback judge） |
| [CO] Competence | CJ08-CJ14（直る達成感）、CJ30, CJ42（完成） |
| [R] Relatedness | CJ21, CJ22, CJ25, CJ26（家族・友達） |
| [PBL] Project | CJ22, CJ30, CJ42, CJ43（真正性・公開） |
| [M] モンテッソーリ | CJ20（不介入の介入）、Phase 0/Phase 2（敏感期） |

**活性化数の多いジャーニーは「教育哲学的に厚い」ジャーニー**＝マーケティングで前面に出すべきジャーニー。

---

## 参照
- [`experimental-customer-jobs-v8.md`](./experimental-customer-jobs-v8.md)
- 関連文献：Papert, S. (1980) *Mindstorms* / Deci & Ryan (1985) *Intrinsic Motivation* / Maria Montessori 各著作
