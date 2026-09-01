#!/usr/bin/env python3
"""Regenerate the OpenRouter free-model deployment.

OpenRouter's free lineup rotates: models graduate to paid, new launches appear
free for a while, endpoints vanish. Rather than pin a model id that rots, this
picks the best currently-free model and writes it out as the `openrouter-free`
deployment. The NAME is stable, so every fallback chain in config.yaml keeps
working while the model underneath changes.

    scripts/refresh-openrouter-free.py              # rewrite openrouter-free.yaml
    scripts/refresh-openrouter-free.py --dry-run    # show the ranking, write nothing
    scripts/refresh-openrouter-free.py --top 10     # show more candidates
    scripts/refresh-openrouter-free.py --prefer qwen deepseek

Run it weekly (see service/openrouter-refresh.timer) or by hand. It rewrites one
file; nothing else in the stack changes.

WARNING for anyone editing the output format: an `include:`d file may contain
ONLY list-valued top-level keys. LiteLLM extends lists but REPLACES dicts, so a
`router_settings:` or `litellm_settings:` block in here would silently clobber
the main config's copy. model_list only.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

API = "https://openrouter.ai/api/v1/models"
OUT = Path(__file__).resolve().parent.parent / "litellm" / "openrouter-free.yaml"

# Families worth having as a last-resort generalist, best first. Anything not
# listed still ranks, just below these.
DEFAULT_PREFER = ["deepseek", "qwen", "llama", "mistral", "nemotron", "glm", "gpt-oss", "gemma"]

# Free-but-not-useful: image/audio-only, tiny models, and anything whose free
# listing is a preview that disappears mid-session.
EXCLUDE_SUBSTRINGS = ["vision-only", "embed", "rerank", "tts", "whisper", "guard", "moderation"]
MIN_CONTEXT = 32768


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "hermes-stack/1.0"})
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def is_free(model: dict) -> bool:
    pricing = model.get("pricing") or {}
    def zero(field: str) -> bool:
        try:
            return float(pricing.get(field, "1")) == 0.0
        except (TypeError, ValueError):
            return False
    return zero("prompt") and zero("completion")


def score(model: dict, prefer: list[str]) -> float:
    mid = model.get("id", "").lower()
    ctx = model.get("context_length") or 0
    # Context is the thing a last-resort model is actually for: it is the one
    # asked to hold a prompt the metered tiers already refused.
    s = min(ctx, 1_000_000) / 100_000
    for rank, family in enumerate(prefer):
        if family in mid:
            s += (len(prefer) - rank) * 2.0
            break
    if ":free" in mid:
        s += 1.0            # explicit free variant, not a temporarily-zeroed price
    return s


def eligible(model: dict) -> bool:
    mid = model.get("id", "").lower()
    if any(bad in mid for bad in EXCLUDE_SUBSTRINGS):
        return False
    if (model.get("context_length") or 0) < MIN_CONTEXT:
        return False
    modality = ((model.get("architecture") or {}).get("modality") or "").lower()
    return "text" in modality or not modality


def render(model: dict, runner_up: list[dict]) -> str:
    ctx = int(model.get("context_length") or MIN_CONTEXT)
    max_out = int((model.get("top_provider") or {}).get("max_completion_tokens") or 0) or 8192
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    alts = "\n".join(f"#   {m['id']}  ({m.get('context_length')} ctx)" for m in runner_up)
    return f"""# GENERATED — do not edit by hand.
# Written by scripts/refresh-openrouter-free.py on {stamp}.
# Re-run that script to re-pick; the deployment name stays `openrouter-free`
# so every fallback chain in config.yaml keeps working across a rotation.
#
# Runners-up at the time of writing:
{alts or "#   (none)"}
#
# Only list-valued top-level keys belong in an include: file. LiteLLM extends
# lists but REPLACES dicts, so adding router_settings here would clobber the
# main config's copy.

model_list:
  - model_name: openrouter-free
    litellm_params:
      model: openrouter/{model['id']}
      api_key: os.environ/OPENROUTER_API_KEY
      # 20 RPM on free variants regardless of credit; 50 requests/day unless the
      # account has ever purchased $10 of credit, then 1000/day.
      rpm: 15
      tpm: 100000
    model_info:
      max_input_tokens: {min(ctx, 200000)}
      max_tokens: {min(max_out, 8192)}
      supports_vision: false
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--prefer", nargs="*", default=DEFAULT_PREFER)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    try:
        payload = fetch(API)
    except Exception as exc:  # noqa: BLE001
        print(f"could not reach OpenRouter: {exc}", file=sys.stderr)
        print("leaving the existing openrouter-free.yaml in place", file=sys.stderr)
        return 1

    free = [m for m in payload.get("data", []) if is_free(m) and eligible(m)]
    if not free:
        print("no free models matched the filters; leaving the current file alone", file=sys.stderr)
        return 1

    free.sort(key=lambda m: score(m, args.prefer), reverse=True)

    print(f"{len(free)} free models available. Top {args.top}:")
    for m in free[: args.top]:
        print(f"  {score(m, args.prefer):6.2f}  {m['id']:<52} {m.get('context_length'):>9} ctx")

    best, *rest = free
    text = render(best, rest[: args.top - 1])

    if args.dry_run:
        print("\n--- would write ---")
        print(text)
        return 0

    tmp = args.out.with_suffix(".yaml.tmp")
    tmp.write_text(text)
    tmp.replace(args.out)
    print(f"\nwrote {args.out}: openrouter-free -> {best['id']}")
    print("restart or reload the proxy to pick it up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
