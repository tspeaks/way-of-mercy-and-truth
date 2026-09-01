# Assessment of the Hermes free-tier routing plan

Verified against `litellm` 1.99.0 (source read, not docs), the Hermes Agent
configuration reference, and current provider limits, on 2026-09-01.

**Verdict: the architecture is right, the config as written will not run.** Six
concrete defects, one wrong premise, and no portability story. All six defects
are fixed in `litellm/config.yaml` and `hermes/config.yaml`; the portability gap
is what the rest of this bundle exists for.

---

## What the plan gets right

LiteLLM Proxy in front of Hermes is the correct shape. One local endpoint, one
model name (`smart-router`), all provider churn absorbed below the agent — that
is exactly the seam you want when the machine underneath is about to change.

The Auto Router v2 complexity router is real and the plan's config shape is
close to correct: `tiers`, `keyword_tier_rules`, `session_affinity`,
`session_affinity_ttl_seconds`, `adaptive`, `tier_boundaries`, and
`complexity_router_default_model` are all genuine keys
(`litellm/router_strategy/complexity_router/config.py`). Session affinity and
`adaptive: false` are the right calls for quota-limited providers: predictable
placement, no exploration spending someone else's daily allowance.

Conservative `rpm`/`tpm` below published limits is right, and it is right for
the boring reason — staying inside a provider's published limits is the deal
you agreed to — not because of how the traffic looks.

## Six defects that break it

**1. The Cloudflare URL is sent literally.**
```yaml
api_base: "https://api.cloudflare.com/client/v4/accounts/os.environ/CLOUDFLARE_ACCOUNT_ID/ai/v1"
```
LiteLLM expands `os.environ/NAME` only when it is the *entire* value. Mid-string
it is not interpolated, so this requests a literal `/accounts/os.environ/` path
and 404s every time. Fixed by putting the whole URL in `CLOUDFLARE_API_BASE`.
`scripts/validate-config.py` now fails the build on this pattern anywhere.

**2. `model_info.max_tokens` is output tokens, not context — so the Cerebras 8K
guard does nothing.** The plan's risk table claims `max_tokens: 8192` means
"LiteLLM won't route long-context requests to it." It does not. Context-window
filtering reads `max_input_tokens`, and only when `enable_pre_call_checks: true`
is set on the router (default: `False`). As written, a 40K-token prompt is
handed to Cerebras and fails at the provider mid-session. Fixed with
`max_input_tokens` on every deployment, `enable_pre_call_checks: true`, and a
`context_window_fallbacks` chain that reroutes an oversized prompt instead of
failing it.

**3. A tier with a list of models picks at random, not in order.**
`SIMPLE: ["pollinations-gpt5", "qwen3-flash"]` reads like a preference order. It
is not: `complexity_router.py:1516` is `random.choice(model)`. So the plan's
tier lists produce exactly the provider-bouncing the plan says it wants to
avoid. Fixed: one model per tier, ordered failover in `router_settings.fallbacks`.

**4. The fallback block is in the wrong place, so "Gemini stays last resort" is
not enforced.** `fallbacks` is a Router-level setting, not a per-deployment one.
Nested under an entry in `model_list` it does not become the router's fallback
chain. Fixed: `fallbacks` and `context_window_fallbacks` under `router_settings`,
with Gemini last in every chain.

**5. The Cerebras deployment names a model that is probably not on the free
tier, at a TPM above the account cap.** Free tier is currently ~5 RPM / 30K TPM /
1M tokens per day, on `gpt-oss-120b` and GLM-4.7 — `qwen3-235b` is no longer
listed. The plan sets `tpm: 50000`, above the 30K account cap, which means
LiteLLM's own limiter will let through traffic the provider rejects. Fixed to
`cerebras/gpt-oss-120b` at `tpm: 25000`. Confirm against your dashboard —
`scripts/preflight.sh` will tell you what the key can actually see.

**6. Several Hermes keys do not exist.** `auxiliary.title_gen` is
`auxiliary.title_generation`. `provider: custom` with an inline `base_url` is not
how custom endpoints are declared — they go in the `providers:` dictionary
(`api:`, `api_key:`, `transport:`, `default_model:`, per-model `context_length`)
and are referenced by name. `delegation.max_concurrent_children` does not appear
in the configuration reference; I left it out rather than ship a key that
silently does nothing. Also `general_settings.no_auth` is not a LiteLLM setting.

