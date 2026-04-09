# 構造設計書: タイルマップ編集の反映バグ修正

`gherkin.md` シナリオ5（★核心）を解決する。Code Makerで編集したタイルが「黙って草に化ける」バグを修正する。

---

## バグの全体像

```mermaid
graph TD
    subgraph INIT["初期化時（.pyxres不存在）"]
        A1[world_map<br/>T_GRASS, T_TREE等] --> A2[_bake_world_to_tilemap]
        A2 --> A3[_pixel_pos_for_tile<br/>オートタイル解決]
        A3 --> A4[tilemap 0 に書き込み<br/>グリッド座標]
        A4 --> A5[pyxel.save .pyxres]
    end

    subgraph EDIT["Code Maker編集"]
        A5 --> B1[ユーザーがタイルを配置]
        B1 --> B2[tilemap 0 が書き換わる]
        B2 --> B3[.pyxres保存]
    end

    subgraph RESTART["ゲーム再起動（.pyxres存在）"]
        B3 --> C1[pyxel.load .pyxres]
        C1 --> C2[_build_reverse_tile_map<br/>逆引き辞書生成]
        C2 --> C3[_derive_world_from_tilemap<br/>tilemap→world_map復元]
        C3 --> C4{逆引き成功?}
        C4 -->|成功| C5[正しいタイルID]
        C4 -->|失敗| C6[T_GRASS<br/>★黙って草に化ける]
    end

    style C6 fill:#a44,color:#fff
    style B1 fill:#49a,color:#fff
```

---

## 根本原因（実機検証済み）

> **`tu * 8` の座標計算は正しい**ことを実機検証で確認済み（2026-04-09）。tile_bank のピクセル座標(col*16)と tilemap のグリッド座標(tu=col*2) から `tu*8 = col*16` で一致する。

| # | 原因 | 箇所 | 影響 |
|---|---|---|---|
| ~~①スケーリング不一致~~ | ~~実機検証で否定。`tu*8` は正しい~~ | - | - |
| ②デフォルト値上書き | `.get(key, T_GRASS)` で逆引き失敗時に全てT_GRASSになる | main.py 1464行 | 「草に化ける」の直接原因 |
| ③オートタイル非復元 | 初期化時は `_pixel_pos_for_tile` で変種選択するが、復元時は基底タイルしか返さない | main.py 1436行 vs 1464行 | 道・水辺が単色になる |
| ④逆引き辞書の登録漏れ★ | **tile_bankに5タイルしかないが、tilemapには23種のキーが出現**。path/shore variantの逆引き登録が不十分で490/2500セル(20%)がミスする | main.py 1332-1346行 | 全ミスがT_GRASSに化ける |

### 実機検証データ（2026-04-09）

```
tilemap unique keys: 23
tile_bank (basic tiles only): 5
Hit: 2010 / 2500 (80%)
Miss: 490 / 2500 (20%) ← これが草に化けるセル
```

### 逆引き辞書の登録漏れの詳細

```mermaid
graph TD
    subgraph REG["_build_reverse_tile_map の登録"]
        R1["tile_bank: 5タイル<br/>(0,0) (16,0) (32,0) (48,0) (64,0)"]
        R2["path_variant_bank: 10変種"]
        R3["shore_variant_bank: 4変種"]
        R4["water2: 1"]
        R1 --> R5["tile_id_by_pixel<br/>計20キー登録"]
        R2 --> R5
        R3 --> R5
        R4 --> R5
    end

    subgraph TM["tilemap[0] に出現するキー"]
        T1["23種類のユニークキー"]
    end

    R5 -.->|"3キーが未登録<br/>→ 490セルがミス<br/>→ T_GRASSに化ける"| T1

    style T1 fill:#a44,color:#fff
```

**次回セッションの実装で確認すべきこと**: `_build_reverse_tile_map` 実行時点で `tile_id_by_pixel` に何キー登録されているか、tilemapの23キーのうちどれが漏れているかを特定する。

---

## 設計判断

