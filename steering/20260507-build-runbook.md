---
status: done
priority: normal
scheduled: 2026-05-07T00:00:00.000+09:00
dateCreated: 2026-05-07T00:00:00.000+09:00
dateModified: 2026-05-07T00:00:00.000+09:00
tags:
  - task
  - docs
  - infra
---

# 2026年5月7日 build 起動方法 runbook を docs に明文化

> 状態：④ Tasklist
> 次のゲート：完了確認（このタスクは自動委任で完遂）

---

## 1) Journey（どこへ行くか）

- **深層的目的**：AI（Claude）が毎回迷わずに build を起動できる。`PYTHONPATH=.` の付け忘れや
  `build_codemaker.py` / `build_web_release.py` のどちらを実行すべきかを毎回探さないで済む。
- **やらないこと**：build 仕様自体の変更（CJ44 確定版の方針はそのまま）。

### 背景

`steering/20260507-bundle-rebuild-after-bgm-ssot.md` の Discussion で気づきとして残した
「`build_release_artifacts.py` は `from tools.build_codemaker import ...` をしているため、
コマンドラインから直接実行するには `PYTHONPATH=.` 指定が必要。`build_web_release.py` 側は
`sys.path.insert` で済ませている。両者の起動方法を docs/architecture.md に書いておくと
次の人が悩まないかもしれない」を、本タスクで実施する。

ユーザー（AI コラボ運用）からの直接の指示：
> buildの起動方法については、記載するタスクノートを起票して下さい。
> ユーザーは主にaiで、毎回迷わずに起動できるのがマター

### 完了条件（CoVe 検証項目）

1. `docs/architecture.md` に「build の起動方法（runbook）」セクションが存在する
2. そのセクションが以下を明記している：
   - `python tools/build_codemaker.py`（dist/code-maker.zip だけを再生成する場合）
   - `PYTHONPATH=. python tools/build_web_release.py`（dist/ 配下の全 release artifacts を再生成する場合）
   - `PYTHONPATH=.` が必要な理由（`build_release_artifacts.py` が `from tools.build_codemaker import ...` を持つため）
   - 「BGM / pyxres / view を変更したあとは必ず両方を実行する」順序
3. AI 用エントリ `AGENTS.md` から該当セクションへのリンクが書ける（または既存リンクを再利用できる）こと
4. 既存テストが green のまま

---

## 2) Gherkin（完了条件）

```gherkin
Feature: AI が docs だけを見て build を再生できる
  Scenario: build runbook が docs/architecture.md に書かれている
    Given docs/architecture.md を読む
    When build の起動方法を探す
    Then "build の起動方法" or "build runbook" のセクションが見つかる
    And `python tools/build_codemaker.py` が記載されている
    And `PYTHONPATH=. python tools/build_web_release.py` が記載されている
    And `PYTHONPATH=.` が必要な理由が 1 文で書かれている

  Scenario: BGM / pyxres / view を変更した後の手順が明確
    Given 開発者または AI が src/scenes/*/view.py または assets/blockquest.pyxres を変更した
    When docs/architecture.md::build の起動方法 を読む
    Then 順序 (1) build_codemaker.py → (2) build_web_release.py が見える
    And 「dist/code-maker.zip / dist/pyxel.html / dist/pyxel.pyxapp / dist/play.html / dist/index.html が再生成される」の説明がある
```

---

## 3) Design

- 編集対象: `docs/architecture.md` のみ
- 追加するセクション位置: `## 3. 全体構造` の直後（または `4. ディレクトリ詳細` の前）に
  独立セクション `## 3.5 build の起動方法（runbook）` として追加
- 検証: 上記 Gherkin の Scenario を grep + 読みで確認

---

## 4) Tasklist

- [x] docs/architecture.md に runbook セクションを追記（`## 3.5 build の起動方法（runbook）`）
- [x] CoVe 検証（grep で 2 つのコマンドが現れること、PYTHONPATH 要否の説明があること）
- [x] 既存テスト全 green を再確認（**675 passed, 2 skipped**）
- [x] git status 確認

---

## 5) Result

`docs/architecture.md` に新規セクション `## 3.5 build の起動方法（runbook）` を追加した。
構成：

- `3.5.1 dist/code-maker.zip だけを再生成する` — `python tools/build_codemaker.py`、PYTHONPATH 不要
- `3.5.2 dist/ 配下の全 release artifacts を再生成する` — `PYTHONPATH=. python tools/build_web_release.py`、
  なぜ PYTHONPATH=. が必要か（`build_release_artifacts.py` が `from tools.build_codemaker import ...` を
  しているため）も明記
- `3.5.3 BGM / pyxres / view / scene を変更したときの順序` — pytest → release ビルド → bundle 自己検査
  → git status の 4 ステップ
- `3.5.4 よくある落とし穴` — `build_release_artifacts.py` を直接叩くと NG、pyxres は SSoT として
  `assets/blockquest.pyxres` を直接更新する 等

CoVe 検証結果（grep）:

```
docs/architecture.md
53:## 3.5 build の起動方法（runbook）
62:python tools/build_codemaker.py
72:PYTHONPATH=. python tools/build_web_release.py
77:- **PYTHONPATH=. が必要な理由**：…
91:   PYTHONPATH=. python tools/build_web_release.py
107:  必ず `PYTHONPATH=. python tools/build_web_release.py` の方を使うこと
```

→ Gherkin Scenario 2 件すべてパス。

最終 pytest: **675 passed, 2 skipped**（7.37s）

---

## 6) Discussion

### 結果

ユーザーからの「主に AI で運用するので毎回迷わずに起動できるのがマター」という要請に応える形で、
build runbook を `docs/architecture.md` に明文化した。
これで AI（Claude）は次回以降、`docs/architecture.md::3.5` を 1 回読むだけで build 手順が確定する。

### 気づき

- 同時並行で実施した `Game.current_bgm` 撤去（CJ44 確定版の追加整理）でも build 再生が必要だったため、
  この runbook の最初のユーザーは早速「次セッションの自分（AI）」になる
- 落とし穴セクション（3.5.4）に「`build_release_artifacts.py` を直接叩くと ModuleNotFoundError」と書いた。
  これは前タスクで実際に踏んだ罠なので、以降の AI が同じ罠に落ちないことを期待
- 将来 build 構造を変えるなら（例: `tools/build_codemaker.py` を package 化して PYTHONPATH 不要にする）、
  3.5.2 の「PYTHONPATH=. が必要な理由」の項を削除する形で改訂すること
