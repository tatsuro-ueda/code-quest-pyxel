#!/usr/bin/env bash
# PostToolUse hook: G3 (SSoT編集後の自動codegen)
# stdin: JSON with tool_name, tool_input { file_path }
# assets/*.yaml が編集されたら tools/gen_data.py を自動実行する

set -euo pipefail

# デバッグ用バイパス
if [[ "${CLAUDE_GUARD_BYPASS:-}" == "1" ]]; then
  exit 0
fi

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# assets/*.yaml の編集でなければスキップ
if ! echo "$FILE_PATH" | grep -q '/assets/.*\.yaml$'; then
  exit 0
fi

# gen_data.py が存在しなければスキップ（タスク1の成果物が未配置の場合）
GEN_SCRIPT="tools/gen_data.py"
if [[ ! -f "$GEN_SCRIPT" ]]; then
  echo "G3: tools/gen_data.py が見つかりません。SSoT基盤(タスク1)を確認してください。"
  exit 0
fi

# 自動codegen実行
if python "$GEN_SCRIPT" 2>&1; then
  echo "G3: assets/*.yaml の変更を検出し、src/generated/*.py を再生成しました。"
  exit 0
else
  echo "G3: codegen に失敗しました。assets/*.yaml の内容を確認してください。"
  exit 1
fi
