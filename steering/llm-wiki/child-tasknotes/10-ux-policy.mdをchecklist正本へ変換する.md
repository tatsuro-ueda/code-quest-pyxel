# 10 ux-policy.md を checklist 正本へ変換する

- 推奨タイトル:
  - `YYYY年M月D日 ux-policy.md を checklist 正本へ変換する`
- 目的:
  - UX 方針を開発前に確認できる checklist にする
- 入力:
  - `ux-policy.md`
  - UI 関連の tasknotes
- 完了条件:
  - `ux checklist` 相当ができている
  - 危険操作や確認 UI 方針を見落としにくい
- 最初の一手:
  - ux-policy の禁止事項と推奨事項を確認項目に変換する
- メモ:
  - UX 正本が未作成でも、CC が初版 `docs/ux-policy.md` を起こして前進してよい
- 委任メモ:
  - 🟢 CC が既存 docs と tasknotes から初版 `ux-policy.md` を作ってから checklist 化してよい
- 先に決めること:
  - `docs/ux-policy.md` は CC が新規作成してよい

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 入力欠落

下書きの入力 `ux-policy.md` は **存在しない**。代替候補：

| 候補 | サイズ | 適性 |
|---|---|---|
| `docs/customer-journeys.md` | 95KB | △ journey から ux 方針を抽出する作業が要る |
| `docs/product-requirements-av.md` | 17KB | ○ UI / AV 方針を一部含む |
| `docs/product-requirements-narrative.md` | 10KB | ○ メッセージ表記方針を含む |
| `docs/customer-jobs.md` | 7.8KB | ○ 子どもの jobs（観点として使える） |
| メモリ: `project_ui_policy.md` | - | ◎ 子ども向けひらがな表記、iframe方式Web配信、ボタンフェードアウト |

### 09 との重大な違い

`architecture_rules.yml` のような構造化された正本は ux 側には**ない**。

→ 単純な「変換」では成立しない。**CC が `ux-policy.md` 自体を新規作成**してから checklist 化するのが筋。

### 推奨アプローチ

**事前ステップ: CC が ux-policy.md を新規作成**

1. メモリ `project_ui_policy.md` を起点に骨格を作る
2. `product-requirements-av.md` `product-requirements-narrative.md` から UI / 表記方針を抽出
3. `customer-journeys.md` から「ここで子どもがハマる」観点を抽出
4. closed tasknote から UI 方針が変わった節目を補強
5. `docs/ux-policy.md` として確定（→ 01 の正本棚卸しに追加）

**本ステップ: ux-checklist.md に変換**

ux-policy.md ができたら 09 と同じ翻訳手順で checklist 化。

### checklist の最低項目（メモリ + product-requirements から先取り）

- [ ] 子ども向けひらがな表記になっているか
- [ ] 漢字を使う場合、ふりがな or 文脈で意味が取れるか
- [ ] 危険操作（保存上書き、データ削除）に確認 UI があるか
- [ ] ボタンのフェードアウト（押した実感）が機能しているか
- [ ] iframe 方式の Web 配信で全画面プレイができるか
- [ ] 戦闘・対話・移動で UI 要素が重ならないか（直近 open task の事例）
- [ ] エラー時の文言が子どもに伝わるか

### 委任時の暴走パターン

- `customer-journeys.md` から抽出 → checklist が journey の要約になる
  - 防止策: 「customer-journey から方針を**抽出**するが、checklist 項目は方針側に寄せる」
- 大人向けの UX 原則を持ち込む（Material Design 等）
  - 防止策: 子ども向け前提（メモリ参照）を tasknote 冒頭に明記
- `ux-policy.md` を作らずに直接 checklist 化 → 根拠が消える
  - 防止策: 事前ステップを必須にする

### 完了条件（拡張）

- `docs/ux-policy.md` が新規作成されている
- ux-policy.md が 01 の正本リストに追加されている
- `ux-checklist.md` 相当が出ている
- 子ども向け前提が明記されている
- 危険操作 UI 項目が含まれている
