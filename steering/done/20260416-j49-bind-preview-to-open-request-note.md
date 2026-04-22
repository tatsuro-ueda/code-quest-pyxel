---
status: done
priority: high
scheduled: 2026-04-16T07:30:00+00:00
dateCreated: 2026-04-16T07:30:00+00:00
dateModified: 2026-04-16T07:56:00+00:00
tags:
  - task
  - j49
  - j31
  - j33
  - preview
  - selector
  - build
---

# 2026年4月16日 J49 次の依頼が来たら前の preview を current に繰り上げる

> 状態：(5) Discussion
> 次のゲート：（ユーザー）新しい依頼を起票したときの運用をこのまま回す

---

## 1) 改善対象ジャーニー

- **根拠となるカスタマージャーニー**：`docs/customer-journeys.md` の `CJ31: 子どもが変更を承認する`
- **関連するカスタマージャーニー**：`docs/customer-journeys.md` の `CJ33: 子どもが変更を選んで適用する`
- **深層的目的**：新しい依頼が来たとき、前のおためしばんを自動で current に回しつつ、トップページの `おためしばん` には今の依頼の差分だけが出るようにする
- **やらないこと**：この note で個別のゲームロジック差分を足すこと、selector の見た目だけを変えること

### 人間の期待

- **この note が `done` なら、人間は何が成立していると思うか**：新しい preview 依頼ノートで build すると、前のおためしばんは current に繰り上がり、新しい差分だけが `おためしばん` に残る。今の依頼に対応する preview をまだ作っていないなら card は出ない
- **その期待を裏切りやすいズレ**：前のおためしばんがずっと preview のまま残る、新しい preview の説明に前回ぶんまで混ざる、`main.py` が古いままで current / preview の役割が逆転する
- **ズレを潰すために見るべき現物**：`steering/20260416-j48-preview-must-reflect-current-request.md`、`tools/build_web_release.py`、`test/test_build_web_release.py`、`preview_meta.json`、`main.py`、`main_preview.py`、`index.html`

### 現状

- 現在の build は `preview_meta.json` の request note と open note の一致で preview card を出し分けようとしている
- しかし新ルールでは、それだけでは足りず、次の依頼が来た瞬間に前の preview を current に繰り上げる必要がある
- いまのままだと、古い preview を隠せても `main.py` は古いままで、新しい preview の差分説明に前回ぶんまで混ざりうる

### 今回の方針

- preview build 時に、現在の preview 依頼ノートを `preview_meta.json` に記録しつつ、その時点の `main_preview.py` を `.preview_snapshot.py` として保存する
- 次の preview build で open preview note の path が変わっていたら、保存済み snapshot を `main.py` に反映してから新しい preview を組み立てる
- 通常 build 時には、現時点で有効な preview 依頼ノートの path と `preview_meta.json` の記録が一致する場合だけ `おためしばん` を出し、まだ今の依頼向け preview ができていなければ隠す

---

## 2) カスタマージャーニーgherkin（完了条件）

### シナリオ1：正常系

> {前の preview が残っている} で {次の preview 依頼ノートで build する} と {前の preview が current に繰り上がり、新しい差分だけが `おためしばん` に残る}

### シナリオ2：異常系

> {今の依頼に対応する preview source をまだ作っていない} で {通常 build を実行する} と {前の preview を今の依頼の `おためしばん` として表示しない}

### シナリオ3：回帰確認

> {前の preview を current に繰り上げたあと} で {新しい preview を build する} と {トップページの説明は今回の差分だけを説明する}

### 対応するカスタマージャーニーgherkin

- `docs/cj-gherkin-platform.md` `CJG31`
- `Scenario: 次の依頼が来ると前のおためし版がもとのまま版へ繰り上がる`
- `docs/cj-gherkin-platform.md` `CJG33`
- `Scenario: 変更一覧は今の依頼に対応するおためし版だけを説明する`
- `docs/cj-gherkin-platform.md` `CJG33`
- `Scenario: 前のおためし版を繰り上げたあとは新しい差分だけを説明する`

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：`superpowers:systematic-debugging`、`superpowers:test-driven-development`
- **MCP**：追加なし

