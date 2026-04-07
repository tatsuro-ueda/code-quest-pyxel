# 効果音機能設計

本ドキュメントは `sfx-concepts.md` の6カテゴリ＋4ルールをブロッククエストの実装に落とし込む設計書である。
現行コードの効果音層（`playTone`, `sfx*` 関数群）に対して
**何を残し・何を変え・何を追加するか**を定義する。

> 制約: 単一 `index.html`、Web Audio API OscillatorNode のみ、外部音声ファイル不使用。

---

## 設計方針

| コンセプトカテゴリ | 本ゲームでの実装方針 |
|-------------------|---------------------|
| ①フィードバック音 | 既存のカーソル/決定/キャンセル音を維持。購入成功/失敗音を分離 |
| ②状態変化音 | レベルアップ/勝利/敗北は既存。毒・治癒・セーブ・ゾーン移動を追加 |
| ③予兆音 | エンカウント突入音は既存。ボス前接近音・ダンジョン侵入音を追加 |
| ④強調音 | ボス撃破専用ファンファーレを追加 |
| ⑤空間音 | 歩行SE（足音）を追加。地形による音色変化で場所を表現 |
| ⑥操作感の音 | 攻撃/被ダメ/魔法は既存。クリティカルヒット用の強化版を追加 |

---

## 1. 既存SE 棚卸し

### 1.1 現行SE一覧

| 関数名 | 概念カテゴリ | 周波数帯 | 音量 | 用途 | 使用回数 |
|--------|:---:|---------|------|------|:---:|
| `sfxCursor()` | ① | 800Hz | 0.05 | メニュー/バトルのカーソル移動 | 26箇所 |
| `sfxSelect()` | ① | 600→900Hz | 0.10 | 決定/メニュー開/町・城入り | 11箇所 |
| `sfxAttack()` | ⑥ | 200→150Hz | 0.10 | プレイヤーの物理攻撃 | 1箇所 |
| `sfxHit()` | ⑥ | 100Hz sawtooth | 0.10 | 敵の攻撃がプレイヤーに命中 | 1箇所 |
| `sfxMagic()` | ⑥ | 400〜700Hz sine | 0.08 | スキル使用（攻撃/回復どちらも） | 2箇所 |
| `sfxHeal()` | ② | 500〜800Hz sine | 0.08 | HP/MP回復（アイテム/宿屋） | 4箇所 |
| `sfxLevelUp()` | ② | 300〜700Hz | 0.06 | レベルアップ | 1箇所 |
| `sfxVictory()` | ② | 400〜750Hz | 0.06 | バトル勝利（BGM victory に機能移行済み） | 1箇所 |
| `sfxDead()` | ② | 200→100Hz saw | 0.08 | プレイヤー死亡 | 1箇所 |
| `sfxBattle()` | ③ | 150〜300Hz saw | 0.06 | エンカウント突入 | 1箇所 |
| `sfxMiss()` | ① | 300→200Hz sine | 0.05 | 攻撃ミス/コイン不足 | 3箇所 |

### 1.2 評価

| 評価 | 対象 | 理由 |
|------|------|------|
| ✓ 維持 | `sfxCursor`, `sfxSelect`, `sfxAttack`, `sfxHit`, `sfxMagic`, `sfxHeal`, `sfxLevelUp`, `sfxDead`, `sfxBattle`, `sfxMiss` | 役割が明確。ルール①「意味1つ」を満たす |
| △ 改善 | `sfxVictory` | BGM `victory` トラックと重複。短縮するか残すか検討 |
| ✗ 不足 | — | 下記 §2 で新規追加 |

---

## 2. 新規SE 設計

### 2.1 新規SE一覧

