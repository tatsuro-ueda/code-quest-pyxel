# マップ実装設計書

## 1. マップレイアウト

50×50タイル、TILE=32px、Canvas 640×480（表示領域20×15タイル）

### S字ルート設計

```
  N
  ┌──────────── 50tiles ────────────┐
  │🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊│
  │🌊  🌲🌲                    🌲🌲🌊│
  │🌊  🌲  🏰(25,6)              🌲🌊│ Zone 0
  │🌊      ↓ PATH                  🌊│ 牧歌的
  │🌊  🏘(20,12)はじめの村 ★世界樹 🌊│ 緑豊か
  │🌊          ↓                    🌊│
  │🌊⛰⛰⛰⛰⛰⛰峠(22,16)⛰⛰⛰⛰⛰🌊│ ← 山脈（Zone0/1境界）
  │🌊          ↓                    🌊│
  │🌊      🏘(30,22)ロジックタウン  🌊│ Zone 1
  │🌊          ↓    →🌲(寄り道1)   🌊│ 開けた平原
  │🌊🌊🌊🌊🌊🌊橋(28,28)🌊🌊🌊🌊🌊🌊│ ← 大河（Zone1/2境界）
  │🌊          ↓          ★通信塔  🌊│
  │🌊  🌲(寄り道2)←🏘(18,34)       🌊│ Zone 2
  │🌊              ↓ アルゴリズムの街🌊│ 深い森
  │🌊          砂漠→→→→           🌊│
  │🌊              🕳(38,42)        🌊│ Zone 3
  │🌊          グリッチのサーバー    🌊│ 砂漠・闇
  │🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊│
  S└──────────────────────────────────┘
```

### 構造体座標

| 名称 | 座標 | 備考 |
|------|------|------|
| コードのしろ | (25, 6) | 中央上部、開始地点 |
| はじめの村 | (20, 12) | 西寄り、Zone 0 |
| ロジックタウン | (30, 22) | 東寄り、Zone 1 |
| アルゴリズムの街 | (18, 34) | 西寄り、Zone 2 |
| グリッチのサーバー | (38, 42) | 南東、Zone 3 |
| 世界樹（ランドマーク） | (32, 9) | Zone 0目印、2×3描画 |
| 通信塔（ランドマーク） | (40, 32) | Zone 2目印、1×3描画 |

## 2. ゾーン判定

距離ベース（同心円）→ **Y座標バンド方式**に変更。

```javascript
function getEnemyZone() {
  if (player.inDungeon) return 4;
  if (player.y < 16)  return 0;  // 城〜はじめの村
  if (player.y < 28)  return 1;  // ロジックタウン周辺
  if (player.y < 38)  return 2;  // アルゴリズムの街周辺
  return 3;                       // 砂漠〜ダンジョン
}
```

山脈（y≈16）と大河（y≈28）がバンド境界と一致。
「障壁を越えた＝ゾーン変化」を体感できる。

## 3. 自然障壁

| 障壁 | Y範囲 | 通過点 | 役割 |
|------|-------|--------|------|
| 海（外周） | 0-2, 48-49 | なし | 世界の端 |
| 山脈 | 15-17 | 峠 x≈22 | Zone 0/1 分断 |
| 大河 | 27-29 | 橋 x≈28 | Zone 1/2 分断 |
| 砂漠＋岩場 | 38-47 | 通過可能（高エンカウント） | Zone 3の危険感 |

## 4. デコレーション層

`map[][]` とは別に `deco[][]` 配列を追加。

```javascript
const DECO_NONE=0, DECO_FLOWER1=1, DECO_FLOWER2=2,
      DECO_STONE=3, DECO_MUSHROOM=4, DECO_GRASS_TUFT=5, DECO_STUMP=6;
```

| デコ | 出現タイル | ゾーン傾向 | 描画 |
|------|-----------|-----------|------|
| 花1（白/黄） | GRASS | Zone 0多い | 3×3ピクセル |
| 花2（赤/紫） | GRASS | Zone 0-1 | 3×3ピクセル |
| 小石 | GRASS/SAND | Zone 2-3多い | 2×2グレー |
| キノコ | GRASS(木の近く) | Zone 1-2 | 4×5赤白 |
| 草むら | GRASS | 全域 | 6×4ふさふさ |
| 切り株 | GRASS | Zone 1-2 | 6×4茶色 |

- 衝突判定なし（純粋に視覚のみ）
- ゾーンとベースタイルに応じて手続き的に配置
- 密度：Zone 0=高、Zone 3=低（メリハリ）

## 5. オートタイル（岸辺遷移）

水タイルが陸地と隣接する場合、エッジに砂浜/岸を描画。

