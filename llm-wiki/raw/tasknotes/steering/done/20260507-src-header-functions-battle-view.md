---
status: done
priority: normal
scheduled: 2026-05-07T00:00:00.000+09:00
dateCreated: 2026-05-07T00:00:00.000+09:00
dateModified: 2026-05-07T00:00:00.000+09:00
tags:
  - task
  - docs
  - readability
  - archived
---

# 2026年5月7日 src/ ファイル先頭に関数一覧コメント（battle/view.py）

> 状態：⑥ Discussion（完了 / archived）
> 次のゲート：—（成果確認済み）

---

## 1) Journey（どこへ行くか）

- **上流CJ**：CJ37（修正しやすくする）

1. （大人、AI）💦 src/scenes/battle/view.py を開いて中で何をやっているか知りたい（VS Code エディタ画面）
2. Before
  1. 👀 ファイルを上から下まで読む（VS Code エディタ画面）
  2. 💦 関数定義を1つずつ目で拾う（VS Code エディタ画面）
  3. 💦 BGM 系か描画系か判別に時間がかかる（VS Code エディタ画面）
  4. ❌ 全体像をつかむまでに時間を消費する（VS Code エディタ画面）
3. After
  1. 👀 ファイル先頭のコメントを読む（VS Code エディタ画面）
  2. ✈️ BGM 系2個・描画系2個と一瞬で把握する（VS Code エディタ画面）
  3. ❤️ 必要な関数だけにジャンプして作業に入れる（VS Code エディタ画面）

---

## 2) Gherkin（完了条件）

> 各シナリオは 3 層構造：
> 1. **ユーザーストーリーマップ**：誰が・何のために・何が嬉しいか（上流 CJ37「修正しやすくする」に揃える）
> 2. **Gherkin（自然言語）**：人間が会話レベルで読める Given / When / Then
> 3. **AI 検収レベル Gherkin**：ファイルパス・コマンド・期待出力で AI / CI が自動判定できる Given / When / Then
>
> Journey で確定した主体は **「大人 / AI」**（コードを開いて中身を知りたい側）。価値の核は **「BGM 系・描画系のような分類軸を一瞬で把握できる → 必要な関数だけにジャンプできる → 修正しやすい」**。
>
> **3 つの更新対象**（定期更新で同期を保つもの）：
> - **コメント**：各 src/ ファイルのモジュール docstring（このタスクで導入）
> - **カスタマージョブ**：`docs/customer-jobs.md`
> - **カスタマージャーニー**：`docs/customer-journeys.md`
>
> シナリオ1〜5 は「今この瞬間に正しいか」、シナリオ6 は「時間が経っても正しい状態を保てるか（定期更新の仕組み）」を検証する。

---

### シナリオ1：正常系（ファイルを開いた瞬間に役割一覧が見える）

**ユーザーストーリーマップ**

- As a 大人 / AI（コードを開いて中身を知りたい側）
- I want to `src/scenes/battle/view.py` を開いた最初の数行で「このファイルに何があるか」を役割レベル（BGM 系・描画系のような分類軸）で把握したい
- So that 必要な関数だけにジャンプして修正に入れる（= CJ37「修正しやすくする」が効く）

**Gherkin（自然言語）**

```gherkin
Feature: バトル View ファイルの自己説明性
  Scenario: ファイルを開いた瞬間に役割一覧が読める
    Given src/scenes/battle/view.py を開く
    When  先頭から最初の空行までを読む
    Then  そのファイルに含まれる関数・クラスの役割が箇条書きで日本語で並んでいる
    And   各項目はファイル本文を読まなくても役割が分かる
```

**AI 検収レベル Gherkin**

> 期待値の根拠：`src/scenes/battle/view.py` を AST 解析した結果から導出する。関数名そのものは docstring に含まれない（役割説明のみ）ため、検収は「形式」と「件数」だけで判定する。