| 関数名 | カテゴリ | 周波数 | 波形 | 音量 | 長さ | 用途 | ルール対応 |
|--------|:---:|--------|------|------|------|------|-----------|
| `sfxStep()` | ⑤⑥ | 地形別 | square | 0.03 | 0.04s | 歩行時に毎歩鳴る | ③短い ④なくても成立 |
| `sfxPoison()` | ② | 250→180Hz | sawtooth | 0.07 | 0.2s | バグ汚染を受けた時 | ①意味1つ |
| `sfxCure()` | ② | 600→800Hz | sine | 0.07 | 0.2s | 毒が治った時 | ①意味1つ |
| `sfxSave()` | ① | 500,700,900Hz | sine | 0.06 | 0.3s | セーブ成功 | ①意味1つ ②重要度中 |
| `sfxDungeonIn()` | ③ | 80→40Hz | sawtooth | 0.08 | 0.5s | ダンジョン侵入時 | ③予兆 |
| `sfxBossApproach()` | ③ | 60Hz | sine | 0.06 | 0.8s | ボス部屋隣接時（1回だけ） | ③予兆 ④強調 |
| `sfxBossDefeat()` | ④ | 上昇音列 | square | 0.08 | 1.0s | 魔王グリッチ撃破時 | ④強調（ゲーム中1回） |
| `sfxCritical()` | ⑥ | 250→350Hz | square | 0.12 | 0.15s | クリティカルヒット | ⑥気持ちよさ |
| `sfxZoneChange()` | ② | 400→500Hz | triangle | 0.04 | 0.15s | ゾーン境界を跨いだ時 | ②変化に気づく |
| `sfxPoisonTick()` | ② | 150Hz | sine | 0.04 | 0.08s | 毒歩行ダメージ時 | ③短い ①意味1つ |

### 2.2 各SE詳細設計

#### sfxStep() — 歩行音

地形タイルに応じて音色を変え、「場所らしさ」を表現する（コンセプト⑤）。

```js
function sfxStep(tile){
  const vol=0.03;
  switch(tile){
    case TILE_GRASS:case TILE_PATH:
      playTone(120+Math.random()*30,0.04,'square',vol); break;
    case TILE_SAND:
      playTone(200+Math.random()*50,0.05,'sawtooth',vol*0.7); break;
    case TILE_FLOOR:
      playTone(300+Math.random()*20,0.03,'square',vol*1.2); break;
    case TILE_BRIDGE:
      playTone(250,0.05,'triangle',vol); break;
    default: break; // 水・山・木は歩けないので鳴らない
  }
}
```

**呼び出し箇所**: `update()` 内の移動成功時（`canWalk` が true で座標が変わった直後）。
**設計ルール③**: 0.03〜0.05秒と極めて短く、音量0.03と控えめ。繰り返しストレスなし。
**設計ルール④**: なくてもゲームは成立する。BGMに溶け込む補助的存在。

#### sfxPoison() — バグ汚染を受けた

```js
function sfxPoison(){
  playTone(250,0.1,'sawtooth',0.07);
  setTimeout(()=>playTone(180,0.15,'sawtooth',0.06),80);
}
```

**呼び出し箇所**: `enemyTurn()` 内で `player.poisoned=true` が設定された直後。
**現状**: 毒を受けた時に専用音がなく、被ダメ音（`sfxHit`）しか鳴らない。
毒は重要な状態異常なので、下降する不快な音で「ヤバい」と感じさせる（コンセプト①②）。

#### sfxCure() — 毒治癒

```js
function sfxCure(){
  playTone(600,0.1,'sine',0.07);
  setTimeout(()=>playTone(800,0.12,'sine',0.06),80);
}
```

**呼び出し箇所**: `applyItemEffect()` 内 `curePoison` 処理後、および宿屋利用時。
**現状**: `sfxHeal()` が鳴るがHP回復と区別がつかない。上昇するクリアな音で「治った」感。

#### sfxSave() — セーブ成功

```js
function sfxSave(){
  [0,80,160].forEach((d,i)=>setTimeout(()=>playTone(500+i*200,0.1,'sine',0.06),d));
}
```

**呼び出し箇所**: `saveGame()` 呼び出し直後（メニューのセーブタブ内）。
**現状**: セーブ時に音がなく、メッセージだけ。3音の上昇で「保存できた」安心感。

#### sfxDungeonIn() — ダンジョン侵入

