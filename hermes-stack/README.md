# hermes-stack

Version-controlled, machine-portable configuration for running
[Hermes Agent](https://github.com/NousResearch/hermes-agent) behind a local
[LiteLLM](https://github.com/BerriAI/litellm) proxy that routes by task
complexity across free provider tiers — and, after the hardware migration,
across local inference.

**Start here:** [`docs/ASSESSMENT.md`](docs/ASSESSMENT.md) — what was wrong with
the original plan and what changed.
**Who serves what, and why:** [`docs/ROUTING.md`](docs/ROUTING.md).
**The 8 GB card:** [`docs/LOCAL-MODELS.md`](docs/LOCAL-MODELS.md).
**Moving machines:** [`docs/MIGRATION.md`](docs/MIGRATION.md).
**Writing task prompts for Hermes (portable, any LLM):** [`docs/WRITING-FOR-HERMES.md`](docs/WRITING-FOR-HERMES.md).

## Shape

```
Hermes  ──►  LiteLLM :4000  ──►  SIMPLE     local-coder          (RTX 2070, free)
 (one          (all the          MEDIUM     codestral            (~1B tok/month)
  model         routing,         COMPLEX    nvidia-kimi        (Kimi K3, 1M context)
  name)         all the keys)    REASONING  gemini-flash         (1M context)

                                 short-prompt fallback  groq-fast   (6K TPM fence)
                                 long-prompt rescue     gemini-flash (1M context)
                                 last resort            openrouter-free (rotating)
                                 side tasks only        offtopic    (Aion, 20K tok/day)
```

Hermes only ever asks for `smart-router`. Every provider change, quota
exhaustion, and eventual move to local hardware happens below that line.

## Quickstart

```bash
scripts/bootstrap.sh                 # install litellm, deploy config, validate
$EDITOR ~/.litellm/.env              # fill in keys
scripts/preflight.sh                 # keys reach providers; model ids still exist
scripts/refresh-openrouter-free.py   # pick today's best free last-resort model
scripts/setup-local-model.sh         # local SIMPLE tier, VRAM-resident
scripts/local-tier.sh on
scripts/start-proxy.sh               # or install service/litellm-proxy.service
scripts/smoke-test.sh                # exercise every route through the proxy
```

Before the first Mistral request: **console.mistral.ai → Admin → Privacy →
disable data sharing for model training.** The free tier trains on your prompts
by default.

## Layout

| Path | |
|---|---|
| `litellm/config.yaml` | the router. Validated against real LiteLLM, not from memory |
| `litellm/openrouter-free.yaml` | generated; the current free pick. Never edit by hand |
| `litellm/.env.example` | every secret and the one account-scoped URL |
| `hermes/config.yaml` | Hermes pointed at the proxy; auxiliary + delegation on the cheap tier |
| `scripts/bootstrap.sh` | idempotent install + deploy, backs up whatever it replaces |
| `scripts/validate-config.py` | loads the config into a real Router — offline, no keys needed |
| `scripts/preflight.sh` | probes every provider with your actual key |
| `scripts/explain-routing.py` | shows which tier and model a prompt gets, offline |
| `scripts/smoke-test.sh` | end-to-end through the running proxy, one request per tier |
| `scripts/refresh-openrouter-free.py` | re-pick the best currently-free OpenRouter model |
| `scripts/setup-local-model.sh` | build the local model, stepping context down until it fits VRAM |
| `scripts/local-guard.sh` | fail loudly if any layer spilled to the CPU |
| `scripts/local-tier.sh` | route SIMPLE to local, or back to hosted |
| `scripts/backup.sh` / `restore.sh` | move `~/.hermes` state between machines |
| `service/` | systemd user unit and launchd agent |

## Rules of the road

- **Secrets never enter this repo.** Only `.env.example` is tracked; `.gitignore`
  covers the rest. `bootstrap.sh` chmods the real ones `600`.
- **Run `validate-config.py` before every deploy.** It catches the whole class of
  errors that otherwise surfaces as a 404 three days later.
- **`preflight.sh` is the source of truth about providers**, not the comments in
  the config. Free tiers change without notice; the script asks, the comments remember.
- **`litellm/openrouter-free.yaml` is generated.** Edit the script, not the file.
  An `include:`d file may contain list-valued keys only — LiteLLM extends lists
  but *replaces* dicts, so a `router_settings:` block in there would silently
  clobber the main config's.
- **Nothing local may touch system RAM.** `local-guard.sh` is the check; run it
  after driver updates and whenever the local tier feels slow.
