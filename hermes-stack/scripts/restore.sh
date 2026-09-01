#!/usr/bin/env bash
# Restore a backup.sh archive onto the new machine, then re-run bootstrap so the
# repo's config (which may have moved on) wins over the snapshot's copy.
#
#   scripts/restore.sh hermes-state-20260901-101500.tar.gz

set -euo pipefail
ARCHIVE="${1:?usage: restore.sh <archive.tar.gz>}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

[[ -f "$ARCHIVE" ]] || { echo "no such archive: $ARCHIVE"; exit 1; }

if [[ -d "$HOME/.hermes" ]]; then
  mv "$HOME/.hermes" "$HOME/.hermes.pre-restore.$(date +%s)"
  echo "moved existing ~/.hermes aside"
fi

tar xzf "$ARCHIVE" -C "$HOME"
chmod 600 "$HOME/.hermes/.env" "$HOME/.litellm/.env" 2>/dev/null || true
echo "restored state from $ARCHIVE"

echo "re-running bootstrap so repo config wins over the snapshot's copy"
"$REPO/scripts/bootstrap.sh"
