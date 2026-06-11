#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <github-remote-url> [branch]"
  echo "Example: $0 https://github.com/suzannet-menon/OneTapGOV.git main"
  exit 2
fi
REMOTE_URL="$1"
BRANCH="${2:-$(git rev-parse --abbrev-ref HEAD)}"

echo "Adding remote 'origin' -> $REMOTE_URL (overwrite if exists)"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"

echo "Pushing branch $BRANCH to origin"
git push -u origin "$BRANCH"

echo "Push complete. If the remote is private you may need to use a token in the URL or configure authenticated git (ssh or credential helper)."
