# 02 練習用プロジェクトの closed tasknotes 投入候補と順番を固定する

- 推奨タイトル:
  - `YYYY年M月D日 練習用プロジェクトの closed tasknotes 投入候補と順番を固定する`
- 目的:
  - docs を補う closed tasknotes の順番を決める
- 入力:
  - done tasknotes
  - closed notes
  - issue / PR メモ
- 完了条件:
  - raw に入れる tasknotes 一覧が決まっている
  - 古い順の投入順が決まっている
- 最初の一手:
  - closed note を時系列で並べ、docs 変更理由が強いものから残す
- メモ:
  - docs が薄い所を補う note を優先する
- 委任メモ:
  - 🟡 件数上限と選別基準があると委任しやすい
- 先に決めること:
  - どのタグ群まで raw に入れるか

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 素材の現状

- `steering/done/` に **115件**
- frontmatter は揃っている:
  ```yaml
  status: done
  priority: high
  scheduled: 2026-04-12
  dateCreated: 2026-04-12
  dateModified: 2026-04-12
  tags:
    - guardrails
    - ssot
    - codegen
  ```
- 命名 prefix（タグ的役割）:
  - `g1〜g15` / `guardrails-1〜6`: ガードレール工程
  - `j21〜j49`: journey 番号
  - `cj09〜cj44`: customer journey 番号

### 推奨手順（2段階フィルタ）

**段階 1: 機械的フィルタ（委任可）**

1. frontmatter の `tags` を全件抽出してヒストグラム化
2. 優先タグ候補で絞り込み:
   - `ssot`, `codegen`, `guardrails`（基盤系）
   - `journey-redesign`, `architecture`, `ux-policy`（方針系）
   - `cj`-prefix（customer journey 改訂系）
3. 時期で間引く: 古い方針転換点 + 直近1ヶ月の決定的なものだけ残す
4. **候補を 30件程度まで** に絞る

**段階 2: 本文判定（ユーザー判断含む）**

1. 30件の本文を読む
2. 「docs を変えた理由がこの note にしか書かれていない」ものを残す
3. 投入順: 古い順 + 方針転換点優先

### 委任時の暴走パターン

- 「念のため全件投入」傾向 → summary 生成コスト爆発、noise 増加
- 命名 prefix だけで分類 → 中身を読まずに誤分類
- 同じ work stream の隣接 note を**全部**入れる（例: `guardrails-1〜6` 全部）

**防止策**: 件数上限（30件）とタグフィルタを**先に与える**。AI が「漏れがあるかも」と聞いてきても増やさない。

### 出力フォーマット

```yaml
candidates:
  - file: steering/done/20260412-guardrails-1-ssot-codegen.md
    order: 1
    reason: SSoT + Codegen 基盤の方針確定
    docs_supplemented:
      - architecture_rules.yml
      - framework-rule.md
  - file: ...
```
