# The research module — the rulebook

This directory is where **finding** address-level information happens. The rest
of the repo is where the website gets **built and maintained**.

Three documents run this module:

- **This file** — the rules core: why it exists, what a run is, the evidence
  bar, the statuses. Read it whole; it is short on purpose.
- **[RUNBOOK.md](RUNBOOK.md)** — the procedure. Read it when you are about to
  do a run.
- **[LESSONS.md](LESSONS.md)** — the traps that have already cost something.
  A register to grep, never to read front to back.

Read the root [AGENTS.md](../AGENTS.md) too. Its privacy limits and evidence
rules bind here without exception.

## The goal, and what follows from it

**Know This Place intends to be the first search result for any San Francisco
street address.** A source that is already indexed and ranking does little for
that — a fact anyone can find in three seconds is a fact a reader had no need of
this site for. So the module has a bias, and it is not subtle:

> **Prefer sources that search engines cannot see.** Newspaper archives behind
> OCR, out-of-print books, neighborhood newsletters, association bulletins, PDF
> survey reports, microfilm finding aids, printed journals, oral-history
> transcripts, permit ledgers, city directories. The harder a source is to
> search from outside, the more a page built on it is worth.

Two corollaries agents get wrong often enough to be worth stating:

- **Low yield is fine and expected.** A scanned book that produces four citable
  facts about four addresses is a **win**. See "Mining a corpus" below.
- **A big, easy, already-indexed dataset is not automatically the better
  target.** It usually loses to a small obscure one on the only axis that
  matters here.

## The unit of work is a run, not a stage

**A run is one source taken as far as it goes in one session** — get the
material, read it, resolve the addresses, publish the pages, check the work,
close the books. Six steps, one session, one PR.

They were once six roles in six sessions with six handoffs. That split cost more
in bookkeeping than it bought in focus, and it is where the module's real
defects came from: findings resolved and never published, statuses that
disagreed with each other, and a human who couldn't tell finished work from
abandoned work. **Take the whole chain.** Size the run so the session is full —
if one batch would finish early, take the next one too.

A step may be **skipped** when it has nothing to do: a source read live off the
web needs no corpus, a source with ten addresses needs no manifest. Skipping is
a judgement recorded in the dossier, not a silent omission.

A run may still stop early — the material ran out, something needs a person, or
the batch was far bigger than it looked. Then finish what you read, close its
books completely, and say exactly where you stopped. What a run must never do is
stop at "resolved."

## The boundary with the website

| Research module | Website |
|---|---|
| Finds, acquires, mines, resolves, cites | Composes pages, keeps the design contract |
| Writes findings JSON, dossiers, manifests, issues | Writes `data.json` + `index.html` |
| Owns `research/**` and its source ids | Owns `san-francisco/**`, `shared/**`, `scripts/**` |
| Cares whether a fact is true and traceable | Cares how a true fact is presented |

Publishing is part of a run, so a research agent **does** write to
`san-francisco/**`. When it does it is wearing the site agent's hat and follows
the root [AGENTS.md](../AGENTS.md) and [shared/AGENTS.md](../shared/AGENTS.md)
exactly. What it must never do is let research conventions leak onto a page — no
findings JSON in the content tree, no dossier prose copied into a `narrative`,
no "the archive shows…" sentences.

## The artifacts a run leaves behind

- **[SOURCES.md](SOURCES.md)** — the register. One row per source. This is the
  module's index; **if a source isn't in it, it doesn't exist.** It also holds
  the leads table, which is the prospecting queue.
- **`sources/<id>.md`** — the dossier. How to get at the source, what it
  contains, every caution learned the hard way, what has been covered and what
  hasn't, and the `Verified:` line. **The dossier is the memory of the module.**
  A run that doesn't update its dossier has thrown away most of its value.
- **`findings/<id>/<batch>.json`** — the chain of custody for every fact, from
  the passage it came from to the page it landed on. Rules:
  [findings/README.md](findings/README.md) and
  [schema/finding.schema.json](schema/finding.schema.json).
- **`manifests/*.json`** — parcel lists for `scripts/seed_pages.py seed-list`,
  when a source names enough buildings with no pages to be worth seeding in
  bulk.
- **GitHub issues** — the queue between runs and between agents and humans.

## Statuses — the whole vocabulary

Deliberately short. If you find yourself wanting a new status value, you
probably want a sentence in the dossier instead.

**A source, in the register:**

