#!/usr/bin/env bash
# Snapshot everything that is NOT in this repo but that you would miss on the
# new machine: sessions, memories, skills, goals, cron, auth, and both .env files.
#
#   scripts/backup.sh [outdir]      -> hermes-state-YYYYmmdd-HHMMSS.tar.gz
#
# The archive contains live API keys. It is written 0600. Move it over scp or a
# USB stick; do not put it in the repo, in cloud sync, or in a chat window.

set -euo pipefail
OUT="${1:-$PWD}"
STAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE="$OUT/hermes-state-$STAMP.tar.gz"

[[ -d "$HOME/.hermes" ]] || { echo "no ~/.hermes to back up"; exit 1; }

# Sessions and logs are the bulky, least portable part. Keep sessions (they are
# your history) but drop logs.
tar czf "$ARCHIVE" \
  --exclude='.hermes/logs' \
  --exclude='.hermes/**/__pycache__' \
  --exclude='.litellm/venv' \
  -C "$HOME" \
  .hermes \
  $([[ -f "$HOME/.litellm/.env" ]] && echo .litellm/.env) \
  $([[ -f "$HOME/.litellm/config.yaml" ]] && echo .litellm/config.yaml)

chmod 600 "$ARCHIVE"
echo "wrote $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1))"
echo
echo "Contains live credentials. Transfer it over a channel you trust, and"
echo "delete it from the old machine once the new one is verified."
