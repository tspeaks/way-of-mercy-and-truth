#!/usr/bin/env bash
# Start the proxy in the foreground with the deployed config.
set -euo pipefail
VENV="${LITELLM_VENV:-$HOME/.litellm/venv}"
CONFIG="${LITELLM_CONFIG:-$HOME/.litellm/config.yaml}"
PORT="${LITELLM_PORT:-4000}"

set -a; [[ -f "$HOME/.litellm/.env" ]] && . "$HOME/.litellm/.env"; set +a

exec "$VENV/bin/litellm" --config "$CONFIG" --port "$PORT" "$@"
