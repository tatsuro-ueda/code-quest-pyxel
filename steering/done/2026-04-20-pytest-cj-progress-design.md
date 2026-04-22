# Pytest CJ Progress Design

## Goal

`pytest` を実行するたびに、repo 内の `CJ` / `CJG` の達成率と未達一覧を末尾へ自動表示し、現在の完成度を数字で把握できるようにする。

## Problem

今は `pytest` が「テストが通ったか」だけを返し、プロダクトとして何％の約束を満たしているかは人が docs を読んで手で判断する必要がある。これでは、

- 進捗の全体像が見えにくい
- `部分実装` や `未実装` が見落とされやすい
- 子ども向けの体験要求とテスト結果が切り離される

という問題がある。

## Scope

この設計は次だけを対象にする。

- `pytest` 実行終了時の自動サマリー表示
- `CJ` / `CJG` 達成率の厳密な計算ルール
- 未達一覧の表示
- そのための parser / reporter の配置

この設計では次は扱わない。

- `CJG` と個別テストケースの完全トレーサビリティ付与
- `部分実装` の重み付き採点
- docs の内容自体の書き換え
- build や web UI への進捗表示

## Source of Truth

達成率の SoT は docs の `実装状況` とする。

- `CJ` 一覧: `docs/customer-journeys.md`
- `CJG` 一覧とステータス: `docs/cj-gherkin-*.md`

判定ルールは厳密にする。

- `実装済み` のみ: 達成
- `部分実装` を含む: 未達
- `未実装` を含む: 未達
- `時間目標` を含む: 未達

つまり、「少しできている」は達成率には入れない。

## Metric Definitions

### CJG 達成率

番号付き `CJG` 全体を母数にする。

- 分子: `実装状況` が `実装済み` のみで構成される `CJG`
- 分母: 全 `CJG`

現時点の docs を基準にすると、おおむね次の値になる。

- `CJG` 総数: `40`
- 純粋に達成: `3`
- 達成率: `3 / 40 = 7.5%`

### CJ 達成率

`CJ` 全体を母数にする。

- 分子: 同じ番号の `CJG` が存在し、その `CJG` が達成扱いの `CJ`
- 分母: `docs/customer-journeys.md` にある全 `CJ`

番号対応の専用 `CJG` がない `CJ` は未達扱いにする。現時点では `CJ28` と `CJ42` が該当する。

現時点の docs を基準にすると、おおむね次の値になる。

- `CJ` 総数: `41`
- 達成: `3`
- 達成率: `3 / 41 = 7.3%`

## Output Format

`pytest` の最後に、通常のテストサマリーの後ろへ進捗サマリーを追加する。

表示内容は次の順にする。

1. `CJ` 達成率
2. `CJG` 達成率
3. 対応 `CJG` がない `CJ`
4. 未達の `CJ`
5. 未達の `CJG`

例:

```text
=========================== CJ Progress ===========================
CJ: 3/41 achieved (7.3%)
CJG: 3/40 achieved (7.5%)

CJ without dedicated CJG:
- CJ28 新しいエリアをまるごと追加する
- CJ42 子どもが冒険を最後までやり切れる

Unmet CJ:
- CJ01 はじめてのタイル配置
- CJ02 道を作る
...

Unmet CJG:
- CJG01 はじめてのタイル配置 [部分実装, 時間目標]
- CJG02 道を作る [部分実装, 未実装, 時間目標]
...
=================================================================
```

## Architecture

最小構成は 2 ファイルに分ける。

### 1. `tools/cj_progress_report.py`

責務:

- docs を読む
- `CJ` / `CJG` を parse する
- ステータスを正規化する
- 達成率を計算する
- 表示用データを返す

このモジュールは pure function 中心にする。`pytest` API は持たない。

想定インターフェース:

- `load_cj_catalog(project_root: Path) -> list[CJEntry]`
- `load_cjg_catalog(project_root: Path) -> list[CJGEntry]`
- `build_progress_snapshot(project_root: Path) -> ProgressSnapshot`
- `render_progress_summary(snapshot: ProgressSnapshot) -> str`

