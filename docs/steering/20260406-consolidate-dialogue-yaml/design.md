# Design: `assets/dialogue.yaml` 全会話集約

この文書は、**ゲーム中に実際に表示される会話本文を `assets/dialogue.yaml` に集約し、他の runtime ファイルから削除する**ための設計をまとめる。  
方針は一言で言うと、**「本文は YAML にだけ置く。コードは scene 名と状態だけを扱う」** である。

## 1. 設計の大方針

```mermaid
flowchart TD
    P1[原則1: 実行時の本文原本は assets/dialogue.yaml だけ] --> R1[会話を直す場所を1つに固定する]
    P2[原則2: main.py は本文を持たない] --> R2[文字列の重複と消し漏れを防ぐ]
    P3[原則3: docs は仕様書であり原本ではない] --> R3[実行時の参照先と説明文書を分離する]
    P4[原則4: scene 名でカテゴリが分かる] --> R4[grep しなくても全体像を追える]
    P5[原則5: 移行はカテゴリ単位で進める] --> R5[町 / 戦闘 / ボス / ending を順番に安全に寄せられる]
```

## 2. まず直すべき不整合

```mermaid
flowchart TD
    A[現状] --> B[実ファイルは assets/dialogue.yaml]
    A --> C[main.py は assets/dialogs/dialogue.yaml を読んでいる]
    B --> D[このままでは path truth が2つある]
    C --> D
    D --> E[最初の修正で参照先を assets/dialogue.yaml に統一する]
```

この不整合は小さく見えるが、会話原本を 1 つにする設計では最優先で解消すべきである。  
原本のパスがぶれている状態では、「どこを見ればよいか」が再び曖昧になる。

## 3. 完成後のレイヤー構成

```mermaid
flowchart TD
    subgraph Runtime["ゲーム runtime"]
        Main[main.py]
        Battle[バトル進行]
        Ending[エンディング進行]
    end

    subgraph Adapter["会話アダプタ"]
        Runner[StructuredDialogRunner]
        Resolver[scene resolver]
    end

    subgraph Data["会話データ"]
        Dialogue[assets/dialogue.yaml]
    end

    Main --> Resolver
    Battle --> Resolver
    Ending --> Resolver
    Resolver --> Runner
    Runner --> Dialogue
```

完成後、`main.py` は「どの scene を開くか」「今の状態は何か」を渡すだけにする。  
本文、分岐、連結、選択肢、ボスフェーズ文はすべて `assets/dialogue.yaml` 側に置く。

## 4. 対象範囲

```mermaid
flowchart TD
    A[町会話] --> Z[assets/dialogue.yaml]
    B[城会話] --> Z
    C[ダンジョン突入 / 脱出] --> Z
    D[通常戦闘ログ] --> Z
    E[ボス開始 / フェーズ / 撃破会話] --> Z
    F[逃走 / 敗北 / 勝利メッセージ] --> Z
    G[エンディング本文] --> Z
    H[将来の裏ボス会話] --> Z
```

今回の設計では、**「ユーザーに見せる文章」** を対象にする。  
敵名、アイテム名、ステータス名のようなデータラベルは別テーブルのままでもよいが、画面に出るメッセージ文は YAML に集約する。

## 5. `assets/dialogue.yaml` の構造

### 5.1 ルート構造

```mermaid
flowchart TD
    Root[assets/dialogue.yaml] --> Vars[variables]
    Root --> Scenes[scenes]
    Scenes --> Town[town.*]
    Scenes --> Castle[castle.*]
    Scenes --> Dungeon[dungeon.*]
    Scenes --> Battle[battle.*]
    Scenes --> Boss[boss.*]
    Scenes --> Ending[ending.*]
```

### 5.2 scene 名の命名規則

```mermaid
flowchart TD
    A[town.start.entry] --> Z[カテゴリ: town]
    B[castle.professor.entry] --> Z2[カテゴリ: castle]
    C[dungeon.glitch.enter] --> Z3[カテゴリ: dungeon]
    D[battle.normal.attack.observe] --> Z4[カテゴリ: battle]
    E[boss.glitch.phase80] --> Z5[カテゴリ: boss]
    F[ending.main.line01] --> Z6[カテゴリ: ending]
```

命名規則は以下で固定する。

- `town.*`
- `castle.*`
- `dungeon.*`
- `battle.*`
- `boss.*`
- `ending.*`

これにより、作者は scene 名だけで会話カテゴリを追える。

## 6. データモデル

### 6.1 使うキー

- `variables`
- `scenes`
- `speaker`
- `text`
- `set`
- `choices`
- `next`
- `variants`
- `when`

### 6.2 使い方

```mermaid
flowchart TD
    A[scene を開始する] --> B{variants があるか}
    B -->|ある| C[when を上から評価]
    C --> D[最初に一致した variant を採用]
    B -->|ない| E[scene 本体を採用]
    D --> F[text を返す]
    E --> F
    F --> G[set を反映]
    G --> H{choices があるか}
    H -->|ある| I[選択待ち]
    H -->|ない| J{next があるか}
    J -->|ある| K[次 scene へ]
    J -->|ない| L[終了]
```

### 6.3 実際の整理方針

- 1行ずつ順送りする文は `next` で連結する
- 進行度差分は `variants` で扱う
- 選択肢が必要な会話は `choices` を使う
- 連続する戦闘文の固定フレーズも scene として置く

## 7. main.py 側の責務