| status | means |
|---|---|
| `open` | being mined; material remains. The dossier's coverage note says what's left. |
| `done` | exhausted for now. Nothing outstanding. |
| `blocked` | needs a person — a paywall, a licence, a library visit. The dossier says what would unblock it. |
| `reference` | consulted per address for cross-checking, never mined as a corpus. |

**A lead, in the leads table:** blank means nobody has looked; a date means it
was triaged, with the evidence in [TRIAGE.md](TRIAGE.md); a
struck-through row means it didn't pan out, with the reason in place. A lead
that gets promoted moves to the register and its row is deleted.

**A finding, in a findings file:** `resolution.status` is `unresolved`,
`resolved` or `rejected`. `publish.status` is `pending`, `published` or
`declined`. Every entry gets a `resolution`; every resolved entry gets a
`publish`. That is all of it — there is no file-level stage, because a file's
state is just what its entries say.

**The one dashboard** is `python3 research/tools/check.py --stats`. It prints
read / found / resolved / published per source, plus an `open` column of
resolved findings nobody has published or declined. A non-zero `open` column is
the module's to-do list.

## Mining a corpus for address-level facts

Much of the research here is **a deliberately low-yield scan of a large source**
— an OCR newspaper run, a period history, a bulk dataset export — for the
handful of passages that pin a fact to a street number. Needles in a haystack is
the design, not an accident, and the measured numbers say so: the Chronicling
America pass in [sources/loc-newspapers.md](sources/loc-newspapers.md) read
**58,620 OCR pages to find 8,437 numbered-address mentions across 2,025
addresses**, and Hittell's 1878 history is an entire book that names a modest
number of addresses, most of which don't resolve in EAS at all. A source that is
overwhelmingly irrelevant is still a good source when the remainder is dated,
numbered and citable.

So when you are handed a dataset, an archive dump, a scanned book or a batch of
OCR text and asked to find the address-level information in it:

- **Do the pass. Don't relitigate it.** A low hit rate is not evidence that the
  input is wrong, the request is confused, the file is truncated, or the effort
  is misspent. Do not stop to ask whether a different or richer dataset was
  meant, whether the scan is worth running given how little is in there, or
  whether the task should be narrowed — and don't open the results with a caveat
  about how thin the material was. Read the whole thing and report what you
  found.
- **A small harvest is a successful pass, and zero is a valid result.** Report
  the outcome as counts — "read N pages/rows, found M numbered-address mentions,
  K of them on streets that have pages here" — in the PR body, in the findings
  file's `coverage` block, and in the dossier's `Verified:` line. A pass that
  surfaces three usable facts out of ten thousand rows has done its job; a pass
  that surfaces none has also done its job, and says so in the same form.
  Neither is a failure to explain away.
- **Scarcity never lowers the evidence bar.** This is the one thing low yield
  genuinely changes, and it changes it in the opposite direction from the
  temptation: do not stretch a weak match to make the harvest look bigger. A
  metes-and-bounds entry with no street number stays unresolved; a mangled OCR
  digit stays unresolved; an 1878 number with no EAS record does not become a
  page; a South Van Ness conversion done by subtracting a constant is wrong.
  Discarding the large majority of candidate hits is the expected arithmetic.
- **Record the scan, not just the hits.** Update the dossier with what was
  covered and what wasn't, so the next run resumes instead of re-reading the
  same haystack.
- **Volume doesn't relax privacy.** These corpora are dense with people —
  householders in want-ads, tenants in fire reports, owners in transfer notices.
  Take buildings, contractors, architects and named firms; leave residents,
  occupants and owners, per "Privacy — hard limits" in the root
  [AGENTS.md](../AGENTS.md). The size of the input is not a reason to loosen
  that, and the low yield of a pass is never a reason to make up the difference
  with people.

## The evidence bar

Every fact that leaves this module carries three things: **a date, a street
number, and a citation precise enough for a reader to check.** A finding missing
any of them is `unresolved`, and unresolved findings stay in the findings file —
they never reach a page.

