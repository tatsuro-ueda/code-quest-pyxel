# 詳細設計書: タイルマップ編集の反映バグ修正

`structure-design.md` で決定した方針（D1: ピクセル座標統一 / D3: _rebake_autotiles / D4: TILE_SIZE定数化）を実装レベルに落とし込む。

---

## 1. 修正箇所の全体マップ

```mermaid
graph TD
    subgraph CONST["定数追加"]
        C1[TILE_SIZE = 16<br/>main.py 先頭付近]
    end

    subgraph FIX["座標修正 D1"]
        F1["_derive_world_from_tilemap<br/>key = tu * TILE_SIZE, tv * TILE_SIZE"]
        F2["_derive_dungeon_from_tilemap<br/>key = tu * TILE_SIZE, tv * TILE_SIZE"]
    end

    subgraph WARN["ログ追加 D2"]
        W1["逆引き失敗時に<br/>print warning"]
    end

    subgraph REBAKE["オートタイル再焼き D3"]
        R1["_rebake_autotiles 新規追加"]
        R2["_setup_world_tilemap から呼び出し"]
    end

    C1 --> F1
    C1 --> F2
    F1 --> W1
    F2 --> W1
    F1 --> R1
    F2 --> R1
    R1 --> R2

    style F1 fill:#a44,color:#fff
    style F2 fill:#a44,color:#fff
    style R1 fill:#49a,color:#fff
```

---

## 2. TILE_SIZE 定数（D4）

### 現状

`* 8` がハードコードされている。Pyxel の tilemap.pget/pset はグリッド座標（8px単位）を返すが、ゲームの論理タイルは 16x16px（2x2グリッド）。

### 修正

```python
# main.py 先頭の定数定義エリア（MAP_W, MAP_H 付近）
TILE_SIZE = 16  # 論理タイル1マス = 16x16px = 2x2 Pyxelグリッド
```

---

## 3. _derive_world_from_tilemap 修正（D1 核心）

### 現状のコード（main.py 1455-1467行）

```python
def _derive_world_from_tilemap(self):
    tilemap = pyxel.tilemaps[0]
    derived = []
    for y in range(MAP_H):
        row = []
        for x in range(MAP_W):
            tu, tv = tilemap.pget(2 * x, 2 * y)
            key = (tu * 8, tv * 8)                          # ★バグ
            tid = self.tile_id_by_pixel.get(key, T_GRASS)
            row.append(tid)
        derived.append(row)
    self.world_map = derived
```

### 修正後

```python
def _derive_world_from_tilemap(self):
    tilemap = pyxel.tilemaps[0]
    derived = []
    for y in range(MAP_H):
        row = []
        for x in range(MAP_W):
            tu, tv = tilemap.pget(2 * x, 2 * y)
            key = (tu * TILE_SIZE, tv * TILE_SIZE)           # ★修正: D1
            tid = self.tile_id_by_pixel.get(key, T_GRASS)
            if tid == T_GRASS and key not in self.tile_id_by_pixel:  # D2
                print(f"[tilemap] unknown tile at world ({x},{y}): pixel={key}")
            row.append(tid)
        derived.append(row)
    self.world_map = derived
```

### なぜ tu * TILE_SIZE なのか

```mermaid
graph TD
    subgraph BANK["tile_bank の座標系"]
        B1["_layout_tile_bank で格納<br/>bx = col * 16, by = row * 16"]
        B2["tile_bank[T_TREE] = 32, 0<br/>tile_bank[T_WATER] = 48, 0<br/>...すべてピクセル座標"]
    end

    subgraph REVERSE["逆引き辞書"]
        R1["tile_id_by_pixel のキー<br/>= tile_bank の u, v そのまま<br/>= ピクセル座標"]
    end

    subgraph TILEMAP["tilemap.pget の返り値"]
        T1["tu, tv = グリッド座標<br/>8px単位"]
        T2["tu=4 → ピクセル=32<br/>tu=6 → ピクセル=48"]
    end

    subgraph CALC["キー変換"]
        OLD["旧: tu * 8<br/>tu=4 → 32 ✓ 偶然一致?<br/>tu=2 → 16 ✓<br/>実は col*16/8 = col*2<br/>tu = col*2 なので tu*8 = col*16 ✓"]
        NEW["新: tu * TILE_SIZE<br/>tu=2 → 32 ✗ 不一致!"]
    end

    B1 --> R1
    T1 --> CALC

    style OLD fill:#a94,color:#fff
    style NEW fill:#a94,color:#fff
```

**重要な再検証**: 実は `tu * 8` が正しい可能性がある。

---

## 3.1 座標系の精密な検証

### _layout_tile_bank のレイアウト

```python
col = 0; row = 0
for kind, key, _data in self._tile_iter():
    bx = col * 16; by = row * 16     # ← ピクセル座標
    self.tile_bank[key] = (bx, by)
    col += 1
    if col >= 16: col = 0; row += 1
```

例: col=2, row=0 → `bx=32, by=0`