```mermaid
flowchart TD
    A[イベント発生] --> B[scene 名を決める]
    B --> C[必要な context を作る]
    C --> D[StructuredDialogRunner に渡す]
    D --> E[返ってきた text を表示する]
```

`main.py` が持つ責務は次の 3 つだけに絞る。

1. scene 名の決定  
2. context の生成  
3. 表示タイミングの制御

逆に `main.py` から外す責務は次の通り。

- 本文文字列の保持
- フェーズごとのセリフ分岐の本文部分
- エンディング文の直書き
- 敗北や逃走の固定メッセージ文

## 8. context 設計

```mermaid
flowchart TD
    A[player の生状態] --> B[派生 context を作る]
    B --> C[ProfessorPhase]
    B --> D[BossPhase]
    B --> E[Visited flags]
    B --> F[Ending state]
    C --> G[dialogue.yaml の when で参照]
    D --> G
    E --> G
    F --> G
```

YAML 側には複雑な比較式を書かない。  
たとえば `max_zone_reached >= 3` をそのまま書くのではなく、Python 側で `ProfessorPhase = late` を作って渡す。

### 8.1 代表的な派生 context

- `ProfessorPhase = early | mid | late`
- `BossPhase = intro | phase80 | phase60 | phase40 | phase20 | phase08 | defeat`
- `EndingState = before_clear | after_clear`

## 9. カテゴリ別の実装方式

### 9.1 町 / 城 / ダンジョン

```mermaid
flowchart TD
    A[タイルイベント発生] --> B[座標から scene 名を引く]
    B --> C[dialogue.yaml を読む]
    C --> D[msg_lines を作る]
    D --> E[既存 message window で順送り表示]
```

ここはすでに `show_message(lines)` の流れがあるので、最も移行しやすい。

### 9.2 通常戦闘

```mermaid
flowchart TD
    A[戦闘イベント] --> B[本文テンプレ scene を選ぶ]
    B --> C[enemy 名や dmg を埋め込む]
    C --> D[battle_text に表示する]
```

通常戦闘では、完全固定文だけでなくテンプレート文字列が必要になる。  
そのため `text` は将来的に `{enemy}` や `{dmg}` のような置換を許す設計に寄せる。

### 9.3 ボス会話

```mermaid
flowchart TD
    A[ボス戦開始] --> B[boss.glitch.intro]
    B --> C[HP閾値チェック]
    C --> D[boss.glitch.phase80]
    D --> E[boss.glitch.phase60]
    E --> F[boss.glitch.phase40]
    F --> G[boss.glitch.phase20]
    G --> H[boss.glitch.phase08]
    H --> I[boss.glitch.defeat]
```

ボス会話は scene 名が最も素直に効く領域である。  
HP 閾値判定は Python 側、本文は YAML 側に完全分離する。

### 9.4 エンディング

```mermaid
flowchart TD
    A[clear 条件成立] --> B[ending.main.line01]
    B --> C[ending.main.line02]
    C --> D[ending.main.line03]
    D --> E[ending.main.line04]
    E --> F[描画は既存 draw_ending が行う]
```

エンディングは今 `draw_ending` に直書きが残りやすいので、ここも scene 連結に統一する。

## 10. 移行順

```mermaid
flowchart TD
    S1[Step 1: 参照先を assets/dialogue.yaml に統一] --> S2[Step 2: 町会話を移す]
    S2 --> S3[Step 3: 城会話を移す]
    S3 --> S4[Step 4: ダンジョン入退場文を移す]
    S4 --> S5[Step 5: 通常戦闘メッセージを移す]
    S5 --> S6[Step 6: ボス会話を移す]
    S6 --> S7[Step 7: 敗北 / 逃走 / 勝利文を移す]
    S7 --> S8[Step 8: エンディング文を移す]
    S8 --> S9[Step 9: main.py の本文直書きを削除]
```

この順にする理由は、**線形で単純な会話から先に寄せる方が安全だから**である。

## 11. 削除ルール

```mermaid
flowchart TD
    A[本文を YAML へ移した] --> B[main.py に同じ本文が残っているか]
    B -->|はい| C[削除する]
    B -->|いいえ| D[次へ進む]
    C --> D
    D --> E[grep で残骸確認]
```

削除対象の原則は次の通り。

- `show_message([...])` の固定本文
- `battle_text = "..."` の固定本文
- `draw_ending()` の固定本文
- 旧会話ファイル

削除しないものは次の通り。

- docs 内の説明用引用
- 敵名やアイテム名などのラベルデータ
- UI レイアウトそのもの

## 12. 検証方法

```mermaid
flowchart TD
    A[dialogue.yaml を編集] --> B[Runner 単体テスト]
    B --> C[カテゴリごとの表示テスト]
    C --> D[grep で本文直書き残骸を確認]
    D --> E[手動プレイで町 / 戦闘 / ボス / ending を確認]
```

最低限必要な検証は次の通り。

- `assets/dialogue.yaml` がロードできる
- scene 名参照が壊れていない
- `variants` が想定どおり分岐する
- `next` 連結が正しく動く
- `main.py` に本文直書きが残っていない

## 13. この設計で得るもの

```mermaid
flowchart TD
    A[会話原本が1つになる] --> B[作者が迷わない]
    B --> C[修正コストが下がる]
    C --> D[消し漏れ不安が減る]
    D --> E[将来の会話追加も同じルールで進められる]
```

この設計の価値は、新しい会話言語を導入することではない。  
**「会話を直す時にどこを触ればよいか」を一度で分かるようにすること**にある。
