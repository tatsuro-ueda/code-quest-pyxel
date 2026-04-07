# 技術設計

> Status: Legacy HTML-oriented draft under review.
> This file still contains older `index.html`, `pressKey/releaseKey`, and browser-input assumptions.
> For the current Pyxel project, treat `main.py`, `docs/00-pyxel-design.md`, and `/home/exedev/code-quest-pyxel/AGENTS.md` as the primary source of truth until this document is rewritten.

## ファイル構成

単一HTMLファイル（`index.html`）にすべてのCSS/JSをインライン。
配布利便性を優先し、ファイル分割は行わない。
セクションコメントでコード領域を区分する。

## 入力抽象化レイヤー

### pressKey / releaseKey

```
function pressKey(key)  → keys[key] = true + kbuf.push(key)
function releaseKey(key) → keys[key] = false
```

すべての入力ソース（キーボード、仮想パッド）はこの関数を経由する。
将来 Gamepad API を追加する場合もここに接続するだけ。

### inputMode フラグ

```
let inputMode = 'discrete' | 'continuous'
```

- `continuous`：マップ歩行時。keys[] の押しっぱなしで連続移動
- `discrete`：バトル/メニュー/町等。1タップ=1入力

ゲームループの `update()` 内で `gameState` に応じて自動更新。
仮想パッドはこのフラグだけ参照し、ゲーム状態を直接見ない。

## 仮想ゲームパッド設計

### データ駆動ボタン定義

```js
const PAD_BUTTONS = [
  {id:'up',   keys:['ArrowUp'],   position:'dpad', label:'▲', gridArea:'1/2/2/3'},
  {id:'a',    keys:['Enter','z'], position:'ab',   label:'A'},
  // ← 追加が容易
];
```

ボタン追加は配列に1行足すだけ。HTML生成はデータから動的に行う。

### CSS変数でサイズ一元管理

```css
:root {
  --pad-btn-size: 60px;
  --pad-gap: 4px;
  --pad-opacity: 0.35;
  --pad-opacity-active: 0.6;
  --pad-bottom: 16px;
  --pad-side: 16px;
}
```

ポートレート時は `@media (orientation: portrait)` で上書き。

### レイアウト戦略

| 向き | Canvas | パッド |
|------|--------|--------|
| 横持ち | 全画面 | `position: fixed` で重ね表示 |
| 縦持ち | 上部 | `position: static` + `margin-top: auto` で下部フロー配置 |
| PC | 全画面中央 | 非表示 |

### タッチ判定

- `navigator.maxTouchPoints > 0` で表示判定（タッチ対応PCも対象）
- `touchstart` / `touchend` で管理（`click` は不使用）
- `stopPropagation()` でCanvas側への伝播を防止
- `contextmenu` イベントを `preventDefault()` で長押しメニュー抑止

## デバッグモード設計

### 状態管理

```js
let debugMode = false;       // player オブジェクトに含めない → セーブ対象外
let debugBuf = [];            // 入力シーケンスバッファ
const debugSeq = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown'];
```

`resetGameState()` で `debugMode=false`, `debugBuf=[]` にリセットされる。

### トグル判定

gameLoop 内 `while(key)` ループの先頭で判定：
- `gameState === 'title'` または `gameState === 'map'`（メッセージ非表示時）
- 方向キー入力を `debugBuf` に蓄積、他キーでクリア
- 末尾4件が `debugSeq` と一致 → `debugMode` トグル → バッファクリア

### 影響箇所マップ

| 機能 | 関数 | 変更内容 |
|------|------|----------|
| 起動/解除 | `gameLoop` | ↑↑↓↓ シーケンス照合 |
| エンカウント無効 | `checkEncounter()` | 先頭で `if(debugMode) return` |
| 一撃必殺 | `processBattleInput()` | たたかう時 `dmg = enemy.currentHp` |
| 敵ダメージ無効 | `enemyTurn()` | 全処理スキップ、「効かなかった」メッセージ |
| バグ汚染無効 | `enemyTurn()` | スキップされるため自動的に無効 |
| 毒歩行ダメージ無効 | `update()` | `&&!debugMode` 条件追加 |
| 表示 | `drawMap()` / `drawBattle()` | 🛠 インジケータ描画 |

### 変更しない箇所

| 箇所 | 理由 |
|------|------|
| EXP/コイン獲得 | ストーリー確認にスキル習得・ショップが必要 |
| レベルアップ判定 | 通常通り |
| ボス戦突入 | 座標判定で強制発動、checkEncounter とは独立 |
| セーブ/ロード | debugMode を含めない |

