#!/usr/bin/env bash
# Install and pin the local SIMPLE-tier model for an 8 GB card (RTX 2070).
#
# Hard requirement on this machine: everything stays in VRAM. System RAM is not
# a spillover pool here -- a partial CPU offload is treated as a failure, not as
# a slower success. If the target context will not fit, this steps down until it
# does, and if even the floor will not fit it turns the local tier off rather
# than leaving you with a model that quietly runs on the CPU.
#
#   scripts/setup-local-model.sh              # 32K context, q8_0 KV cache
#   scripts/setup-local-model.sh --ctx 16384  # start lower
#
# Budget at 32K (measured sizes, q4_K_M weights + q8_0 KV):
#   weights ~4.7 GB + KV ~0.9 GB + compute ~0.6 GB = ~6.2 GB of 8 GB

set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BASE_MODEL="${BASE_MODEL:-qwen2.5-coder:7b-instruct-q4_K_M}"
LOCAL_NAME="${LOCAL_NAME:-hermes-local}"
CTX="${CTX:-32768}"
[[ "${1:-}" == "--ctx" ]] && CTX="${2:?}"

# Step-down ladder. q8_0 KV halves cache size; if flash attention is
# unavailable Ollama silently reverts to f16 KV, which doubles it -- that is the
# main reason a 32K attempt can fail on Turing.
LADDER=(32768 24576 16384 8192)

say()  { printf '\033[1m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33mWARN\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31mFAIL\033[0m %s\n' "$*" >&2; exit 1; }

command -v nvidia-smi >/dev/null || die "nvidia-smi not found -- no usable GPU, keep the local tier off"
command -v ollama >/dev/null || die "ollama not installed: curl -fsSL https://ollama.com/install.sh | sh"

TOTAL_MIB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
USED_MIB=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
say "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1), ${USED_MIB}/${TOTAL_MIB} MiB in use"
(( TOTAL_MIB >= 7000 )) || die "under 8 GB of VRAM; this profile does not apply"
(( USED_MIB < 1500 )) || warn "${USED_MIB} MiB already in use (desktop/browser). That eats the headroom this profile needs."

# ── Server-side settings. These are read by the ollama SERVER, not the CLI, so
# they have to be set where the daemon starts, not in this shell.
say "configuring the ollama server for flash attention + q8_0 KV cache"
if systemctl list-unit-files 2>/dev/null | grep -q '^ollama.service'; then
  sudo mkdir -p /etc/systemd/system/ollama.service.d
  sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null <<EOF
[Service]
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
# One model resident, no second copy competing for the same 8 GB.
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
# Keep it warm: reloading a 4.7 GB model on every turn is its own tax.
Environment="OLLAMA_KEEP_ALIVE=30m"
EOF
  sudo systemctl daemon-reload
  sudo systemctl restart ollama
  sleep 3
else
  warn "ollama is not a systemd service here. Start the server with these set:"
  warn '  OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 OLLAMA_MAX_LOADED_MODELS=1 \'
  warn '  OLLAMA_NUM_PARALLEL=1 OLLAMA_KEEP_ALIVE=30m ollama serve'
fi

say "pulling $BASE_MODEL"
ollama pull "$BASE_MODEL"

try_ctx() {   # try_ctx <n> -> 0 if it loads fully on GPU
  local ctx="$1"
  say "building $LOCAL_NAME at ${ctx} context"
  local mf; mf="$(mktemp)"
  cat > "$mf" <<EOF
FROM $BASE_MODEL
# num_gpu 99 = put every layer on the GPU. If they do not all fit, we want a
# hard failure we can see, not a silent CPU split that runs at 2 tok/s.
PARAMETER num_gpu 99
PARAMETER num_ctx $ctx
PARAMETER temperature 0.1
EOF
  ollama create "$LOCAL_NAME" -f "$mf" >/dev/null
  rm -f "$mf"

  # Force a real load, then inspect placement.
  ollama run "$LOCAL_NAME" "ok" >/dev/null 2>&1 || { warn "generation failed at ${ctx}"; return 1; }
  "$REPO/scripts/local-guard.sh" --quiet
}

CHOSEN=0
for ctx in "${LADDER[@]}"; do
  (( ctx > CTX )) && continue
  if try_ctx "$ctx"; then CHOSEN="$ctx"; break; fi
  warn "${ctx} context did not stay in VRAM; stepping down"
  ollama stop "$LOCAL_NAME" 2>/dev/null || true
done

if (( CHOSEN == 0 )); then
  warn "no context size stayed fully in VRAM on this card."
  warn "turning the local tier off; SIMPLE goes back to a hosted provider."
  "$REPO/scripts/local-tier.sh" off
  die "local tier disabled. See docs/LOCAL-MODELS.md for the fallback plan."
fi

say "settled on ${CHOSEN} context, fully GPU-resident"

# LiteLLM must agree with what was actually served, minus room for the reply.
MAX_IN=$(( CHOSEN - 4096 ))
say "set max_input_tokens for local-coder to ${MAX_IN} in litellm/config.yaml if it differs"
say "and point the model id at '${LOCAL_NAME}':"
say "    model: openai/${LOCAL_NAME}"

cat <<EOF

Local tier ready. Next:
  scripts/local-tier.sh on        # route SIMPLE to local-coder
  scripts/local-guard.sh          # re-check placement any time
  scripts/smoke-test.sh           # confirm through the proxy
EOF
