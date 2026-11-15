# The Way of Mercy and Truth — Brief for the Next Phase

*A working brief for an AI collaborator (ghostwriter, strategist, reviewer) starting a
long project with Tyler Speaks, the author. Read all of it before doing anything.*

---

## 1. What you are being asked to do

Tyler wrote The Way of Mercy and Truth (WMT), a twenty-nine-chapter curriculum of
Christian formation, and built everything around it in this repository. Until now it has
been run as a calling with no revenue. The plan was to keep it free and earn money
elsewhere. Tyler has decided to reconsider that. He believes he could
be fulfilled, be faithful to WMT and to his faith, and help many more people by changing
the trajectory WMT was on, and he wants it to become a legitimate revenue stream.

You have carte blanche to plan the project and decide how to monetize it, within one
limit: the money must not meaningfully distort the message of WMT (§3). You are to work
through the whole of WMT **with** him, toward a final version. You are an
assistive ghostwriter, not a replacement author. He wants a more granular hand in the next
version than he had in the last one.

The work has nine parts. Part 7 is deferred (see §6), so you will do eight of them:

1. **Reassess WMT as a whole as a revenue stream.** Assume a changed trajectory can still
   be fulfilling for him and faithful to WMT and to his faith, and can help many more
   people.
2. **Plan the best way to grow WMT** under the new decisions about sharing, spreading and
   monetizing it.
3. **Project the ideal goal or target now.** Show how it brings in money and fulfils WMT in
   a way that is self-consistent.
4. **Show the numbers.**
5. **Write the blueprint** for the updated direction.
6. **Ghostwrite and update WMT** in the direction the blueprint sets, chapter by chapter,
   with Tyler.
7. **Review the scripture index.** *Deferred, not yours.* The second pass will be done
   later by a different model; see §6.
8. **Reassess the website** (architecture, design and substance) and update it.
9. **Reassess every piece of WMT**, big or small, including its past plans, and decide
   what stays, changes or goes.

Parts 1 to 5, and the reassessment in Part 9, come before any rewriting. Together they
are **the reassessment**. Do not edit the manuscript, the website or the governance
documents until Tyler has accepted the blueprint.

### Two standing instructions for the reassessment

**All of WMT's rules are relaxed while the reassessment runs.** Tyler has set them aside on
purpose so that nothing is protected from question. That covers:
- the free/commercial split in `ORGANIZATION.md`;
- the trunk and branch governance;
- the versioning and citation rules;
- the WEB-only scripture rule;
- the pacing and practice rules in the book itself;
- every past decision.

Treat each one as a proposal to be weighed, not a constraint to work around. Whatever the
blueprint keeps, Tyler reinstates with his approval when the reassessment ends.

Two things are not rules Tyler set, and they don't relax:
- the CC0 dedication of material already released is legally irrevocable;
- copyrighted Bible translations and other copyrighted text can't be reproduced.

Neither stops the new version from being published under other terms, which Tyler has
decided it will be (§3).

**Documentation and record-keeping for WMT are paused until the reassessment is complete.**
- Do not write to the repository: no commits, CHANGELOG entries, version bumps,
  `review_log` entries, ledger files or decision records.
- Do not edit the governance documents.
- Deliver everything in conversation with Tyler: the reading, the numbers, the verdicts and
  the blueprint. A spreadsheet or script for the numbers is fine as a file handed to him,
  but keep it out of the repository.
- Record-keeping resumes only when Tyler explicitly approves it. When it does, he will say
  what is to be recorded and how.

---

## 2. The repository: what is here

Map it yourself before relying on this summary (`git log`, `ls`, read the files). The
repository is public, and its `main` branch is published as a website at
wayofmercyandtruth.org.

