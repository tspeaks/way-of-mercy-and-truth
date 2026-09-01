#!/usr/bin/env bash
# Route the SIMPLE tier to the local model, or back to a hosted provider.
#
#   scripts/local-tier.sh on       # SIMPLE -> local-coder
#   scripts/local-tier.sh off      # SIMPLE -> groq-fast
#   scripts/local-tier.sh status
#
# Edits the marked line in both the repo config and the deployed one, so the
# choice survives the next bootstrap.

set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKER='# LOCAL-TIER-LINE'
TARGETS=("$REPO/litellm/config.yaml")
[[ -f "$HOME/.litellm/config.yaml" ]] && TARGETS+=("$HOME/.litellm/config.yaml")

set_to() {
  local model="$1" comment="$2"
  for f in "${TARGETS[@]}"; do
    grep -q "$MARKER" "$f" || { echo "no $MARKER in $f -- edit the SIMPLE tier by hand"; exit 1; }
    # BSD and GNU sed disagree about -i; write through a temp file instead.
    local tmp; tmp="$(mktemp)"
    sed "s|^\( *SIMPLE: *\).*$MARKER.*|\1$model    $MARKER $comment|" "$f" > "$tmp"
    mv "$tmp" "$f"
  done
}

case "${1:-status}" in
  on)
    "$REPO/scripts/local-guard.sh" --quiet || {
      echo "refusing to enable: the local model is not fully in VRAM."
      echo "run scripts/local-guard.sh to see why."
      exit 1
    }
    set_to "local-coder" "free and unmetered; costs electricity"
    echo "SIMPLE -> local-coder. Restart the proxy to apply."
    ;;
  off)
    set_to "groq-fast" "local tier disabled"
    echo "SIMPLE -> groq-fast. Restart the proxy to apply."
    ;;
  status)
    grep -h "$MARKER" "${TARGETS[@]}" | sed 's/^ */  /'
    ;;
  *) echo "usage: local-tier.sh on|off|status"; exit 1 ;;
esac
