# hermes-stack

Version-controlled, machine-portable configuration for running
[Hermes Agent](https://github.com/NousResearch/hermes-agent) behind a local
[LiteLLM](https://github.com/BerriAI/litellm) proxy that routes by task
complexity across free provider tiers — and, after the hardware migration,
across local inference.

**Start here:** [`docs/ASSESSMENT.md`](docs/ASSESSMENT.md) — what was wrong with
the original plan and what changed.
**Moving machines:** [`docs/MIGRATION.md`](docs/MIGRATION.md).
**Adding a GPU:** [`docs/LOCAL-MODELS.md`](docs/LOCAL-MODELS.md).

## Shape

```
Hermes  ──►  LiteLLM :4000  ──►  SIMPLE     qwen3-flash
 (one          (all the          MEDIUM     qwen3-coder
  model         routing,         COMPLEX    qwen3-coder   ← cerebras-fast on short prompts
  name)         all the keys)    REASONING  nvidia-llama4
                                 fallback   cloudflare-llama → gemini-flash (last)
                                 [ local-coder slots in here after migration ]
```

Hermes only ever asks for `smart-router`. Every provider change, quota
exhaustion, and eventual move to local hardware happens below that line.

## Quickstart

```bash
scripts/bootstrap.sh          # install litellm, deploy config, validate
$EDITOR ~/.litellm/.env       # fill in keys
scripts/preflight.sh          # confirm every key reaches its provider
scripts/start-proxy.sh        # or install service/litellm-proxy.service
scripts/smoke-test.sh         # exercise all four tiers through the router
```

## Layout

| Path | |
|---|---|
| `litellm/config.yaml` | the router. Validated against real LiteLLM, not from memory |
| `litellm/.env.example` | every secret and the one account-scoped URL |
| `hermes/config.yaml` | Hermes pointed at the proxy; auxiliary + delegation on the cheap tier |
| `scripts/bootstrap.sh` | idempotent install + deploy, backs up whatever it replaces |
| `scripts/validate-config.py` | loads the config into a real Router — offline, no keys needed |
| `scripts/preflight.sh` | probes every provider with your actual key |
| `scripts/explain-routing.py` | shows which tier and model a prompt gets, offline |
| `scripts/smoke-test.sh` | end-to-end through the running proxy, one request per tier |
| `scripts/backup.sh` / `restore.sh` | move `~/.hermes` state between machines |
| `service/` | systemd user unit and launchd agent |

## Rules of the road

- **Secrets never enter this repo.** Only `.env.example` is tracked; `.gitignore`
  covers the rest. `bootstrap.sh` chmods the real ones `600`.
- **Run `validate-config.py` before every deploy.** It catches the whole class of
  errors that otherwise surfaces as a 404 three days later.
- **`preflight.sh` is the source of truth about providers**, not the comments in
  the config. Free tiers change without notice; the script asks, the comments remember.
