# P1-B: Game instance state inventory

**生成元**: `sed -n '4771,7234p' src/runtime/main_runtime.py | grep -oE 'self\.[a-zA-Z_]+'` から method を除外した 80 件。

## 分類サマリ

| 分類 | 件数 | 移動先 |
|---|---|---|
| GameState（scene 跨ぎ共有 state） | 20 | `src/shared/services/game_state.py` |
| scene-local state（各 scene の model） | 40 | `src/scenes/*/model.py` |
| service-owned（各 service が保有） | 18 | 各 service |
| 注入参照（service instance への参照） | 5 | constructor DI |
| 定数（class 属性） | 1 | `image_banks.py` へ移動 |
| **合計** | **84** | （1 field が複数カテゴリに重複カウント） |

---

## A. GameState（20 fields）

`@dataclass GameState` の中に置く。scene 間で共有される state のみ。

### player（1）

- `player: dict` — 内部キー：`hp / mp / exp / level / stats / inventory / x / y / in_dungeon / glitch_lord_defeated / boss_defeated（legacy）` 等

> **v2 マトリクス修正**: `glitch_lord_defeated` と `in_dungeon` は **player dict 内のキー**（line 335, 5557 で確認）。独立 GameState field として扱わない。

### progression flags（4）

- `cave_unblock_shown: bool` ← from `self._cave_unblock_shown`
- `tree_cleared_shown: bool` ← from `self._tree_cleared_shown`
- `poison_step_counter: int` ← from `self._poison_step_counter`
- `has_save: bool` ← from `self._has_save`

### world / dungeon（6）

- `world_map: list` ← `self.world_map`
- `dungeon_map: list | None` ← `self.dungeon_map`
- `dungeon_rooms: list` ← `self.dungeon_rooms`
- `dungeon_spawn: tuple[int, int] | None` ← `self.dungeon_spawn`
- `dungeon_template: Any` ← `self.dungeon_template`
- `dungeon_template_rooms: list` ← `self.dungeon_template_rooms`

### position / camera（5）

- `cam_x: int` ← `self.cam_x`
- `cam_y: int` ← `self.cam_y`
- `world_return_x: int` ← `self.world_return_x`
- `world_return_y: int` ← `self.world_return_y`
- `last_town_pos: tuple[int, int]` ← `self.last_town_pos`

### scene tracking（2）

- `state: str` ← `self.state`（現在 scene 名、debug bootstrap 用）
- `prev_state: str` ← `self.prev_state`（back navigation 用）

### debug（2）

- `debug_mode: bool` ← `self.debug_mode`
- `debug_seq: list` ← `self.debug_seq`

---

## B. scene-local state（40 fields）

各 scene の `model.py` が保有。scene 内でのみ使う。

### title/model.py（1）

- `title_cursor` ← `self.title_cursor`

### splash/model.py（1）

- `splash_frame` ← `self.splash_frame`

### explore/model.py（4）

- `walk_frame` ← `self.walk_frame`
- `walk_timer` ← `self.walk_timer`
- `move_cooldown` ← `self.move_cooldown`
- `a_cooldown` ← from `self._a_cooldown`

### town/model.py（3）

- `town_menu_cursor` ← `self.town_menu_cursor`
- `town_menu_pos` ← `self.town_menu_pos`
- `menu_message` ← `self.menu_message`（town スコープ内で使用、shop でも使う可能性要調査）

### shop/model.py（4）

- `shop_cursor` ← `self.shop_cursor`
- `shop_inventory` ← `self.shop_inventory`
- `shop_kind` ← `self.shop_kind`
- `shop_message` ← `self.shop_message`

### battle/model.py（12）