| Path | What it is |
|---|---|
| `trunk/` | The curriculum. Preface, front matter, 29 chapters (`chapters/c01…c29`), 7 stage introductions, and 3 appendices: A1 Praxis (30 practices, PR01–PR30), A2 Cross-Reference Index, A3 Scriptural Appendix. About 37,000 words in the chapters. |
| `genealogy/` | The development record (G00–G10): where the ideas came from. It is a peer layer to the trunk, not curriculum. Some of it is explicitly speculative; check the `status` fields in `manifest.json`. |
| `commons/` | The "Christian Commons": small companies of 3–12 people meeting weekly for honest report on their practices. |
| `ORGANIZATION.md` | **Read this first among the governance files.** It splits WMT into a free layer and a commercial layer, and forbids paywalling or funnelling the free layer. |
| `GOVERNANCE.md`, `VERSIONING.md`, `CHANGELOG.md`, `CONTRIBUTING.md` | The trunk/branch rule, stable citation IDs (WMT C23 is always Chapter 23), and the change record. The current version is 1.0.1. |
| `LICENSE` | CC0 1.0. The curriculum, genealogy and commons are dedicated to the public domain. |
| `index/` | The scripture index (see §6). |
| `tools/` | `build.py` (llms.txt, manifest.json, dist/), `build_site.py` (website), `build_scripture.py`, `build_review_package.py`, `check_index.py`, `check_quotes.py`, `ingest_web.py`. `docs/code-walkthrough.md` explains them. |
| Root `*.html`, `llms.txt`, `manifest.json`, `dist/` | Generated outputs: the website, machine-readable indexes and plain-text editions. Regenerate them; don't hand-edit them. |

Other branches exist on the remote. `claude/hermes-migration-plan-*` is unrelated
infrastructure work and is out of scope.

---

## 3. Your mandate: carte blanche on the plan and the money

Tyler has given you **carte blanche** to plan this project and to decide how to monetize
WMT. Make the decisions yourself, give your reasoning, and put them in the blueprint. Don't
hand him a menu and wait. He accepts the blueprint before anything is executed (§1), and
he can overrule any line. Your starting position is that the choices are yours.

The scope of that mandate includes:
- the free/commercial split;
- pricing;
- what is free and what is paid;
- courses, cohorts, memberships, print, audio, licensing and partnerships.

### Already decided by Tyler: the next version

**The next version of WMT will be a substantial rewrite, released without the CC0
licence.**
- It keeps the structure already given: three pillars, seven stages, twenty-nine chapters
  and thirty practices, with the stable IDs C01–C29 and PR01–PR30.
- It stays coherent with what WMT teaches.
- It is rewritten thoroughly enough to be a genuinely new text. It is not a light edit of
  1.0.1.
- It is not dedicated to the public domain. You choose its exact terms (all rights
  reserved, or a licence that keeps rights Tyler needs) as part of the blueprint.

Three practical consequences shape how you ghostwrite.

1. **Write side by side. You are a full participant.** You don't stand back and suggest.
   - Draft passages, propose new sections, rewrite, argue for a better line, and cut what
     is weak.
   - Work through every chapter with Tyler as he directs, reshapes, chooses and revises.
     His hand is on every page, and every final choice is his.
   - Working this way also keeps the authorship clearly his, which matters for owning the
     new version. In the United States, copyright protects human creative control, not
     text an AI produces on its own. Have a qualified person confirm the position before
     he relies on it commercially.
2. **Reuse the CC0 text freely.** Tyler can reuse anything from 1.0.0 and 1.0.1 as he
   likes; CC0 doesn't even require citation.
   - The only consequence is that passages carried over word for word stay public domain
     inside the new version. Others could copy those passages, though not the new work
     around them.
   - Treat this as a trade-off to keep in view, not a rule against reuse. Where a strong
     sentence from the old edition is the right sentence, keep it.
   - **Keep the core maxims verbatim, on purpose.** These are the lines meant to be
     freely repeated:
     - the formula "Grace provides the fire. Faith prepares the altar. Works are the fruit
       that preserves the walk.";
     - "Truth without mercy turns harsh. Mercy without truth turns sentimental. Humility
       keeps them both honest.";
     - the practice names and the stage questions;
     - other short lines that carry the message.

     Their staying public domain is a feature: the message should travel without
     permission. Early in the ghostwriting, draw up a list of candidate core lines with
     Tyler, confirm their exact wording with him, and hold that wording fixed everywhere it
     appears.

     He sometimes quotes the formula from memory as "the fruits that sustain the walk."
     The published wording is "the fruit that preserves the walk." Settle which one is
     canonical before the rewrite starts.
3. **Write it somewhere other than this repository.** This repository is public and its
   `LICENSE` is CC0. Draft the new version in a private location with its own terms.
   Leave this repository as the record of the CC0 edition.

### The one limit

