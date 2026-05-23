# 06 練習用プロジェクトで read-only query を通す

- 推奨タイトル:
  - `YYYY年M月D日 練習用プロジェクトで read-only query を通す`
- 目的:
  - generated knowledge だけで答えを返せる入口を作る
- 入力:
  - indexes
  - current-state
  - summaries
- 完了条件:
  - query が根拠リンク付きで短く答える
  - 情報不足なら不足を返す
- 最初の一手:
  - `architecture は何か` のような質問で最初の spot check をする
- メモ:
  - query は raw を更新しない
- 委任メモ:
  - 🟢 read-only ルールと query 方式は CC が既定値を採って進めてよい
- 先に決めること:
  - QA 蓄積は `A + B のハイブリッド` を既定値としてよい

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 判断ゲート 1: query 実装方式

親note には「query は read-only bridge」とあるだけで、実装が未定義：

| 選択肢 | 説明 | 利点 | 欠点 |
|---|---|---|---|
| A: 手動 QA 蓄積 | `wiki/query/*.md` に質疑応答を残す | 軌跡が残る、Karpathy 流のシンプルさ | 都度書く手間 |
| B: Claude/Codex 直問 | `wiki/` を読ませる規約だけ作る | 自動化される | 軌跡が残らない、再現性低 |
| C: SQLite + SQL | summaries を DB 化 | 高速検索、構造的 | 学習コスト高、scale するまで不要 |

→ 練習段階は **A + B のハイブリッド** を既定値にしてよい：
- ある程度蓄積したい質問は A（`wiki/query/<topic>.md`）
- 一回限りの質問は B（Claude Code に投げる）

### 判断ゲート 2: read-only を守る仕組み

原則表明だけでは AI が破る。**運用ルール**として書く必要がある：

- query セッション中、`Edit` / `Write` で `wiki/raw/` を更新しない
- query が「raw が古い」と判断した場合: `wiki/wiki/maintenance.md` に追記して人が後で対応
- query 結果に必ず**根拠リンク**（summary のパス）を付ける
- 情報不足なら「不足」と返す（推測で埋めない）

### spot check 用の質問セット

最初の動作確認で使う質問（暫定）：

1. `code-quest-pyxel の architecture の核は何か`
   - 期待: `architecture_rules.yml` の principles 要点 + 根拠リンク
2. `子ども向けの UI 表記ルールは何か`
   - 期待: ひらがな表記方針 + 根拠リンク（product-requirements-* もしくは ux-checklist）
3. `SSoT ポリシーとは何か`
   - 期待: YAML → gen_data.py → generated 一方通行 + 根拠
4. `Code Maker の責務は何か`
   - 期待: architecture_rules.yml `code_maker_primary_editor` + 根拠
5. `battle の current-state は`
   - 期待: areas/battle/current-state.md の要約

### query 出力テンプレ

```markdown
## Q: <質問>

### A

<2〜5 文の答え>

### 根拠

- `wiki/summaries/knowledge/<file>-summary.md`
- `wiki/areas/<area>/current-state.md`

### 情報不足（あれば）

- ...
```

### 委任時の暴走パターン

- **「ついでに raw を最新化します」** ← 最大の暴走パターン
  - 防止策: 03 の README + この tasknote で明示禁止
- 推測で埋める（根拠を出さない）
  - 防止策: 出力テンプレに「根拠」セクションを必須化
- summary を経由せず raw を直接読みに行く
  - 防止策: query スコープは summaries / current-state / indexes だけ
