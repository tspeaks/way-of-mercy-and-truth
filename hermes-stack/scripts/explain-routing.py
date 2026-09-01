#!/usr/bin/env python3
"""Show which tier and model a prompt would route to -- offline, no API calls.

Uses LiteLLM's own ComplexityRouter classifier against your real config, so what
it prints is what the proxy will actually do.

    scripts/explain-routing.py                      # run the built-in sample set
    scripts/explain-routing.py "refactor the auth module"
    cat prompts.txt | scripts/explain-routing.py -  # one prompt per line

Use it to answer "am I over-routing to SIMPLE?" before you have a week of traces,
and to sanity-check keyword_tier_rules after you edit them.
"""
import logging
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("LITELLM_LOG", "ERROR")
logging.getLogger("LiteLLM").setLevel(logging.ERROR)

import litellm  # noqa: E402
import yaml  # noqa: E402
from litellm import Router  # noqa: E402
from litellm.router_strategy.complexity_router.complexity_router import (  # noqa: E402
    ComplexityRouter,
)

litellm.suppress_debug_info = True

CONFIG = Path(__file__).resolve().parent.parent / "litellm" / "config.yaml"
ENV_REF = re.compile(r"^os\.environ/(.+)$")

SAMPLES = [
    "rename the variable foo to bar",
    "fix the TypeError in the login handler, stack trace attached",
    "write a function that parses ISO 8601 timestamps",
    "refactor the auth module to use dependency injection instead of globals",
    "what does this regex do?",
    "design a schema for multi-tenant billing with per-seat and usage components",
]


def resolve(v):
    if isinstance(v, dict):
        return {k: resolve(x) for k, x in v.items()}
    if isinstance(v, list):
        return [resolve(x) for x in v]
    if isinstance(v, str):
        m = ENV_REF.match(v)
        if m:
            return os.environ.get(m.group(1)) or f"dummy-{m.group(1).lower()}"
    return v


raw = yaml.safe_load(CONFIG.read_text())
model_list = resolve(raw["model_list"])
router = Router(model_list=model_list, **resolve(raw.get("router_settings") or {}))

entry = next(m for m in model_list if m["model_name"] == "smart-router")
params = entry["litellm_params"]
cr = ComplexityRouter(
    model_name="smart-router",
    litellm_router_instance=router,
    complexity_router_config=params.get("complexity_router_config"),
    default_model=params.get("complexity_router_default_model"),
    derive_savings_baseline=False,
)

def _tier_str(t):
    return getattr(t, "value", str(t))


args = sys.argv[1:]
if args == ["-"]:
    prompts = [line.strip() for line in sys.stdin if line.strip()]
elif args:
    prompts = [" ".join(args)]
else:
    prompts = SAMPLES

width = max((len(p) for p in prompts), default = 0)
width = min(width, 60)
print(f"{'PROMPT':<{width}}  {'TIER':<10} {'SCORE':>6}  {'WHY':<16} MODEL")
print("-" * (width + 50))
for p in prompts:
    tier, score, signals = cr.classify(p)
    why = "score"
    # keyword_tier_rules are applied on the request path, ahead of the scorer --
    # not inside classify() -- so apply the same override here or this tool will
    # under-report every prompt your rules were written to catch.
    override = cr._lexical_tier_override(p.lower())
    if override is not None:
        tier = cr.config.resolve_classified_tier(_tier_str(override.tier))
        why = f"kw:{override.matched_keyword}" if override.matched_keyword else "kw"
    model = cr.get_model_for_tier(tier)
    shown = p if len(p) <= width else p[: width - 1] + "…"
    print(f"{shown:<{width}}  {_tier_str(tier):<10} {score:>6.3f}  {why:<16} {model}")
    if os.environ.get("EXPLAIN_SIGNALS") and signals:
        for sig in signals:
            print(f"{'':<{width}}    · {sig}")