```js
function sfxDungeonIn(){
  playTone(80,0.3,'sawtooth',0.08);
  setTimeout(()=>playTone(40,0.4,'sawtooth',0.06),200);
}
```

**呼び出し箇所**: `enterDungeon()` の先頭。
**現状**: `sfxSelect()` が鳴るが、町に入る音と同じで差別化できていない。
低い sawtooth の下降で「危険な場所に踏み込んだ」予兆感（コンセプト③）。

#### sfxBossApproach() — ボス部屋接近

```js
function sfxBossApproach(){
  playTone(60,0.8,'sine',0.06);
}
```

**呼び出し箇所**: `updateBGM()` 内でボス隣接による無音化が発生した瞬間（1回だけ）。
グローバルフラグ `bossApproachPlayed` で重複再生を防ぐ。
**現状**: BGM が消えるだけで音の予兆がない。低い持続音で「何かいる」感。

#### sfxBossDefeat() — 魔王グリッチ撃破

```js
function sfxBossDefeat(){
  [0,100,200,300,400,500,600,800,1000].forEach((d,i)=>
    setTimeout(()=>playTone(300+i*60,0.2,'square',0.08),d));
}
```

**呼び出し箇所**: `processVictory()` で `bossDefeated=true` が設定された直後。
**現状**: 通常の `sfxVictory()` のみ。ゲーム中1回の最重要イベントなので、
長くて派手な上昇音列で特別感を演出（コンセプト④、ルール②音の強さで重要度）。

#### sfxCritical() — クリティカルヒット

```js
function sfxCritical(){
  playTone(250,0.08,'square',0.12);
  setTimeout(()=>playTone(350,0.1,'square',0.10),60);
}
```

**呼び出し箇所**: `processBattleInput()` 内で攻撃ダメージが通常の1.5倍以上だった時。
**現状**: クリティカル判定は未実装。将来追加時に使用。
暫定で `sfxAttack()` の代替として「大ダメージ時」に使える。

#### sfxZoneChange() — ゾーン移動

```js
function sfxZoneChange(){
  playTone(400,0.08,'triangle',0.04);
  setTimeout(()=>playTone(500,0.1,'triangle',0.04),60);
}
```

**呼び出し箇所**: `updateBGM()` 内でゾーンが変わった検出時。
**現状**: ゾーンが変わってもBGMが切り替わるだけで、プレイヤーが気づきにくい。
控えめな上昇音で「何か変わった」と感じさせる（コンセプト②）。

#### sfxPoisonTick() — 毒歩行ダメージ

```js
function sfxPoisonTick(){
  playTone(150,0.08,'sine',0.04);
}
```

**呼び出し箇所**: `update()` 内の毒ダメージ発生時（`player.steps%4===0`）。
**現状**: 毒でHPが減る時に音がなく、気づきにくい。
短く控えめな音で「まだ毒が効いている」とリマインド（コンセプト②、ルール③短い）。

---

## 3. 既存SEの改善

### 3.1 sfxVictory の扱い

BGM `victory` トラックが導入済みのため、`sfxVictory()` は以下のように使い分ける：

| 場面 | 使用する音 |
|------|----------|
| 通常バトル勝利 | BGM `victory`（2小節のファンファーレ）|
| ボス撃破 | `sfxBossDefeat()` → BGM `victory` |

`sfxVictory()` 関数自体は残す（フォールバック用）が、通常勝利時の呼び出しは
BGM `victory` に置き換え済みのため、追加の変更は不要。

### 3.2 sfxSelect の使い分け検討

現在 `sfxSelect()` は以下すべてで使われている：

- メニュー/バトルの決定
- 町に入る
- 城に入る
- ダンジョンに入る
- ショップ購入成功

町/城は引き続き `sfxSelect()` を使用。
ダンジョンは `sfxDungeonIn()` に置き換える。
ショップ購入成功は `sfxSelect()` のまま（購入失敗は `sfxMiss()` で差別化済み）。

---

## 4. 音のレイヤー設計（BGMとの共存）

