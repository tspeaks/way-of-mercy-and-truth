# Local inference on the RTX 2070

**Constraint that drives every choice here: the model must live entirely in the
8 GB of VRAM.** System RAM on this tower is not a spillover pool, so a partial
CPU offload is a failure to fix, not a slower configuration to accept. Ollama
will happily split a model across GPU and CPU and never tell you — it just gets
mysteriously slow — which is why `scripts/local-guard.sh` exists and why
`setup-local-model.sh` treats any CPU placement as a hard stop.

## The budget

| Component | Size |
|---|---|
| `qwen2.5-coder:7b-instruct-q4_K_M` weights | ~4.7 GB |
| KV cache, 32K context, `q8_0` | ~0.9 GB |
| Compute buffers | ~0.6 GB |
| **Total** | **~6.2 GB of 8 GB** |

That leaves ~1.8 GB for the desktop. A browser with hardware acceleration can
eat most of it, which is the most common reason a setup that worked yesterday
spills today. `local-guard.sh` warns below 400 MiB free.

## The one thing most likely to go wrong

`q8_0` KV cache **requires flash attention**. If it is not enabled on the Ollama
*server* — or the driver will not do it on Turing — Ollama silently reverts to
`f16` KV, which doubles the cache to ~1.8 GB. Total goes to ~7.1 GB, the desktop
pushes it past 8, and layers land on the CPU.

Both settings are read by the server process, not the CLI, so setting them in
your shell does nothing. `setup-local-model.sh` writes them into a systemd
override:

```
OLLAMA_FLASH_ATTENTION=1
OLLAMA_KV_CACHE_TYPE=q8_0
OLLAMA_MAX_LOADED_MODELS=1     # no second model competing for the same 8 GB
OLLAMA_NUM_PARALLEL=1          # one context at a time
OLLAMA_KEEP_ALIVE=30m          # reloading 4.7 GB every turn is its own tax
```

If flash attention is unavailable, the fix is a smaller context, not a smaller
quant: `--ctx 16384` puts an f16 cache back under 1 GB.

## Setup

```bash
scripts/setup-local-model.sh     # tries 32K, steps down 24K -> 16K -> 8K
scripts/local-tier.sh on         # route SIMPLE to it (refuses if not VRAM-resident)
scripts/local-guard.sh           # re-check any time
```

`setup-local-model.sh` builds a `hermes-local` model with `num_gpu 99` — every
layer on the GPU — so a model that does not fit fails visibly rather than
degrading to 2 tokens/second. If no context in the ladder fits, it calls
`local-tier.sh off` itself and tells you.

Re-run `local-guard.sh` after driver updates and after any unexplained slowdown.

## What it does and does not serve

**SIMPLE tier only.** Renames, formatting, small functions, "what does this
do" — the highest-volume, lowest-stakes traffic. Moving it local takes the bulk
of your requests off every hosted free tier at once, leaving those quotas for
work that needs them.

It is deliberately **not** the delegation target. `OLLAMA_NUM_PARALLEL=1` means
one context at a time, so concurrent subagents would serialise behind each
other. Delegation goes to `qwen3-flash` instead.

It is also not the compression model: compression reads the whole context, and
28K will not hold a conversation that has grown past it.

## When the local tier is off

`local-tier.sh off` points SIMPLE at `groq-fast`. Nothing else changes — the
fallback chains already run through `groq-fast → qwen3-flash → codestral`, so
the stack keeps working at a slightly higher hosted cost.

## After the hardware upgrade

The seam is the same; only the numbers move.

| VRAM | Model | Serves |
|---|---|---|
| 8 GB (today) | Qwen2.5-Coder 7B Q4_K_M | SIMPLE |
| 16 GB | Qwen2.5-Coder 14B Q4_K_M | SIMPLE, MEDIUM |
| 24 GB | Qwen2.5-Coder 32B Q4_K_M | SIMPLE, MEDIUM, some COMPLEX |
| 48 GB+ | 32B at Q8, or 70B at Q4 | everything but REASONING |

Leave REASONING hosted regardless — it is a small fraction of requests and the
one place a frontier-class model still earns its keep.

MoE models (a 30B-A3B, say) are the usual advice for a small card because only
~3B parameters are active per token — but that advice assumes you can offload
experts to system RAM. On this tower that assumption does not hold, so a dense
7B that fits entirely in VRAM is the better answer until the card changes.