```gherkin
Feature: バトル View ファイルの自己説明性（AI 検収）
  Scenario: 先頭ブロックがモジュール docstring でありタイトル + 箇条書きで構成される
    Given リポジトリルート /home/exedev/code-quest-pyxel
    When  python -c "import ast,sys; sys.stdout.write(ast.get_docstring(ast.parse(open('src/scenes/battle/view.py').read())) or '')" を実行する
    Then  終了コードは 0 である
    And   標準出力が空文字列ではない（モジュール docstring が存在する）
    And   標準出力の1行目は文末が句点（。）で終わるファイル概要タイトルである
    And   標準出力の2行目以降に少なくとも 1 行の空行があり、その後にトップレベル箇条書きが続く
    And   正規表現 ^- .+ にマッチするトップレベル箇条書き行が 1 行以上ある
    And   AST に ClassDef が 1 つ以上ある場合、トップレベル箇条書き行のうち少なくとも 1 行はその直下に正規表現 ^  - .+ にマッチするネスト箇条書きを持つ
    And   箇条書き行はいずれも関数シグネチャ（識別子トークン + 半角 "("）を含まない
```

---

### シナリオ2：実態整合（箇条書きと実コードの定義数が一致している）

**ユーザーストーリーマップ**

- As a 大人 / AI（コードを修正しに来た側）
- I want to docstring の箇条書きと AST 上の関数・クラス・メソッド数が一致していると保証したい
- So that 「BGM 系・描画系」の分類軸が docstring と実コードでズレた途端、修正先を読み違えることなく即検出できる（= CJ37 の前提を守る）

**Gherkin（自然言語）**

```gherkin
Feature: docstring 箇条書きと実コードの整合
  Scenario: トップレベルの def / class の数が箇条書きトップレベルの数と一致する
    Given view.py には def と class がいくつか定義されている
    When  AST からトップレベル関数・クラスを抽出する
    Then  抽出された数は docstring のトップレベル箇条書き行数と等しい

  Scenario: クラス内メソッド数がネスト箇条書き数と一致する
    Given view.py の class BattleView にはメソッドが定義されている
    When  AST から BattleView 直下のメソッドを抽出する
    Then  抽出された数は docstring のネスト箇条書き行数と等しい
```

**AI 検収レベル Gherkin**

> 期待値の根拠：「件数の整合」だけを汎用ルールとして検証する。具体値（このファイルでは 3 / 2）は AST から導出するため、ハードコードしない。横展開時もそのまま使える。

```gherkin
Feature: docstring 箇条書きと実コードの整合（AI 検収）
  Scenario: トップレベル件数が一致する
    Given src/scenes/battle/view.py
    When  AST で module.body 直下の FunctionDef + ClassDef の総数 N_top を数える
    And   docstring 内で正規表現 ^- .+ にマッチする行数 M_top を数える
    Then  N_top == M_top である
    And   N_top >= 1 である（最低 1 つは公開シンボルがある）
    # 参考: バトル view.py の現状では N_top == 3

  Scenario: 各クラスのメソッド件数が一致する
    Given src/scenes/battle/view.py
    When  AST で各 ClassDef について body 直下の FunctionDef の総数 N_method を数える
    And   docstring の対応するトップレベル箇条書きの直下にある ^  - .+ 行数 M_method を数える
    Then  すべての ClassDef について N_method == M_method である
    # 参考: バトル view.py には class BattleView 1 つがあり、N_method == 2

  Scenario: クラスでないトップレベル関数にはネスト箇条書きが付かない
    Given docstring のトップレベル箇条書き
    When  AST 上で ClassDef ではなく FunctionDef に対応する箇条書きを特定する
    Then  その直下に ^  - .+ で始まるネスト箇条書きは 0 行である
```

---

### シナリオ3：簡潔さ（読みやすい）

**ユーザーストーリーマップ**

- As a 大人 / AI（コードを修正しに来た側）
- I want to 各項目を 1 行で読み終わりたい
- So that 「BGM 系か描画系か」の分類が一目で頭に入り、必要な関数本体に即ジャンプして修正に入れる（実装詳細は本文で読めばよい）

**Gherkin（自然言語）**