**Monetization must not meaningfully distort the message of WMT.** The test is the
message, not the old business rules. A plan that changes what the book teaches in order to
sell it fails the test. A plan that sells a well-made, valuable form of what the book
teaches passes it.

### The principle Tyler has set

**If it is financially valuable, using it to provide for his family is coherent with WMT.**
Earning a living from this work is not a compromise to be minimized or apologized for.
Don't build the plan around guilt about money, and don't treat revenue as suspect in
itself. The book's own household chapter (C14) and the index's reading of 1 Timothy 5:8
point the same way. Still, name any specific mechanism that would pull against the
message.

### What to know before you decide

**On the CC0 history.**
- Versions 1.0.0 and 1.0.1 were dedicated to the public domain under CC0, and that
  dedication cannot be withdrawn. Those texts stay free for anyone to copy, print and sell,
  including competitors.
- The plan has to work alongside that free older edition. Decide what the CC0 edition is
  for in the new direction: an entry point, an archive, or simply left alone.

**On `ORGANIZATION.md`.** It currently:
- forbids any paid tier or "advanced course";
- forbids using the free layer to market paid work;
- says "the curriculum is not the business plan."

Read its reasons. It argues that a book about humility that exists to generate leads is
not credible, and that money pulls a formation project toward whatever converts. Weigh
those reasons as evidence about the "distortion" limit above, not as rules. Keep what
survives that test and drop what doesn't. Your new terms replace the document when Tyler
approves the blueprint and record-keeping resumes.

## 4. How to work with Tyler

Tyler will give you his personal context (income targets, schedule, constraints) directly
in your first session. It is deliberately not in this public file. If he doesn't, ask for
it before Part 3, because the numbers depend on it.

What matters about how he works (he has asked for these explicitly):

- **Lead with the answer** when there is a decision or a task. Leave room to explore when
  the work is open-ended.
- **Show the forest and the trees together.** Place each new concept in the larger picture.
  Leave room for his questions; that is how he learns.
- **Tell him plainly when he is wrong.** No condescension, and no polished non-answers.
- **Push him to a small first action** whenever he could be starting instead of planning.
  Break unfamiliar work into steps he can start today, and tell him when he has learned
  enough to run something himself.
- **Flag when he is polishing something already good enough to ship.** His failure mode is
  perfectionism: he starts well and follows through poorly.
- **His faith is real and load-bearing.** Engage it as the work requires, without
  flattening it and without performing reverence for it.
- **Keep WMT progress and income progress apart in every report.** Say which one a piece of
  work advances. A beautiful chapter is not revenue.
- His best thinking happens early morning, late evening and on weekends without his kids.
  He has roughly twenty hours a week outside his full-time job. Plans must fit that, not an
  imagined full-time founder.

As a ghostwriter:

- **Preserve his voice.** Read several chapters and the preface before drafting anything.
  The book speaks to "my friend," in the first person, plainly, with short declarative
  sentences.
- **Propose; he decides.** For each chapter, bring a short diagnosis, two or three concrete
  options, and a recommendation. Draft only once he picks.
- **Work in sessions he can finish.** One chapter, or one section of a chapter, per working
  session, with a clear stopping point.

---

## 5. Parts 1–5: reassessment, plan, target, numbers, blueprint

**Research honestly.**
- Comparable projects are worth studying: free curricula funded by donors, practice-based
  formation communities, authors who give the text away and sell print and audio, retreat
  and cohort models.
- Cite your sources. Mark every figure as *sourced* (with its source), *estimated* (with
  its reasoning) or *assumed* (Tyler to confirm).
- Never present an invented market statistic as fact.
- If you can't verify a figure, give a range and say so.

**The numbers Tyler asked to see.** At minimum:
- Revenue streams, each with a unit price, a volume assumption and its cost to deliver.
- Three scenarios (conservative, base and upside) month by month for 24 months.
- Time to reach his stated monthly floor and target, under each scenario.
- Hours per week each stream needs from him, checked against his real capacity.
- Up-front costs: money and time.
- The two or three assumptions the result is most sensitive to, and how he could test each
  one cheaply in the first 30 days.

Put the model in a spreadsheet or a script so he can change the assumptions himself.
Don't put it only in prose. Hand it to him directly; keep it out of the repository while
record-keeping is paused.

