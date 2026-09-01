#!/usr/bin/env bash
# Probe every provider with your real key, and check that the model ids in
# config.yaml actually exist on the provider right now.
#
# Free-tier model ids get deprecated with little notice (Groq retired qwen3-32b;
# Cerebras dropped qwen3-235b from the free tier). A config comment remembers
# what was true when it was written; this asks.
#
#   scripts/preflight.sh              # reachability + model id check
#   scripts/preflight.sh --quick      # reachability only

set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${LITELLM_CONFIG:-$HOME/.litellm/config.yaml}"
[[ -f "$CONFIG" ]] || CONFIG="$REPO/litellm/config.yaml"
set -a; [[ -f "$HOME/.litellm/.env" ]] && . "$HOME/.litellm/.env"; set +a

QUICK=0
[[ "${1:-}" == "--quick" ]] && QUICK=1

pass=0; fail=0; skip=0
declare -A MODELS_JSON=()

row()  { printf '  %-22s %s\n' "$1" "$2"; }
ok()   { row "$1" "$(printf '\033[32mOK\033[0m    %s' "${2:-}")"; pass=$((pass+1)); }
bad()  { row "$1" "$(printf '\033[31mFAIL\033[0m  %s' "${2:-}")"; fail=$((fail+1)); }
none() { row "$1" "$(printf '\033[90mSKIP\033[0m  %s' "${2:-no key set}")"; skip=$((skip+1)); }

# probe <label> <models-url> <auth-header>  -- stores the model list for later
probe() {
  local label="$1" url="$2" auth="$3" body code
  body=$(curl -sS -m 20 -w '\n%{http_code}' -H "$auth" "$url" 2>&1) || { bad "$label" "connection error"; return; }
  code=$(tail -n1 <<<"$body")
  case "$code" in
    200)
      MODELS_JSON[$label]="$(head -n-1 <<<"$body")"
      local n; n=$(grep -o '"id"' <<<"${MODELS_JSON[$label]}" | wc -l | tr -d ' ')
      ok "$label" "$n models visible" ;;
    401|403) bad "$label" "HTTP $code — key rejected" ;;
    404) bad "$label" "HTTP $code — wrong base URL or path" ;;
    405)
      if [[ "$label" == "cloudflare" ]]; then
        # Cloudflare's OpenAI-compatible endpoint does not implement GET
        # /models (confirmed: error 7001 "GET not supported for requested
        # URI"). This is not a key or config problem -- verified 2026-09-01
        # with a real POST /chat/completions, which returned 200. Not
        # re-tested here on every run to avoid spending real neuron budget.
        none "$label" "GET /models unsupported by this provider; verify with a real completion instead"
      else
        bad "$label" "HTTP $code"
      fi ;;
    429) bad "$label" "HTTP $code — rate limited or quota exhausted" ;;
    *)   bad "$label" "HTTP $code" ;;
  esac
}

bearer() { echo "Authorization: Bearer $1"; }

echo "Provider reachability:"

[[ -n "${LOCAL_API_BASE:-}" ]] \
  && probe "local (ollama)" "$LOCAL_API_BASE/models" "$(bearer "${LOCAL_API_KEY:-none}")" \
  || none "local (ollama)" "LOCAL_API_BASE not set"

[[ -n "${GROQ_API_KEY:-}" ]] \
  && probe "groq" "https://api.groq.com/openai/v1/models" "$(bearer "$GROQ_API_KEY")" || none "groq"

[[ -n "${MISTRAL_API_KEY:-}" ]] \
  && probe "mistral" "https://api.mistral.ai/v1/models" "$(bearer "$MISTRAL_API_KEY")" || none "mistral"

[[ -n "${SAMBANOVA_API_KEY:-}" ]] \
  && probe "sambanova" "https://api.sambanova.ai/v1/models" "$(bearer "$SAMBANOVA_API_KEY")" || none "sambanova"

[[ -n "${OPENROUTER_API_KEY:-}" ]] \
  && probe "openrouter" "https://openrouter.ai/api/v1/models" "$(bearer "$OPENROUTER_API_KEY")" || none "openrouter"

[[ -n "${AION_API_KEY:-}" ]] \
  && probe "aion labs" "https://api.aionlabs.ai/v1/models" "$(bearer "$AION_API_KEY")" || none "aion labs"

