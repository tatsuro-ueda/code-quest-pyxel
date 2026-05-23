#!/usr/bin/env bash

set -euo pipefail

if [[ "$#" -eq 0 ]]; then
  echo "usage: scripts/commit-tasknote.sh -m 'tasknote: ...' [git-commit-args...]" >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "${REPO_ROOT}" ]]; then
  echo "commit-tasknote: not inside a git repository" >&2
  exit 1
fi
cd "$REPO_ROOT"

TASKNOTE_PRECOMMIT=1 git commit "$@"
