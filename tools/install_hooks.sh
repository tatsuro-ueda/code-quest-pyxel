#!/usr/bin/env bash
# .git/hooks/post-commit を冪等に作成する。
#
# 使い方:
#   bash tools/install_hooks.sh
#
# 実行後、git commit のたびに tools/update_top_changes.py が走り、
# Claude Haiku が「子どもに関係する変更」を判定して top_changes.json に
# 追記する。ANTHROPIC_API_KEY 未設定時は silent skip。

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/.git/hooks/post-commit"

mkdir -p "$ROOT/.git/hooks"

cat > "$HOOK" <<'POST_COMMIT'
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

chmod +x "$HOOK"
echo "[install-hooks] installed: $HOOK"
echo "[install-hooks] tip: ANTHROPIC_API_KEY を環境に設定すると AI 判定が有効化されます。"
