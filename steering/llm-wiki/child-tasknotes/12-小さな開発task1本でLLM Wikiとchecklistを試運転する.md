# 12 小さな開発 task 1 本で LLM Wiki と checklist を試運転する

- 推奨タイトル:
  - `YYYY年M月D日 小さな開発 task 1 本で LLM Wiki と checklist を試運転する`
- 目的:
  - wiki と checklist が実戦で役立つかを見る
- 入力:
  - current-state
  - query
  - architecture checklist
  - ux checklist
- 完了条件:
  - 小さな開発 task 1本で事前確認に使った記録が残る
  - 足りない導線や監査不足が別 note になっている
- 最初の一手:
  - 影響範囲の小さい UI か refactor task を1本選ぶ
- メモ:
  - ここで初めて「本番へ持っていけるか」を判断する
- 委任メモ:
  - 🟢 CC が試運転 task の選定から事前確認、実施、評価記録まで進めてよい
- 先に決めること:
  - 既存 open task を優先しつつ、必要なら派生した小 task を切ってよい

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 試運転 task 選定の判断ゲート

- **簡単すぎる**: checklist が機能しても価値が見えない（試運転として弱い）
- **複雑すぎる**: checklist で防げる範囲を超える（評価が曖昧になる）
- **適切**: 「ある程度判断が分かれる、影響が限定的、checklist の一部に該当する」もの

### 候補

| 候補 | 種別 | 試運転適性 | コメント |
|---|---|---|---|
| `steering/20260517 アプリ：battle-stale-spell-message.md` | 既存 open task（戦闘メッセージ残留） | ○ | 適切な難度。ただし「試運転」と「本物の開発」を兼ねるので評価が混ざる |
| 新規の小さな UI 改修 | 捨て試運転 | ◎ | 評価がクリアだが、現実の課題と切り離されるリスク |
| 新規の小さな refactor（例: `BattlePresenter` の小規模整理） | 捨て試運転 | ○ | architecture-checklist が刺さりやすい |

→ **既存 open task を兼ねる**方針を既定値にして、CC が候補を 1 本に絞って進めてよい。
→ 既存 open が不適切なら、派生した小 task を切る方へ CC が切り替えてよい。

### 試運転手順

1. task 候補を CC が 1 本に絞る
2. **事前**: checklist を 1 件ずつ確認
   - architecture-checklist
   - framework-checklist（09 で B を選んだ場合）
   - ux-checklist
3. **事前**: query で関連 area の current-state を確認
4. 実装
5. **事後**: checklist で気づけたこと／気づけなかったことを記録
6. 不足項目を別 note に切り分ける

### 評価軸

- checklist で防げた事故の数
- checklist が**ない**項目で起きた事故の数
- query が役立った場面の数
- query が**間違った**答えを返した数
- 全体としての所要時間（wiki が無い場合との比較感）

### 委任時の暴走パターン

- 「checklist 全項目 OK」とだけ報告する → 評価にならない
  - 防止策: 各項目で「OK / NA / 不足」と理由を求める
- 試運転 task を価値の薄い捨て課題へ逃がす
  - 防止策: まず既存 open task を優先し、切り替え理由を記録する

### 完了条件（拡張）

- 試運転 task 候補が 1 本に絞られている
- 試運転 task が選定されている
- 事前 checklist 確認の記録が残っている
- 事後評価（気づけた／気づけなかった）の記録が残っている
- 不足項目が別 note として切られている
- 「本番運用に持っていけるか」のユーザー判断が記録されている
