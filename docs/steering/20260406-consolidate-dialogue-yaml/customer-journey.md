# Customer Journey Map: `assets/dialogue.yaml` 集約

この文書は、**「ゲーム内のすべての会話を `assets/dialogue.yaml` に集約し、他のファイルから消したい」** というカスタマー（あなた）の体験を整理したジャーニーマップである。

## 1. カスタマー像

- 役割: このゲームの作者
- 目的: セリフを迷わず直せる状態にしたい
- 不満: 会話が `assets/dialogue.yaml` と `main.py` などに散っていて、直す場所が毎回変わる
- 成功条件: 「会話を直す = `assets/dialogue.yaml` を開く」で済む

## 2. 現在のジャーニー

```mermaid
flowchart TD
    A[会話を1つ直したいと思う] --> B[まず assets/dialogue.yaml を開く]
    B --> C{そこに目的のセリフがあるか}
    C -->|ある| D[編集できる]
    C -->|ない| E[main.py を検索する]
    E --> F{battle_text や show_message にあるか}
    F -->|ある| G[コードの中の文字列を直す]
    F -->|ない| H[docs を読む]
    H --> I[story-design / playthrough で正解を探す]
    I --> J[どれが実際の表示元か迷う]
    G --> K[他にも同じ文が残っていないか不安になる]
    J --> K
    D --> K
    K --> L[修正後も repo 全体を grep したくなる]
    L --> M[1行直すだけなのに疲れる]
```

## 3. 現在の感情の流れ

```mermaid
flowchart TD
    A[開始時: よし直そう] --> B[assets/dialogue.yaml に無い]
    B --> C[あれ? まだ main.py に残っている]
    C --> D[どれが本物の表示元か分からない]
    D --> E[直しても消し漏れが怖い]
    E --> F[修正そのものより探索の方が重い]
    F --> G[会話編集のたびに気分が重くなる]
```

## 4. カスタマーが本当に欲しい体験

```mermaid
flowchart TD
    A[会話を直したい] --> B[assets/dialogue.yaml を開く]
    B --> C[scene 名で検索する]
    C --> D[本文を直す]
    D --> E[ゲームを確認する]
    E --> F[終わり]
```

- 探す場所が 1 つ
- 消す場所も 1 つ
- 正解の原本も 1 つ
- 「この文、別の場所にもあるかも」という不安がない

## 5. 理想ジャーニー

```mermaid
flowchart TD
    A[会話を1つ直したい] --> B[assets/dialogue.yaml を開く]
    B --> C[scene 一覧から対象を見つける]
    C --> D[text を修正する]
    D --> E[必要なら variants / next を直す]
    E --> F[ゲームで表示確認する]
    F --> G[他ファイルを探し回らずに完了する]
    G --> H[会話編集は怖くないという感覚になる]
```

## 6. 集約作業そのもののジャーニー

```mermaid
flowchart TD
    A[会話の集約を始める] --> B[repo 内の表示文を棚卸しする]
    B --> C[町会話を assets/dialogue.yaml に移す]
    C --> D[城会話を assets/dialogue.yaml に移す]
    D --> E[戦闘会話を assets/dialogue.yaml に移す]
    E --> F[ボス会話を assets/dialogue.yaml に移す]
    F --> G[エンディング会話を assets/dialogue.yaml に移す]
    G --> H[main.py 側の文字列を削除する]
    H --> I[grep で会話の残骸を確認する]
    I --> J[会話の原本が1つになった状態を得る]
```

## 7. ステージ別マップ

| ステージ | あなたの行動 | 頭の中 | 痛み |
|---|---|---|---|
| 会話を直したい | まずファイルを開く | 「どこにある?」 | 原本が1つではない |
| 探索する | `assets/dialogue.yaml` と `main.py` を見る | 「まだ別の場所にもありそう」 | 探索コストが高い |
| 修正する | 文字列を直す | 「これで本当に全部?」 | 消し漏れ不安が残る |
| 確認する | 実機で表示を見る | 「見た目は直ったが構造は汚いまま」 | 毎回同じ不安が再発する |
| 理想状態 | `assets/dialogue.yaml` だけ直す | 「ここが唯一の原本」 | 探索ストレスが消える |

## 8. このジャーニーマップが示す優先順位

```mermaid
flowchart TD
    A[最優先: 会話の原本を1つにする] --> B[assets/dialogue.yaml を唯一の編集入口にする]
    B --> C[main.py の文字列を削除する]
    C --> D[戦闘 / ボス / エンディングも同じ場所に寄せる]
    D --> E[会話編集のたびに grep しなくてよい状態にする]
```

## 9. 完了した時のあなたの状態

- 「会話を直す場所はどこ?」で止まらない
- `assets/dialogue.yaml` を見れば全体像が見える
- 会話の追加と削除が怖くない
- 仕様変更が来ても、触る中心がぶれない
