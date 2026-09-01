# Known issues

Bugs observed in the running stack that live in Hermes Agent or LiteLLM
itself, not in this repo's config. Tracked here so they survive past the
Telegram scrollback, and so a fix upstream (or a workaround in config) has
something to check off against.

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
