# Known issues

Bugs observed in the running stack that live in Hermes Agent or LiteLLM
itself, not in this repo's config. Tracked here so they survive past the
Telegram scrollback, and so a fix upstream (or a workaround in config) has
something to check off against.

## What to do when you're back at the machine

In priority order, based on everything confirmed today plus the upstream
release research below:

1. **Check your installed Hermes version** (`hermes --version` or the
   version shown in `/status`). If you're behind `v0.21.0` (2026.8.31,
   "Pantheon"), upgrade — see "Upstream release research" below for why
   this specific jump matters, not just general hygiene.
2. **Redeploy and actually restart the LiteLLM proxy** — this is still the
   most likely fix for tonight's MEDIUM-tier failure specifically. Run the
   checklist under "Tool-calling still broken proxy-wide" below.
3. **Retest file+whoami, then the read-only probe**, in that order, before
   trusting any task from today's list.
4. **If local-coder (SIMPLE tier) is still narrating instead of executing
   after steps 1–3**, that's likely a separate, deeper bug — see "SIMPLE
   tier has its own upstream bug" below. Don't burn more time on the
   LiteLLM config for that one; it's an Ollama-side chat-template problem
   with no simple config fix.

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

## Tool-calling still broken proxy-wide, survives `/restart` + `/new`

**Observed:** 2026-09-01, via the Telegram gateway, after a clean
`/restart` (gateway) and a fresh `/new` session.

**Symptom:** asked to write a file and run `whoami` — a plain request with
none of the `keyword_tier_rules` trigger words, so it falls through to the
**default MEDIUM tier (`mistral-tools`)**, not SIMPLE. Response came back
as narrated JSON (`{"name": "write_file", "arguments": {...}}`) printed as
chat text instead of an executed tool call. Repro'd again separately with
a `terminal` call (`diff -r ~/consulting-site`) — same pattern, JSON
printed instead of run.

**Why this matters more than it first looked:** this repo's own history
(commit `574cf4f`) already diagnosed and fixed this exact symptom by
removing a global `drop_params` from `litellm/config.yaml` that was
silently stripping `tools` from every request before it reached any
provider — see the comment in `litellm_settings:` in that file. The
MEDIUM tier (`mistral-tools`) is specifically documented as the
tool-capable default (commit `ee56e22`), so a MEDIUM-tier request failing
this way means the fix either isn't deployed to the box running the proxy,
or the proxy process hasn't been restarted since it was deployed — LiteLLM
only reads `~/.litellm/config.yaml` at startup, and `/restart` in Telegram
restarts the **Hermes gateway**, not the separate `litellm-proxy` service.

**Not yet confirmed:** whether this also means *read*-only tool calls
(file reads, not just writes/execution) are being stripped. If the whole
`tools` array is dropped wholesale rather than specific tool names, the 7
pure-analysis/REASONING-tier tasks from today's task list would also come
back ungrounded (plausible-sounding, not actually based on the real code)
even though their deliverable is text-only. Worth testing with a read-only
probe (e.g. "read `consulting-site/package.json` and list its
dependencies verbatim") before trusting any of them.

**Remediation checklist, for when back at the machine:**
```bash
cd ~/way-of-mercy-and-truth/hermes-stack   # wherever this repo is checked out there
git pull                                    # bring in 574cf4f + this doc's updates
scripts/validate-config.py                  # confirm litellm/config.yaml loads clean
cp litellm/config.yaml ~/.litellm/config.yaml
systemctl --user restart litellm-proxy      # NOT just Hermes's /restart
scripts/smoke-test.sh                       # confirms real tool-calling end to end
```
Then retry the file+whoami test in Telegram, and only after that passes,
retest the read-only probe above before trusting any REASONING-tier task.

**Status:** confirmed live 2026-09-01, unresolved. Update once the box has
actually had the proxy config redeployed and the service restarted, and
the retest is done.

## Upstream release research (2026-09-01)

Checked the last several Hermes Agent releases
([NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/releases))
for anything relevant to the two bugs above. Neither has an explicit
"fixed the drop_params/tools-stripping bug" or "fixed leaked compaction
prompt" line item, but several changes are directly relevant:

- **v0.20.0 "Herald" (2026.8.3)** introduced a real compression overhaul:
  per-model threshold overrides, an *absolute token threshold*
  (`compression.threshold_tokens`, separate from the percentage
  `threshold` this repo's `hermes/config.yaml` sets), an N-message tail
  guarantee, and — most relevant to the leak — **opt-in idle-triggered
  compaction**. That's a second, independent trigger for the compaction
  path beyond the 50% threshold this repo configures. If idle-triggered
  compaction got turned on (by default post-upgrade, or already set
  somewhere not tracked in this repo), that alone would explain compaction
  firing at 13% context with no threshold breach — **this is now the
  leading hypothesis for the leaked-compaction-prompt bug**, ahead of the
  original "tool-call retry path misfired" guess above. Check
  `compression.idle_triggered` (or similarly named key — confirm the exact
  name against your installed version's schema) in `~/.hermes/config.yaml`
  once home.
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

None of this replaces actually redeploying the LiteLLM proxy config
(that's still the confirmed cause of tonight's MEDIUM-tier failure) — it's
additional context for the compaction leak specifically, and a reason to
upgrade Hermes itself while at the machine, not just the proxy.

## SIMPLE tier (local-coder / Ollama) has its own, separate upstream bug

Distinct from the proxy-wide issue above. Even after the LiteLLM proxy fix
lands, local-coder specifically may keep narrating tool calls instead of
executing them, because of a bug in **Ollama's own chat-template parser**,
not Hermes or LiteLLM:

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

Bottom line for local-coder: don't chase this one via `litellm/config.yaml`
edits. If it's still broken after the proxy redeploy, it's an Ollama/vLLM
decision, not a routing-config bug.