### _bake_world_to_tilemap の書き込み

```python
u, v = self._pixel_pos_for_tile(wm, x, y, tile)  # ← ピクセル座標 (32, 0)
tu, tv = u // 8, v // 8                            # ← グリッド座標 (4, 0)
tilemap.pset(2*x, 2*y, (tu, tv))                   # ← (4, 0) を格納
```

### _derive_world_from_tilemap の読み出し

```python
tu, tv = tilemap.pget(2*x, 2*y)    # ← グリッド座標 (4, 0)
key = (tu * 8, tv * 8)              # ← (32, 0)
```

### 逆引き辞書のキー

```python
self.tile_id_by_pixel[(u, v)] = tid  # ← (32, 0)
```

### 検証結果

```mermaid
graph TD
    A["tile_bank: bx = col * 16<br/>col=2 → bx=32"] --> B["逆引きキー: 32, 0"]
    C["tilemap書込: tu = 32 // 8 = 4"] --> D["tilemap読出: tu = 4"]
    D --> E["key = 4 * 8 = 32"]
    E --> F{"32 == 32?<br/>一致する!"}
    F -->|はい| G["tu * 8 は正しい"]

    style G fill:#4a9,color:#fff
```

**`tu * 8` は実は正しい。** tile_bank が 16px単位、Pyxelグリッドが 8px単位なので:
- 書込: `bx(=col*16) // 8 = tu`
- 読出: `tu * 8 = col*16 // 8 * 8 = col*16` → 一致

### では真の原因は何か

```mermaid
graph TD
    Q["tu * 8 が正しいなら<br/>なぜ草に化ける?"]
    Q --> H1{"tile_bank に<br/>全タイルが登録<br/>されているか?"}
    Q --> H2{"_build_reverse_tile_map<br/>の呼び出し順序は<br/>正しいか?"}
    Q --> H3{"Code Makerが<br/>書き込むtilemap座標は<br/>_bake と同じ体系か?"}

    style Q fill:#a94,color:#fff
```

**D1の判断を保留し、実装フェーズで実機検証が必要。**

---

## 4. _derive_dungeon_from_tilemap 修正

`_derive_world_from_tilemap` と同じ修正を適用。

### 現状（main.py 1407-1421行）

```python
def _derive_dungeon_from_tilemap(self):
    tilemap = pyxel.tilemaps[0]
    dg = self.dungeon_template
    oy = self.DUNGEON_TM_OFFSET_Y
    derived = []
    for y in range(len(dg)):
        row = []
        for x in range(len(dg[0])):
            tu, tv = tilemap.pget(2 * x, oy + 2 * y)
            key = (tu * 8, tv * 8)                     # D1と同じ修正
            tid = self.tile_id_by_pixel.get(key, T_FLOOR)
            row.append(tid)
        derived.append(row)
    self.dungeon_template = derived
```

### 修正方針

- D1修正を適用する場合は `tu * TILE_SIZE` に変更
- D2: 逆引き失敗時に `print(f"[tilemap] unknown tile at dungeon ...")` 追加
- D1保留の場合も D2 のログは追加する（デバッグ用）

---

## 5. _rebake_autotiles 新規追加（D3）

### 処理フロー

```mermaid
graph TD
    A["_derive_world_from_tilemap 完了<br/>world_map に基底タイルID格納済み"] --> B["_rebake_autotiles 呼び出し"]
    B --> C["world_map の全セルを走査"]
    C --> D{タイル種別}
    D -->|T_PATH| E["get_path_variant で<br/>周辺を見て変種を決定"]
    D -->|T_WATER| F["get_shore_variant で<br/>周辺を見て変種を決定"]
    D -->|その他| G["tile_bank から<br/>そのまま取得"]
    E --> H["tilemap 0 に<br/>2x2グリッドで書き込み"]
    F --> H
    G --> H
    H --> I["ダンジョンも同様に処理"]
```

### 概念コード

```python
def _rebake_autotiles(self):
    """world_map / dungeon_template から tilemap[0] を再焼き込みする。

    _derive_*_from_tilemap() で基底タイルIDを復元した後に呼ぶ。
    オートタイル変種を周辺タイルから再計算してtilemap[0]に書き戻す。
    """
    self._bake_world_to_tilemap()
    self._bake_dungeon_to_tilemap()
```

**注意**: `_rebake_autotiles` の実体は既存の `_bake_world_to_tilemap` + `_bake_dungeon_to_tilemap` と同じ。新メソッドとして分離するか、直接呼ぶかは実装時に判断。

### _bake_world_to_tilemap が既にオートタイル解決をしている

```python
def _bake_world_to_tilemap(self):
    for y in range(MAP_H):
        for x in range(MAP_W):
            tile = wm[y][x]
            u, v = self._pixel_pos_for_tile(wm, x, y, tile)  # ← オートタイル解決
            tu, tv = u // 8, v // 8
            tilemap.pset(...)
```

つまり `_rebake_autotiles` は既存メソッドの再利用で実現できる。

