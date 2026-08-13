# Contributing

Two kinds of contribution, handled differently.

## 1. Corrections to the trunk

The book asks to be checked. Corrections are the mechanism working.

Open an issue for:

- a scripture citation that does not say what the text claims
- a source characterized in a way its author would not recognize
- an internal contradiction between chapters
- a practice whose instructions cannot be followed as written
- typos, broken links, formatting errors

Use the issue templates. For anything touching meaning, quote the passage and say what
you think it should say instead.

## 2. Everything else — branches

Adaptations, translations, field reports, group materials, work on sources not treated
here, or a version that disagrees with this one.

None of that goes in the trunk. All of it is welcome as a branch or fork.

```
branches/<your-name>/<short-description>/
  README.md      # what you changed and why
  ...
```

State plainly what you changed. Do not present a branch as the trunk.

## Working on the genealogy

`genealogy/` is a living layer and revisions are expected. Two rules:

- Do not move genealogy material into `trunk/`. They answer different questions and are
  kept apart deliberately.
- Do not remove a `status: speculative` marker to make material look more settled than it
  is.

## Working on the manuscript

Sections live in `trunk/` as Markdown with YAML front matter. **Never edit the `id`
field** — IDs are permanent.

After editing, rebuild the machine-readable artifacts:

```bash
python3 tools/build.py
```

This regenerates `llms.txt`, `manifest.json`, and `dist/`. Commit those alongside your
change.

## Commit messages

State what changed and why, in that order. The governance rule — *keep the history
visible; if you change something, say what you changed and why* — applies to commits as
much as to branches.

```
C23: correct Aphrahat attribution in the hidden-life passage

The claim about secrecy as mechanism is Aphrahat's; the framing about
energy being one supply is mine. Signposted accordingly.
```

## The capture pipeline

Drafting happens away from the keyboard as often as at it. The working loop:

1. **Capture** — voice memo, whenever the thinking happens
2. **Transcribe** — same day or next
3. **Edit** — a real editing pass, not a transcript dump
4. **Branch** — as your own work, marked as yours
5. **Propose** — only if it belongs in the trunk

Step 3 is not optional. Publishing unedited transcripts as if they were finished work
inflates volume and costs durability. Fewer words, higher precision.