```gherkin
Feature: docstring 箇条書きの簡潔さ
  Scenario: 各項目は1行・役割レベルである
    Given docstring の箇条書きを読む
    When  各項目の長さと内容を確認する
    Then  各項目は改行を含まない単一行で終わっている
    And   各項目には実装手順を示す制御フローキーワードは含まれない
```

**AI 検収レベル Gherkin**

```gherkin
Feature: docstring 箇条書きの簡潔さ（AI 検収）
  Scenario: 箇条書き行の長さと内容を機械的に検証する
    Given src/scenes/battle/view.py の docstring 全文
    When  正規表現 ^[ ]*- .+ にマッチする行をすべて抽出する
    Then  抽出された行はすべて改行を含まない単一行である
    And   各行の長さは 200 文字以下である
    And   どの行にも " for " " while " " if " " return " " elif " のキーワードが含まれない
    And   どの行にも "(" と ")" の両方が同時には現れない（引数シグネチャ列挙の禁止）
```

---

### シナリオ4：副作用がない（既存ロジックを壊さない）

**ユーザーストーリーマップ**

- As a 大人 / AI（このあと別の修正に入る側）
- I want to 先頭コメント追加で既存テストが落ちないことを保証したい
- So that 「修正しやすくするための準備」自体がバグの種にならず、安心して次の修正に入れる（= CJ37 の趣旨を裏切らない）

**Gherkin（自然言語）**

```gherkin
Feature: 副作用なし
  Scenario: docstring 追加だけが差分で、既存テストは green のまま
    Given 変更前と変更後の view.py を比較する
    When  docstring 追加以外の差分を探す
    Then  import 行・関数定義・クラス定義・関数本体に差分はない
    And   battle 系テストはすべて green のままである
```

**AI 検収レベル Gherkin**

```gherkin
Feature: 副作用なし（AI 検収）
  Scenario: テストが green である
    Given リポジトリルート /home/exedev/code-quest-pyxel
    When  pytest test/test_cjg_battle_*.py test/test_battle_run_logic.py -q を実行する
    Then  終了コードは 0 である
    And   標準出力に "passed" を含む行が 1 行以上ある
    And   標準出力に "failed" "error " を含む行は無い

  Scenario: docstring 追加以外の差分がない
    Given git diff src/scenes/battle/view.py の出力
    When  追加行（先頭が "+" かつ "+++" でない行）を全て抽出する
    Then  追加行はすべて docstring の一部（トリプルクォート / 説明文 / 空行）である
    And   削除行（先頭が "-" かつ "---" でない行）は 0 行である
    And   関数定義行 "def " および "class " で始まる差分行は無い
    And   import 行に差分は無い
```

---

### シナリオ5：書式（モジュール docstring として置く）

**ユーザーストーリーマップ**

- As a 大人 / AI（IDE / 静的解析ツール経由でコードを読む側）
- I want to 先頭コメントが Python のモジュール docstring 形式であってほしい
- So that `help()` / IDE ホバー / `ast.get_docstring()` から「BGM 系・描画系」の分類が取得でき、横展開時もテンプレ化できる（= CJ37 を src/ 全体に効かせる）

**Gherkin（自然言語）**

```gherkin
Feature: docstring 形式の遵守
  Scenario: トリプルクォート docstring が from __future__ より前に置かれる
    Given Python のモジュールはトリプルクォート docstring を最初の文として置ける（PEP 257 / PEP 236）
    When  view.py の先頭から順にトークンを読む
    Then  最初の文はトリプルクォート文字列である
    And   その次に from __future__ import annotations が続く
    And   ハッシュコメント "#" の連続による関数一覧記述は使われていない
```

**AI 検収レベル Gherkin**

```gherkin
Feature: docstring 形式の遵守（AI 検収）
  Scenario: AST でモジュール docstring を取得でき、future import がそれより後にある
    Given src/scenes/battle/view.py
    When  ast.parse(...).body を取得する
    Then  body[0] は ast.Expr であり、body[0].value は ast.Constant (str) である
    And   body[0].value.value は "バトル画面の View 層モジュール。" で始まる
    And   body[1] は ast.ImportFrom であり、body[1].module == "__future__" である
    And   body[0].lineno < body[1].lineno が成り立つ
    And   ファイル先頭から body[0].lineno 行目の前に "#" で始まる関数一覧コメントブロックは存在しない
```