## バトルロジック設計

バトルの主要ロジックは描画/音声から分離した純粋関数として抽出済み。

```
processBattleInput(key)    ← UI入力ハンドラ（sfx 呼び出しを含む）
  ├─ calcDamage()           ← 純粋関数
  ├─ applySpellEffect()     ← ロジック関数（テスト可能）
  ├─ applyItemEffect()      ← ロジック関数（テスト可能）
  └─ processVictory()       ← ロジック関数（テスト可能）
       └─ processLevelUp()   ← ロジック関数（テスト可能）

enemyTurn()                ← UI入力ハンドラ（sfx 呼び出しを含む）
  ├─ calcDamage()           ← 純粋関数
  └─ applySpellEffect()     ← 敵が使う場合も共通

processDefeat()              ← ロジック関数（テスト可能）
```

### 呼び出し規約

- **sfx関数**は抽出したロジック関数の内部では呼ばない
- sfx は呼び出し元（`processBattleInput`, `enemyTurn` 等）が担当
- ロジック関数は結果オブジェクトを返し、呼び出し元がそれに基づき sfx/描画を判断

## ショップ/宿屋ロジック設計

`processTownInput` 内の購入/宿泊ロジックを分離：

```
tryPurchase(type, id)  → {success, spent} or {success:false, reason}
tryInn(townIdx)        → {success, spent} or {success:false}
```

- UI（sfx/メッセージ）は `processTownInput` 側が担当
- `tryPurchase` は item/weapon/armor を統一的に処理

## アイテム/スキル効果設計

バトル中とメニューの両方で同じロジックをDRYに利用：

```
applyItemEffect(item)       → {msg}      … HP/MP回復、毒解除、ワープ
applySpellEffect(sp, target) → {type, msg} … 回復または攻撃
```

- バトル中: `processBattleInput` が呼び出し、結果を `battleState.msg` に反映
- メニュー: `processMenuInput` が呼び出し、結果を `showMsg()` に反映
- 戦闘中に「セーブポイント」（ワープ）は使用不可 → `processBattleInput` 側でガード

## 状態生成設計

テスト容易性のためにファクトリ関数を導入：

```js
function createInitialPlayer() {
  return {
    x: CASTLE_POS.x, y: CASTLE_POS.y,
    hp: 30, maxHp: 30, mp: 10, maxMp: 10,
    atk: 5, def: 3, agi: 5,
    lv: 1, exp: 0, gold: 50,
    weapon: null, armor: null,
    items: [{id:0, qty:3}],
    spells: [],
    poisoned: false,
    lastTown: {x: CASTLE_POS.x, y: CASTLE_POS.y},  // コピー（参照共有防止）
    inDungeon: false,
    bossDefeated: false,
    steps: 0,
  };
}

function resetGameState() {
  gameState = 'title';
  debugMode = false;
  debugBuf = [];
  battleState = null;
  menuState = null;
  msgQueue = [];
  msgCurrent = null;
  msgCallback = null;
  animTimer = 0;
  lastTime = 0;
  moveTimer = 0;
  kbuf = [];
  Object.keys(keys).forEach(k => delete keys[k]);
}
```

- `createInitialPlayer()` は毎回新しいオブジェクトを返す（参照共有なし）
- `lastTown` は `CASTLE_POS` のコピーを格納（直接参照だと変更時に副作用が発生するため）
- テストでは `beforeEach` で `player = createInitialPlayer(); resetGameState();` を呼ぶ

## 音声

Web Audio API によるチップチューン効果音。
`playTone(freq, dur, type, vol)` で生成。
AudioContext は最初のユーザー操作（pressKey 内）で resume。

ロジック関数（`processVictory`, `applySpellEffect` 等）は sfx を呼ばない。
sfx は呼び出し元の UI ハンドラが担当する。

## Node.js テスト統合

`index.html` 末尾の条件分岐でテスト対応：

```js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { /* 全関数 + データ + getter/setter */ };
} else {
  initGamepad();
  requestAnimationFrame(gameLoop);
}
```

- ブラウザ: `module` 未定義 → 通常のゲーム起動
- Node: `require('./index.html')` 相当の流れで全ロジックを公開
- getter/setter でグローバル状態（player, gameState, debugMode 等）を外部から読み書き可能
- 詳細は `docs/testing.md` 参照
