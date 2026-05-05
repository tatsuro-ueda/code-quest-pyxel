---
status: open
priority: normal
scheduled: 2026-05-06T01:00:00.000+09:00
dateCreated: 2026-05-06T01:00:00.000+09:00
dateModified: 2026-05-06T01:00:00.000+09:00
tags:
  - task
---

# 2026年5月6日 BGM も pyxres を SSoT にする（AudioManager の Code Maker 編集無効問題を解消）

> 状態：① Journey 起票完了
> 次のゲート：（ユーザー）Journey/Gherkin/Design/Tasklist の妥当性を確認 →「実装」or「修正」と指示

---

## 1) Journey（どこへ行くか）

- **深層的目的**：「Code Maker で編集すれば必ず鳴る」を約束する
- **やらないこと**：BGM トラック内容の作曲改編／チャネルゲイン設計の変更／runtime の再生タイミング変更（別タスク）

1. ❓ （子ども）町の BGM をもっと冒険っぽくしたいな（生活）
2. 💦 （親 / AI）Pyxel Code Maker で `town` の sounds スロットを編集して保存（Code Maker）
3. 💦 （子ども）ゲームを起動してフィールドに出る（Web）
4. Before
  1. ❌ いつもと同じ BGM が流れる（Web）
  2. ❌ （子ども）え、変えたのに……（生活）
  3. ❌ Code Maker は飾りに見える → 編集する気が失せる
5. After
  1. ✅ 編集した新しい BGM が流れる（Web）
  2. ♥️ （子ども）変えたのが鳴った！もっといじりたい（生活）
  3. ♥️ Code Maker = 自分の楽器 → CJ15/CJ16 が成立、Buy2 約束が回復

### Before（現状）

- 😕 **BGM は pyxres を完全無視**：`src/runtime/app.py:75` で `setup_image_banks` の後にもう 1 回 `AudioManager(pyxel)` が呼ばれ、`_load_tracks` が無条件で `CHIPTUNE_TRACKS`（Python 定数）を `pyxel.sounds[mslot/bslot/dslot].set(...)` と `pyxel.musics[i].set(...)` に書き戻す。**Code Maker で BGM を編集して pyxres を保存しても、起動時に Python 定数で上書きされて消える**。
- 😕 一方 **SFX は pyxres を尊重**：`SfxSystem._slot_has_sound(slot)` で「pyxres にすでに sound が入っている slot は fallback をスキップ」する設計（`src/shared/services/audio_system.py:286-296`）。docstring にも「Code Maker / pyxel.load() 済み slot があればそれを優先する」と明記されている。**BGM 側だけこの設計が抜けている非対称**。
- 😕 ImageBanks setup_image_banks の docstring (`src/shared/services/image_banks.py:65-71`) は「pyxres は画像バンクと音バンクの両方を含む。pyxel.load すると AudioManager / SfxSystem が既に書き込んだ sounds 0-42 も .pyxres の内容で上書きされる」と正しい挙動を書いているが、その後の app.py:75 の `AudioManager(pyxel)` 再呼びが BGM だけ Python 定数で覆い直すので、**実装と docstring が乖離**している。
- 😕 影響範囲（customer-journeys.md と対応）：
  - **CJ15「フィールド BGM をゾーンごとに付ける」** ❌ 反映されない
  - **CJ16「戦闘 BGM を付ける」** ❌ 反映されない
  - **CJ17「効果音をイベントに紐づける」** ⚠ SFX 紐付け部分のみ OK、BGM の差し替えは NG
  - **CJ24「効果音を自分で作る」** ✅ SFX 側は対称な設計があるので OK
- 😕 これは **Buy2「Pyxel Code Maker は子どもの正式な編集面」** という Make 約束を BGM について破っている状態。framework-rule.md M4-2（2026-05-05 改訂）で `ImageBanks` は「pyxres = SSoT」へ移行済だが、`AudioManager` には同じ移行が及んでいない。
- 😕 framework-rule.md M4-2 の記述に `AudioManager` は **無印**で並んでいる（`ImageBanks` のように責務範囲を限定する注記がない）。読み手は「AudioManager も SSoT 設計だろう」と誤読しうる。

### After（達成状態）