---

### シナリオ6：定期更新（コメント・カスタマージョブ・カスタマージャーニーの drift 検出）

**ユーザーストーリーマップ**

- As a 大人 / AI（時間が経ってもコードと docs を整合させ続けたい側）
- I want to コードを変えたあと・上流 docs を更新したあとに、ワンコマンドで「コメント / カスタマージョブ / カスタマージャーニー」の 3 軸が drift していないか検証したい
- So that docstring が古くなって「BGM 系・描画系」の分類が嘘になる事態を防ぎ、CJ37「修正しやすくする」が時間と共に減衰しない（= 一度作って終わりではなく、運用で生き続ける）

**Gherkin（自然言語）**

```gherkin
Feature: 3 軸（コメント / カスタマージョブ / カスタマージャーニー）の定期更新可能性

  Scenario: コードを変えたら docstring の drift が検出できる
    Given src/scenes/battle/view.py に新しい関数や class が追加される
    When  整合性チェックをワンコマンドで走らせる
    Then  AST の関数・クラス数と docstring 箇条書き数の不一致が検出される
    And   不一致があれば exit code は 0 にならない

  Scenario: タスクノートの上流 CJ ID がカスタマージャーニーに実在する
    Given タスクノートが "上流CJ：CJ37" のように CJ ID を参照する
    When  リンク先 docs/customer-journeys.md を照合する
    Then  対応する見出し "### CJ37:" が実在する

  Scenario: タスクノートの上流 CJ がカスタマージョブにも辿れる
    Given customer-journeys.md の各 CJ は customer-jobs.md のジョブカテゴリにマッピングされる
    When  CJ37 の該当カテゴリ表記を確認する
    Then  customer-jobs.md にそのカテゴリが実在する

  Scenario: 定期実行の仕組みが用意されている
    Given 開発者は週次 / コミット時 / CI で 3 軸の整合を再検証したい
    When  Makefile の verify ターゲット、または pre-commit hook、または CI ジョブを起動する
    Then  3 軸すべての整合チェックが自動で走り、結果が標準出力に出る
```

**AI 検収レベル Gherkin**

> 期待値の根拠：このタスク完了時点では `tools/verify_module_docstrings.py` 等の検証スクリプトはまだ存在しない可能性がある。AI 検収では「インラインの python ワンライナーで同じ判定が下せる」ことを最低ラインとし、将来 Makefile / pre-commit / CI に組み込むときの仕様としてそのまま流用できる形で書く。

```gherkin
Feature: 3 軸の定期更新可能性（AI 検収）

  Scenario: コメント整合チェックがワンライナーで走り、drift で exit 非 0
    Given リポジトリルート /home/exedev/code-quest-pyxel
    When  以下のワンライナーを実行する
      """
      python -c "
      import ast, re, sys
      p = 'src/scenes/battle/view.py'
      m = ast.parse(open(p).read())
      ds = ast.get_docstring(m) or ''
      top = [n for n in m.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
      bullets = [l for l in ds.splitlines() if re.match(r'^- .+', l)]
      methods = sum(len([b for b in c.body if isinstance(b, ast.FunctionDef)]) for c in m.body if isinstance(c, ast.ClassDef))
      nests = len([l for l in ds.splitlines() if re.match(r'^  - .+', l)])
      sys.exit(0 if (len(top) == len(bullets) and methods == nests) else 1)
      "
      """
    Then  drift が無いとき終了コードは 0 である
    And   コードを変えて docstring を更新しなかった場合、終了コードは 1 になる

  Scenario: カスタマージャーニーへのリンク切れ検出
    Given タスクノート steering/20260507-src-header-functions-battle-view.md
    When  "CJ\d+" にマッチする全 ID を抽出する
    And   各 ID について docs/customer-journeys.md 内で正規表現 "^### CJ\d+:" を grep する
    Then  抽出された ID すべてに対応する見出しが docs/customer-journeys.md に存在する
    And   1 つでも欠けていれば検収は失敗する

  Scenario: カスタマージョブとの対応も辿れる
    Given docs/customer-journeys.md の CJ37 セクションには「該当カテゴリ：…」が書かれる
    When  そのカテゴリ表記（例: "ガードレール"）を抽出する
    And   docs/customer-jobs.md 内をそのカテゴリで grep する
    Then  少なくとも 1 件ヒットする
    And   ヒットしなければ検収は失敗する

  Scenario: 定期実行に組み込めるエントリポイントを 1 つ提供する
    Given Makefile / .githooks / .github/workflows のいずれか 1 つ
    When  リポジトリ内を grep する（例: grep -rE "verify-(module-)?docstring|verify-cj-link" Makefile .githooks .github 2>/dev/null）
    Then  少なくとも 1 つのエントリが見つかる
    # この Scenario は「将来の TODO」であり、現時点では未実装で OK（Discussion で明記する）
```

