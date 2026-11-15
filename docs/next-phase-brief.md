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

You are to work through the whole of WMT **with** him, toward a final version. You are an
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

## 3. The central tension: settle it with Tyler, don't assume it away

Two facts shape every revenue idea. The first is legal; the second is one of Tyler's own
rules, relaxed for the reassessment but still worth understanding. Present both plainly in
Part 1, before any plan:

**CC0 is irrevocable.** Anyone may already copy, print, sell, adapt or train on everything
released. No plan can rely on exclusive rights to text that has already been published.
Revenue has to come from what CC0 doesn't give away: Tyler's time, judgment, voice and
presence; manufactured objects (print, audio); services; community; and new work not yet
released, if he chooses to release future work under different terms.

**`ORGANIZATION.md` currently forbids what some monetization models need.** It rules out
any "advanced course" or members-only tier, and any use of the free layer as marketing for
the paid layer. It says "the curriculum is not the business plan." Its reasons are serious:
a book about humility that exists to generate leads is not credible, and money drifts a
formation project toward whatever converts.

Tyler's new direction may keep that split and build revenue alongside it, revise it, or
replace it. That is his decision. Your job:

- Lay out the real options. These include at least the following, each with its
  trade-offs and its consistency with what WMT teaches:
  - keep the split and monetize only the commercial layer it already permits;
  - donor or patron support for free work;
  - paid cohorts, facilitation or retreats that sell time, not access;
  - new non-CC0 works;
  - revising the split.
- Recommend one, with your reasons.
- Whatever he decides is recorded later, when the pause on record-keeping lifts.

Do not treat the old rule as a mistake to be overcome, and do not treat it as untouchable
either.

---

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
