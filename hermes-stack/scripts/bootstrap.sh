#!/usr/bin/env bash
# Stand up the whole stack on a fresh machine. Idempotent -- safe to re-run.
#
#   scripts/bootstrap.sh            install + deploy config
#   scripts/bootstrap.sh --no-deploy   install only, leave ~/.litellm and ~/.hermes alone
#
# Works on Linux and macOS. Installs LiteLLM into its own venv so it never
# collides with system Python or with Hermes' own dependencies.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${LITELLM_VENV:-$HOME/.litellm/venv}"
LITELLM_HOME="$HOME/.litellm"
HERMES_HOME="$HOME/.hermes"
DEPLOY=1
[[ "${1:-}" == "--no-deploy" ]] && DEPLOY=0

say() { printf '\033[1m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33mWARN\033[0m %s\n' "$*" >&2; }

backup() {   # backup <file> -- keep a timestamped copy before overwriting
  [[ -f "$1" ]] || return 0
  cp -p "$1" "$1.bak.$(date +%Y%m%d%H%M%S)"
  say "backed up existing $(basename "$1")"
}

# ── Python + LiteLLM ─────────────────────────────────────────────────────────
command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }
PYV=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
case "$PYV" in
  3.9|3.10|3.11|3.12|3.13) ;;
  *) warn "python $PYV is untested with litellm[proxy]; 3.11-3.13 is the safe range" ;;
esac

say "installing litellm[proxy] into $VENV"
mkdir -p "$LITELLM_HOME"
[[ -d "$VENV" ]] || python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet --upgrade 'litellm[proxy]' pyyaml
say "litellm $("$VENV/bin/pip" show litellm | awk '/^Version/{print $2}') installed"

# ── Config deployment ────────────────────────────────────────────────────────
if [[ $DEPLOY -eq 1 ]]; then
  say "deploying litellm config -> $LITELLM_HOME/config.yaml"
  backup "$LITELLM_HOME/config.yaml"
  cp "$REPO/litellm/config.yaml" "$LITELLM_HOME/config.yaml"

  if [[ ! -f "$LITELLM_HOME/.env" ]]; then
    cp "$REPO/litellm/.env.example" "$LITELLM_HOME/.env"
    chmod 600 "$LITELLM_HOME/.env"
    warn "created $LITELLM_HOME/.env from the template -- fill in your keys before starting"
  else
    chmod 600 "$LITELLM_HOME/.env"
    say "kept existing $LITELLM_HOME/.env"
  fi

  if command -v hermes >/dev/null; then
    mkdir -p "$HERMES_HOME"
    say "deploying hermes config -> $HERMES_HOME/config.yaml"
    backup "$HERMES_HOME/config.yaml"
    cp "$REPO/hermes/config.yaml" "$HERMES_HOME/config.yaml"
    if [[ ! -f "$HERMES_HOME/.env" ]]; then
      cp "$REPO/hermes/.env.example" "$HERMES_HOME/.env"
      chmod 600 "$HERMES_HOME/.env"
      warn "created $HERMES_HOME/.env -- set LITELLM_MASTER_KEY to match ~/.litellm/.env"
    fi
  else
    warn "hermes not on PATH; skipping ~/.hermes deployment."
    warn "install it first:  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"
  fi
fi

# ── Validate ─────────────────────────────────────────────────────────────────
say "validating config"
"$VENV/bin/python" "$REPO/scripts/validate-config.py" "$LITELLM_HOME/config.yaml" 2>/dev/null \
  || "$VENV/bin/python" "$REPO/scripts/validate-config.py" "$REPO/litellm/config.yaml"

cat <<EOF

Next:
  1. Fill in keys:        \$EDITOR ~/.litellm/.env
  2. Check they work:     scripts/preflight.sh
  3. Start the proxy:     scripts/start-proxy.sh   (or install the service unit)
  4. Smoke test:          scripts/smoke-test.sh
  5. Point Hermes at it:  hermes config get model
EOF
