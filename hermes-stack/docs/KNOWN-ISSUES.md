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

**Status:** unresolved / unreproduced as of this writing. Update this
entry once the `/restart` + retest happens, whichever way it goes.
