---
id: "WMT G10"
title: "Editions Consulted"
kind: genealogy
status: partial
status_note: "Two entries still open — Pseudo-Clementines and Barnabas base translations unconfirmed"
---

# Editions Consulted

This section records which translations and editions the material in `trunk/` was
actually built from. It exists for three reasons, in ascending order of importance.

The first is practical. A reader who wants to check a claim needs to know where to
look. Naming the edition is the difference between a reference and a gesture.

The second is legal hygiene. The curriculum is released CC0, which is a claim that
every word in it is free to take. That claim has to be true, and it is only
demonstrably true if the sourcing is visible. It is.

The third is the one that matters. This project holds that what it teaches was
entrusted to it — by the biblical authors, by the ancient writers, and by the
translators without whom none of those writers would be legible to a modern reader
at all. Translators are the least visible link in that chain and the easiest to
omit. Recording them is not a legal formality. It is the same stewardship the
curriculum asks of its readers, applied to the curriculum's own debts.

## Scripture

All biblical quotation in `trunk/` is from the **World English Bible (WEB)**, a
modern English translation placed in the public domain by its producers.

This is a deliberate choice, not a convenience. Most modern English translations are
under copyright, and quoting one at length would have made a CC0 release either
false or impossible. The WEB was translated precisely so that work like this could be
built on it and given away. Choosing it is the reason the curriculum can be handed on
without conditions.

## Direct quotation

The **Didache** is the only non-scriptural source quoted directly anywhere in the
curriculum. Two passages appear in *WMT C05, The Apprenticeship*: the sharing
instruction from Didache 4, and a single word from the vice list in Didache 2.

Both are quoted in archaic English and trace to the **Roberts–Donaldson translation,
*Ante-Nicene Fathers*, Vol. 7 (1885)** — long in the public domain.

A note on how that text was reached. The working document was Dr. James D. Tabor's
adapted edition of the Didache, which he makes freely available and which is built on
the Roberts–Donaldson base. Tabor's adaptation modernizes the English of both passages;
the curriculum quotes the older wording, so what appears in *WMT C05* is the 1885 text
rather than his revision. His document is nonetheless how this project found the
Didache, and the debt is real.

## Paraphrase

Everywhere else, ancient sources are paraphrased rather than quoted — summarized in
the curriculum's own voice, with the source named. This is a matter of pedagogy first:
the curriculum is a road, not an anthology, and a paraphrase that lands is worth more
to a reader than a rendering that is technically exact and inert.

It also means the curriculum reproduces no translator's protected wording. Ideas are
not owned; a particular English rendering of them is. The list below records the
editions consulted regardless, because the point of this section is the debt, not the
liability.

### Public-domain editions

These are nineteenth-century translations, long out of copyright. Material from them
could be quoted directly if a future revision wanted to, though the curriculum
currently paraphrases them like everything else.

| Source | Edition consulted |
|---|---|
| Didache | Roberts–Donaldson, *Ante-Nicene Fathers* Vol. 7, 1885 — reached via Tabor's freely distributed adaptation |
| The Shepherd of Hermas | Roberts–Donaldson, *Ante-Nicene Fathers* |
| Theophilus of Antioch | Roberts–Donaldson, *Ante-Nicene Fathers* |
| Aphrahat, *Demonstrations* | Schaff, *Nicene and Post-Nicene Fathers*, Series 2 |
| Ephrem the Syrian | *Nicene and Post-Nicene Fathers*, via the Christian Classics Ethereal Library |
| John Cassian | *Nicene and Post-Nicene Fathers*, via the Christian Classics Ethereal Library |

Aphrahat and Ephrem come from the same NPNF volume, reached by two different routes —
one through the printed Schaff series, one through CCEL's edition of it. They are the
same underlying text.

### Editions under copyright

These are modern scholarly translations, most of Syriac or monastic material that has
no nineteenth-century English equivalent. Without this work these sources would have
been inaccessible to this project entirely.

| Source | Edition consulted |
|---|---|
| Dorotheos of Gaza | Eric P. Wheeler, *Discourses and Sayings*, Cistercian Publications, 1977 |
| Isaac of Nineveh | Sebastian Brock |
| The Book of Steps (*Liber Graduum*) | Robert A. Kitchen |
| Pseudo-Macarius (the Macarian Homilies) | George A. Maloney |
| Desert Fathers (*Apophthegmata Patrum*) | Benedicta Ward |

**Nothing from these editions is quoted anywhere in `trunk/`.** For this group the
paraphrase discipline is not a stylistic preference — it is the thing that keeps the
CC0 release truthful. A future revision may quote freely from the public-domain group
above. It may not quote from this one without either securing permission or switching
to a public-domain edition, and there may not be one.

### Still to confirm

| Source | Edition consulted |
|---|---|
| The Pseudo-Clementines | Tabor, *Specific Texts of the Pseudo-Clementines* — freely distributed; underlying base translation not yet identified |
| Epistle of Barnabas | A House of Israel / Firmament edition — needs checking against its underlying base translation |

Both of these were reached through community or ministry editions rather than a named
scholarly one. Such editions are almost always built on a public-domain base — usually
Roberts–Donaldson or Lightfoot for Barnabas — but "almost always" is not a record.
These two entries stay open until the base translation is confirmed by name.

## A note of thanks

A substantial part of the Layer 2 material reached this project through study
documents that **Dr. James D. Tabor** prepares and distributes freely: the Didache,
the Pseudo-Clementine texts, the Delitzsch Hebrew James, and a Q reconstruction
arranged from Luke. These are not commercial publications. They are made available for
the benefit of anyone who wants to read the sources, which is the same instinct that
produced this curriculum and the reason it is given away.

The debt is acknowledged with gratitude and without any claim of endorsement. Nothing
here should be read as implying that Dr. Tabor has reviewed, approved, or is
associated with the Way of Mercy and Truth.

## A standing caution for future work

Two of the freely distributed documents named above present their English text from
the **Revised Standard Version** — the Q arrangement, and the English facing column of
the Delitzsch Hebrew James. The RSV is under copyright.

Those documents were used for study, and no English wording from either appears in
`trunk/`. But the risk is live rather than historical, and it will present itself
specifically in the scriptural cross-reference work: when a passage is close at hand in
a study document, the path of least resistance is to quote what is in front of you.

The rule for all future additions is therefore simple and admits no exception:

- **Scripture is quoted from the WEB, and from nothing else.**
- **Patristic material is paraphrased**, or quoted only from an edition confirmed to be
  in the public domain.
- **Any new source is recorded in the table above before its material enters `trunk/`.**

The first two rules protect the CC0 release. The third protects this section from
becoming what it was written to correct.