- 🙂 `AudioManager._load_tracks` に **`_slot_has_sound` / `_music_has_data` ガード**を追加。pyxres にすでに sounds/musics が入っている slot はスキップし、空 slot だけ `CHIPTUNE_TRACKS` で埋める（SFX と完全に対称）。
- 🙂 `CHIPTUNE_TRACKS` は Python 定数として残るが、責務は **「pyxres 不在時／空 slot 限定の fallback」**に降格。
- 🙂 起動時に「Code Maker で編集した BGM」が **そのまま鳴る**。CJ15/CJ16 が runtime で成立、Buy2 約束が BGM についても回復。
- 🙂 `framework-rule.md` M4-2 で `AudioManager` の責務記述を `ImageBanks` と同じ形式に揃える（「pyxres ロード後は読み取り専用、書き込みは空 slot fallback のみ」）。
- 🙂 `audio_system.py` の AudioManager docstring も「Code Maker 編集を優先する」と明記（SFX docstring と対称）。
- 🙂 静的 guard：`AudioManager._load_tracks` が `_slot_has_sound` / `_music_has_data` を呼ぶことを AST で検証（SFX と同じ pattern が崩れないこと）。
- 🙂 customer-journeys CJ15/CJ16 の感情遷移「❌放置 / ❌ゲームっぽくない → ❤️世界が立ち上がる / ❤️緊張感」が **runtime 動作で実現可能**になる（現状は docs だけ書かれている状態を脱する）。

---

## 2) Gherkin（完了条件）

### シナリオ 1：pyxres 編集済の BGM slot が起動時に保護される（正常系）

- 🧱 Given：pyxres が町用 BGM の sounds 0/1/2 に独自データを持って保存済み
- 🎬 When：`python main.py` 起動 → `setup_image_banks` で `pyxel.load(pyxres)` → `AudioManager(pyxel)` 再 init
- ✅ Then：`AudioManager._load_tracks` が町 slot をスキップし、`pyxel.sounds[0/1/2]` の中身は **pyxres の独自データのまま**。`pyxel.musics[town_index]` の中身も無変更。

### シナリオ 2：pyxres 不在 / 空 slot は CHIPTUNE_TRACKS で埋まる（fallback 確認）

- 🧱 Given：`assets/blockquest.pyxres` を一時退避（不在状態）
- 🎬 When：`python main.py` 起動
- ✅ Then：fallback bake 経路で `paint_tile_bank` 等が走り、`AudioManager._load_tracks` も全 slot に `CHIPTUNE_TRACKS` を書き込む（`_slot_has_sound` が False を返すため）。BGM は従来通り鳴る。

### シナリオ 3：SFX と同じ docstring / コードパターンが揃う

- 🧱 Given：実装後の `audio_system.py`
- 🎬 When：`AudioManager._load_tracks` を読む
- ✅ Then：先頭で `if self._slot_has_sound(mslot) and self._slot_has_sound(bslot) and self._slot_has_sound(dslot) and self._music_has_data(music_index(scene_name)): continue` 的な早期 continue が入っている。`SfxSystem._load` と対称。docstring も「Code Maker 編集を優先する」と明記。

### シナリオ 4：チャネルゲイン設定は pyxres と独立に動く（リスク確認）

- 🧱 Given：pyxres 在中で BGM 上書きをスキップした起動
- 🎬 When：`AudioManager._load_tracks` 完了直後
- ✅ Then：`pyxel.channels[MELODY_CHANNEL].gain` 等は **依然として `CHIPTUNE_TRACKS["title"]["gain"]` に設定**される（ミキサー設定であり pyxres には保存されないため）。pyxres 尊重対象は sounds/musics の **データ内容**のみ。

### シナリオ 5：framework-rule M4-2 の記述が AudioManager にも及ぶ

- 🧱 Given：実装後の `docs/framework-rule.md`
- 🎬 When：M4-2「Infrastructure Service」節を読む
- ✅ Then：`AudioManager` 行に `ImageBanks` と同じ形式の注記が入る：「pyxres ロード後は **空 slot 限定の fallback 書き込みのみ**、編集済 slot は Code Maker 優先（2026-05-06 改訂）」。

### シナリオ 6：再侵入を防ぐ静的 guard

- 🧱 Given：実装完了後の repo
- 🎬 When：`pytest test/test_cjg_framework_rule_guards.py -q` を実行
- ✅ Then：以下の guard が緑：
  - **G1**: `AudioManager._load_tracks` の AST に `_slot_has_sound` または `_music_has_data` の呼び出しが含まれる（無条件 `.set` 呼びへの retreat を検出）
  - **G2**: `audio_system.py` で `pyxel.sounds[...].set(` 呼び出しは必ず `_slot_has_sound` チェック後の分岐に存在する（grep ベースでよい）