| # | 論点 | 決定 | 理由 | 代替案と却下理由 |
|---|---|---|---|---|
| ~~D1~~ | ~~逆引きキーの座標系~~ | ~~実機検証で `tu*8` が正しいことを確認。修正不要~~ | 2026-04-09 検証済み | - |
| D1' | 逆引き辞書の登録漏れ修正 | **`_build_reverse_tile_map` で全variantキーが正しく登録されるよう修正**。実行時のキー数とtilemapのキー数が一致することを検証 | 490/2500セル(20%)がミスする根本原因 | - |
| D2 | 逆引き失敗時の挙動 | **`T_GRASS` のまま**だが、①の修正で逆引き失敗が発生しなくなる。デバッグ用にwarningログを追加 | デフォルト値自体は安全側に倒す設計として正しい。問題は逆引きが壊れていたこと | 例外を投げる: ゲームが落ちる（KA2違反） |
| D3 | オートタイル復元 | `_derive_world_from_tilemap` 実行後に **`_rebake_autotiles`** を呼び、world_mapからtilemap[0]を再焼き込み | Code Makerで基底タイルを配置→ゲーム側でオートタイル変種を再計算、が最も確実 | 逆引きで変種→基底の変換: 変種パターンが多く漏れが出る |
| D4 | タイルサイズの前提 | **16x16px** をTILE_SIZE定数として明示 | 現在 `*8` がハードコードされておりタイルサイズが曖昧。16px前提を明示する | 8pxのまま: Pyxelのpget/psetがタイルグリッド(8px)単位だが、ゲームの論理タイルは16px |

### 判断の依存関係

```mermaid
graph TD
    D1P["D1': 逆引き辞書の<br/>登録漏れ修正"] --> D2[D2: 逆引き失敗時<br/>warningログ追加]
    D1P --> D3[D3: _rebake_autotiles<br/>復元後に再焼き込み]

    style D1P fill:#a44,color:#fff
    style D3 fill:#49a,color:#fff
```

---

## 修正後のデータフロー

```mermaid
graph TD
    subgraph FLOW["Code Maker編集後のゲーム起動"]
        A[pyxel.load .pyxres] --> B["_build_reverse_tile_map<br/>★D1': 全variantを登録"]
        B --> C[_derive_world_from_tilemap]
        C --> D["key = tu*8, tv*8<br/>（座標計算は正しい）"]
        D --> E[tile_id_by_pixel.get key]
        E --> F{ヒット?}
        F -->|はい| G[正しいタイルID<br/>world_mapに設定]
        F -->|いいえ| H[T_GRASS + warning<br/>★D2: ログ追加]
        G --> I[_rebake_autotiles<br/>★D3: オートタイル再計算]
        H --> I
        I --> J[tilemap 0 に再書き込み<br/>オートタイル変種が正しく配置]
        J --> K[描画: 編集内容が<br/>正しく反映される]
    end

    style D fill:#4a9,color:#fff
    style I fill:#4a9,color:#fff
    style K fill:#4a9,color:#fff
```

---

## 修正対象ファイル

```mermaid
graph TD
    subgraph main.py
        M1["_build_reverse_tile_map<br/>★D1': 登録漏れ修正"]
        M2[_derive_world_from_tilemap<br/>座標計算は変更なし<br/>D2: warningログ追加]
        M3[_derive_dungeon_from_tilemap<br/>D2: warningログ追加]
        M4[_setup_world_tilemap<br/>★D3: rebake呼び出し追加]
    end

    M1 --> M2
    M1 --> M3
    M2 --> M4
    M3 --> M4

    style M1 fill:#a44,color:#fff
    style M4 fill:#49a,color:#fff
```

---

## 実装ステップ

```mermaid
graph TD
    S1["Step 1<br/>_build_reverse_tile_map の<br/>登録漏れを特定・修正<br/>D1'"] --> S2[Step 2<br/>warningログ追加<br/>D2]
    S2 --> S3[Step 3<br/>_setup_world_tilemap に<br/>rebake呼び出し追加<br/>D3]
    S3 --> S4[Step 4<br/>テスト: 編集→保存→リロード<br/>で草に化けないことを確認]

    style S1 fill:#a44,color:#fff
    style S3 fill:#49a,color:#fff
    style S4 fill:#4a9,color:#fff
```

---

## 参照

- [`./gherkin.md`](./gherkin.md) — 受け入れ条件（シナリオ5が核心）
- [`./journey.md`](./journey.md) — 体験設計
- [`./problem.md`](./problem.md) — 課題定義