```javascript
// 4方向の陸地隣接をビットマスクで判定
const isLand = t => t!==TILE_WATER && t!==TILE_BRIDGE;
const nN = (my>0 && isLand(map[my-1][mx])) ? 1 : 0;
const nS = (my<MH-1 && isLand(map[my+1][mx])) ? 1 : 0;
const nE = (mx<MW-1 && isLand(map[my][mx+1])) ? 1 : 0;
const nW = (mx>0 && isLand(map[my][mx-1])) ? 1 : 0;
// 各辺に砂浜エッジを描画
if(nN) { ctx.fillStyle='#d4c080'; px(sx,sy,TILE,4); }
if(nS) { ctx.fillStyle='#d4c080'; px(sx,sy+TILE-4,TILE,4); }
// ... etc
```

## 6. ランドマーク

### 世界樹（Zone 0目印）
- 位置: (32, 9)、2×3タイル描画（通常の木より大きい）
- 幹が太い、樹冠が画面上に広がる
- 黄緑のハイライト葉、落ち葉のデコレーション
- マップタイル自体は TILE_TREE だが特別描画

### 通信塔（Zone 2目印）
- 位置: (40, 32)、1×3タイル描画
- 金属質（グレー3色）、赤い点滅ライト
- マップタイルは TILE_MOUNTAIN だが特別描画

## 7. 蛇行パスアルゴリズム

直線L字パス → オーガニックな蛇行パスに変更。

```javascript
function carveWindingPath(x1,y1,x2,y2) {
  let cx=x1, cy=y1;
  while(cx!==x2 || cy!==y2) {
    // 目標方向へ進むが30%の確率で垂直方向にずれる
    if(Math.random()<0.3 && cx!==x2 && cy!==y2) {
      // ランダムに水平/垂直を選択
      if(Math.random()<0.5) cx += (x2>cx)?1:-1;
      else cy += (y2>cy)?1:-1;
    } else {
      // より遠い軸を優先
      if(Math.abs(x2-cx) > Math.abs(y2-cy)) cx += (x2>cx)?1:-1;
      else cy += (y2>cy)?1:-1;
    }
    if(map[cy][cx]===TILE_GRASS) map[cy][cx]=TILE_PATH;
  }
}
```

## 8. 寄り道（分岐）

| 分岐 | 入口 | 行き先 | 内容 |
|------|------|--------|------|
| 分岐1 | ロジックタウン東 | (38, 24) 森の空き地 | 将来の宝箱/イベント |
| 分岐2 | アルゴリズムの街西 | (10, 36) 深い森 | 将来の宝箱/イベント |

メインルートからPATHで接続。行き止まりにデコ密度を上げる。

## 9. タイルキャッシュ（オフスクリーンCanvas）

毎フレーム `fillRect` × 数十回 → `drawImage` × 1回に圧縮。

```javascript
const tileCache = {};  // key: "type_zone_hash" → OffscreenCanvas

function getCachedTile(type, zone, h) {
  const key = `${type}_${zone}_${(h*10|0)}`;
  if (!tileCache[key]) {
    const oc = document.createElement('canvas');
    oc.width = TILE; oc.height = TILE;
    const octx = oc.getContext('2d');
    // render tile to offscreen
    tileCache[key] = oc;
  }
  return tileCache[key];
}
```

- アニメーション付きタイル（水・旗など）は2フレーム分キャッシュ
- ゾーン変更時にキャッシュクリア

## 10. セーブ互換性

```javascript
function saveGame() {
  player.saveVersion = 2;
  localStorage.setItem('dqsave', JSON.stringify(player));
}

function loadGame() {
  const d = localStorage.getItem('dqsave');
  if (d) {
    player = JSON.parse(d);
    if (!player.saveVersion || player.saveVersion < 2) {
      // 旧セーブ：座標をリセット
      player.x = CASTLE_POS.x;
      player.y = CASTLE_POS.y;
      player.lastTown = {x: CASTLE_POS.x, y: CASTLE_POS.y};
    }
    return true;
  }
  return false;
}
```

## 11. 変更対象まとめ

| 対象 | 変更前 | 変更後 |
|------|--------|--------|
| CASTLE_POS | (6,5) | (25,6) |
| TOWNS | [(15,8),(35,18),(42,38)] | [(20,12),(30,22),(18,34)] |
| DUNGEON_POS | (44,8) | (38,42) |
| getEnemyZone() | hypot距離 | Y座標バンド |
| 地形生成 | ランダム散布 | 意図的配置 |
| タイル描画 | 毎フレームfillRect | オフスクリーンキャッシュ |
| carvePath() | L字 | 蛇行 |
| 新規: deco[][] | なし | デコレーション層 |
| 新規: オートタイル | なし | 水辺エッジ遷移 |
| 新規: ランドマーク | なし | 世界樹・通信塔 |
| セーブ | バージョンなし | saveVersion: 2 |