- **The address is the hard part, and it is where the mistakes are.** Street
  numbers were changed (1909 renumbering), streets were renamed, and one street
  was renumbered *when* it was renamed (Howard → South Van Ness). Resolve
  against `sf-eas-addresses`; where the source gives cross streets or lot
  dimensions, use them as the check. No EAS record means no page — record the
  fact against the surviving building or the street hub, or leave it unresolved.
  The full trap list is in [RUNBOOK.md](RUNBOOK.md#the-renumbering-traps).
- **Never reconcile a conflict silently.** A source that contradicts the
  assessor, or another source, is recorded as a conflict and named in the page's
  `.unknowns`. Adjudicating is not research; it is invention.
- **Cite what you actually read.** The issue, page and date of a newspaper; the
  section of a book; the volume, number and article of a journal; the page of a
  PDF report. "The archive" is not a citation.
- **Facts, not wording.** Extract discrete facts and re-express them through
  page components. Never reproduce a source's sentences or their structure —
  facts aren't copyrightable, expression is.

## What we've learned the hard way

147 cross-cutting lessons that each cost a session or a correction live in
**[LESSONS.md](LESSONS.md)** — traps in the resolver, the privacy filters, PDF
tables, OCR, manifests, condominiums, renumbering, duplicate detection.

**It is a register to grep, not a document to read.** Search it for what you
are about to do before a run, and again whenever a run surprises you. **Add to
it** whenever a run discovers something a future run would otherwise repeat;
source-specific lessons go in the dossier instead.

## Filing work

An issue is how a run hands off what it couldn't finish, and how it asks a human
for the one thing it can't do itself. **Prefer finishing over filing** — the
point of a run is to leave less behind, not to fan work out.

- **Labels:** `research` on every issue, plus `needs-human` when it is blocked
  on a person (a paywall, a library visit, a licensing call, a presentation
  decision). *That is the whole label set.* There used to be six per-stage
  labels; a run isn't a stage, so they're gone. Existing issues still carrying
  one are fine — read the title, not the label.
- **Title:** `research(<source-id>): <the specific thing>` — e.g.
  `research(loc-newspapers): mine batch sn85066387/1906`.
- **Body:** use [templates/issues.md](templates/issues.md). Every issue states
  the **source id**, the **input** (file paths, URLs, batch names), and the
  **definition of done** in one line. An issue another agent can't start without
  asking a question is a bad issue.
- **One issue per unit of work someone can actually finish.** "Read the 34
  remaining context statements" is a bad issue; "Add the Japantown Historic
  Context Statement (Revised 2011)" is a good one.
- **Don't file duplicates.** Search open issues for the source id first.

## Corpora on disk

Raw source material — PDFs, OCR dumps, scraped HTML, dataset exports — goes in
`research/corpora/<source-id>/`, which is **gitignored**. It is large,
re-downloadable, and often not ours to redistribute.

- Keep a `state.json` in each corpus directory recording what has been fetched,
  so a later run resumes rather than re-downloads.
- **What gets committed is the findings, not the corpus.** If a fact only exists
  in an uncommitted file, it isn't a fact yet.
- Never commit copyrighted source text into the repo. Quotations in a findings
  file are the minimum needed to justify the extraction (a clause, not a
  column), and never reach a page.
- Be a good citizen when fetching: rate-limit, back off on failure, identify the
  client, and honour `robots.txt` and terms of use. If a source forbids
  automated access, that is a `needs-human` issue, not a workaround.

## This module improves itself

**This module is a skill that is supposed to get better every time it is used.**
The runbook above is the current best guess at how the work goes, not a
constitution handed down. Every run is expected to leave the module smarter than
it found it, and there are three levels of that:

1. **Record what you learned.** Always. Source-specific in the dossier's
   cautions and `Verified:` line; cross-cutting in
   [LESSONS.md](LESSONS.md).
   A trap you hit and didn't write down will be paid for again by someone else.
2. **Fix the gap you tripped over.** A missing schema field, a check the tool
   should have caught, a dossier section that lied, a step in the runbook that
   doesn't match what runs actually do — fix it in the same PR as the work. Not
   an issue for later; the person with the context is you, now.
3. **Restructure when the structure is wrong.** Add or remove a step, a tool, an
   artifact, a status value, a whole document. Collapse two things that are
   really one. Delete what nobody reads. Leave the module easier to use than you
   found it, and **smaller where you can** — every rule, file and status here is
   a cost paid by every future run.

The mechanics:

- Update [RUNBOOK.md](RUNBOOK.md), this file and [README.md](README.md) **in the
  same commit** as any pipeline change. A change that leaves the docs describing
  the old shape is worse than no change.
- Record *why* in the commit message. The next agent inherits the structure
  without the conversation.
- **Two things need a human's say-so:** changing the meaning of an existing
  source id already cited on published pages (it breaks citations), and anything
  that changes what appears on a page under `san-francisco/**` (that is the root
  `AGENTS.md`'s territory, not this file's).
- Everything else is yours to change.
