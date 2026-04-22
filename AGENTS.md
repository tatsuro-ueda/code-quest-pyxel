# AGENTS.md — Block Quest Pyxel の作業ルール

## これは何のファイルか

- このファイルは `/home/exedev/code-quest-pyxel` で作業する Codex への指示です。
- これは「読むだけのメモ」ではありません。**守るためのルール**です。
- この repo で迷ったら、まずこのファイルに戻ってください。

## いちばん大事な約束

この製品の根本価値は、**子どもでもゲームを編集できること**です。

ここでいう「編集できる」は、ただ技術的にファイルを開けることではありません。

- 子どもが見ている編集画面が分かりやすい
- 変えたものが、そのままゲームに出る
- 親や AI が隠れた仕組みを長く説明しなくても進められる

Codex は、この価値を弱くする提案を勝手にしてはいけません。

特に次は**勝手に下げない**でください。

- `Pyxel Code Maker`
- `Tilemap / Resource Editor / Sprite / Sound / Music` の編集面
- `子どもが自分で見た目や音を変えられる` という約束

`Pyxel Code Maker` は、この製品で**子どもが見た目や音を編集する正式な場所**です。
Codex は、ユーザーが明示的に頼んだ場合を除き、
`Code Maker を不要にする`
`Code Maker を脇役にする`
`resource 編集をやめる`
方向へ話を進めてはいけません。

## docs の扱い方

### docs は「参考資料」ではなく「要求」

- `docs/customer-journeys.md` は、作りたい体験の要求です。
- `docs/cj-gherkin-*.md` は、その体験について
  `何を約束するか`
  `何を壊してはいけないか`
  `どう確かめるか`
  を固定する要求です。

つまり:

- `CJ` は「どんな体験にしたいか」
- `CJG` は「その体験をどう守るか」

を表します。

Codex は、これらを**読んで終わり**にしてはいけません。
**従って実装と判断を合わせる**必要があります。

### docs と code が食い違ったら

- code は「いま実際に動いているもの」です。
- docs は「この製品が守るべき約束」です。

この2つが食い違ったら、
`code があるから正しい`
とは考えないでください。

正しい考え方はこれです。

- `code = 現在の実態`
- `docs = 守るべき要求`
- 食い違い = **未実装 / バグ / 仕様ずれ**

このずれを見つけたら、
言い訳せず、
曖昧にせず、
`どこがずれているか`
を明記してください。

## ユーザーへの向き合い方

- ユーザーに「どう指示すればいいか」を背負わせないでください。
- ユーザーに「どの道具を先に使うべきか」を考えさせないでください。
- ユーザーが「まだ違う」と言ったら、まず現物を確認してください。
- 先に実装の理屈を守らないでください。先に体験のずれを見てください。

Codex の仕事は、
`ユーザーの指示を技術的に翻訳すること`
であって、
`ユーザーに Codex の使い方を教育させること`
ではありません。

## まず何を正とするか

### 人が見ているものを先に正とする

子どもや親が見ているものが主語の問題では、
その見えているものを最初の正として扱ってください。

たとえば:

- `Code Maker`
- `Resource Editor`
- `Tilemap`
- `Sprite`
- `Sound`
- `Music`
- `index.html`
- 共有 URL
- save/load の実際の見え方

です。

`runtime code を直した`
`build script を直した`
だけで終わりだと思ってはいけません。

人が見ているものが

- `zip`
- `.pyxres`
- selector page
- 配信中の HTML
- 実際の save data

なら、**その実物**を見て確認してください。

## 道具の選び方

### Codex が自分で選ぶ

道具選びは Codex の責任です。
ユーザーに毎回言わせないでください。

### 問題ごとの最初の確認先

| 問題の主語 | 最初に見るもの |
|---|---|
| `Pyxel Code Maker`, `Resource Editor`, `Tilemap`, `Sprite`, `Sound`, `.pyxres` | `pyxel` MCP |
| Web ページ, selector, wrapper, 公開 URL | ブラウザ / 実 endpoint |
| build 生成物, zip, 配布物 | できあがったファイルの中身 |
| save/load | 実際の save payload |
| ゲーム画面の動き | 実際の画面 / 実行結果 |

この repo では特に次を守ってください。

- `Code Maker` や `.pyxres` が出てきたら、まず resource の実体を見る
- `Tilemap` や `Resource Editor` の話なら、まず `pyxel` MCP を使う
- build script の推測は、そのあとにする

## Pyxel Code Maker と `.pyxres` の扱い

### 役割の分担

- 子どもや親は `Pyxel Code Maker` で見た目や音を編集する
- Codex は code, build, packaging, guardrail, test を整える
- Codex は `.pyxres` の**実体を直接いじらない**
- Codex は `.pyxres` の中身を変える依頼を、自分の実装タスクとして抱え込まない

### Codex がやってよいこと

- `.pyxres` を `pyxel` MCP で調べる
- `Code Maker` 互換 build を直す
- `zip` に正しい `.pyxres` が入るようにする
- `Code Maker` で見えるものと実ゲームの一致を確認する
- `.pyxres` を触る必要がある依頼を、人の Code Maker 作業と Codex の build / verify 作業に切り分ける

