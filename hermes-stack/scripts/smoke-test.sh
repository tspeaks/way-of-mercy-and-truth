#!/usr/bin/env bash
# Exercise the running proxy end to end: one request per tier, reporting which
# deployment actually served it. This is the "is the migration done?" check.
set -uo pipefail
set -a; [[ -f "$HOME/.litellm/.env" ]] && . "$HOME/.litellm/.env"; set +a

BASE="${LITELLM_BASE:-http://127.0.0.1:4000}"
KEY="${LITELLM_MASTER_KEY:?set LITELLM_MASTER_KEY}"

command -v jq >/dev/null || { echo "jq required"; exit 1; }

if ! curl -sS -m 5 "$BASE/health/readiness" >/dev/null 2>&1; then
  echo "proxy not answering at $BASE — start it with scripts/start-proxy.sh"
  exit 1
fi

ask() {  # ask <label> <prompt>
  local label="$1" prompt="$2" out model
  out=$(curl -sS -m 120 "$BASE/v1/chat/completions" \
    -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
    -d "$(jq -nc --arg p "$prompt" '{model:"smart-router",messages:[{role:"user",content:$p}],max_tokens:64}')")
  model=$(jq -r '.model // "?"' <<<"$out")
  if [[ "$(jq -r 'has("error")' <<<"$out")" == "true" ]]; then
    printf '  %-12s \033[31mFAIL\033[0m  %s\n' "$label" "$(jq -r '.error.message' <<<"$out" | head -c 100)"
    return 1
  fi
  printf '  %-12s \033[32mOK\033[0m    served by %s\n' "$label" "$model"
}

echo "Routing smoke test against $BASE:"
rc=0
ask SIMPLE    "rename the variable foo to bar in this line: let foo = 1;" || rc=1
ask COMPLEX   "fix this bug: TypeError: cannot read property 'id' of undefined in getUser()" || rc=1
ask REASONING "refactor: what is the better architecture here, a queue or direct calls?" || rc=1

echo
echo "Side-task route (Aion, off-topic budget):"
out=$(curl -sS -m 60 "$BASE/v1/chat/completions" \
  -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  -d '{"model":"offtopic","messages":[{"role":"user","content":"one-line title for a bug fix commit"}],"max_tokens":32}')
if [[ "$(jq -r 'has("error")' <<<"$out")" == "true" ]]; then
  printf '  %-12s \033[31mFAIL\033[0m  %s\n' "offtopic" "$(jq -r '.error.message' <<<"$out" | head -c 100)"; rc=1
else
  printf '  %-12s \033[32mOK\033[0m    served by %s\n' "offtopic" "$(jq -r '.model' <<<"$out")"
fi

echo
echo "Long-context fallthrough (should NOT land on groq-fast, cerebras-fast or local-coder):"
long=$(head -c 40000 /dev/urandom | base64 | tr -d '\n' | head -c 40000)
ask LONG "summarize: $long" || rc=1

exit $rc
