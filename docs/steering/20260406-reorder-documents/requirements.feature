Feature: Pyxel版ドキュメント再整理

  Scenario: 現行プロジェクトの範囲をpyxel配下に限定する
    Given 現行プロジェクトのルートは "/home/exedev/code-quest-pyxel" である
    And "/home/exedev/game" 配下の "pyxel" 以外の兄弟ディレクトリは現行プロジェクトに含まれない
    When ドキュメントの参照範囲を定義する
    Then 参照対象は "/home/exedev/code-quest-pyxel" 配下のファイルだけである

  Scenario: プロジェクト専用AGENTSを正本にする
    Given 親ディレクトリの AGENTS.md には旧HTML版のルールが含まれている
    And 現行のPyxel版実装は Python と Pyxel を前提にしている
    When AGENTSの適用方針を整理する
    Then "/home/exedev/code-quest-pyxel" 専用の AGENTS.md を現行ルールの正本にする
    And 親ディレクトリの AGENTS.md を Pyxel版実装のルールとしては採用しない

  Scenario: AGENTSの必読文書一覧を実在ファイル名に合わせる
    Given 現在の docs 配下には番号付きファイル名の文書が存在する
    When AGENTSの必読文書一覧を見直す
    Then 一覧には実在する docs ファイルだけを記載する
    And 存在しない "docs/concept.md" のような旧ファイル名は記載しない

  Scenario: 旧HTML版前提の文書を現行仕様から外す
    Given docs 内には "index.html" や "pressKey/releaseKey" を前提にした記述が残っている
    And 現行実装のエントリポイントは "main.py" である
    When ドキュメントの現行性を判定する
    Then 旧HTML版前提の記述は現行のPyxel仕様として扱わない
    And Pyxel版向けに更新または別扱いにする対象として明示する

  Scenario: 正本ソースと配布物を区別する
    Given "main.py" はPyxel版の正本ソースである
    And "pyxel.html" と "pyxel.pyxapp" は配布または生成に使う成果物である
    When ドキュメントのメンテナンス対象を整理する
    Then 実装ルールは "main.py" を中心に記述する
    And 配布物の説明は正本ソースとは区別して扱う

  Scenario: 整理作業の優先順位を固定する
    Given AGENTSとdocsの整合性に崩れがある
    When 再整理の作業順を決める
    Then 最初にAGENTSとdocsの整合性を直す
    And コード修正はその後に必要な場合だけ行う