- `battle_enemy` ← `self.battle_enemy`
- `battle_enemy_hp` ← `self.battle_enemy_hp`
- `battle_phase` ← `self.battle_phase`
- `battle_boss_phase` ← `self.battle_boss_phase`
- `battle_is_glitch_lord` ← `self.battle_is_glitch_lord`
- `battle_is_professor` ← `self.battle_is_professor`
- `battle_item_select` ← `self.battle_item_select`
- `battle_spell_select` ← `self.battle_spell_select`
- `battle_menu` ← `self.battle_menu`
- `battle_text` ← `self.battle_text`
- `battle_text_timer` ← `self.battle_text_timer`
- `noise_guardian_battle` ← from `self._noise_guardian_battle`

### menu/model.py（3）

- `menu_cursor` ← `self.menu_cursor`
- `menu_item_cursor` ← `self.menu_item_cursor`
- `menu_sub` ← `self.menu_sub`

### settings/model.py（2）

- `settings_cursor` ← `self.settings_cursor`
- `settings_origin` ← `self.settings_origin`

### ai_help/model.py（1）

- `ai_help_status` ← from `self._ai_help_status`

### professor/model.py（6）

- `professor_choice_active` ← `self.professor_choice_active`
- `professor_choice_cursor` ← `self.professor_choice_cursor`
- `professor_intro_idx` ← `self.professor_intro_idx`
- `professor_intro_lines` ← `self.professor_intro_lines`
- `professor_ending_idx` ← `self.professor_ending_idx`
- `professor_ending_lines` ← `self.professor_ending_lines`

### ending/model.py（1）

- `ending_lines` ← `self.ending_lines`

### dialog 関連（2、service に入るが scene-local な意味）

- `dialog` ← `self.dialog`（現在 active な `dialog_runner` instance、持たない scene もある）

---

## C. service-owned state（18 fields）

### shared/services/message_display.py（4）

- `msg_callback` ← `self.msg_callback`
- `msg_index` ← `self.msg_index`
- `msg_lines` ← `self.msg_lines`
- `say_buffer` ← from `self._say_buffer`

### shared/services/vfx.py（2）

- `vfx_timer` ← `self.vfx_timer`
- `vfx_type` ← `self.vfx_type`

### shared/services/image_banks.py（10 + 1 定数）

- `font` ← `self.font`
- `has_jp_font` ← `self.has_jp_font`
- `tile_bank` ← `self.tile_bank`
- `tile_bank_water2` ← `self.tile_bank_water2`
- `sprite_bank` ← `self.sprite_bank`
- `path_variant_bank` ← `self.path_variant_bank`
- `shore_variant_bank` ← `self.shore_variant_bank`
- `tile_id_by_pixel` ← `self.tile_id_by_pixel`
- `pyxres_loaded` ← from `self._pyxres_loaded`
- `pyxres_path` ← from `self._pyxres_path`
- （定数）`DUNGEON_TM_OFFSET_Y` ← `self.DUNGEON_TM_OFFSET_Y`

---

## D. 注入参照（5、DI される service instance）

これらは state ではなく **依存性**。GameState には入れず、`BlockQuestApp` が保有して scene / service に渡す。

- `audio` ← `self.audio`（AudioManager instance）
- `sfx` ← `self.sfx`（SfxSystem instance、audio_system.py に吸収後は `audio.sfx` として参照に変わる可能性）
- `input_state` ← `self.input_state`（InputStateTracker instance）
- `save_store` ← `self.save_store`（SaveStore instance）
- `dialog` ← `self.dialog`（**active dialog_runner を保持する slot、下記注意**）

---

## マトリクス v2 の修正点

1. **`glitch_lord_defeated` を GameState field から削除** — player dict 内のキーなので、個別 field ではない
2. **`in_dungeon` も GameState field にしない** — 同じく player dict 内
3. **GameState field 数は 19 → 20** に訂正（上記の削除と、正しく数え直した結果）

## 次 step

- **P1-B3**：本 file が inventory 成果物（完了）
- **P1-F1**：本 inventory を基に `GameState` dataclass を実装
- **P1-G 各タスク**：本 inventory を参照して scene-local / service-owned state を migrate
