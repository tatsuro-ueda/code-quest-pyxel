#!/usr/bin/env bash
# .git/hooks/{pre-commit,post-commit} を冪等に作成する。
#
# 使い方:
#   bash tools/install_hooks.sh
#
# pre-commit:
#   - make verify（モジュール docstring drift / CJ-CJob 整合 / scene_to_cj 対応表）
#   - pytest（既存テスト）
#   どちらかが失敗するとコミットがブロックされる。
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
# 1) make verify（モジュール docstring drift / CJ-CJob 整合 / scene_to_cj 対応表）
# 2) pytest（既存テスト）
# 緊急時は SKIP_TESTS=1 git commit でバイパス可能。

set -euo pipefail

if [[ "${SKIP_TESTS:-}" == "1" ]]; then
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  exit 0
fi
cd "$REPO_ROOT"

echo "pre-commit: make verify ..."
if ! make verify; then
  echo "pre-commit: verify FAILED. Commit blocked."
  echo "  - Fix docstring drift / CJ link / map issues."
  echo "  - Or use SKIP_TESTS=1 git commit to bypass (not recommended)."
  exit 1
fi

echo "pre-commit: pytest ..."
if python -m pytest test/ -q --tb=short 2>&1; then
  echo "pre-commit: All tests passed."
  exit 0
else
  echo "pre-commit: Tests failed. Commit blocked."
  echo "  - Fix failing tests, or SKIP_TESTS=1 git commit to bypass."
  exit 1
fi
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
