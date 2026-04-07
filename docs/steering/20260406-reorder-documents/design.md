# Docs Reorder Design

## Goal

`/home/exedev/code-quest-pyxel` を現行プロジェクトの唯一の正本として扱い、  
AGENTS と docs の説明を現在の Pyxel 実装に一致させる。

この設計の目的は、今後の作業者が

- どのフォルダを本体として見るべきか
- どの文書を先に読むべきか
- どの文書が旧HTML版の説明で、どの文書が現行Pyxel版の説明か

を迷わず判断できる状態を作ることにある。

## Current Problems

### 1. プロジェクトの境界が分かりにくい

`/home/exedev/game` 配下には旧バージョンの資産も残っている。  
しかし現行プロジェクトは `/home/exedev/code-quest-pyxel` のみである。

### 2. AGENTS が現行実装と一致していない

現在効いている親ディレクトリの `AGENTS.md` は、旧HTML版の前提を多く含んでいる。

例:

- `index.html` 単一ファイル前提
- `pressKey/releaseKey` 前提
- `createInitialPlayer()` / `resetGameState()` 前提

一方、現行実装は `main.py` を起点とする Pyxel + Python 構成である。

### 3. docs のファイル名と参照名がずれている

AGENTS では `docs/concept.md` のような旧名称を参照している。  
実ファイルは `docs/10-concept.md` のような番号付きファイル名で管理されている。

### 4. docs 内に旧HTML版の記述が混在している

一部文書は Pyxel 前提だが、別の文書には `index.html`、`localStorage`、Web Audio 前提の説明が残っている。  
このため、文書同士を読んでも結論が一致しない。

## Design Principles

### 1. 正本はひとつにする

現行プロジェクトの正本は `/home/exedev/code-quest-pyxel` だけに限定する。  
兄弟ディレクトリの旧バージョンは参照対象から外す。

### 2. 実装に合わせて説明を書く

文書は理想像ではなく、まず現行実装に合っていることを優先する。  
今のコードに存在しない構造や関数を、現行ルールとして書かない。

### 3. 現行文書と旧文書を混ぜない

旧HTML版の説明はそのまま現行仕様として扱わない。  
必要なら「旧設計」または「移行元情報」として分離する。

### 4. 読む順番を固定する

作業者が毎回迷わないように、AGENTS には「どの文書をどの順番で読むか」を現実のファイル名で書く。

## Target State

### AGENTS

`/home/exedev/code-quest-pyxel/AGENTS.md` を新設し、Pyxel版専用ガイドにする。

この AGENTS には次を記載する。

- 現行プロジェクトは `/home/exedev/code-quest-pyxel` のみであること
- 兄弟ディレクトリの旧版は対象外であること
- 必読 docs の実ファイル名
- 現行実装の基本前提
  - エントリポイントは `main.py`
  - 配布物として `pyxel.html` と `pyxel.pyxapp` がある
  - docs と実装がずれた場合は、まず現行実装を確認すること

### Docs Inventory

docs は次の3種類に分けて整理する。

1. 現行Pyxel版の正本ドキュメント
2. 現行Pyxel版への変換・補助ドキュメント
3. 旧HTML版の説明が残っており、更新または隔離が必要なドキュメント

### Naming

AGENTS の参照名は、必ず docs 内の実在ファイル名と一致させる。  
`docs/concept.md` のような仮想的な旧名は使わない。

## Proposed Document Roles

### 現行Pyxel版の入口

- `docs/00-pyxel-design.md`
- `docs/10-concept.md`
- `docs/20-requirements.md`
- `docs/30-story-concepts.md`
- `docs/35-story-design.md`
- `docs/50-map-concepts.md`
- `docs/55-map-design.md`
- `docs/60-visual-requirements.md`
- `docs/65-visual-design.md`
- `docs/70-audio-concepts.md`
- `docs/75-audio-design.md`
- `docs/80-sfx-concepts.md`
- `docs/85-sfx-design.md`
- `docs/95-testing.md`
- `docs/97-acceptance.feature`

### 再点検が必要な文書

少なくとも次は旧HTML版の説明が混ざっている可能性が高いため、現行仕様としては再点検対象にする。

- `docs/90-architecture.md`
- `docs/92-functional-design.md`

## Scope

この設計で最初に行う対象は文書整理だけとする。

含むもの:

- Pyxel版専用 AGENTS の定義
- docs の参照整理
- 旧HTML版前提の文書の棚卸し
- 現行文書の役割分け

含まないもの:

- ゲームロジックの変更
- 描画や音声の改修
- 旧兄弟ディレクトリの削除
- 配布物の再生成

## Migration Plan

### Phase 1: AGENTS を正す

- Pyxel専用 AGENTS を `/home/exedev/code-quest-pyxel` に置く
- 現行スコープと必読 docs を明記する

### Phase 2: docs の目録を正す

- すべての必読文書を実在ファイル名で列挙する
- 現行Pyxel版の入口文書を固定する

### Phase 3: 旧記述を仕分ける

- HTML版前提が残る文書を特定する
- 更新対象と参考資料を分離する

### Phase 4: 必要ならコード側に進む

- docs と実装を見比べる
- 本当に必要な差分だけをコード修正候補にする

## Risks

### 1. 文書だけ直して満足してしまう

文書を直しても、実装との差分が残る可能性はある。  
そのため、docs 整理の完了はコード一致の完了を意味しない。

### 2. 旧文書を完全に消してしまう

旧HTML版の情報にも歴史的価値はある。  
削除ではなく、まず「現行仕様ではない」と区別するほうが安全である。

### 3. 正本の判断が再びぶれる

AGENTS、docs、実装の3つで「どれが正本か」が違うと再発する。  
AGENTS で最初に正本の定義を書くことが重要である。

## Acceptance Criteria

- `/home/exedev/code-quest-pyxel` が現行プロジェクトの唯一の対象として文書化されている
- Pyxel専用 AGENTS が存在する
- AGENTS の必読 docs 一覧が実在ファイル名と一致する
- `main.py` が現行実装の入口として扱われている
- `pyxel.html` と `pyxel.pyxapp` が配布・成果物として区別されている
- `docs/90-architecture.md` と `docs/92-functional-design.md` が再点検対象として認識されている
- コード修正は docs 整理の後段で扱う方針が明記されている
