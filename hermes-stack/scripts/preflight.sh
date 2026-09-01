#!/usr/bin/env bash
# Probe every provider directly with your real key and report which are live.
#
# Endpoints, model ids and free-tier limits on this stack change without notice.
# Rather than trusting a config comment written months ago, ask each provider.
# Run this after bootstrap, after any provider change, and first thing on the
# new machine after migration.
#
#   scripts/preflight.sh

set -uo pipefail
set -a; [[ -f "$HOME/.litellm/.env" ]] && . "$HOME/.litellm/.env"; set +a

pass=0; fail=0; skip=0

row() { printf '  %-22s %s\n' "$1" "$2"; }
ok()   { row "$1" "$(printf '\033[32mOK\033[0m    %s' "${2:-}")"; pass=$((pass+1)); }
bad()  { row "$1" "$(printf '\033[31mFAIL\033[0m  %s' "${2:-}")"; fail=$((fail+1)); }
none() { row "$1" "$(printf '\033[90mSKIP\033[0m  %s' "${2:-no key set}")"; skip=$((skip+1)); }

# probe <label> <url> <auth-header>
probe() {
  local label="$1" url="$2" auth="$3"
  local body code
  body=$(curl -sS -m 20 -w '\n%{http_code}' -H "$auth" "$url" 2>&1) || { bad "$label" "connection error"; return; }
  code=$(tail -n1 <<<"$body")
  case "$code" in
    200) ok "$label" "$(head -n-1 <<<"$body" | tr -d '\n' | head -c 60)…" ;;
    401|403) bad "$label" "HTTP $code — key rejected" ;;
    404) bad "$label" "HTTP $code — wrong base URL or path" ;;
    429) bad "$label" "HTTP $code — rate limited or quota exhausted" ;;
    *)   bad "$label" "HTTP $code" ;;
  esac
}

echo "Provider reachability:"

[[ -n "${DASHSCOPE_API_KEY:-}" ]] \
  && probe "qwen/dashscope" "${DASHSCOPE_API_BASE:?}/models" "Authorization: Bearer $DASHSCOPE_API_KEY" \
  || none "qwen/dashscope"

[[ -n "${CEREBRAS_API_KEY:-}" ]] \
  && probe "cerebras" "https://api.cerebras.ai/v1/models" "Authorization: Bearer $CEREBRAS_API_KEY" \
  || none "cerebras"

[[ -n "${NVIDIA_API_KEY:-}" ]] \
  && probe "nvidia nim" "https://integrate.api.nvidia.com/v1/models" "Authorization: Bearer $NVIDIA_API_KEY" \
  || none "nvidia nim"

[[ -n "${CLOUDFLARE_API_KEY:-}" ]] \
  && probe "cloudflare" "${CLOUDFLARE_API_BASE:?}/models" "Authorization: Bearer $CLOUDFLARE_API_KEY" \
  || none "cloudflare"

[[ -n "${GEMINI_API_KEY:-}" ]] \
  && probe "gemini" "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" "X-Ignore: 1" \
  || none "gemini"

[[ -n "${LOCAL_API_BASE:-}" ]] \
  && probe "local inference" "$LOCAL_API_BASE/models" "Authorization: Bearer ${LOCAL_API_KEY:-none}" \
  || none "local inference" "not configured yet (pre-migration)"

echo
echo "Config sanity:"
if [[ "${CLOUDFLARE_API_BASE:-}" == *"YOUR_ACCOUNT_ID"* ]]; then
  bad "cloudflare base url" "still has the placeholder account id"
fi
if [[ "${LITELLM_MASTER_KEY:-}" == *"CHANGE-ME"* ]]; then
  bad "master key" "still the template value"
fi
if [[ -f "$HOME/.hermes/.env" ]] && [[ -f "$HOME/.litellm/.env" ]]; then
  h=$(grep -h '^LITELLM_MASTER_KEY=' "$HOME/.hermes/.env" | head -1)
  l=$(grep -h '^LITELLM_MASTER_KEY=' "$HOME/.litellm/.env" | head -1)
  [[ "$h" == "$l" ]] && ok "master key match" "hermes and litellm agree" \
                     || bad "master key match" "~/.hermes/.env differs from ~/.litellm/.env"
fi

echo
echo "$pass ok, $fail failed, $skip skipped"
[[ $fail -eq 0 ]]
