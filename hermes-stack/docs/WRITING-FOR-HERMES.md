# Writing task prompts and markdown files for this Hermes setup

You are being asked to write a markdown file, skill file, task list, or set
of instructions that a Hermes Agent instance will read and act on. This
document explains the one thing that matters most when you do that: **the
literal wording of each step decides which underlying AI model does the
work, not the file's title or your intent.**

Read this whole document before writing anything. It is short.

## The mechanism

This Hermes instance never talks to a specific model directly. Every
message it receives goes through one endpoint — `smart-router` — which
classifies the message and dispatches it to one of four tiers, each backed
by a different real model with different capabilities and a different cost.

For each message, the router checks, in this exact order:

1. **Keyword match.** If the text contains one of the trigger words in the
   table below, that tier wins immediately — no further reasoning happens.
   The three keyword lists are checked in a fixed priority order: REASONING
   is checked before COMPLEX, which is checked before SIMPLE. If a phrase
   matches more than one list, the higher-priority one wins.
2. **Heuristic score.** If nothing matches, a general complexity scorer
   picks a tier, defaulting to MEDIUM for anything it can't confidently
   place.

| Tier | Trigger words (case-insensitive substring match) | What it's for |
|---|---|---|
| REASONING | `refactor`, `architecture`, `design pattern`, `system design`, `trade-off`, `migrate`, `scalab` (matches "scalability" etc.) | Judgment calls between real options — architecture decisions, weighing trade-offs. Not for execution. |
| COMPLEX | `fix`, `bug`, `error`, `stack trace`, `exception`, `traceback`, `failing test`, `regression` | Debugging that needs to see a lot of the codebase at once to find a root cause, not just patch a symptom. |
| SIMPLE | `rename`, `format`, `lint`, `typo`, `comment`, `docstring`, `import` | Pure tidying with no logic change. Runs on a small local model on the user's own GPU — free and instant. |
| *(no match)* | — | The default tier. Ordinary feature-building work that isn't clearly one of the above. This is where most real work should land. |

The exact keyword list lives in `litellm/config.yaml` under
`keyword_tier_rules`, and the exact model behind each tier lives in the same
file under `tiers:`. **Read that file directly if you have access to it —
this table is a snapshot and the owner may have changed it since.** If you
don't have access to the file, ask the user to confirm the current tier
assignments before relying on specifics beyond the mechanism itself.

### Known capability gaps (verified 2026-09-01, may have changed)

Not every model behind every tier can actually execute a tool call — some
will describe an action in plain text instead of using the real function-
calling protocol, which means Hermes ends up describing work instead of
doing it. As of the date above:

- SIMPLE tier's local model did **not** support real tool-calling.
- The default (no-match) tier's model was swapped specifically because the
  original choice couldn't call tools either, even though it had a larger
  free quota.
- COMPLEX and REASONING tiers' models did support real tool-calling.

If you're writing a task that needs Hermes to actually create or edit a
file, run a command, or otherwise take a real action — rather than just
produce an answer or a plan — steer it away from any tier you haven't
confirmed can execute, or ask the user which tiers currently support real
tool use before assuming.

## How to write each step

When you write a file that breaks work into steps — a procedure, a task
list, a checklist — write each step the way you'd honestly describe it to a
person, then check it against the table above. The honest description
usually already contains the right word, because the tiers map to real
differences in what a step needs:

- A step that's genuinely just tidying (renaming a variable, fixing
  formatting, adding a missing docstring) — say so plainly. It lands
  SIMPLE.
- A step that's chasing down why something's broken — use "fix," "bug," or
  name the actual error or exception. It lands COMPLEX.
- A step that's a real design decision (which pattern, how to structure for
  scale, whether to migrate an approach) — use "refactor," "architecture,"
  or "trade-off" language. It lands REASONING.
- Ordinary feature-building work that isn't especially simple, buggy, or
  architectural doesn't need special wording — let it fall through to the
  default tier. That's correct for most real work.

**Do not force a keyword into a step that doesn't genuinely call for that
tier just to route it somewhere specific.** That spends the owner's free-
tier budget dishonestly and hands the step to a model mismatched for the
actual job — a routing decision made on false pretenses helps no one.

If one step is really two different kinds of work — "fix the bug, then
refactor the module so it doesn't happen again" — split it into two steps
so each is classified on its own merits, instead of one step racing to
whichever keyword happens to match first.

## Before you hand the file back

Skim every step you wrote and ask: does the literal wording match what this
step actually needs? A step that reads as "update the `getUser` function"
with no other signal will fall through to the default tier — fine for most
feature work, but call it out if a step that's *obviously* a deep bug hunt
or an architecture call is worded vague enough to miss its intended tier.

If you're unsure what the current tier assignments or known gaps are
because you don't have access to `litellm/config.yaml`, say so explicitly
in your output rather than guessing — the mechanism in this document is
stable, but which model sits behind which tier, and which of them can
actually call tools, are live facts that change as the owner tunes the
system.