### 4.1 周波数帯マッピング

`audio-design.md` §4.1 で定義した周波数帯に新規SEを配置する。

| 周波数帯 | BGM | 既存SE | 新規SE |
|----------|-----|--------|--------|
| 40〜100Hz | ベース (C2〜C3) | — | `sfxDungeonIn`, `sfxBossApproach` |
| 100〜300Hz | — | `sfxAttack`, `sfxHit`, `sfxBattle` | `sfxStep`, `sfxPoison`, `sfxPoisonTick`, `sfxCritical` |
| 300〜600Hz | — | `sfxLevelUp`, `sfxMiss` | `sfxSave`, `sfxZoneChange`, `sfxBossDefeat` |
| 600〜900Hz | メロディ (C5〜) | `sfxCursor`, `sfxSelect`, `sfxMagic`, `sfxHeal` | `sfxCure` |

### 4.2 音量階層

設計ルール②「音の強さで重要度を分ける」に基づく音量設計：

| 重要度 | 音量 | 該当SE |
|:---:|------|--------|
| 環境（日常） | 0.03〜0.04 | `sfxStep`, `sfxPoisonTick`, `sfxZoneChange` |
| 操作（応答） | 0.05 | `sfxCursor` |
| 行動（結果） | 0.07〜0.10 | `sfxSelect`, `sfxAttack`, `sfxHit`, `sfxMagic`, `sfxHeal`, `sfxMiss`, `sfxPoison`, `sfxCure`, `sfxSave` |
| 重要（転機） | 0.06〜0.08 | `sfxBattle`, `sfxLevelUp`, `sfxVictory`, `sfxDead`, `sfxDungeonIn`, `sfxBossApproach` |
| 最重要（1回） | 0.08〜0.12 | `sfxBossDefeat`, `sfxCritical` |

---

## 5. 実装計画

### 5.1 新規追加するコード

`index.html` 内、既存 `sfxMiss()` の直後に新規SE関数を追加する。

```
function sfxMiss(){...}         // ← 既存

// ===== NEW SFX =====
function sfxStep(tile){...}     // ← 新規
function sfxPoison(){...}       // ← 新規
function sfxCure(){...}         // ← 新規
function sfxSave(){...}         // ← 新規
function sfxDungeonIn(){...}    // ← 新規
function sfxBossApproach(){...} // ← 新規
function sfxBossDefeat(){...}   // ← 新規
function sfxCritical(){...}     // ← 新規
function sfxZoneChange(){...}   // ← 新規
function sfxPoisonTick(){...}   // ← 新規
```

### 5.2 既存コードの変更箇所

| 変更箇所 | 変更内容 |
|----------|---------|
| `update()` 内の移動成功時 | `sfxStep(tile)` 呼び出し追加 |
| `update()` 内の毒ダメージ時 | `sfxPoisonTick()` 呼び出し追加 |
| `enemyTurn()` 内の毒付与時 | `sfxPoison()` 呼び出し追加 |
| `enterDungeon()` | `sfxSelect()` → `sfxDungeonIn()` に変更 |
| `saveGame()` 呼び出し後 | `sfxSave()` 追加 |
| `processVictory()` 内のボス撃破 | `sfxBossDefeat()` 追加 |
| `updateBGM()` 内のボス隣接無音化 | `sfxBossApproach()` 追加（フラグ制御） |
| `updateBGM()` 内のゾーン変更検出 | `sfxZoneChange()` 追加 |
| `applyItemEffect()` の毒治癒 | `sfxCure()` 呼び出し追加（呼び出し元で） |
| `resetGameState()` | `bossApproachPlayed=false` リセット追加 |
| `module.exports` | 新規SE関数を追加 |

### 5.3 新規グローバル変数

```js
let bossApproachPlayed = false;  // ボス接近音の重複防止フラグ
let lastZone = -1;               // ゾーン変更検出用
```

`resetGameState()` で両方リセットする。

---

## 6. 実装優先度

