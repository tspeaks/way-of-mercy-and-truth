# Known issues

Bugs observed in the running stack that live in Hermes Agent or LiteLLM
itself, not in this repo's config. Tracked here so they survive past the
Telegram scrollback, and so a fix upstream (or a workaround in config) has
something to check off against.

## What to do when you're back at the machine

**Resolved 2026-09-02** — see "SIMPLE tier (local-coder / Ollama)" below
for the actual root cause and the fix that's now live in
`litellm/config.yaml`. Nothing left to do here except:

1. Confirm `git pull` + redeploy brought in the SIMPLE-tier fix
   (`cp litellm/config.yaml ~/.litellm/config.yaml` + restart
   `litellm-proxy`, same as every deploy tonight).
2. Retest the file+whoami-style request through `smart-router` and confirm
   it now executes for real.
3. Consider your installed Hermes version (`hermes --version` / `/status`)
   against `v0.21.0` "Pantheon" while you're in there — see "Upstream
   release research" below — but that's general hygiene, not required for
   tonight's bug.

## Internal compaction prompt leaked into user-facing chat

**Observed:** 2026-09-01, via the Telegram gateway.

**Symptom:** Hermes' internal context-compaction instructions — the prompt
it sends to a model to summarize a conversation before trimming it —
appeared verbatim in the chat the user was reading, instead of being
consumed internally. The leaked text included the compaction prompt's own
scaffolding (`CRITICAL: Respond with TEXT ONLY`, an `<analysis>`/`<summary>`
structure, `Do NOT call any tools`). This is orchestration text meant for
whichever model Hermes calls internally for compaction — it was never
meant to reach the user.

**Why it's surprising:** `/status` at the time showed context usage at
13%. `hermes/config.yaml` sets `compression.threshold: 0.50` — compaction
should not fire until context crosses 50%. So this was not a normal
threshold-triggered compaction; something else invoked the compaction path
early and then failed to keep its output internal.

**Preceded by:** in the same session, Hermes had been describing tool
calls in plain text instead of actually executing them ("fake tool
calls"). That symptom on its own is consistent with a message landing on a
tier whose model doesn't support real tool-calling (see the "Known
capability gaps" table in [`WRITING-FOR-HERMES.md`](WRITING-FOR-HERMES.md)
— true of the SIMPLE tier and, before it was swapped out, the default
tier). Whether the fake-tool-call symptom and the leaked-compaction-prompt
symptom share a cause, or are two independent bugs that happened to
surface back to back, is not established.

**Working hypothesis, unconfirmed:** something in Hermes' tool-call
retry/error-handling path misfired into triggering the compaction/
summarization logic out of band, and the summarization call's own prompt
(or response scaffolding) got written to the outward-facing chat instead
of being trimmed and applied silently.

