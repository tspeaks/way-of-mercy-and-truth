# Governance: The Trunk and What Grows From It

This document is the operational form of the Final Note at the end of the book. The
book states the rule; this states how the rule is enforced in a repository.

## The Trunk

The `main` branch is the trunk. It holds the common curriculum: twenty-nine chapters,
seven stages, three appendices, and the front matter.

A trunk has to be stable or it is not a trunk. Its purpose is that people walking this
road at different times and in different places can be said to be walking the same road.

Accordingly:

- The trunk changes slowly and visibly.
- No change reaches the trunk without a record of what changed and why.
- The trunk is never rewritten in place. History is never squashed, force-pushed, or
  amended after publication.

## Branches

Anyone may develop this material further. That is expected and welcome. The rule is the
one the book already states:

> Where you develop it, develop it as your own branch and say that it is yours. Do not
> quietly rewrite the trunk and hand it on as though it had always said what you have
> made it say.

In practice:

- Fork the repository, or open a branch under `branches/<your-name>/<short-description>`.
- Say in your README what you changed and why you changed it.
- Do not present a branch as the trunk.

A branch that disagrees with the trunk is not a problem. A branch that disguises itself
as the trunk is.

## Stable citation identifiers

Every section carries a permanent ID in its front matter:

| Prefix | Meaning | Example |
|---|---|---|
| `WMT P0` | Preface | `WMT P0` |
| `WMT S1`–`WMT S7` | Stages | `WMT S3` |
| `WMT C01`–`WMT C29` | Chapters | `WMT C23` |
| `WMT A1`–`WMT A3` | Appendices | `WMT A1` |
| `WMT PR01`–`WMT PR30` | Practices | `WMT PR12` |
| `WMT G00`–`WMT G09` | Genealogy | `WMT G04` |

**These IDs never change.** Wording may be revised; titles may be sharpened; file paths
may move. The ID stays. This is what lets someone cite `WMT C23` in a study group,
a footnote, or a conversation ten years from now and have it still resolve.

If a section is ever retired, its ID is retired with it. IDs are never reused.

## Versioning

The trunk is versioned `MAJOR.MINOR.PATCH`.

- **PATCH** — typos, formatting, broken links. No change to meaning.
- **MINOR** — clarifications, added scripture references, expanded practice notes. The
  teaching is unchanged; the expression is improved.
- **MAJOR** — a change in what the book actually teaches: a stage reordered, a practice
  withdrawn, a source reassessed, a position reversed.

Every MAJOR release requires an entry in `CHANGELOG.md` stating what changed, why, and
what a reader who learned the previous version should now understand differently.

The current version is recorded in `VERSION`.

## The genealogy layer

`genealogy/` is a peer to the trunk, not part of it. It records how the project developed:
sources, sequence, and reasoning.

It is governed differently. The trunk is stable and changes slowly, because people are
walking it. The genealogy is **living** — it is revised as the project develops, and it
carries no expectation of stability. It is not versioned with the trunk.

One rule applies to it specifically: **material marked `status: speculative` in its front
matter is fenced.** It is recorded because it is genuinely part of the development, not
because it carries the same weight as the rest. It must never be presented as curriculum,
and it must not migrate into `trunk/`.

## What does not belong in the trunk

From the Final Note:

> Around it there will be, God willing, other things: the records of people who actually
> walked this and found where it fails; practices adapted to circumstances I never
> imagined; work on sources I did not treat; small companies of people meeting somewhere
> and doing the plain work of mercy in their own streets. None of that belongs in this
> book.

So: field reports, adaptations, commentary, translations, group materials, and
disagreements all live in branches, forks, or the Commons — not in the trunk.

A curriculum that tried to contain its own future would be neither.

## Corrections

The book asks to be checked rather than trusted. Corrections are therefore not a
nuisance; they are the mechanism working.

Open an issue if you find:

- a scripture citation that does not say what the text claims it says
- a source characterized in a way its author would not recognize
- an internal contradiction between chapters
- a practice whose instructions cannot actually be followed as written

> I would rather be corrected in the open than agreed with in the dark.