### Codex が勝手にやってはいけないこと

- `.pyxres` をテキストとして直接編集する
- 子どもの編集面を内部都合で別のものに置き換える
- `Code Maker` を不要と判断する
- `resource は編集対象から外す方がよい` と、要求に逆らって勝手に結論づける

### runtime が `.pyxres` を勝手に更新する設計について

これは**特に慎重に扱う**こと。

もし runtime が `.pyxres` を自動更新しているなら、
Codex はそれを当然と思わず、
次を必ず確認してください。

- `CJ26`
- `CJG23`
- `CJG24`
- `CJG26`
- `CJG37`
- `CJG41`

つまり、
`人が Code Maker で触るはずの実体を runtime が勝手に書き換えてよいのか`
を、体験の約束から確かめてください。

## いまの実装の事実

- runtime の入口は `main.py`
- `index.html` は比較ページ
- `production/play.html` は `production/pyxel.html` を包む本番ラッパー
- `development/play.html` は `development/pyxel.html` を包む開発版ラッパー
- `production/pyxel.html` と `production/pyxel.pyxapp` は本番配布物
- `development/pyxel.html` と `development/pyxel.pyxapp` は開発版配布物
- 用語は `開発版` / `本番`
- 関連 metadata は `development_meta.json`

## まず読むべき文書

常に重要:

- `docs/customer-journeys.md`
- `docs/cj-gherkin-platform.md`
- 必要な分野の `docs/cj-gherkin-*.md`
- 関係する `steering/`
- 関係する `steering/done/`

次の分野を触る前は、必ず関連 docs を先に読んでください。

- build / release
- `index.html`
- `production/play.html`
- `development/play.html`
- 開発版 / 本番 / 承認フロー
- `top_changes.json`, `development_meta.json`
- runtime / deploy / logs / 公開 URL
- `Code Maker` 連携

最低限、実装とテストも確認してください。

- `tools/build_web_release.py`
- `test/test_build_web_release.py`

## done の意味

`done` は、
`コードがある`
`テストが通る`
だけではありません。

**人がタイトルを見て自然に期待する状態**です。

たとえば:

- ログが見える → 本当に公開アクセスが記録されている
- URL が使える → 本当にその URL で見られる
- Code Maker で編集できる → 本当に開いて編集して Run できる
- 編集面が真実 → 編集画面で見えたものが、そのままゲームに出る

ユーザーが「違う」と言ったときは、
まず現物確認をしてください。
先に defending しないでください。

## steering note の書き方

runtime / deploy / logs / 公開 URL / build pipeline / Code Maker 連携の note では、
閉じる前に次をそろえてください。

- 人間は `done` を見て何が本当だと思うか
- それを証明する本物の path / process / file は何か
- 何をどう live に確認したか

新しい note は `steering/_template.md` を使ってください。

## データの流れ

生成ファイルは直接編集しません。

```text
assets/*.yaml
  -> tools/gen_data.py
  -> src/generated/*.py
  -> src/game_data.py
  -> main.py
```

## 直接編集してはいけないもの

| Path | 理由 | 代わりにやること |
|---|---|---|
| `src/generated/*.py` | YAML から自動生成される | `assets/*.yaml` を直して `python tools/gen_data.py` |
| `*.pyxres` | 人が Code Maker で触る resource 本体 | Pyxel Code Maker で編集し、Codex は build / verify で支える |

## 直接 import してはいけないもの

| Path | 理由 | 代わりにやること |
|---|---|---|
| `from src.generated.*` | loader を通す前提 | `from src.game_data import ENEMIES` など |

## 変更したら毎回やること

```bash
python tools/gen_data.py    # YAML を変えたとき
python -m pytest test/ -q
```

- テストが落ちたら、そのままにしないでください
- 失敗が既知なら、その理由をはっきり書いてください
- 「今回は docs だけだからテスト不要」と決めつけないでください

## 追加の確認コマンド

```bash
python tools/test_headless.py
python tools/test_save_compat.py
python tools/test_web_compat.py
```

## この repo での基本ルール

1. 判断はこの repo の中で完結させる
2. docs は読むだけでなく従う
3. `customer-journeys` と `CJG` に逆らう方向へ勝手に最適化しない
4. `Pyxel Code Maker` を子どもの正式な編集面として守る
5. `*.pyxres` の実体は人が Code Maker で編集する
6. Codex は build, test, packaging, guardrail を整えてその体験を支える
7. 変更後は `pytest` を回す
8. セリフや世界観の言い回しは今の雰囲気にそろえる

## 作業前の短い確認

- [ ] 今回の主語は何か。子どもが見ているものか、内部実装か
- [ ] 関連する `CJ` / `CJG` を読んだか
- [ ] docs と code のずれを把握したか
- [ ] 最初に見るべき実物を見たか
- [ ] ユーザーに道具選びを押しつけていないか
- [ ] `pytest` まで含めて終えるつもりか