### 調査起点

- `tools/build_web_release.py`
  preview metadata の生成、繰り上げ snapshot の保存、通常 build 側の preview 表示条件
- `test/test_build_web_release.py`
  preview の繰り上げと差分説明を固定しやすい既存 fixture とテスト群
- `steering/*.md`
  現在の preview 依頼ノートをどう特定するか

### 実装案

- `steering/` から `status: open` かつ `tags` に `preview` を持つ task note を探す
- preview build 時は、その note の path と trace 用 hash を `preview_meta.json` に記録し、同時に現在の `main_preview.py` を `.preview_snapshot.py` として保存する
- 次の preview build で open preview note の path が変わっていたら、保存済み snapshot を `main.py` へ反映してから、新しい `main_preview.py` との差分を取り直す
- 通常 build 時は、`preview_meta.json` の note path が現行の open preview note と一致する場合だけ preview card を出す
- open preview note が 0 件または複数件なら、preview は曖昧として隠す

### 検証方針

- 先にテストで「前の preview を current に繰り上げずに build すると説明が前回ぶんまで混ざる」ことを Red にする
- 次に「note が変わったが今の依頼向け preview がまだないとき preview を隠す」ケースを Red にする
- 実装後、targeted test、full test、build を順に回して `main.py` / `preview_meta.json` / `index.html` が新ルールどおりに揃うことを確認する

---

## 4) Tasklist

- [x] 旧前提の J49 を新ルール用に組み替える
- [x] 前の preview を current に繰り上げる failing test を追加する
- [x] 今の依頼向け preview がまだないとき隠す既存テスト群を新ルールに合わせて維持する
- [x] build ロジックを修正する
- [x] build 結果と note を更新する

---

## 5) Discussion（記録・反省）

> Observe → Think → Act を刻む。未来の自分が復元できることが目的。

### 2026年4月16日 07:30（旧起票）

**Observe**：`CJ31/CJG31` では `おためしばん` の意味を明確化したが、実装はまだ `main_preview.py` と `preview_meta.json` の整合しか見ていなかった。  
**Think**：その時点では「今の依頼」を build が判断できる anchor として preview 依頼ノートを使うのが最小に見えた。  
**Act**：J49 を起票し、`おためしばん` を現在の open preview note に結びつける実装へ進もうとした。

### 2026年4月16日 08:15（方針修正）

**Observe**：ユーザーから「`おためしばん` は原則として承認で、次の更新が来たら前のおためしばんが本番になる」と追加ルールが出た。前の案は preview を隠せても、前のおためしばんを current に回すところまでは扱えていなかった。  
**Think**：このルールでは、`request note が一致するか` だけでは不十分で、前のおためしばんを source レベルで current に繰り上げる仕組みが必要になる。  
**Act**：J49 を「次の依頼が来たら前の preview を current に繰り上げる」実装 note として組み替え、snapshot を使った roll-forward と新しい差分だけの説明へ設計を更新した。

### 2026年4月16日 07:56（実装・検証完了）

**Observe**：`test/test_build_web_release.py` に roll-forward の Red テストを足すと、preview の差分検出が unified diff の文脈行まで読んでおり、前回ぶんの説明が新しい preview に混ざっていた。さらに、同じ note を編集しただけでも hash 変化で「新しい依頼」と誤判定する余地があった。  
**Think**：必要なのは `main_preview.py` の前回版を保存しておく snapshot と、「同じ依頼かどうか」は note の path で判定することだった。差分説明は changed lines だけを見るようにしないと、繰り上げ後も前回ぶんが残る。  
**Act**：`tools/build_web_release.py` に `.preview_snapshot.py` の保存、`roll_forward_approved_preview()`、changed-lines ベースの preview change list、snapshot cleanup を実装した。検証は `python -m pytest test/test_build_web_release.py -q` で `27 passed`、`python -m pytest test/ -q` で `171 passed, 2 skipped`、`make build` 完走、`python tools/build_web_release.py --preview` 完了、`python tools/test_web_compat.py` は sandbox 外で `OK: Web版テスト通過（10秒間クラッシュ・致命的エラーなし）` を確認した。
