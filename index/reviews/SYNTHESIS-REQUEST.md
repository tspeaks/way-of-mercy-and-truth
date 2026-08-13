# Synthesis request — six earlier books

Per-entry verdicts for the books below were already produced and are recorded. What was not
carried across were the answers to the brief's synthesis questions. This asks for those, and
only those, in a single pass.

**Do not re-review the individual entries.** Those verdicts stand and have been adjudicated.
The synthesis questions ask about each book *as a whole*, which is a different job.

For each book, attach its review package — `index/reviews/<book>-package.md` — which prints
every entry with its scripture in full. Two of the five questions cannot be answered without it:
gaps requires knowing what the book contains beyond what was indexed, and stated claims requires
checking assertions against the text.

## Return format

```json
{ "book": "Jonah",
  "overreach": "…", "gaps": "…", "redundancy": "…",
  "confidence_calibration": "…", "stated_claims": "…" }
```
One object per book, in an array.

## The five questions

1. **Overreach** — which connections are forced, or read the framework into a passage that
   does not support it. Be blunt; this is the failure mode most worth catching.
2. **Gaps** — which passages carry weight in the book that the index underplays or misses,
   especially anything skipped because it did not fit the framework neatly.
3. **Redundancy** — where several entries make the same connection, and which should merge.
4. **Confidence calibration** — which `high` entries should drop, which `medium` ones are solid.
   Across all books, confidence has predicted flags weakly, so treat the markings as weak evidence.
5. **Stated claims** — where a book file carries a note making an argument about the book rather
   than tagging it, check the claim against the text. These are listed per book below.

## A caution that runs both ways

Practice tags are assigned from the definitions in the brief's table, never from practice names.
Six instances of that error have occurred in this project: four by the drafter, two by the
reviewer, the latter as proposed additions in the 1 John pass. Apply the test to anything you
propose adding as strictly as to anything you propose removing:

> Does the passage prescribe this practice, enact it, or show what its absence costs — or does
> it merely share the practice's subject matter?

---

## Proverbs

- Package: `index/reviews/proverbs-package.md`
- 42 entries, of which 12 are thematic clusters
- Status: chapters 1-9 (pericopes) and 10-29 (clusters); 30-31 pending
- Confidence: high 40, medium 2
- Prior citations (the author's own judgments, the calibration set): Proverbs 1:7, Proverbs 3:5-8, Proverbs 4:10-19, Proverbs 4:20-27
- Author placed — settled, do not propose changes: Proverbs 3:32-35, Proverbs · Pride and the low place

**Claims to check under question 5:**

- *Structural note* — Proverbs 1-9 is continuous instruction — a father to a son, and Wisdom calling in the street — and indexes exactly like James or Jonah. Proverbs 10-29 is roughly 600 free-standing couplets in no narrative or argumentative order. Indexed at the density used for the first two books, that section alone would produce several hundred single-verse entries, most of them near-duplicates, and the index would become longer and less usable than the text it serves. That section needs a cluster entry — one entry gathering non-contiguous verses on a single theme — which the current schema cannot express, since it assumes one contiguous range per entry. That is a real decision about what the index is, not a formatting detail, and it is left open here deliberately.

- *Schema note* — Two entry kinds. A pericope entry has a single contiguous 'ref'. A cluster entry has 'kind':'cluster' and a 'refs' array of non-contiguous verses gathered by theme, used for the aphorism collections where couplets on one subject are scattered across twenty chapters. A cluster claims thematic coverage, not verse coverage: verses not gathered into any cluster are not thereby judged to anchor nothing.

- *Method rule* — Practice tags are assigned from the definition in the Praxis Appendix, never from the practice's name. PR20 means breaking one's routine for a guest — the routine is what is given up — and read from the name alone it appears to mean the opposite.

---

## Song of Solomon

- Package: `index/reviews/song-of-solomon-package.md`
- 10 entries
- Status: complete — selective by design; see coverage_note
- Confidence: high 6, medium 4

**Claims to check under question 5:**

- *Interpretive note* — This book has been read allegorically for most of Christian history — the bride and bridegroom as the soul and God, or the church and Christ. On that reading it would anchor almost the whole curriculum: the search scenes would become the dark night, the mutual belonging would become abiding, the locked garden would become the interior life. The index does not take that route, and the reason is method rather than doctrine. WMT's genealogy nowhere adopts an allegorical hermeneutic, and an index that quietly supplied one would be importing an interpretive commitment the curriculum never made, under cover of tagging. So the book is indexed on its plain sense: love between two people, desired, sought, lost, found, and finally declared unpurchasable. Anyone who wants the allegorical layer should add it deliberately, as its own decision, and record it.

- *Coverage note* — Roughly half the book is not indexed. The wasfs — the extended descriptions of the beloved's body in 4:1-7, 5:10-16, 6:4-10, and 7:1-9 — are the largest omission. They are poetry of desire and admiration, and on a plain reading they anchor nothing in a curriculum of formation. Indexing them would have required either allegory or a stretched tag, and both were declined. The dream-search sequences are indexed once rather than twice, since the second repeats the first with a darker ending. Verses left out are not judged to be of lesser worth; they are judged to have no anchor here.

---

## Jonah

- Package: `index/reviews/jonah-package.md`
- 16 entries
- Status: first pass
- Confidence: high 14, medium 2

**Claims to check under question 5:**

- *Genre note* — Narrative. Pericopes are scenes rather than arguments, and the protagonist is a negative exemplar for most of the book. Entries tagged counter-example are still real anchors: the curriculum uses failure as instruction throughout, and Jonah is the canon's most sustained portrait of a man who holds correct doctrine and refuses the mercy that follows from it.

- *Method rule* — A counter-example entry carries the practice tag whose absence the passage demonstrates. The mode field exists so that a negative anchor can be recorded honestly; leaving practices empty on counter-examples defeats it and hides real anchors.

---

## Matthew

- Package: `index/reviews/matthew-package.md`
- 22 entries
- Status: partial — the Sermon on the Mount (chapters 5-7) only
- Confidence: high 20, medium 2

**Claims to check under question 5:**

- *Synoptic note* — Entries carry an optional synoptic_parallel field recording the corresponding passage in Luke. It is a plain cross-reference: the same material appears in both Gospels, and a reader working through one may want the other. Pericope boundaries follow Matthew's own arrangement, so a parallel sometimes covers only part of an entry. All scripture is WEB, per the standing rule in WMT G10.

---

## John

- Package: `index/reviews/john-package.md`
- 29 entries
- Status: partial — chapters 13-21 only; chapters 1-12 pending
- Confidence: high 29

**Claims to check under question 5:**

- *Prediction note* — The prediction was only half a genuine test. C11 quotes John 1:14 in its own text, so John was always going to close it — that is a foregone conclusion, not a confirmed forecast, and the honest anchor for C11 is John 15 rather than anything predicted. C28 was the real test: it argues for rhythm and continuity over intensity, drawn from the Didache rather than from John, and nothing guaranteed a Johannine anchor. John 21:1-14 supplies one.

---

## James

- Package: `index/reviews/james-package.md`
- 36 entries
- Status: pilot
- Confidence: high 29, medium 7
- Prior citations (the author's own judgments, the calibration set): James 1:13-15, James 1:22-25, James 1:26-27, James 2:12-13, James 2:14-17, James 3:9-12, James 3:17-18
- Author placed — settled, do not propose changes: James 4:1-3, James 4:4-6, James 5:19-20

---

