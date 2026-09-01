# After the hardware: adding local inference

The point of the seam is that local models are an *addition*, not a rebuild.
When the new box is running, one uncommented block in `litellm/config.yaml` and
one edited tier moves your highest-volume traffic off every free tier at once.

## Why this is the biggest win available

Tier volume is inverted from tier value: SIMPLE and MEDIUM are most of your
requests and least of your thinking. Those are exactly the ones a local 7B–32B
coder model handles well. Move them local and the remote free tiers stop being a
budget you spend on `rename this variable` and start being a reserve you spend
on the hard 10%.

Local also removes the two failure modes this stack cannot otherwise fix: a
provider changing its free tier overnight, and a daily cap landing mid-task.

## Sizing

Pick by VRAM, not by benchmark score. A model that fits with room for a real
context window beats a bigger one that swaps.

| VRAM | Model to run | Serves | Context to expect |
|---|---|---|---|
| 8–12 GB | Qwen2.5-Coder 7B (Q5_K_M) | SIMPLE | 16–32K |
| 16 GB | Qwen2.5-Coder 14B (Q4_K_M) | SIMPLE, MEDIUM | 32K |
| 24 GB | Qwen2.5-Coder 32B (Q4_K_M) | SIMPLE, MEDIUM, some COMPLEX | 32–64K |
| 48 GB+ | 32B at Q8, or a 70B at Q4 | everything but REASONING | 64–128K |
| Apple silicon | same, via MLX or Ollama; unified memory means ~⅔ of total RAM | as above | as above |

Leave REASONING remote regardless of VRAM. It is a small fraction of requests
and the one place a frontier-class model still pays for itself.

## Serving it

**Ollama** — simplest, good enough, OpenAI-compatible at `:11434/v1`:

```bash
ollama pull qwen2.5-coder:32b
ollama serve
```

**vLLM** — faster under concurrency (which matters once Hermes delegates to
subagents), OpenAI-compatible at `:8000/v1`:

```bash
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct \
  --max-model-len 65536 --gpu-memory-utilization 0.90
```

Set the context you configure in LiteLLM to what you actually served with
(`--max-model-len`), not what the model card claims.

## Wiring it in

1. In `~/.litellm/.env`:
   ```
   LOCAL_API_BASE=http://127.0.0.1:11434/v1
   LOCAL_API_KEY=not-needed
   ```
2. In `litellm/config.yaml`, uncomment the `local-coder` block and set `model:`
   to the id your server actually serves (`ollama list` / the vLLM `--served-model-name`),
   and `max_input_tokens` to what you served.
3. Move the tiers:
   ```yaml
   tiers:
     SIMPLE:    local-coder
     MEDIUM:    local-coder
     COMPLEX:   qwen3-coder
     REASONING: nvidia-llama4
   ```
4. Keep remote as the safety net — local goes down too:
   ```yaml
   fallbacks:
     - local-coder: ["qwen3-flash", "qwen3-coder"]
   ```
5. `scripts/validate-config.py && scripts/preflight.sh && scripts/smoke-test.sh`

Then re-run `scripts/explain-routing.py` and confirm the mix moved where you
expect. Total edit: two files, five minutes, no change anywhere in Hermes.

## Worth doing at the same time

Local inference makes `evey-council` cheap — a 3-model debate costs electricity
rather than a daily cap. If you want the council pattern, this is when to turn
it on, with two local seats and one remote for genuine diversity of opinion.
