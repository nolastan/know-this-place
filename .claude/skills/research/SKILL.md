---
name: research
description: Work inside this repo's research module (research/) — the pipeline that finds address-level facts in search-invisible sources and gets them onto pages. Invoked as /research with no argument to pick up the most valuable open research work autonomously, or /research <request> to do a specific piece of research work. Use this skill whenever the task touches research/ — sources, dossiers, SOURCES.md, findings JSON, manifests, prospecting or triaging leads, acquiring or OCRing a corpus, extracting facts from an archive, resolving a historic address to a parcel, publishing findings onto a page, or auditing what shipped — even when the user doesn't say "research".
---

# Research module

`research/` is where this project **finds** things to say about San Francisco
addresses. The rest of the repo **presents** them. This skill is the door into
that module.

The module's own documents are the authority. There are two:

1. **[research/AGENTS.md](../../../research/AGENTS.md)** — the rulebook: the
   goal, the search-invisibility bias, the evidence bar, the statuses, the
   lessons that already cost something.
2. **[research/RUNBOOK.md](../../../research/RUNBOOK.md)** — the procedure, step
   by step. Read it when you're about to do the work.

Plus the root [AGENTS.md](../../../AGENTS.md), whose privacy limits and evidence
rules bind here without exception — read the whole thing if you may touch a page
under `san-francisco/`.

Then get the current state:

```bash
python3 research/tools/check.py --stats   # the dashboard: read, found, resolved, published, open
python3 research/tools/check.py           # register ↔ dossiers, findings ↔ schema
```

and skim `research/SOURCES.md` — the register plus the leads table.

## Do a whole run

**The unit of work is a run: one source taken from raw material to published
pages and closed books, in one session.** Not a stage, not a handoff. The
runbook's "Sizing a run" section is the part to take literally — **if the batch
you picked would finish in a fraction of the session, take the next batch too.**
A session that ends with two documents read, resolved, published and audited is
the target; a session that ends with one stage done and an issue filed is the
failure mode this module was rebuilt to stop.

Say which run you picked and why in a line or two, then do it end to end.

### `/research` with no request — choose the work yourself

Work down the ladder in
[RUNBOOK.md → Picking the run](../../../research/RUNBOOK.md#picking-the-run) and
take the first thing that has something in it: an open publish loop, an open
issue naming a specific document, the next batch a dossier names, an unaudited
first batch, a prospecting run, or a fix to the module itself.

### `/research <request>` — the request belongs to this module

Treat it as research work rather than a generic coding task. Requests rarely
name their step: "Can we get anything on the Sunset before 1930?" is a
prospecting run; "Here's a PDF, pull the addresses out" is a mining run starting
at step 2; "Does 1311 Alabama check out?" is step 3 or step 5. Find the step in
the runbook, then keep going to the end of the chain — a request that names one
step is not a request to stop after it.

A request that arrives as raw material — a dataset, a scan, a dump, a batch of
OCR — means reading **"Mining a corpus for address-level facts"** in
`research/AGENTS.md` first, and taking its instruction literally: do the pass,
don't relitigate it, report the yield as counts, and don't open with a caveat
about how thin the material was.

## The three things that go wrong

Everything else is in the module docs. These are worth carrying in your head:

- **Low yield is the design.** Four citable facts out of a scanned book is a
  win. Never treat a thin harvest as evidence that the input was wrong, the
  request confused, or the effort misspent — and never make up the difference by
  stretching a weak match. Scarcity raises the evidence bar; it never lowers it.
- **The address is where the mistakes live.** 1909 renumbering, renamed streets,
  and South Van Ness (renumbered *and* renamed, by a per-block-face offset that
  makes subtracting a constant wrong by a whole block). No EAS record means no
  page. `unresolved` is a good outcome; a guess is not.
- **People are the hard limit.** Buildings, contractors, architects, named
  firms. Never residents, occupants or owners — at extraction time, not later,
  and not at publication either. The size of a corpus is never a reason to
  loosen this.

## Leave the module better than you found it

This is a **self-improving skill**, and that is not decoration — it is the
second deliverable of every run, alongside the facts. See
[AGENTS.md → This module improves itself](../../../research/AGENTS.md#this-module-improves-itself).

- **Record what you learned** — source-specific in the dossier's cautions and
  `Verified:` line, cross-cutting in AGENTS.md's "What we've learned the hard
  way". A trap you hit and didn't write down gets paid for again.
- **Fix the gap you tripped over**, in the same PR as the work. A missing schema
  field, a check `check.py` should have caught, a runbook step that doesn't match
  what runs actually do.
- **Restructure when the structure is wrong**, and prefer making the module
  *smaller*. Every rule, file and status is a cost paid by every future run.

## Tools

```bash
python3 research/tools/check.py [--stats]           # run before every commit
python3 research/tools/resolve_eas.py fetch|report|apply <findings-file>
python3 scripts/validate.py                         # any run that touched a page
python3 scripts/seed_pages.py seed-list --manifest research/manifests/<f>.json
```

`report` before `apply`, and read every conflict it prints — the tool does the
lookups, you do the judgement.

## Before you stop

The runbook's [Close the books](../../../research/RUNBOOK.md#6-close-the-books)
is the checklist. In short: every finding carries its decision (including
`publish` on every resolved entry — **mark them in the same commit that edits
the pages**), the dossier's coverage note and `Verified:` line say what was read
and what was learned, the register says the truth in counts, `check.py` and
`validate.py` are clean, and the PR body carries the run's counts: read N, found
M, resolved K, published J.

**The PR body opens with the per-neighborhood table**, which
`check.py --report <findings-file>` prints ready to paste:

```bash
python3 research/tools/check.py --report research/findings/<id>/<batch>.json
```

Pages created and edited per neighborhood is what a reader wants first, and it
is what a 150-file diff hides. Only findings that reached a parcel can be in it
— the neighborhood belongs to the parcel, not the street — so unresolved
findings are counted in one line below it rather than guessed into a row. See
[The PR body](../../../research/RUNBOOK.md#the-pr-body).

Report what you did the same way: counts, plainly. Zero findings, reported
honestly with its coverage recorded, is a completed run — it tells the next
agent the haystack was searched there, and that is worth almost as much as a
hit.