| 優先度 | 項目 | 効果 | 工数 |
|:---:|------|------|:---:|
| S | `sfxStep()` — 歩行音 (§2.2) | 世界の存在感が大幅UP | 小 |
| S | `sfxPoison()` / `sfxPoisonTick()` — 毒関連 (§2.2) | 状態異常の認知改善 | 小 |
| A | `sfxSave()` — セーブ音 (§2.2) | 操作フィードバック改善 | 小 |
| A | `sfxDungeonIn()` — ダンジョン侵入 (§2.2) | 予兆感・差別化 | 小 |
| A | `sfxCure()` — 毒治癒 (§2.2) | HP回復との差別化 | 小 |
| B | `sfxZoneChange()` — ゾーン移動 (§2.2) | 進行感の認知 | 小 |
| B | `sfxBossApproach()` — ボス接近 (§2.2) | 無音演出の強化 | 小 |
| B | `sfxBossDefeat()` — ボス撃破 (§2.2) | 最重要イベントの強調 | 小 |
| C | `sfxCritical()` — クリティカル (§2.2) | 操作感の向上（要バトルロジック拡張） | 中 |

工数: 小 = ~5行（関数定義+呼び出し追加）, 中 = ~20行（ロジック変更を伴う）

---

## 7. 変更影響範囲

| 変更 | 影響する関数/変数 | テスト影響 |
|------|-------------------|------------|
| sfxStep 追加 | update() 内の移動処理 | テスト対象外（Audio依存） |
| sfxPoison 追加 | enemyTurn() | 既存テストへの影響なし（sfx はモック済み） |
| sfxPoisonTick 追加 | update() 内の毒ダメージ | テスト対象外 |
| sfxSave 追加 | processMenuInput() | 既存テストへの影響なし |
| sfxDungeonIn 追加 | enterDungeon() | sfxSelect→sfxDungeonIn の変更のみ |
| sfxBossApproach 追加 | updateBGM() | ロジック変更（フラグ追加） |
| sfxBossDefeat 追加 | processVictory() | 既存テストへの影響なし |
| sfxZoneChange 追加 | updateBGM() | ロジック変更（lastZone 追加） |
| sfxCure 追加 | applyItemEffect() 呼び出し元 | 既存テストへの影響なし |
| bossApproachPlayed 追加 | resetGameState() | resetGameState テスト更新 |
| lastZone 追加 | resetGameState() | resetGameState テスト更新 |

`module.exports` に全新規SE関数 + `bossApproachPlayed`(getter/setter) + `lastZone`(getter/setter) を追加すること。

---

## 設計原則（sfx-concepts.md との対応）

| コンセプトカテゴリ | 本設計での実現 |
|-------------------|---------------|
| ①フィードバック音 | `sfxCursor`/`sfxSelect`/`sfxMiss`（既存）+ `sfxSave`（新規） |
| ②状態変化音 | `sfxLevelUp`/`sfxDead`（既存）+ `sfxPoison`/`sfxCure`/`sfxPoisonTick`/`sfxZoneChange`（新規） |
| ③予兆音 | `sfxBattle`（既存）+ `sfxDungeonIn`/`sfxBossApproach`（新規） |
| ④強調音 | `sfxBossDefeat`（新規、ゲーム中1回の最重要イベント） |
| ⑤空間音 | `sfxStep`（新規、地形別音色で場所を表現） |
| ⑥操作感の音 | `sfxAttack`/`sfxHit`/`sfxMagic`（既存）+ `sfxCritical`（新規） |

| 設計ルール | 本設計での遵守 |
|-----------|---------------|
| ①意味1つ | 1関数=1用途。`sfxPoison`≠`sfxHit`、`sfxCure`≠`sfxHeal` |
| ②強さで重要度 | 0.03(環境)→0.05(操作)→0.10(行動)→0.12(最重要) の5段階 |
| ③繰り返し耐性 | 全SE が 0.03〜1.0秒。高頻度の `sfxStep` は0.04秒/vol0.03 |
| ④音なしでも成立 | 全SEを無効にしてもゲームプレイに支障なし |
