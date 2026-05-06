"""post-commit hook の本体：commit log を Claude Haiku で解釈して
top_changes.json に「子どもに関係する変更」を 1 行追記する。

呼び出し元: .git/hooks/post-commit (install_hooks.sh で配置)

挙動:
  1. 直前 commit の subject + body を取得
  2. AUTO_MARKER (`[top-changes auto]`) があれば即 exit 0（再帰防止）
  3. ANTHROPIC_API_KEY が無ければ stderr 警告のみで exit 0
  4. Claude Haiku に判定させる:
       - 関係なし → exit 0（top_changes.json は無変更）
       - 関係あり → 1 行翻訳を返す
  5. top_changes.json の changes 先頭に prepend（MAX_KEEP=20 で truncate）
  6. tools/render_top_changes.py を呼んで index.html を更新
  7. git commit --amend --no-edit で直前 commit に取り込む
       commit body 末尾に AUTO_MARKER を残して再帰を断つ

すべての fail パスで exit 0 を返す（commit 自体を壊さない）。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOP_CHANGES_PATH = ROOT / "top_changes.json"
INDEX_HTML_PATH = ROOT / "index.html"
RENDER_SCRIPT = ROOT / "tools" / "render_top_changes.py"

AUTO_MARKER = "[top-changes auto]"
MAX_KEEP = 20
MODEL = "claude-haiku-4-5-20251001"


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
    ).strip()


def _today_short() -> str:
    """`5/6` 形式（先頭 0 なし）。"""
    import datetime as _dt
    today = _dt.date.today()
    return f"{today.month}/{today.day}"


def _is_auto_amend(subject: str, body: str) -> bool:
    return AUTO_MARKER in subject or AUTO_MARKER in body


def _build_prompt(subject: str, body: str) -> str:
    today = _today_short()
    return (
        "次の git commit が「Block Quest（子ども向け Pyxel RPG）の利用者（小学生）に関係する変更」かを判定し、\n"
        f"関係する場合のみ、小学生でも分かる短い 1 行（漢字最小、絵文字なし、日付 \"{today}: \" で始める）を JSON で返してください。\n"
        "関係しない場合は {\"include\": false} を返してください。\n"
        "- 関係する例：新機能、バグ修正で遊びやすくなった、新しい敵 / 装備 / マップ、UI 改善\n"
        "- 関係しない例：refactor、test、docs（README/AGENTS 等）、build、CI、内部リファクタ\n\n"
        f"commit subject: {subject}\n"
        f"commit body: {body}\n\n"
        "JSON 形式: {\"include\": true, \"line\": \"...\"} または {\"include\": false}"
    )


def call_claude(prompt: str, *, api_key: str, model: str = MODEL) -> dict:
    """Claude Haiku を呼んで JSON を返す。失敗時は {include: false}。"""
    try:
        from anthropic import Anthropic
    except ImportError:
        print("[top-changes] anthropic SDK が無いのでスキップ", file=sys.stderr)
        return {"include": False}

    client = Anthropic(api_key=api_key)
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        # ```json ... ``` で囲まれていたら剥がす
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:]
        return json.loads(text.strip())
    except Exception as exc:
        print(f"[top-changes] Claude 呼び出し失敗: {exc}", file=sys.stderr)
        return {"include": False}


def prepend_change(line: str, *, max_keep: int = MAX_KEEP) -> bool:
    """top_changes.json の `changes` の先頭に line を挿入する。`changed?` を返す。"""
    if not TOP_CHANGES_PATH.exists():
        return False
    data = json.loads(TOP_CHANGES_PATH.read_text(encoding="utf-8"))
    changes = data.get("changes", [])
    if not isinstance(changes, list):
        return False
    if changes and changes[0] == line:
        # 連続同一行を防止（rebase / amend 等で同じ commit が再度通る場合）
        return False
    changes.insert(0, line)
    data["changes"] = changes[:max_keep]
    TOP_CHANGES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )
    return True


def render_index() -> None:
    subprocess.check_call([sys.executable, str(RENDER_SCRIPT)], cwd=ROOT)


def amend_with_marker(subject: str, body: str) -> None:
    """直前 commit に top_changes.json + index.html を amend で取り込む。

    commit body 末尾に AUTO_MARKER を残し、次回 hook で再帰を断つ。
    """
    new_body = body.rstrip()
    if AUTO_MARKER not in new_body:
        new_body = (new_body + "\n\n" + AUTO_MARKER).strip()
    new_message = subject if not new_body else f"{subject}\n\n{new_body}"
    subprocess.check_call(["git", "add", "top_changes.json", "index.html"], cwd=ROOT)
    subprocess.check_call(
        ["git", "commit", "--amend", "-m", new_message],
        cwd=ROOT,
    )


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    dry_run = "--dry-run" in argv

    try:
        subject = _git("log", "-1", "--format=%s")
        body = _git("log", "-1", "--format=%b")
    except Exception as exc:
        print(f"[top-changes] git log 取得失敗: {exc}", file=sys.stderr)
        return 0

    if _is_auto_amend(subject, body):
        # 自分が打った amend commit に再度反応するのを止める
        return 0

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "[top-changes] ANTHROPIC_API_KEY 未設定のためスキップ "
            "（手で top_changes.json を編集すれば反映できます）",
            file=sys.stderr,
        )
        return 0

    prompt = _build_prompt(subject, body)
    if dry_run:
        print("[top-changes] --dry-run prompt:")
        print(prompt)
        return 0

    result = call_claude(prompt, api_key=api_key)
    if not result.get("include"):
        return 0

    line = result.get("line", "").strip()
    if not line:
        return 0

    if not prepend_change(line):
        return 0

    try:
        render_index()
    except Exception as exc:
        print(f"[top-changes] render 失敗: {exc}", file=sys.stderr)
        return 0

    try:
        amend_with_marker(subject, body)
        print(f"[top-changes] 追加: {line}")
    except Exception as exc:
        print(f"[top-changes] amend 失敗: {exc}", file=sys.stderr)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
