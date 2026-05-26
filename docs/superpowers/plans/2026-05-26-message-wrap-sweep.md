# Fixed-Width Message Wrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** battle と shop の固定幅 message 枠で長文が右にはみ出さないようにする

**Architecture:** `text_writer.wrap_text()` を呼ぶ View 専用 helper を追加し、battle と shop の描画だけを helper 利用へ寄せる。文言生成や state 遷移は変更せず、View と test に修正を閉じる。

**Tech Stack:** Python 3, pytest, Pyxel view layer

---

### Task 1: Add the failing rendering tests

**Files:**
- Modify: `test/test_cjg_battle_message_wrap.py`
- Create: `test/test_cjg_shop_message_wrap.py`

- [ ] **Step 1: Write the failing shop rendering test**

```python
class ShopMessageWrapTest(unittest.TestCase):
    def test_long_shop_message_uses_multiple_lines(self) -> None:
        vm = ShopViewModel(
            title="ぶきや",
            gold_label="G:999",
            rows=[],
            empty_message=None,
            message="コードエディタをてにいれた。いろがつく。インデントがそろう。それだけでうそみたいにうれしい。",
        )
```

- [ ] **Step 2: Run the targeted tests to verify RED**

Run: `python -m pytest test/test_cjg_battle_message_wrap.py test/test_cjg_shop_message_wrap.py -q`
Expected: shop の長文描画 assertion が FAIL する

- [ ] **Step 3: Tighten the battle test to keep existing behavior**

```python
self.assertEqual(
    BattleView._resolve_main_message_lines(main_text, text_writer),
    ["1行目", "2行目"],
)
```

- [ ] **Step 4: Re-run targeted tests**

Run: `python -m pytest test/test_cjg_battle_message_wrap.py test/test_cjg_shop_message_wrap.py -q`
Expected: FAIL の原因が wrap helper 未適用だけに絞られる

- [ ] **Step 5: Commit**

```bash
git add test/test_cjg_battle_message_wrap.py test/test_cjg_shop_message_wrap.py
git commit -m "test: 固定幅メッセージの折返し回帰条件を追加したい"
```

### Task 2: Add the shared View helper and wire battle/shop to it

**Files:**
- Create: `src/shared/ui/wrapped_text.py`
- Modify: `src/scenes/battle/view.py`
- Modify: `src/scenes/shop/view.py`

- [ ] **Step 1: Add the shared helper**

```python
def resolve_wrapped_lines(
    text: str,
    text_writer,
    *,
    max_chars: int,
    max_rows: int,
) -> list[str]:
    wrap_text = getattr(text_writer, "wrap_text", None)
    if not callable(wrap_text):
        return [text]
    return wrap_text(text, max_chars=max_chars)[:max_rows]
```

- [ ] **Step 2: Update battle to use the helper**

```python
return resolve_wrapped_lines(
    main_text,
    text_writer,
    max_chars=MAIN_MESSAGE_WRAP_WIDTH,
    max_rows=MAIN_MESSAGE_MAX_ROWS,
)
```

- [ ] **Step 3: Update shop to draw up to two wrapped lines**

```python
for i, line in enumerate(resolve_wrapped_lines(vm.message, text_writer, max_chars=28, max_rows=2)):
    text_writer.text(8, 200 + i * 12, line, 11)
```

- [ ] **Step 4: Run targeted tests to verify GREEN**

Run: `python -m pytest test/test_cjg_battle_message_wrap.py test/test_cjg_shop_message_wrap.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/shared/ui/wrapped_text.py src/scenes/battle/view.py src/scenes/shop/view.py test/test_cjg_battle_message_wrap.py test/test_cjg_shop_message_wrap.py
git commit -m "fix: 固定幅メッセージを枠内で折り返したい"
```

### Task 3: Run regression and artifact verification

**Files:**
- Modify: `steering/2026年5月26日 UI：固定幅メッセージのはみ出しを横断修正する.md`

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest test/ -q`
Expected: PASS

- [ ] **Step 2: Rebuild browser artifacts**

Run: `PYTHONPATH=. python tools/build_web_release.py`
Expected: exit 0

- [ ] **Step 3: Copy and review the checklist**

Run: `cp docs/development-checklist.md /tmp/development-checklist-20260526-1426.md`
Expected: `/tmp/development-checklist-20260526-1426.md` が作成される

- [ ] **Step 4: Update tasknote with facts and closeability**

```markdown
- `python -m pytest test/ -q` は ... passed
- `PYTHONPATH=. python tools/build_web_release.py` は成功
```

- [ ] **Step 5: Commit**

```bash
git add steering/2026年5月26日\ UI：固定幅メッセージのはみ出しを横断修正する.md dist/
git commit -m "docs: 折返し修正の検証結果を記録したい"
```
