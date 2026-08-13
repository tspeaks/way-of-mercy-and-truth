# Second-Pass Review Brief

Give this file, plus `james.json`, to the reviewing model. It contains everything
needed to review the index without access to the full curriculum.

---

## What The Way of Mercy and Truth is

A twenty-nine chapter curriculum of Christian formation, released to the public domain.
It arranges existing material — biblical, patristic, Syriac, monastic — into a
developmental path. It claims to add nothing; it claims only to order what is there,
according to the sequence in which human beings actually change.

**Three pillars**, drawn from Micah 6:8:

- **Truth** — what is actually so
- **Mercy** — what love does with it
- **Humility** — what keeps the other two honest

Truth without mercy turns harsh. Mercy without truth turns sentimental.

**Seven stages**, each answering one question:

| | Stage | Question | Chapters |
|---|---|---|---|
| S1 | Foundations | How should one live? | C01–C05 |
| S2 | Perception | How should one see? | C06–C08 |
| S3 | Abiding | How does one remain? | C09–C12 |
| S4 | Community | How should people live together? | C13–C18 |
| S5 | Healing | How is the heart healed? | C19–C22 |
| S6 | Transformation | How does the heart change? | C23–C26 |
| S7 | Mature Mercy | What does the transformed person become? | C27–C29 |

**Chapters:**

C01 The Ground Beneath Everything · C02 The Skill of Living · C03 The Blueprint of
Mercy · C04 The Mirror · C05 The Apprenticeship · C06 The Opening of the Eyes ·
C07 Cleansing the Eyes · C08 The True Prophet · C09 The Secret Place · C10 The Delight
of Remaining · C11 The Vine · C12 The Proof · C13 Ordinary Faithfulness · C14 The
Household · C15 The Architecture of Peace · C16 The Logic of Service · C17 The
Citizen-Stranger · C18 Holy Detachment · C19 The Door Not the Wall · C20 The Watchman
at the Gate · C21 The Physician's Manual · C22 The Quiet Soul · C23 The Hidden Life ·
C24 The Landscape of Wonder · C25 The Architecture of Growth · C26 The Temple of Light ·
C27 The Ocean · C28 The Liturgy of the Ordinary · C29 The Fully Formed Heart

**Thirty practices (PR01–PR30):**

PR01 The Moral Audit · PR02 Interior Diagnosis · PR03 Self-Accusation · PR04 The
Discipline of Unknowing · PR05 Habitual Almsgiving · PR06 Non-Retaliation · PR07 The
Daily Anchors · PR08 Sacred Lament · PR09 The Architecture of Peace · PR10 The
Citizen-Stranger · PR11 The Failure Recovery Protocol · PR12 Watchfulness · PR13 The
Hidden Life · PR14 The Discipline of Gradualism · PR15 Shedding Harshness · PR16
Listening as Mercy · PR17 Covering Weakness · PR18 Absorbing the Blow · PR19
Spontaneous Service · PR20 The Sacrifice of Routine · PR21 Verbal Almsgiving · PR22
Unreciprocated Care · PR23 The Sacrament of the Ordinary · PR24 The Compass · PR25
Deferential Seating · PR26 Unobligated Loyalty · PR27 Virtue Construction · PR28 The
Heavenly Palace · PR29 Merciful Reintegration · PR30 The Secret Rhythmic Devotion

**Two commitments that constrain this work:**

1. All scripture is quoted from the **World English Bible** (public domain) and from
   nothing else.
2. The curriculum is **CC0**. Nothing in the index may reproduce copyrighted
   translation wording of any kind.

---

## What a good entry looks like

An entry connects a passage to the curriculum in a way that would change how someone
reads one or the other. It is not a topical label.

**Good:** James 3:3-6 → C20, PR12. *Three images for the disproportion between a small
thing and what it steers or destroys — the governing logic of Watchfulness.*
The connection explains why the passage belongs where it is placed.

**Bad:** James 3:3-6 → C20. *Both are about the tongue.*
True, and useless. Shared vocabulary is not a thematic connection.

**The practice test.** Four of the five errors caught in the first review were practice
tags attached to passages whose chapter and stage placement was correct. So practice
tags carry a stricter burden than chapter tags. Before a practice is tagged, it must
pass this question:

> Does the passage prescribe this practice, enact it, or show what its absence costs —
> or does it merely share the practice's subject matter?

Only the first three qualify. *Asking God for wisdom* shares subject matter with the
Discipline of Unknowing and prescribes nothing of the kind; that tag was an error.
Apply this test to every practice tag and flag any that fails it.

**Also bad:** stretching a passage to fill a gap. If a practice has no genuine anchor
in this book, that absence is data. Do not invent one.

---

## Narrative books and the `mode` field

Entries in a narrative book carry a `mode` field with one of three values:

- `prescribes` — the passage commands the practice
- `exemplifies` — someone in the passage does it
- `counter-example` — the passage shows what its absence costs

This exists because narrative teaches differently from instruction. Jonah holds correct
doctrine and refuses the mercy that follows from it for four chapters, so most of what
that book anchors, it anchors negatively. A counter-example is a real anchor, not a weak
one — but a tag that could not distinguish the two would misrepresent the text.

When reviewing a narrative book, check the mode as carefully as the tags. A passage
marked `exemplifies` where the character is in fact failing is a substantive error.

## Your task

Review every entry in the index file you are given and return your findings as JSON. For each entry you
would change, give:

```json
{
  "ref": "James 4:1-3",
  "verdict": "overreach | understated | miscategorized | redundant | sound",
  "note": "one or two sentences",
  "suggested_change": { "chapters": ["C22"], "practices": ["PR03"] }
}
```

Then answer four questions about the set as a whole:

1. **Overreach.** Which connections are forced? Where has the drafter read WMT's
   framework into a passage that does not support it? Be specific and be blunt — this
   is the failure mode most worth catching.

2. **Gaps.** Which passages carry weight in James that the index underplays or misses?
   Note especially anything the drafter may have skipped because it did not fit the
   framework neatly.

3. **Redundancy.** Where do several entries make the same connection? Which should be
   consolidated?

4. **Confidence calibration.** The drafter marked 26 entries `high` and 9 `medium`.
   Which `high` entries should be downgraded? Which `medium` ones are actually solid?

---

## Two things worth knowing before you start

**Seven entries are marked `prior: true`.** These were already cited in the curriculum
before this index existed — they are the author's own prior judgments, not the
drafter's. Treat them as the calibration set. If your reading of them diverges sharply
from what is recorded, say so, but note that you are disagreeing with the author rather
than with the drafter.

**The coverage is deliberately uneven.** Thirteen of the thirty practices have no anchor
in James, and five chapters have none. The drafter's position is that this reflects what
James actually is — a letter about wisdom, speech, partiality, and community, not about
contemplative interiority. Test that claim rather than assuming it. If you think a
missing connection is real, name it.