---

## 6. _setup_world_tilemap の修正

### 現状（main.py 1355-1390行）

```python
if self._pyxres_loaded:
    self._derive_world_from_tilemap()
    self._derive_dungeon_from_tilemap()
else:
    self._bake_world_to_tilemap()
    self._bake_dungeon_to_tilemap()
```

### 修正後

```python
if self._pyxres_loaded:
    self._derive_world_from_tilemap()
    self._derive_dungeon_from_tilemap()
    # D3: オートタイル変種を再計算してtilemap[0]に書き戻す
    self._bake_world_to_tilemap()
    self._bake_dungeon_to_tilemap()
else:
    self._bake_world_to_tilemap()
    self._bake_dungeon_to_tilemap()
```

```mermaid
graph TD
    A{".pyxres 存在?"} -->|はい| B["_derive_world_from_tilemap<br/>tilemap→world_map復元"]
    B --> C["_derive_dungeon_from_tilemap<br/>tilemap→dungeon復元"]
    C --> D["_bake_world_to_tilemap<br/>★D3追加: オートタイル再焼き込み"]
    D --> E["_bake_dungeon_to_tilemap<br/>★D3追加: ダンジョン再焼き込み"]

    A -->|いいえ| F["_bake_world_to_tilemap<br/>初回生成"]
    F --> G["_bake_dungeon_to_tilemap"]
    G --> H["pyxel.save .pyxres"]

    style D fill:#49a,color:#fff
    style E fill:#49a,color:#fff
```

---

## 7. 実装前に実機検証すべきこと

structure-design.md の D1 で「`tu*8` → `tu*TILE_SIZE`」と決定したが、座標系を精密に検証した結果、`tu*8` が正しい可能性がある。

### 検証手順

```mermaid
graph TD
    V1["1. .pyxres を削除して起動<br/>→ 初回生成"] --> V2["2. tile_bank の内容を<br/>printで出力"]
    V2 --> V3["3. tilemap.pget で<br/>既知タイルの tu,tv を確認"]
    V3 --> V4["4. tu*8 と tile_bank の<br/>u,v が一致するか確認"]
    V4 --> V5{"一致する?"}
    V5 -->|はい| V6["tu*8 は正しい<br/>→ 真の原因は別にある"]
    V5 -->|いいえ| V7["tu*TILE_SIZE に修正"]

    V6 --> V8["_build_reverse_tile_map の<br/>登録内容を全件dump<br/>→ 漏れているタイルを特定"]

    style V5 fill:#a94,color:#fff
    style V6 fill:#a94,color:#fff
```

### 検証用デバッグコード

```python
# _build_reverse_tile_map の末尾に追加
print(f"[debug] tile_id_by_pixel keys: {sorted(self.tile_id_by_pixel.keys())}")
print(f"[debug] tile_bank values: {sorted(self.tile_bank.values())}")

# _derive_world_from_tilemap のループ内に追加（最初の5件のみ）
if y == 0 and x < 5:
    print(f"[debug] ({x},{y}): tu={tu}, tv={tv}, key={key}, "
          f"found={key in self.tile_id_by_pixel}")
```

---

## 8. テスト方針

### テストシナリオとgherkinの対応

```mermaid
graph TD
    G5["gherkin シナリオ5<br/>黙って消えない<br/>★核心"] --> T1["テスト1: .pyxres削除→起動<br/>→Code Maker編集→再起動<br/>→タイルが草に化けない"]

    G2["gherkin シナリオ2<br/>オートタイル"] --> T2["テスト2: 道タイルの隣を編集<br/>→道が自然に繋がる"]

    G6["gherkin シナリオ6<br/>ゲームが落ちない"] --> T3["テスト3: ランダムにタイル配置<br/>→ゲームが正常起動"]

    T1 --> M["手動テスト<br/>Code Maker実機操作"]
    T2 --> M
    T3 --> M

    style T1 fill:#a44,color:#fff
    style M fill:#4a9,color:#fff
```

### テスト手順

| # | テスト | 手順 | 期待結果 |
|---|---|---|---|
| 1 | 基本反映 | .pyxres削除→起動→Code Makerで城タイルを配置→保存→再起動 | 城タイルが正しく表示される |
| 2 | 草に化けない | テスト1と同じ手順で、リロード後にworld_mapを確認 | T_GRASSでなく配置したタイルIDが入っている |
| 3 | オートタイル | 道タイルの隣に木を配置→再起動 | 道が自然に繋がり直す |
| 4 | ダンジョン | ダンジョン領域のタイルを編集→再起動 | 編集が反映される |
| 5 | 安全性 | 全マスを同じタイルで埋める→再起動 | ゲームが正常に起動する |

---

## 参照

- [`./structure-design.md`](./structure-design.md) — 構造設計（D1-D4の判断）
- [`./gherkin.md`](./gherkin.md) — 受け入れ条件（シナリオ5が核心）
- [`./journey.md`](./journey.md) — 体験設計