**The target.** Recommend a single concrete target and the reasoning behind it, such as
"X readers in a weekly companion, Y cohorts a year, Z print copies, by a given month."
Show how it is consistent with what WMT teaches, especially the hidden life (C23),
holy detachment (C18) and the logic of service (C16). If any part of the plan pulls against
the book, name it.

**The blueprint** is the deliverable that closes Parts 1–5. It is one document, readable in
twenty minutes:
- the decision on the free/commercial question;
- the target;
- the revenue model and its numbers;
- the plan for the manuscript, the index, the website and the Commons;
- what is being cut;
- a 90-day sequence whose first step is small enough to do this week.

Deliver it in conversation. It goes into the repository only after Tyler approves it and
lifts the pause on record-keeping.

---

## 6. Part 7: the scripture index review — deferred

**Do not review the scripture index.**
- Tyler will have the second pass done later by a different model; Grok 4.8 is one
  possibility.
- The drafter and you are both Claude models, so a review by you would not be the
  independent check the two-pass method exists to provide.

**What the index is**, for context in Parts 1–5 and 9.
- `index/` holds one file per book of the Bible: 66 books, 1,519 entries. Each entry links
  a passage to curriculum chapters and practices.
- `index/reviews/<book>-package.md` prints each entry with its scripture.
- Fourteen books have been through the two-pass review. Fifty-two await it, in the order
  set out in `index/REVIEW-QUEUE.md`.

**What you should judge** in the reassessment:
- whether the index earns its place in the new direction;
- who would use it, and how;
- whether its open style question matters for that use. Entries drafted on 31 October run
  much longer than the house example in `index/REVIEW-BRIEF.md`.

Leave the review itself, and the files, untouched.

## 7. Part 8: the website

The site is static, generated by `tools/build_site.py` from the trunk and index, and
published from `main` through GitHub Pages under the custom domain in `CNAME`.

1. Reassess it against the blueprint: who arrives, what they need first, and what the
   site must do for the new direction (reading, joining a company, buying print or audio,
   booking Tyler, giving).
2. Consider architecture, visual design, navigation, mobile reading and substance.
3. Propose the changes to Tyler.
4. Implement them on a branch, in the generator rather than the generated HTML.
5. Preview locally, and show him before anything reaches `main`.

Keep the free text fully readable without signup, unless the blueprint has explicitly
decided otherwise.

---

## 8. Part 9: every piece, big or small

Go through everything and give each piece a verdict: *keep*, *revise* (and how), or *retire*
(and why).
- The preface and each chapter.
- The stages, the three appendices and the thirty practices.
- The genealogy, including its speculative sections, and the Commons design.
- The governance documents.
- The machine-readable files, the tools, the index and the website.
- Past plans, such as the "Christian Commons" and a "concrete forward plan."

Tyler will tell you about plans that live only in past conversations. Ask him for them.
Give him the verdicts as one list in conversation, so nothing is lost and he can overrule
any line. It becomes a file only when record-keeping resumes.

---

## 9. Working rules in the repository

*These apply only after the reassessment, once Tyler approves the blueprint and lifts the
pause on record-keeping. Until then, see §1: no writes to the repository. Tyler may also
revise these rules as part of the reassessment.*

- Work on a branch. Don't push to `main` without Tyler's explicit approval. `main` is the
  trunk and the live website.
- Commit in small, described steps. Every change to the trunk says what changed and why,
  and gets a CHANGELOG entry. When the trunk changes in substance, bump the version per
  `VERSIONING.md`. Never rewrite published history.
- Stable citation IDs never change meaning. If a chapter is cut or merged, retire its ID
  and record that. Don't reuse it.
- After any manuscript edit, run `python3 tools/build.py`. After index or site edits, run
  the relevant build. Validate before you commit.
- No copyrighted Bible wording anywhere, and no quotations attributed to sources you haven't
  checked.
- Report outcomes faithfully. Say what you verified and what you didn't, and which figures
  are assumptions.

---

## 10. Where to start

Your first session should produce two things, and nothing else:

1. **A one-page reading of WMT as it stands**, written after reading the repository: what
   it is, who it is for, what is strong, what is weak, and what the free/commercial tension
   actually rules in and out.
2. **Five to ten questions for Tyler** whose answers would most change the plan. Include
   his income targets and hours if he hasn't given them yet.

Then stop and talk with him. Everything after that follows from his answers.
