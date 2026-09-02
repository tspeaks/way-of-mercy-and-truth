#!/usr/bin/env bash
# Fail loudly if the local model is not entirely resident in VRAM.
#
# On this tower system RAM is not a safety net -- a model that spills into it is
# a problem to fix, not a slower configuration to live with. Run this after any
# driver update, model change, or unexplained slowdown.
#
#   scripts/local-guard.sh            # report and exit non-zero on any CPU split
#   scripts/local-guard.sh --quiet    # exit code only, for scripts

set -uo pipefail
QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1
say() { (( QUIET )) || printf '%s\n' "$*"; }

command -v ollama >/dev/null || { say "ollama not installed"; exit 1; }

PS_OUT="$(ollama ps 2>/dev/null)"
if [[ -z "$PS_OUT" ]] || [[ $(wc -l <<<"$PS_OUT") -le 1 ]]; then
  # Not loaded is a normal idle state (Ollama's own keep-alive timer unloads
  # it), not a residency violation -- there's nothing to check placement on.
  # Exit 0 so callers like preflight.sh don't conflate "nothing loaded" with
  # "loaded and split onto the CPU" (confirmed live 2026-09-02: it was
  # reporting FAIL on an idle box with no model resident at all).
  say "no model is loaded, nothing to check. Load one to test residency:  ollama run hermes-local 'ok'"
  exit 0
fi

say "$PS_OUT"

# `ollama ps` reports placement in a PROCESSOR column: "100% GPU" when it all
# fits, "43%/57% CPU/GPU" when it does not.
if grep -qi "cpu" <<<"$PS_OUT"; then
  say ""
  say "FAIL: part of the model is on the CPU."
  say "      On this 8 GB card that means the context or the quant is too big."
  say "      Fix, in order of preference:"
  say "        1. scripts/setup-local-model.sh --ctx 16384   (smaller context)"
  say "        2. confirm OLLAMA_FLASH_ATTENTION=1 and OLLAMA_KV_CACHE_TYPE=q8_0"
  say "           are set on the SERVER -- without flash attention the KV cache"
  say "           silently reverts to f16 and doubles in size"
  say "        3. close whatever else is holding VRAM (browser, compositor)"
  say "        4. scripts/local-tier.sh off                  (give up, route hosted)"
  exit 1
fi

if command -v nvidia-smi >/dev/null; then
  read -r used total <<<"$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | head -1 | tr ',' ' ')"
  say ""
  say "VRAM: ${used}/${total} MiB used"
  headroom=$(( total - used ))
  if (( headroom < 400 )); then
    say "WARN: only ${headroom} MiB free. A long prompt can still push this over;"
    say "      consider dropping to a 24576 context."
  fi
fi

say "OK: fully GPU-resident"
