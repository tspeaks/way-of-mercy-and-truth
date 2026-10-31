# Indexing order for the remaining canon

**Status, 31 October 2026 (11:10 CT).** Every book in the canon now has an index file. That is
66 books and 1,519 entries, with 15,645 of the WEB's 31,102 verses in indexed pericopes. The day
began with 14 books and 467 entries. The 52 books added today are drafted, validated and
quotation-checked against the WEB with `tools/check_quotes.py`, and they await second-pass review
(see `REVIEW-QUEUE.md`).

Coverage is uneven by design. The Gospels, Acts and the epistles are indexed close to verse by
verse. The narrative and prophetic books of Tiers 5 and 6 are indexed selectively, under the Song
of Solomon and herem precedents. That covers the historical books, Ezekiel, Daniel, Revelation,
Leviticus, Numbers and Chronicles. Each of these files carries a `coverage_note` listing what was
left out and why. A low verse count in those books is a decision, not a gap.

Tiers 1 to 6 are therefore closed as first drafts. What remains is review, not drafting.

On the practices that were thin this morning:
- **PR26** (Unobligated Loyalty) now has fourteen anchors. They include Ittai (2 Samuel 15:19-22),
  Onesiphorus (2 Timothy 1:15-18), Rizpah (2 Samuel 21:10) and Joseph of Arimathaea (Mark 15:43).
- **PR28** (The Heavenly Palace) has eleven positive anchors and nine counter-examples. Acts 2 and 4,
  2 Corinthians 8-9 and 1 Timothy 6:17-19 lead, and Exodus 16:18 is the root Paul draws on.
- **PR30** (The Secret Rhythmic Devotion) gained Daniel 6:10 ("three times a day… as he did before").
- **PR24** (The Compass) is still the thinnest practice. It has one positive anchor (Ephesians
  2:11-22, medium) and one counter-example (Isaiah 65:5). Nothing in the remaining canon did what
  the practice describes. The open question is whether the 1 John 4:20-21 proposal in
  `REVIEW-QUEUE.md` should be adopted.
- **PR27** (Virtue Construction) has a single anchor, Hebrews 12:4-13, at medium. It is flagged for
  review because it states the practice's premise, that hardship is the material of formation,
  rather than its stone-by-stone act. Whether any scripture prescribes PR27 itself is the clearest
  open question in the index.

*Originally written with thirteen books started: 9 complete, 4 partial, 53 untouched,
and roughly 29,000 of the WEB's 31,098 verses unindexed.*

This is a working order, not a rule. It is arranged so that each tier answers a
question the index cannot currently answer, rather than by canonical sequence or by
size.

---

## Tier 1 — Close the four partial books

**Proverbs 30-31** · 64 verses · Agur and Lemuel, the acrostic. Pericope pattern
already established; an hour's work, and it removes the last "pending" from a book
otherwise finished.

**Luke 10-24** · ~825 verses · The densest unindexed formation material in any Gospel.
The Good Samaritan, Martha's kitchen, the Prodigal, Lazarus at the gate, the Pharisee
and the tax collector, Zacchaeus, the road to Emmaus. **Luke 10:38-42 is the best
remaining candidate for PR20** — a guest has arrived and someone is defending her
routine, which is the practice exactly.

**Matthew 8-28** · ~960 verses · Four more discourses, the parables of the kingdom,
the unforgiving servant, the sheep and the goats, the passion.

**Jeremiah 21-52** · ~1,100 verses · Four sections remain. Chapters 30-33 are the ones
worth reaching: the new covenant written on hearts, and the field bought at Anathoth
with the siege ramps already against the wall.

*Why first:* a partial book is the one place this index misrepresents itself. Every
other honest gap is visible; a half-indexed book looks finished from the outside.

---

## Tier 2 — Books that ground or close a named practice

Small, high-yield, and each one answers something specific.

| Book | Verses | Why |
|---|---|---|
| **Ruth** | 85 | PR26 is *defined* as "the Ruth principle." Its named source text is unindexed. |
| **1 Peter** | 105 | Sojourners and exiles — the core text for C17, the Citizen-Stranger. |
| **2 Peter** | 61 | 1:5-7 adds virtue to virtue in sequence. **The strongest candidate for PR27**, Virtue Construction. |
| **Ecclesiastes** | 222 | Reality exceeding one's grasp, sustained for twelve chapters. PR04 and C18. |
| **Philippians** | 104 | The kenosis hymn — C16 and C23. |
| **Ephesians** | 155 | One body, both brought near. **The likeliest anchor for PR24**, the Compass. |
| **Colossians** | 95 | Hidden with Christ — C23. |

*Why second:* four practices are unanchored, and three of them plausibly close here for
about 800 verses of work. That is the best ratio available anywhere in the canon.

---

## Tier 3 — The formation backbone

**Deuteronomy** · 959 · 30:15-20 sets life and death before them and says choose. The
Two Ways in its original form, upstream of both the Didache and C01.

**Genesis** · 1,533 · **Chapter 18 is the classic PR20 text** — three visitors, a meal
prepared, a routine abandoned. Also C14 and C01.

**Psalms** · 2,461 · The lament corpus. Sacred Lament is already the best-grounded
practice in the index; Psalms would settle it permanently, and C09 with it. Large enough
to need sectioning by book (1-41, 42-72, 73-89, 90-106, 107-150).

**Isaiah** · 1,292 · C03 and C27. Section along the standard seams.

**Job** · 1,070 · The counterweight to Jonah 9:1-12 — an entire book on affliction
without a moral root, plus the friends as a sustained counter-example to PR02.

---

## Tier 4 — Acts and the Pauline letters

**Acts** · 1,004 · 2:44-47 and 4:32-37 hold goods in common and distribute to any who
had need. **The strongest candidate for PR28**, the Heavenly Palace.

**2 Corinthians** · 257 · Chapters 8-9 are the collection — surplus redirected rather
than accumulated. A second PR28 anchor.

Then **Romans**, **1 Corinthians**, **Galatians**, **Hebrews**, **1-2 Thessalonians**,
**1-2 Timothy**, **Titus**, **Philemon**.

---

## Tier 5 — The remaining narrative and prophetic books

Mark, the historical books, the remaining prophets, Revelation.

**Mark** is worth doing before the others: it is the shortest Gospel, and with Matthew,
Luke, and John indexed it completes the four.

---

## Tier 6 — Books likely to anchor little

Leviticus, Numbers, the Chronicles genealogies, and the census and boundary lists.

These should still be indexed, and the Song of Solomon precedent applies: index what
genuinely anchors, record in a `coverage_note` what was left out and why, and do not
stretch a tag to fill the space. A book that anchors three passages honestly is worth
more to this tool than one that anchors thirty by inference.

---

## A note on pace

At roughly 250 verses and 20 entries per working section, the remaining canon is on the
order of a hundred sessions. That is not an argument against doing it. It is an argument
for the file structure holding: each book stands alone, each section states its own
status, and nothing already finished has to be revisited when the next one is added.

Anyone picking this up later should be able to start at any tier without reading the
ones above it.