### シナリオ 7：既存テストが緑のまま

- 🧱 Given：作業前 `pytest test/ -q` = 718 passed（test/test_audio_system.py 内の AudioManager テストを含む）
- 🎬 When：ガード追加 + AudioManager 改修後
- ✅ Then：718 + 新 guard 数 で全緑。特に `test_audio_system.py` で「pyxres 不在時に CHIPTUNE_TRACKS が書かれる」を検証している既存ケースが壊れない（fallback 経路は維持）。

### シナリオ 8：実機で Code Maker 編集 BGM が鳴る（最終確認 / 人作業）

- 🧱 Given：実装後、Pyxel Code Maker で町 BGM の melody slot を改編して pyxres 保存
- 🎬 When：`python main.py` 起動 → タイトル → 町に入る
- ✅ Then：**改編した melody が鳴る**（従来は Python 定数の melody が鳴っていた）。これが達成されると Buy2 約束が BGM について実際に成立。

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：Read / Edit / Bash / pytest。実機検証は人作業（Pyxel Code Maker での編集→起動→聴覚確認）。

### 構成図

```text
                    Before（現状）                                        After
                    ────────────                                        ─────
pyxres ──pyxel.load──► sounds 0-32 ──┐                pyxres ──pyxel.load──► sounds 0-32 ──┐
                                     │                                                     │
                                     ▼                                                     ▼
              AudioManager._load_tracks                          AudioManager._load_tracks
              ↓ 無条件で .set() で上書き                           ↓ _slot_has_sound() で gate
              CHIPTUNE_TRACKS の melody/bass/drum                  pyxres にあれば skip
              を sounds 0-32 に書く                                空なら CHIPTUNE_TRACKS を書く
                                     │                                                     │
                                     ▼                                                     ▼
                            sounds 0-32 = Python 定数               sounds 0-32 = pyxres 優先（fallback あり）
                            ❌ Code Maker 編集が消える               ✅ Code Maker 編集が生きる
```

### コード変更（最小差分）

`src/shared/services/audio_system.py::AudioManager` に SFX と対称な 2 つのヘルパを追加し、`_load_tracks` をガードする。

```python
class AudioManager:
    """Pyxel 音声 API をラップし、シーンごとの BGM 再生と ON/OFF を管理する。

    2026-05-06 改訂：pyxres = SSoT。`_load_tracks` は **空 slot 限定の fallback**
    として CHIPTUNE_TRACKS を書く。Code Maker / pyxel.load() 済み slot は優先。
    SFX 側 `SfxSystem._slot_has_sound` と対称な設計。
    """

    def _slot_has_sound(self, slot: int) -> bool:
        """SfxSystem._slot_has_sound と同じ判定（重複 OK、責務分離のため AudioManager にも持つ）。"""
        sound = self.pyxel.sounds[slot]
        for attr in ("notes", "tones", "volumes", "effects"):
            try:
                if len(getattr(sound, attr)) > 0:
                    return True
            except Exception:
                continue
        return False

    def _music_has_data(self, music_index_value: int) -> bool:
        """pyxel.musics[i] に既に data が入っているか判定。"""
        music = self.pyxel.musics[music_index_value]
        # pyxel.Music は snds_list / seqs 等の属性を持つ。FakeMusic 互換のため
        # 複数の属性名を try する。
        for attr in ("snds_list", "seqs", "sequences", "seqs0", "snds0"):
            try:
                value = getattr(music, attr)
                if isinstance(value, (list, tuple)):
                    if any(len(seq) > 0 for seq in value if hasattr(seq, "__len__")):
                        return True
            except Exception:
                continue
        return False

    def _load_tracks(self):
        """空 slot に CHIPTUNE_TRACKS を fallback として流し込む（pyxres 優先）。"""
        for scene_name in TRACK_ORDER:
            data = CHIPTUNE_TRACKS[scene_name]
            speed = data["speed"]
            mslot = melody_slot(scene_name)
            bslot = bass_slot(scene_name)
            dslot = drum_slot(scene_name)
            midx = music_index(scene_name)

            if (
                self._slot_has_sound(mslot)
                and self._slot_has_sound(bslot)
                and self._slot_has_sound(dslot)
                and self._music_has_data(midx)
            ):
                continue  # pyxres 編集を優先（Code Maker SSoT）

            # 1 つでも欠けていれば、scene 単位で fallback で埋める
            if not self._slot_has_sound(mslot):
                self.pyxel.sounds[mslot].set(data["melody"], "p", "6", "n", speed)
            if not self._slot_has_sound(bslot):
                self.pyxel.sounds[bslot].set(data["bass"], "t", "5", "n", speed)
            if not self._slot_has_sound(dslot):
                self.pyxel.sounds[dslot].set(data["drums"], "n", "4", "f", speed)
            if not self._music_has_data(midx):
                self.pyxel.musics[midx].set([mslot], [bslot], [dslot], [])

        # チャネルゲインは pyxres ではなく runtime mixer 設定なので常に設定
        title_gain = CHIPTUNE_TRACKS["title"]["gain"]
        self.pyxel.channels[MELODY_CHANNEL].gain = title_gain
        self.pyxel.channels[BASS_CHANNEL].gain = title_gain * 0.7
        self.pyxel.channels[DRUM_CHANNEL].gain = title_gain * 0.5
```

