#!/usr/bin/env python3
"""Offline validation of the LiteLLM config.

Builds a real litellm.Router from the config with dummy credentials. This catches
schema errors, bad complexity-router keys, fallback chains that name a model that
does not exist, and mid-string os.environ/ mistakes -- without making a single
network call or needing any real API key.

Run this before every deploy, and after every edit to litellm/config.yaml.

    scripts/validate-config.py [path/to/config.yaml]

Exit code 0 = config loads clean.
"""
import logging
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("LITELLM_LOG", "ERROR")
logging.getLogger("LiteLLM").setLevel(logging.ERROR)

CONFIG = Path(sys.argv[1] if len(sys.argv) > 1 else
              Path(__file__).resolve().parent.parent / "litellm" / "config.yaml")

try:
    import litellm
    import yaml
    from litellm import Router
except ImportError as exc:  # pragma: no cover
    sys.exit(f"missing dependency: {exc}. Run scripts/bootstrap.sh first.")

litellm.suppress_debug_info = True

ENV_REF = re.compile(r"^os\.environ/(.+)$")
MID_STRING_ENV = re.compile(r".+os\.environ/")

problems: list[str] = []
warnings: list[str] = []


def resolve(value):
    """Mirror LiteLLM's os.environ/ expansion, and flag the mid-string mistake."""
    if isinstance(value, dict):
        return {k: resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v) for v in value]
    if isinstance(value, str):
        m = ENV_REF.match(value)
        if m:
            return os.environ.get(m.group(1)) or f"dummy-{m.group(1).lower()}"
        if MID_STRING_ENV.match(value):
            problems.append(
                f"'os.environ/' appears mid-string and will NOT be expanded: {value!r}. "
                "Move the whole value into one env var."
            )
    return value


raw = yaml.safe_load(CONFIG.read_text())

# Resolve `include:` the way the proxy does: extend list-valued keys, replace
# everything else. That replace-on-dict behaviour is a foot-gun -- an included
# file carrying router_settings would silently wipe the main config's -- so
# refuse anything but lists in an included file.
for include_file in raw.pop("include", []) or []:
    inc_path = CONFIG.parent / include_file
    if not inc_path.exists():
        problems.append(f"include: {include_file!r} does not exist (the proxy will refuse to boot)")
        continue
    included = yaml.safe_load(inc_path.read_text()) or {}
    for key, value in included.items():
        if not isinstance(value, list):
            problems.append(
                f"include: {include_file!r} sets non-list key {key!r}; LiteLLM REPLACES dicts on "
                "include, so this would clobber the main config. Included files may define lists only."
            )
            continue
        raw.setdefault(key, [])
        raw[key].extend(value)

model_list = raw.get("model_list") or []
router_settings = raw.get("router_settings") or {}

declared = {m["model_name"] for m in model_list}
seen: dict[str, int] = {}
for entry in model_list:
    seen[entry["model_name"]] = seen.get(entry["model_name"], 0) + 1
for name, count in seen.items():
    if count > 1:
        warnings.append(
            f"{name!r} is declared {count} times; LiteLLM treats those as load-balanced "
            "deployments and picks between them at random, not in order."
        )

# Every name referenced by a tier or a fallback chain must be a real deployment.
for entry in model_list:
    cfg = (entry.get("litellm_params") or {}).get("complexity_router_config") or {}
    for tier, target in (cfg.get("tiers") or {}).items():
        for name in (target if isinstance(target, list) else [target]):
            if isinstance(name, str) and name not in declared:
                problems.append(f"tier {tier} points at undeclared model {name!r}")
        if isinstance(target, list) and len(target) > 1:
            warnings.append(
                f"tier {tier} has {len(target)} models; LiteLLM picks among them with "
                "random.choice(), not in order. Use router_settings.fallbacks for ordered failover."
            )
    default = (entry.get("litellm_params") or {}).get("complexity_router_default_model")
    if default and default not in declared:
        problems.append(f"complexity_router_default_model {default!r} is not declared")

for key in ("fallbacks", "context_window_fallbacks", "content_policy_fallbacks"):
    for chain in router_settings.get(key) or []:
        for src, targets in chain.items():
            if src not in declared:
                problems.append(f"{key}: source {src!r} is not declared")
            for dst in targets:
                if dst not in declared:
                    problems.append(f"{key}: {src} falls back to undeclared {dst!r}")

# Context-window guards are inert unless pre-call checks are on.
if not router_settings.get("enable_pre_call_checks"):
    warnings.append(
        "router_settings.enable_pre_call_checks is not true -- max_input_tokens will be "
        "ignored and oversized prompts will fail at the provider instead of re-routing."
    )

for entry in model_list:
    info = entry.get("model_info") or {}
    if entry["model_name"] == "smart-router":
        continue
    if "max_input_tokens" not in info:
        warnings.append(
            f"{entry['model_name']}: no max_input_tokens. Context-aware routing cannot "
            "protect this deployment (model_info.max_tokens is OUTPUT tokens, not context)."
        )

# The real test: does LiteLLM itself accept this?
try:
    router = Router(model_list=resolve(model_list), **resolve(router_settings))
except Exception as exc:  # noqa: BLE001
    problems.append(f"litellm.Router rejected the config: {type(exc).__name__}: {exc}")
else:
    names = sorted({d["model_name"] for d in router.model_list})
    print(f"Router built OK with {len(names)} deployments: {', '.join(names)}")

for w in warnings:
    print(f"WARN  {w}")
for p in problems:
    print(f"FAIL  {p}")

if problems:
    sys.exit(1)
print("config OK")
