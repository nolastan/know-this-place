# Research

Finding things to say about San Francisco addresses that nothing else on the
internet says.

This module is deliberately separate from the website. Everything under
`san-francisco/`, `shared/` and `scripts/` is about **presenting** what we know;
everything here is about **finding it** — reading newspaper archives, mining
survey PDFs, combing newsletters, and turning what turns up into verified,
sourced facts a page can carry.

Two documents run it:

- **[AGENTS.md](AGENTS.md)** — the rulebook. Why the module exists, what a run
  is, the evidence bar, the statuses, and the lessons that already cost
  something.
- **[RUNBOOK.md](RUNBOOK.md)** — the procedure, step by step.

## What we're looking for

The site's goal is to be the first search result for any San Francisco address.
That makes **search-invisible sources the valuable ones** — newspaper OCR,
out-of-print books, neighborhood newsletters, printed journals, PDF survey
reports, city directories, oral histories. If Google already surfaces it for an
address query, mining it adds little.

Low yield is expected and fine. A 200-page report that produces six citable
facts about six buildings is a good day's work.

## How the work divides

It doesn't, much — and that is deliberate. **The unit of work is a run: one
source taken from raw material to published pages and closed books, in one
session.** Six steps, one session, one PR:

```
get it ──▶ read it ──▶ place it ──▶ publish it ──▶ check it ──▶ close the books
on disk    findings     which        onto pages     against      dossier,
           JSON         parcel?                     the source   register, counts
```

Each step still leaves a **file** behind, because that is what survives a
session that has to stop early. But stopping early is the exception, not the
design: a run that ends at "resolved" leaves the most expensive state in the
module. Sizing, and what to do when a batch turns out too big, are in
[RUNBOOK.md](RUNBOOK.md#sizing-a-run).

Prospecting — finding and triaging new sources — is the other kind of run, and
has its own half of the runbook.

## Layout

```
research/
  AGENTS.md          The rulebook: goal, the run, evidence bar, statuses, lessons
  RUNBOOK.md         The procedure: both kinds of run, step by step
  README.md          This file
  SOURCES.md         The register — every source, its status and its yield —
                     plus the leads table and the triage notes
  sources/<id>.md    One dossier per source: access, cautions, coverage log
  findings/          The chain of custody, one JSON file per batch
  schema/            The findings JSON schema
  manifests/         Parcel lists produced here, consumed by seed_pages.py
  templates/         Dossier skeleton and GitHub issue bodies
  tools/check.py     Consistency + schema checks, and the dashboard (stdlib only)
  tools/resolve_eas.py  Addresses → parcels: the EAS/parcel/roll joins, with the
                     reason for each decision
  corpora/           Raw downloaded material — gitignored, never committed
```

## Running it

```bash
python3 research/tools/check.py          # register ↔ dossiers, findings ↔ schema
python3 research/tools/check.py --stats  # the dashboard: yield and open loops
```

`--stats` is the one place to look for where things stand. Its `open` column —
resolved findings nobody has published or declined — is the module's to-do list.

Agents working in Claude Code have a `/research` skill
([../.claude/skills/research/SKILL.md](../.claude/skills/research/SKILL.md)):
`/research` on its own picks up the most valuable open work, `/research
<request>` routes a request into the runbook. It is a door into the documents
above, not a substitute for them.

Site-side commands a run needs when it publishes (`seed_pages.py seed-list`,
`build_sitemap.py`, `build_map_index.py`, `validate.py`) are documented in the
root [README.md](../README.md) and [AGENTS.md](../AGENTS.md).