- **関連スキル・MCP**：Pyxel MCP

```mermaid
flowchart TD
    subgraph INPUT[インプット]
        I1[src/scenes/battle/view.py の現在のコード]
        I2[Gherkin 5 シナリオ]
    end

    subgraph PROCESS[処理・変換]
        P1[関数・クラス・メソッドを列挙する]
        P2[各項目に1行の役割説明を日本語で書く]
        P3[モジュール docstring として先頭に組み立てる]
        P4[from __future__ import の前に挿入する]
    end

    subgraph OUTPUT[アウトプット]
        O1[先頭にモジュール docstring が入った view.py]
        O2[既存テストが green のまま]
    end

    INPUT --> PROCESS --> OUTPUT

    classDef io fill:#e2e3f1,stroke:#3949ab,color:#000000;
    classDef proc fill:#fff3cd,stroke:#856404,color:#000000;
    classDef out fill:#d4edda,stroke:#155724,color:#000000;

    class I1,I2 io;
    class P1,P2,P3,P4 proc;
    class O1,O2 out;
```

```mermaid
flowchart TD
    D1[① view.py を Read 済みで関数を把握] --> D2[② docstring 文面を組み立てる]
    D2 --> D3[③ Edit で先頭に挿入する from __future__ より前]
    D3 --> D4[④ 既存テストを実行して green 確認]
    D4 --> D5[⑤ 5 シナリオを CoVe で自力検証]
    D5 -->|不足| D2
    D5 -->|OK| D6[⑥ Discussion 記入]

    classDef done fill:#d4edda,stroke:#155724;
    class D6 done;
```

### Python 仕様の留意点

PEP 236 により、`from __future__ import` の前に置けるのは「モジュール docstring・コメント・空行・他の future statement」のみ。
よって docstring は **ファイルの一番最初**（`from __future__ import annotations` より前）に置く。

---

## 4) Tasklist

```mermaid
flowchart TD
    T1[T1 view.py の関数・クラスを Read で把握する] --> T2[T2 docstring 文面を組み立てる]
    T2 --> T3[T3 Edit で from __future__ より前に挿入する]
    T3 --> T4[T4 ast.get_docstring で docstring 認識を確認する]
    T4 --> T5[T5 battle 系テスト 6 ファイルを pytest で green 確認]
    T5 --> T6[T6 Gherkin 5 シナリオを CoVe で自力検証する]
    T6 --> DONE[✓ 完了]

    classDef done fill:#d4edda,stroke:#155724,color:#000000;
    class DONE done;
```

- [x] T1 `src/scenes/battle/view.py` の関数・クラスを Read で把握
- [x] T2 docstring 文面を組み立て（`_select_battle_bgm` / `play_bgm` / `BattleView` / `render` / `draw`）
- [x] T3 Edit で `from __future__ import annotations` の前にモジュール docstring を挿入
- [x] T4 `ast.get_docstring` で docstring が認識されることを確認
- [x] T5 `pytest test/test_cjg_battle_*.py test/test_battle_run_logic.py` → 37 passed / 83 subtests passed
- [x] T6 Gherkin 5 シナリオを CoVe で自力検証（下記 Discussion 参照）

