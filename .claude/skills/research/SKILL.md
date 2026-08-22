---
name: research
description: Work inside this repo's research module (research/) — the pipeline that finds address-level facts in search-invisible sources and gets them onto pages. Invoked as /research with no argument to pick up the most valuable open research work autonomously, or /research <request> to do a specific piece of research work. Use this skill whenever the task touches research/ — sources, dossiers, SOURCES.md, findings JSON, manifests, prospecting or triaging leads, acquiring or OCRing a corpus, extracting facts from an archive, resolving a historic address to a parcel, publishing findings onto a page, or auditing what shipped — even when the user doesn't say "research".
---

# Research module

`research/` is where this project **finds** things to say about San Francisco
addresses. The rest of the repo **presents** them. This skill is the door into
that module: it tells you how to orient, how to pick work, and how to leave the
module in a state the next session can resume from.

The module's own documents are the authority. This file never restates their
rules — it points at them, and adds only what a session needs to start and stop
well.

## Orient first, always

Read these before touching anything, in this order:

1. **[research/AGENTS.md](../../../research/AGENTS.md)** — the rulebook. The
   goal, the search-invisibility bias, the six-stage pipeline, the evidence bar,
   the low-yield doctrine, the issue protocol.
2. **The root [AGENTS.md](../../../AGENTS.md)** — its privacy limits and
   evidence rules bind here without exception. Read the whole thing if you may
   touch a page under `san-francisco/`.
3. **The playbook for the stage you're about to work** —
   `research/roles/{prospector,acquirer,extractor,resolver,publisher,auditor}.md`.
   Read the one you need, not all six.

Then get the current state:

```bash
python3 research/tools/check.py --stats   # yield per source: read, found, resolved, published
python3 research/tools/check.py           # register ↔ dossiers, findings ↔ schema
```

and skim `research/SOURCES.md` — the register plus the leads table. If a source
isn't in the register, it doesn't exist yet.

## Two ways this skill gets invoked

### `/research` with no request — choose the work yourself

You are being asked to advance the module's goals on your own judgement. Pick
**one unit of work someone could actually finish this session**, say what you
picked and why in a line or two before you start, then do it end to end.

Work down this ladder and take the first thing that has something in it:

1. **Finish chains already half-built.** Value already on disk is the cheapest
   value there is. In `check.py --stats`, a gap between the `resolved` and
   `published` columns is a publish pass sitting there waiting; a gap between
   `found` and `resolved` is a resolve pass. Findings entries at
   `publish.status: "pending"` will otherwise be re-published by someone else,
   and entries left `unresolved` are facts the project paid to find and never
   used.
2. **A source's first published batch that nobody has audited.** The auditor
   playbook is explicit that systematic errors are cheapest to catch there, and
   an unaudited first batch is the module's largest silent risk.
3. **The issue queue.** Search open issues labelled `research` and take one that
   names a specific batch, file or report — not a standing "read the remaining
   N" issue. Prefer a source already at status `mining`: continuing a source
   whose dossier records its traps beats opening a new one whose traps you'll
   pay to learn.
4. **A `mining` source whose dossier names its next batch.** The coverage note
   is the queue when no issue exists.
5. **Triage the leads table.** When the register is short on `high`
   search-invisibility sources, or leads have piled up untriaged, run a triage
   pass — verdicts and sampled evidence, not thirteen dossiers. The prospector
   playbook's two gears matter here; picking the wrong one wastes the session.
6. **Fix the module.** If the structure is fighting the work — a missing schema
   field, a role that doesn't match what sessions actually do, a tool everyone
   rewrites by hand — change it, per "Amending this module" in
   `research/AGENTS.md`. Docs and playbooks change in the same commit.

Prefer depth over breadth: one batch read whole and handed off cleanly is worth
more than three batches sampled. When the unit turns out bigger than a session,
finish what you can, record exactly where you stopped, and file the issue for
the remainder.

### `/research <request>` — the request belongs to this module

Treat the request as research work and route it, rather than answering it as a
generic coding task:

- Work out which stage it lands in, read that role playbook, and follow it.
  Requests rarely name their stage. "Can we get anything on the Sunset before
  1930?" is prospecting. "Here's a PDF, pull the addresses out" is extraction.
  "Does 1311 Alabama check out?" is resolving or auditing.
- A request may span several stages for a small source — running all six in one
  session is normal and correct. Each stage still has to leave its **file**
  behind before the next one starts, because that file is what survives the
  session.
- A request that arrives as raw material — a dataset, a scan, a dump, a batch of
  OCR — is an extraction pass. Read **"Mining a corpus for address-level facts"**
  in `research/AGENTS.md` before you start, and take its instruction literally:
  do the pass, don't relitigate it, report the yield as counts, and don't open
  with a caveat about how thin the material was.
- If the request would put something on a page, you are wearing the site agent's
  hat for that part: root `AGENTS.md` and `shared/AGENTS.md` govern, exactly.

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

## Tools

```bash
python3 research/tools/check.py [--stats]           # run before every commit
python3 research/tools/resolve_eas.py fetch|report|apply <findings-file>
python3 scripts/validate.py                         # any pass that touched a page
python3 scripts/seed_pages.py seed-list --manifest research/manifests/<f>.json
```

`report` before `apply`, and read every conflict it prints — the tool does the
lookups, you do the judgement.

## Before you stop

A session's real output is what the next session can pick up. Leave all of it
true:

- **The findings file** — every entry carries the decision your stage owed it
  (`coverage` filled in even when nothing was found; `resolution` for a resolve
  pass; `publish` marked `published` with its PR or `declined` with a reason).
- **The dossier** (`research/sources/<id>.md`) — the coverage note and the
  `Verified:` line, naming what was read and what wasn't. *A pass that doesn't
  update its dossier has thrown away most of its value.*
- **The register** (`research/SOURCES.md`) — status and coverage phrase, in
  counts, not adjectives.
- **An issue** for what you didn't finish and for the next stage, using
  `research/templates/issues.md`. Search open issues for the source id first;
  one issue per unit someone can finish.
- **`check.py` clean** (and `validate.py` too, if a page was touched), then a
  commit on a branch — never `main` — whose message and PR body carry the pass's
  counts: read N, found M, resolved K, published J.

Report what you did the same way: counts, plainly. Zero findings, reported
honestly with its coverage recorded, is a completed pass — it tells the next
agent the haystack was searched there, and that is worth almost as much as a
hit.