## One wrong premise

> "Each provider sees a normal first-party API call... no third-party harness in
> the provider's eyes."

That is true of Qwen, Cerebras, NVIDIA, Cloudflare and Gemini. It is not true of
Pollinations, which sits in tier 1 as the workhorse: it is a third-party relay
serving other vendors' frontier models. Routing your default traffic through it
is the same category of thing the plan rejects OmniRoute for — the difference is
the fingerprinting, not the intermediary. You cannot simultaneously claim
"direct API calls only" and put a relay in position 1.

So it is commented out in `litellm/config.yaml` and Qwen holds the primary slot
(unlimited-ish, 131K context, genuinely first-party, strong at code). If you
decide you want Pollinations anyway, uncomment it — but do it as a decision,
not as an accident of copying the config.

The related framing — self-imposed caps "to avoid looking like a bot", cooldowns
that "look like normal backoff" — is worth restating in the form that survives
contact with a provider's support team: you are staying inside published limits
because that is the agreement. Same numbers, and it stays true when someone asks.

## An empirical finding the plan could not have known

`keyword_tier_rules` are applied on the request path, ahead of the scorer — not
inside the classifier. That matters because the heuristic scorer, on its default
boundaries, sends most real coding prompts to SIMPLE or MEDIUM. Measured with
`scripts/explain-routing.py` against this exact config:

```
PROMPT                                              TIER        SCORE  WHY          MODEL
rename the variable foo to bar                      SIMPLE     -0.100  kw:rename    qwen3-flash
fix the TypeError in the login handler, stack ...   COMPLEX     0.000  kw:fix       qwen3-coder
write a function that parses ISO 8601 timestamps    SIMPLE      0.050  score        qwen3-flash
refactor the auth module to use dependency inj...   REASONING   0.150  kw:refactor  nvidia-llama4
design a schema for multi-tenant billing with ...   MEDIUM      0.150  score        qwen3-coder
```

Note the last row: a genuine architecture question scores 0.150 and lands in
MEDIUM because no keyword caught it. Your keyword rules are not a nice-to-have
on top of the classifier — on the default `tier_boundaries` they are doing most
of the routing. Budget time for extending them, and use `explain-routing.py`
rather than waiting a week for traces to tell you the same thing.

## On the plugin stack

Nine plugins is more than you can evaluate at once, and several of them cost
tokens to save tokens. Sequence it:

1. **Free first.** `tool_output.max_bytes` / `max_lines` and Hermes' built-in
   `compression` are already in `hermes/config.yaml`. Truncating tool output at
   the source beats compressing it with a model call.
2. **Then measure.** Langfuse, self-hosted. Until you can see which tier serves
   what, every other tuning decision is a guess — including whether you have a
   token problem at all.
3. **Then compress** (RTK, Headroom) against a measured baseline, so you can
   tell whether the compression call costs more than it saves.
4. **Quality last.** `evey-council` runs three models on your hardest prompts —
   which are also your longest. On daily-capped free tiers that is a 3x multiplier
   applied precisely where it hurts most. It may still be worth it; just do not
   turn it on before step 2 tells you what headroom you have.

The plan's numbers — "quality floor ~60%", "2–3x throughput", "+10–15 points" —
have no stated source. Treat them as vendor claims until your own traces agree.

Package names to double-check before installing: the plan says
`pip install hermes-rtkit`, but the PyPI package is `rtk-hermes` (different
author from the `hermes-rtkit` GitHub repo). Install from the repo you actually
audited, and read what a plugin does before giving it your terminal.

## The gap the plan does not address

Everything lives in `~/.litellm` and `~/.hermes` on one machine, assembled by
hand. That is fine until the day you migrate — at which point the setup exists
only as a document describing what you once typed.

That is what this bundle is: the same architecture, corrected, in version
control, deployable onto a new machine with `bootstrap.sh` and verifiable with
`preflight.sh` and `smoke-test.sh`. See `docs/MIGRATION.md`.