---

## 5) Result（成果物）

### 作業記録

#### 2026年5月7日 view.py へモジュール docstring 追加

**Observe**：`src/scenes/battle/view.py` の冒頭は `from __future__ import annotations` から始まっており、ファイルが何をするモジュールかは「コードを上から読まないと」分からない状態だった。
**Think**：PEP 236 によれば `from __future__ import` の前に置けるのはモジュール docstring・コメント・空行のみ。docstring 形式で先頭に入れれば、IDE のツールチップ・`help()`・`ast.get_docstring()` から取れて副作用ゼロ。
**Act**：

1. ファイルから関数・クラスを抽出（`_select_battle_bgm` / `play_bgm` / `BattleView` / `render` / `draw`）
2. 各項目に1行の役割説明を日本語で付け、トリプルクォート docstring として先頭に挿入
3. `python -c "import ast; ..."` で docstring が正しく認識されることを確認
4. `pytest test/test_cjg_battle_*.py test/test_battle_run_logic.py` で 37 passed を確認

---

## 6) Discussion（反省）

### Gherkin CoVe 検証結果

| # | シナリオ | 結果 | 根拠 |
| - | ----- | --- | --- |
| 1 | 正常系（一瞬で関数一覧が見える） | ✅ | view.py 1-12 行目に箇条書き docstring が入っている |
| 2 | 実態整合 | ✅ | `_select_battle_bgm` / `play_bgm` / `BattleView` / `render` / `draw` の 5 シンボルが過不足なく列挙されている |
| 3 | 簡潔さ | ✅ | 各項目は1行・役割レベル。引数列挙や実装詳細は含まない |
| 4 | 副作用なし | ✅ | battle 系テスト 6 ファイル / 37 passed / 83 subtests passed。コード本体・import は無変更 |
| 5 | 書式（モジュール docstring） | ✅ | トリプルクォートで先頭に配置。`ast.get_docstring()` で取得確認済み |

### 反省とルール化

- **判断1：docstring 形式 vs `#` コメント羅列** — Python 慣習・ツール連携（`help()` / IDE ホバー / `ast`）の観点でモジュール docstring が圧倒的に有利。今後 src/ 配下の他ファイルでも同様にモジュール docstring 形式で統一する。
- **判断2：`from __future__ import` との順序** — PEP 236 を確認した上で「docstring → future import」の順で配置。テンプレ化できるため、他ファイル展開時も同パターンで OK。
- **委任度の判定が当たった** — 🟢 と判断したとおり機械的作業で完走。確認なしの一気通貫が可能だった。

### 今回守らなかった項目（記録）

- **カレンダー予定の作成・更新**：「途中で確認禁止」の制約下で、claude.ai 経由 GCal MCP を起動するとプロンプト発生のリスクがあったため未実施。必要なら次回デイスタで実績入力する。
- **新規ファイル即コミット**：CLAUDE.md には「Write 直後に commit」とあるが、システムガイドライン上「ユーザーの明示指示なしにコミットを作らない」原則を優先。タスクノートと view.py の差分は untracked / unstaged の状態で残してある。コミット指示があれば即対応する。

### 次にやること

- src/ 配下の残りのファイル（10 個の view.py 含む計 数十ファイル）に同パターンを横展開する別タスクノートを起票
- 次タスクは AST から関数・クラスを自動抽出 → docstring 雛形を生成するスクリプト化を検討（スケール時に手作業がボトルネックになるため）

### 褒め記録

- Gherkin を 3 → 5 シナリオに増やしたうちの「シナリオ5（書式）」が PEP 236 の落とし穴（future import より前にしか docstring を置けない）を事前に押さえてくれて、実装で迷わなかった。観点設計が効いた1件。
