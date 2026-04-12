#!/usr/bin/env bash
# PreToolUse hook: G1 (generated編集禁止), G2 (pyxres編集禁止), G14 (直接import禁止)
# stdin: JSON with tool_name, tool_input { file_path, new_string/content }
# exit 0 = allow, exit 2 = block

set -euo pipefail

# デバッグ用バイパス
if [[ "${CLAUDE_GUARD_BYPASS:-}" == "1" ]]; then
  exit 0
fi

INPUT=$(cat)

# file_path を抽出（Edit/Write 共通）
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# G1: src/generated/ の直接編集をブロック
if echo "$FILE_PATH" | grep -q '/src/generated/'; then
  echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"G1: このファイルは自動生成物です。assets/*.yaml を編集して make gen を実行してください。"}}'
  exit 2
fi

# G2: .pyxres の直接編集をブロック
if echo "$FILE_PATH" | grep -q '\.pyxres$'; then
  echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"G2: .pyxres は Code Maker 経由でのみ編集可能です。直接編集はできません。"}}'
  exit 2
fi

# G14: src.generated の直接importをブロック
# Edit の new_string、Write の content をチェック
CONTENT=$(echo "$INPUT" | grep -o '"new_string"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"new_string"[[:space:]]*:[[:space:]]*"//;s/"$//')
if [[ -z "$CONTENT" ]]; then
  CONTENT=$(echo "$INPUT" | grep -o '"content"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"content"[[:space:]]*:[[:space:]]*"//;s/"$//')
fi

if echo "$CONTENT" | grep -qE '(from src\.generated|import src\.generated)'; then
  echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"G14: 生成物の直接importは禁止です。src/game_data.py のローダ経由でアクセスしてください。"}}'
  exit 2
fi

exit 0