### 2. `test/conftest.py`

責務:

- `pytest_terminal_summary` にフックする
- `tools.cj_progress_report` を呼ぶ
- 失敗しても pytest 自体を落とさず、進捗サマリーだけを安全に出す

方針:

- parser error や docs 不整合があっても、テスト実行結果そのものは潰さない
- その代わりサマリーに `CJ progress unavailable: ...` と出す

## Parsing Rules

### `CJ`

`docs/customer-journeys.md` から次の形式だけを拾う。

- `### CJ01: はじめてのタイル配置`

抽出する値:

- `id`: `CJ01`
- `title`: `はじめてのタイル配置`

### `CJG`

`docs/cj-gherkin-*.md` から次の形式だけを拾う。

- `## CJG01: はじめてのタイル配置`

さらに、そのブロック内の `実装状況:` の箇条書きから種別を拾う。

- `- \`実装済み\`: ...`
- `- \`部分実装\`: ...`
- `- \`未実装\`: ...`
- `- \`時間目標\`: ...`

同じ `CJG` に複数種別がある場合は、それを全部保持する。

## Edge Cases

### `CJ` に対応 `CJG` がない

現時点では `CJ28`, `CJ42` が該当する。未達として数え、専用一覧にも出す。

### `CJG` があるが対応 `CJ` がない

現時点では `CJG37` が該当する。`CJG` 達成率の母数には含めるが、`CJ` 達成率には使わない。

### docs の移動や rename

ファイル path は固定せず、`docs/cj-gherkin-*.md` の glob で読む。

### docs の書式崩れ

規定形式に一致しない場合は parser で拾わず、サマリーに warning を出せるようにする。

## Testing Strategy

次のテストを追加する。

### `test/test_cj_progress_report.py`

- `CJ` 総数と `CJG` 総数が現行 docs と一致する
- `純粋に達成` の `CJG` が `CJG16`, `CJG20`, `CJG32` である
- `CJ28`, `CJ42` が `CJ without dedicated CJG` として出る
- `CJG37` が `CJG` には含まれるが `CJ` 側には対応しない
- 厳密判定で `部分実装` が未達になる
- `render_progress_summary()` が必要情報を含む

### `test/conftest.py` の統合確認

専用の terminal snapshot までは不要とし、まずは reporter 関数単体のテストに寄せる。`pytest` hook 自体は薄く保つ。

## Alternatives Considered

### A. `test/conftest.py` に全部書く

利点:

- ファイル数が少ない

欠点:

- parser と pytest hook が混ざる
- 単体テストしにくい

今回は不採用。

### B. 重み付き採点を先に入れる

利点:

- 進捗感が出やすい

欠点:

- 50% の意味が主観的になる
- まず必要なのは厳密でぶれない数字

今回は不採用。

### C. `CJG` と各テストを完全マッピングする

利点:

- 一番強い保証になる

欠点:

- 今すぐには重い
- docs とテストの両方へ大きい整備が必要

将来の発展案として残す。

## Recommended Approach

`tools/cj_progress_report.py` + `test/conftest.py` の 2 段構成で、まず docs SoT の厳密判定を毎回の `pytest` に載せる。

これにより、

- 実装コストを小さく抑えつつ
- 毎回同じルールで
- `CJ` / `CJG` の達成率を数字で見えるようにできる

## Rollout

1. reporter module を追加する
2. 単体テストを追加する
3. `test/conftest.py` で `pytest_terminal_summary` に差し込む
4. `python -m pytest test/ -q` で通常サマリーの後ろに進捗が出ることを確認する

## Acceptance Criteria

- `pytest` の最後に `CJ` / `CJG` 達成率が必ず出る
- `CJ` / `CJG` の分母と分子が docs から再計算される
- `部分実装`, `未実装`, `時間目標` は未達扱いになる
- `CJ28`, `CJ42` が対応 `CJG` なしとして出る
- `CJG37` が `CJG` 集計には含まれる
- parser / reporter は単体テストで固定される