### docstring 更新

| ファイル | 更新内容 |
|---|---|
| `src/shared/services/audio_system.py::AudioManager` クラス docstring | 「pyxres = SSoT、CHIPTUNE_TRACKS は空 slot fallback」と明記 |
| `src/shared/services/audio_system.py::_load_tracks` docstring | 「空 slot 限定の fallback」と明記 |
| `docs/framework-rule.md` M4-2 Infrastructure Service の `AudioManager` 行 | 「pyxres ロード後は空 slot 限定の fallback、編集済 slot は Code Maker 優先（2026-05-06 改訂）」を追記 |
| `src/shared/services/image_banks.py::setup_image_banks` docstring | 「Audio も pyxres を尊重するようになった」と更新（過去の「上書きされる」記述を修正） |

### 静的 guard（test_cjg_framework_rule_guards.py に追加）

```python
def test_audio_manager_load_tracks_uses_pyxres_guard(self):
    """AudioManager._load_tracks が _slot_has_sound / _music_has_data を呼んでいる。

    pyxres = SSoT 化（2026-05-06 改訂）。CHIPTUNE_TRACKS を無条件で
    pyxel.sounds[*].set() するコードへの retreat を AST で検出して即 fail。
    """
    src = (ROOT / "src" / "shared" / "services" / "audio_system.py").read_text(encoding="utf-8")
    func = _function_node_in_class(src, "AudioManager", "_load_tracks")
    calls = _calls_in(func)
    self.assertTrue(
        "_slot_has_sound" in calls or "_music_has_data" in calls,
        "_load_tracks が pyxres ガードを失っている（Code Maker 編集が runtime に届かなくなる）",
    )
```

### 手順フロー

1. **影響範囲 grep**：`AudioManager / CHIPTUNE_TRACKS / _load_tracks / pyxel.sounds.*set / pyxel.musics.*set` の利用箇所列挙。
2. **`audio_system.py::AudioManager` 改修**：`_slot_has_sound` / `_music_has_data` 追加、`_load_tracks` をガード化、docstring 更新。
3. **既存 test 確認**：`test/test_audio_system.py` / `test/test_cjg_audio_manager_behavior.py` / `test/test_cj24_sound_editor_truth.py` を読み、空 slot 前提のケース（FakeSound 初期化直後で pyxres 不在に相当）が引き続き通るか確認。必要なら fixture 微調整。
4. **pytest 緑確認**（718 passed 維持）。
5. **静的 guard 追加**：`test_cjg_framework_rule_guards.py` に AST ベースのチェックを追加 → 718 → 719 passed。
6. **docstring 更新**：`framework-rule.md` M4-2、`audio_system.py` AudioManager、`image_banks.py` setup_image_banks。
7. **commit**：`refactor(audio): BGM も pyxres を SSoT にする（Code Maker 編集を優先）`。
8. **実機目視確認**（人作業）：Pyxel Code Maker で町 BGM の melody slot を改編 → `python main.py` 起動 → 町で改編 melody が鳴ることを聴覚確認。
9. **commit (b)**：必要なら docstring 微修正と確認結果メモ。
10. **`make build`** → `production/` 再生成 → commit → push。
11. **Result / Discussion 記入** → steering/done/ へ移動。

### リスクと対処

