#!/usr/bin/env bash
# .git/hooks/{pre-commit,post-commit} を冪等に作成する。
#
# 使い方:
#   bash tools/install_hooks.sh
#
# pre-commit:
#   - repo 管理の .githooks/pre-commit を実行
#   - tasknote commit 時は TASKNOTE_PRECOMMIT=1 で shared tasknote lint を実行
#   - 通常は make verify を実行
#   緊急時は SKIP_TESTS=1 git commit でバイパス可能。
#
# post-commit:
#   - tools/update_top_changes.py（top_changes.json を Claude Haiku で更新）
#   失敗時も silent skip でコミットを壊さない。

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_DIR="$ROOT/.git/hooks"
mkdir -p "$HOOK_DIR"

# ----- pre-commit -----
PRE_COMMIT="$HOOK_DIR/pre-commit"
cat > "$PRE_COMMIT" <<'PRE_COMMIT'
#!/usr/bin/env bash
# Auto-installed by tools/install_hooks.sh
# repo 管理の .githooks/pre-commit へ委譲する。

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "${REPO_ROOT}" ]]; then
  exit 0
fi
cd "$REPO_ROOT"

HOOK_SCRIPT="$REPO_ROOT/.githooks/pre-commit"
if [[ ! -x "${HOOK_SCRIPT}" ]]; then
  echo "pre-commit: missing executable ${HOOK_SCRIPT}" >&2
  echo "  - Re-run: bash tools/install_hooks.sh" >&2
  exit 1
fi

exec "$HOOK_SCRIPT" "$@"
PRE_COMMIT
chmod +x "$PRE_COMMIT"
echo "[install-hooks] installed: $PRE_COMMIT"

# ----- post-commit -----
POST_COMMIT="$HOOK_DIR/post-commit"
cat > "$POST_COMMIT" <<'POST_COMMIT'
#!/usr/bin/env bash
# Auto-installed by tools/install_hooks.sh
# top_changes.json を Claude Haiku 経由で自動更新する。
# 失敗時も silent (exit 0) で commit を壊さない。

set +e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  exit 0
fi

PYTHON_BIN="${PYTHON:-python3}"
"$PYTHON_BIN" "$REPO_ROOT/tools/update_top_changes.py"
exit 0
POST_COMMIT
chmod +x "$POST_COMMIT"
echo "[install-hooks] installed: $POST_COMMIT"

echo
echo "[install-hooks] tip: ANTHROPIC_API_KEY を環境に設定すると post-commit の AI 判定が有効化されます。"
echo "[install-hooks] tip: 緊急時のバイパスは SKIP_TESTS=1 git commit"
