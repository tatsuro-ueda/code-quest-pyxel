---
source: raw/tasknotes/steering/done/20260412-guardrails-3-headless-test.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 ガードレール(3) ヘッドレステスト基盤 Summary Draft

## summary

この tasknote は、壊れた版を子どもに届けない最後の build gate として、`tools/test_headless.py` による headless 起動テストを入れた記録です。初回は G8 に絞り、`main.py` を直接書き換えずに `pyxel.init` をモンキーパッチして `headless=True` を強制し、`Game()` 初期化と 1 フレーム描画までを通す設計を採りました。

## key_points

- 深層的目的は、壊れた版を子どもに届けない最後の防壁を作ることだった。
- 初回スコープは G8 の起動テストだけに絞り、G9 の 4 シナリオ走破は後日に回した。
- `tools/test_headless.py` が `main.py` の import、`Game()` 初期化、`update()`、`draw()` 1 回を headless で実行する。
- `pyxel.init` をモンキーパッチして `headless=True` を差し込み、production code を直接変更しない設計にした。
- import error、初期化 crash、1 フレーム未満で落ちる版は build failure にできる形を狙った。
- `make build` や承認キューとの本格統合は、この時点では未完了の後続タスクとして残した。

## important_quotes

- "壊れた版を子どもに届けない最後の防壁。"
- "G8（起動テスト）のみ実装。G9（4シナリオ）は後日"
- "これにより main.py のコードを一切変更しない。"

## open_questions

- G9 の移動、戦闘、行動、セーブの 4 シナリオをどの形で追加するか。
- `tools/test_headless.py` を build や approval queue にどの順序で組み込むか。
- headless gate と既存 pytest の役割分担をどこまで明文化するか。