[[ -n "${CEREBRAS_API_KEY:-}" ]] \
  && probe "cerebras" "https://api.cerebras.ai/v1/models" "$(bearer "$CEREBRAS_API_KEY")" || none "cerebras"

[[ -n "${NVIDIA_API_KEY:-}" ]] \
  && probe "nvidia nim" "https://integrate.api.nvidia.com/v1/models" "$(bearer "$NVIDIA_API_KEY")" || none "nvidia nim"

[[ -n "${CLOUDFLARE_API_KEY:-}" ]] \
  && probe "cloudflare" "${CLOUDFLARE_API_BASE:?}/models" "$(bearer "$CLOUDFLARE_API_KEY")" || none "cloudflare"

[[ -n "${GEMINI_API_KEY:-}" ]] \
  && probe "gemini" "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" "X-Ignore: 1" \
  || none "gemini"

# ── Model ids: is what the config asks for actually served? ──────────────────
if (( ! QUICK )); then
  echo
  echo "Configured model ids:"
  # deployment name -> "provider-label|model id as the provider knows it"
  check_model() {
    local dep="$1" label="$2" want="$3"
    local json="${MODELS_JSON[$label]:-}"
    [[ -z "$json" ]] && { none "$dep" "$label not reachable"; return; }
    # Tag-tolerant: Ollama returns local models as "name:tag" (e.g.
    # "hermes-local:latest"), so an exact quoted match on the bare name
    # never matches. Accept an optional ":anything" before the closing quote.
    if grep -Eq "\"${want}(:[^\"]*)?\"" <<<"$json"; then
      ok "$dep" "$want"
    else
      bad "$dep" "$label does not list '$want' — edit config.yaml"
    fi
  }
  check_model "groq-fast"          "groq"           "openai/gpt-oss-20b"
  check_model "codestral"          "mistral"        "codestral-latest"
  check_model "sambanova-deepseek" "sambanova"      "DeepSeek-V3.1"
  check_model "nvidia-nemotron"    "nvidia nim"     "nvidia/llama-3.1-nemotron-70b-instruct"
  check_model "cerebras-fast"      "cerebras"       "gpt-oss-120b"
  check_model "offtopic"           "aion labs"      "aion-labs/aion-3.0-mini"
  check_model "local-coder"        "local (ollama)" "hermes-local"
  # openrouter-free is regenerated from the live list, so it is checked there
  if [[ -n "${MODELS_JSON[openrouter]:-}" ]] && [[ -f "$REPO/litellm/openrouter-free.yaml" ]]; then
    want=$(grep -o 'model: openrouter/[^ ]*' "$REPO/litellm/openrouter-free.yaml" | head -1 | sed 's|model: openrouter/||')
    [[ -n "$want" ]] && check_model "openrouter-free" "openrouter" "$want"
  fi
fi

echo
echo "Config sanity:"
[[ "${CLOUDFLARE_API_BASE:-}" == *"YOUR_ACCOUNT_ID"* ]] && bad "cloudflare base url" "still has the placeholder account id"
[[ "${LITELLM_MASTER_KEY:-}" == *"CHANGE-ME"* ]] && bad "master key" "still the template value"
if [[ -f "$HOME/.hermes/.env" && -f "$HOME/.litellm/.env" ]]; then
  h=$(grep -h '^LITELLM_MASTER_KEY=' "$HOME/.hermes/.env" | head -1)
  l=$(grep -h '^LITELLM_MASTER_KEY=' "$HOME/.litellm/.env" | head -1)
  [[ "$h" == "$l" ]] && ok "master key match" "hermes and litellm agree" \
                     || bad "master key match" "~/.hermes/.env differs from ~/.litellm/.env"
fi
if [[ -n "${LOCAL_API_BASE:-}" ]] && command -v ollama >/dev/null; then
  if "$REPO/scripts/local-guard.sh" --quiet; then ok "local VRAM residency" "no CPU spill"
  else bad "local VRAM residency" "model is partly on the CPU — run scripts/local-guard.sh"; fi
fi

echo
echo "$pass ok, $fail failed, $skip skipped"
[[ $fail -eq 0 ]]