| リスク | 対処 |
|---|---|
| `_music_has_data` が pyxel.Music の実 API（`snds_list` 等）と FakeMusic（test 用）の双方で動く保証 | 複数属性名を try、いずれも空なら False。`FakeMusic.set_calls` で test 側も補強。失敗したら test を追加 |
| 既存 `test_audio_system.py` が「`_load_tracks` 後に sounds[*].set が必ず呼ばれる」を assert している場合 | test を「pyxres 空 slot 前提なら従来通り、pyxres 在中 slot ならスキップ」の 2 ケースに分割 |
| pyxres 内の sounds 0-32 が現状 CHIPTUNE_TRACKS と同じ内容で焼き戻されている可能性 | 起動時に「同じ音」が鳴るので一見何も変わらない。実機確認は **Code Maker で編集 → 起動** の流れで差分を作って判定 |
| AudioManager が **2 回 init** される現状（app.py:66 と :75）の意味 | 1 回目は pyxres ロード前で空 slot 状態、2 回目は pyxres ロード後。両方とも `_slot_has_sound` ガードがあれば挙動正しい（1 回目は fallback、2 回目は skip）。冗長だが安全側に倒して残す |
| `play_scene` 内の `CHIPTUNE_TRACKS[scene_name]["gain"]` 参照は ok か | OK。gain は mixer 設定で pyxres には保存されない。本タスクで触らない |

### ゲート

- ユーザー承認待ち。承認後は途中で止めずに完走可（実機目視確認の 1 ステップだけ人作業）。

---

## 4) Tasklist

> 上から順に実施。CC が CoVe で自力検証しながら進める。

- [ ] （CC）影響範囲 grep（`AudioManager / CHIPTUNE_TRACKS / _load_tracks / pyxel\\.sounds.*set / pyxel\\.musics.*set`）
- [ ] （CC）`src/shared/services/audio_system.py::AudioManager` に `_slot_has_sound` / `_music_has_data` 追加
- [ ] （CC）`_load_tracks` をガード化（scene 単位で空 slot のみ fallback 書込み）
- [ ] （CC）AudioManager クラス / `_load_tracks` の docstring 更新
- [ ] （CC）`pytest test/test_audio_system.py test/test_cjg_audio_manager_behavior.py test/test_cj24_sound_editor_truth.py -v` で個別緑確認
- [ ] （CC）`pytest test/ -q` 全緑確認（718 passed 維持）
- [ ] （CC）`test_cjg_framework_rule_guards.py` に G1（`_load_tracks` ガード AST 検証）+ G2（grep ベース）追加 → 718 → 720 passed
- [ ] （CC）`docs/framework-rule.md` M4-2 の AudioManager 行を ImageBanks と同じ形式で更新
- [ ] （CC）`src/shared/services/image_banks.py::setup_image_banks` docstring を「Audio も pyxres を尊重」に更新
- [ ] （CC）commit (a)：`refactor(audio): BGM も pyxres を SSoT にする（Code Maker 編集を優先）`
- [ ] （ユーザー）Pyxel Code Maker で町 BGM melody slot を改編 → `python main.py` 起動 → 町で改編 melody が鳴ることを聴覚確認
- [ ] （CC）`make build` → `production/code-maker.zip` 等再生成 → commit (b)：`build: BGM SSoT 化に伴う bundle 再ビルド`
- [ ] （CC）`git push origin main`
- [ ] （CC）Result セクションに作業ログ、Discussion に保留点・要約を記入
- [ ] （CC）steering/done/ へ移動

### 作業記録

> Observe → Think → Act を刻む。

#### 2026-05-06 01:00（起票）

**Observe**：直前会話で「pyxel.bltm が 1 か所だけのわりに shared/services にマップ系コードが多い」を整理した流れで、ユーザーから「音楽や効果音は pyxres から直読みしているか？」と問い。grep で `AudioManager._load_tracks` が無条件 `.set()` を打つことを発見。SFX 側には `_slot_has_sound` ガードがあって対称が崩れている。
**Think**：BGM 側に同じガードを入れれば SFX と完全対称になり、最小差分で「Code Maker 編集が runtime に反映」が成立。`_music_has_data` は pyxel.Music API の属性名を複数 try する防御的な実装で FakeMusic 互換も担保。framework-rule.md M4-2 と image_banks.py docstring も同改訂で揃える。
**Act**：本タスクノートを起票し Journey/Gherkin/Design/Tasklist を書いた。実装単位は最小（audio_system.py への 2 ヘルパ追加 + `_load_tracks` のガード化 + docstring 3 か所）。ユーザー承認後に実装へ進む。

---

## 5) Result（成果物）

実装後に作業ログを書く。

---

## 6) Discussion（反省）

実装後に保留点・指針・要約を書く。

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：