**What this repo's config can and can't do about it:** nothing directly —
`compression:` in `hermes/config.yaml` sets *when* and *how aggressively*
compaction runs (`threshold`, `target_ratio`, `protect_last_n`,
`protect_first_n`) and *which model* does the summarizing
(`auxiliary.compression.model: nvidia-kimi`), but the leak itself is
Hermes Agent's own handling of that model's output, not a config value.
This is a bug to report upstream at
[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
if it reproduces after a clean `/restart` + fresh `/new` session, with the
`/debug local` (or `/debug nous`) capture from around the incident
attached.

**Status:** retested 2026-09-01 after `/restart` + fresh `/new`. The leak
itself did **not** reproduce — the new session came up clean (`smart-router`
/ `http://127.0.0.1:4000/v1` / 131K context, no stray internal text). Whether
that means it's fixed or just didn't happen to trigger again is unknown; the
fake-tool-call symptom that preceded it, however, is confirmed still present
and is now its own entry below — treat this one as inconclusive rather than
closed until the tool-calling bug is actually resolved and retested cleanly.

## RETRACTED: `smart-router` does NOT drop `tools` — misdiagnosed 2026-09-01, corrected 2026-09-02

**This entry is wrong and is kept only so the mistake doesn't get made
twice.** The real bug is documented properly under "SIMPLE tier
(local-coder / Ollama)" below.

What actually happened: the isolation test compared two `curl` requests —
`"model": "smart-router"` (failed, JSON dumped in `content`) vs.
`"model": "mistral-tools"` (worked, real `tool_calls`) — and concluded the
router itself was stripping `tools` before forwarding to whatever
deployment it picked. **That conclusion never checked which deployment
`smart-router` actually picked.** It turned out to matter: the prompt used
for the repro ("write `reload worked` to `/tmp/mcp-test.txt` using the
`write_file` tool") scores `0.0` on the heuristic complexity scorer —
solidly SIMPLE tier, not MEDIUM as assumed all night — so the `smart-router`
request was silently landing on `local-coder` (Ollama), while the
"comparison" request went straight to `mistral-tools`. Two different
requests, two different bugs got attributed to one cause.

This was only caught by turning on `LITELLM_LOG=DEBUG` and reading the
actual `routing_decision` LiteLLM logs per request
(`'routed_model': 'local-coder', 'cause': 'heuristic_scorer', 'tier':
'SIMPLE', 'score': 0.0`) — the same debug log also proves `tools` rode
along correctly the entire way through LiteLLM's request-building
pipeline (present in `Params passed to completion()`, `Non-Default params`,
`Final returned optional params`, and the literal outbound request body).
LiteLLM's router has no bug here. Lesson for next time: **verify the
actual routing decision before trusting an isolation test that assumes it.**

A GitHub issue with this wrong diagnosis was drafted for
[BerriAI/litellm](https://github.com/BerriAI/litellm) but **was never
filed** — the session asked to file it independently refused to do so
without verifying against the litellm codebase first and was still
waiting on that when this was caught. No correction needed on their
repository; nothing to retract there.

## Upstream release research (2026-09-01)

Checked the last several Hermes Agent releases
([NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/releases))
for anything relevant to the two bugs above. Neither has an explicit
"fixed the drop_params/tools-stripping bug" or "fixed leaked compaction
prompt" line item, but several changes are directly relevant:

- **v0.20.0 "Herald" (2026.8.3)** introduced a real compression overhaul:
  an *absolute token threshold* (`compression.threshold_tokens`, separate
  from the percentage `threshold` this repo's `hermes/config.yaml` sets),
  a no-LLM `proactive_prune_tokens` pass, an N-message tail guarantee, and
  opt-in idle-triggered compaction (`compression.idle_compact_after_seconds`).
  **Correction, 2026-09-02:** pulled the actual config reference
  ([`website/docs/user-guide/configuration.md`](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/configuration.md)
  in the hermes-agent repo) — `idle_compact_after_seconds` defaults to `0`
  (disabled), and this repo's `hermes/config.yaml` never set it before
  tonight. So idle-triggered compaction was never on, and was **not** the
  cause of the 13%-context leak — that was the leading hypothesis in the
  previous version of this entry; it's ruled out now, not confirmed. The
  original "tool-call retry path misfired" guess further up is back to
  being the best remaining lead, still unconfirmed. `idle_compact_after_seconds`
  is now pinned explicitly to `0` in `hermes/config.yaml` so this doesn't
  have to be rediscovered.
  - Same release added "structured local logging for compression
    attempts" — if that's on, there may already be a local log of the
    exact incident to check instead of only having the Telegram
    transcript.
- **v0.21.0 "Pantheon" (2026.8.31)** added structured-output resilience
  (a retry path when a provider rejects structured output, with an
  auxiliary call translating response formats "for Anthropic wires") and
  a "deep redaction sweep" closing secret-leak gaps across terminal
  errors, `.env` reads, checkpoints, and ACP logs. Not a confirmed fix for
  either bug specifically, but both are the right shape of change — worth
  updating to regardless, since a redaction/leak-focused sweep happened
  between the version that likely produced tonight's incidents and now.

This is additional context for the compaction leak specifically, and a
reason to upgrade Hermes itself while at the machine — it isn't related to
the SIMPLE-tier/Ollama bug below, which turned out to be the actual cause
of tonight's tool-calling failures, not a LiteLLM proxy deploy problem.

## SIMPLE tier (local-coder / Ollama) has its own, separate upstream bug — CONFIRMED, this was tonight's actual bug

**Confirmed live 2026-09-02** via `LITELLM_LOG=DEBUG`, not just a
theoretical concern anymore — see the retraction above. Every "tool-calling
is broken" symptom seen tonight (Telegram file+whoami, the terminal-diff
narration, the `curl` isolation) traces back to this one thing: the
complexity router's heuristic scorer rates short, plainly-worded action
requests as SIMPLE tier, which was mapped to `local-coder` (Ollama), whose
chat-template parser can't return structured `tool_calls` for this model —
a bug in **Ollama's own chat-template parser**, not Hermes or LiteLLM:

- [`NVIDIA/NemoClaw#2731`](https://github.com/NVIDIA/NemoClaw/issues/2731)
  (closed, fixed by PR #2737 upstream in that project): a Hermes-family
  model served through Ollama emits correct tool-call tokens, but "Ollama's
  per-model template router fails to extract the tool-call into the
  structured field once prompt complexity crosses a threshold" — a minimal
  single-tool probe works, but a realistic multi-tool agent request (the
  actual shape Hermes sends) returns `tool_calls: null` with the JSON
  dumped into `content` as text instead. The same weights on **vLLM** with
  `--enable-auto-tool-choice --tool-call-parser hermes` parse correctly
  under the same load — confirming the bug is Ollama's parser, not the
  model. There is no Ollama-side config fix; the only confirmed workaround
  found is switching the local serving backend from Ollama to vLLM, which
  is a real infrastructure change (different VRAM/quantization story on an
  8 GB card — re-run `scripts/setup-local-model.sh`'s context step-down
  logic against whatever vLLM's footprint actually is before assuming it
  fits) — not something to attempt tonight from a phone.
- [`NousResearch/hermes-agent#26489`](https://github.com/NousResearch/hermes-agent/issues/26489)
  (**open**, no fix version, last confirmed against v0.13.0): a related but
  different symptom for the exact `provider: custom` + LiteLLM-fronting-Ollama
  shape this stack uses (matches the "Provider: custom" line the `/new`
  banner showed tonight) — Hermes probes Ollama-native endpoints
  (`/api/tags`, `/v1/props`), those 404 through a generic OpenAI-compatible
  proxy like LiteLLM (expected), and Hermes never falls back to a plain
  `POST /v1/chat/completions` call, hanging instead of erroring. Not what
  we saw tonight (we got a narrated response, not a hang) — but confirms
  this exact `provider: custom` + LiteLLM + Ollama combination has more
  than one open upstream rough edge. Worth knowing before spending more
  time assuming local-coder's problems are all this repo's config's fault.

**Fix applied 2026-09-02:** `litellm/config.yaml`'s `complexity_router_config.tiers.SIMPLE`
now points at `mistral-tools` instead of `local-coder` — a real, working,
tool-capable deployment, at the cost of a request instead of free
electricity. `hermes/config.yaml`'s emergency stopgap (forcing every
request through `mistral-tools` regardless of tier) has been reverted;
`smart-router` is back to being the default for both COMPLEX and
REASONING traffic, which were never actually broken. This is a real fix
for the symptom, not a full fix for the underlying cause — `local-coder`
itself is still broken for tool-calling and sits unused in the tier map
until it's moved off Ollama (the confirmed vLLM workaround above) or
Ollama fixes its parser upstream. Re-add it to `SIMPLE` only after
confirming real tool-calling works against it directly, the same way this
whole investigation confirmed `mistral-tools` does.
