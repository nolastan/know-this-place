# Research

Finding things to say about San Francisco addresses that nothing else on the
internet says.

This module is deliberately separate from the website. Everything under
`san-francisco/`, `shared/` and `scripts/` is about **presenting** what we
know; everything here is about **finding it** — reading newspaper archives,
mining survey PDFs, combing newsletters, and turning what turns up into
verified, sourced facts a page can carry.

**Start with [AGENTS.md](AGENTS.md).** It is the rulebook, and it binds humans
and agents alike.

## What we're looking for

The site's goal is to be the first search result for any San Francisco address.
That makes **search-invisible sources the valuable ones** — newspaper OCR,
out-of-print books, neighborhood newsletters, printed journals, PDF survey
reports, city directories, oral histories. If Google already surfaces it for an
address query, mining it adds little.

Low yield is expected and fine. A 200-page report that produces six citable
facts about six buildings is a good day's work.

## Layout

```
research/
  AGENTS.md          The rulebook: goal, pipeline, evidence bar, issue protocol
  README.md          This file
  SOURCES.md         The register — every source, its status and its yield
  sources/<id>.md    One dossier per source: access, cautions, coverage log
  findings/          Machine-readable handoffs between pipeline stages
  schema/            The findings JSON schema
  roles/             One playbook per specialized job (prospect → audit)
  manifests/         Parcel lists produced here, consumed by seed_pages.py
  templates/         Dossier skeleton and GitHub issue bodies
  tools/check.py     Consistency + schema checks (stdlib only)
  tools/resolve_eas.py  Addresses → parcels: the EAS/parcel/roll joins a
                     resolver makes, with the reason for each decision
  corpora/           Raw downloaded material — gitignored, never committed
```

## How the work divides

Six stages, each with a playbook in [roles/](roles/) and each handing the next
one a file rather than a conversation, so a different agent can pick it up in a
different session:

1. **[Prospector](roles/prospector.md)** — find a source worth mining, rate how
   invisible it is to search, register it.
2. **[Acquirer](roles/acquirer.md)** — get at it: download, OCR, page through
   an archive, work out the URL the vault actually serves.
3. **[Extractor](roles/extractor.md)** — read the messy thing and write
   structured findings JSON. One entry per dated, numbered, citable fact.
4. **[Resolver](roles/resolver.md)** — turn "1311 Alabama street, 1895" into a
   parcel that exists today, or mark it unresolved. Most of the mistakes in
   this project live in this step.
5. **[Publisher](roles/publisher.md)** — put resolved findings on pages under
   the root `AGENTS.md` rules, or into a manifest for the seeder, and open a PR.
6. **[Auditor](roles/auditor.md)** — spot-check what got published against what
   was found, and close the loop in the dossier.

A single session can run all six for a small source, or one stage for one batch
of a large one. Either is a complete piece of work as long as it leaves the
register, the dossier and the issue queue telling the truth about where things
stand.

## Running it

```bash
python3 research/tools/check.py          # register ↔ dossiers, findings ↔ schema
python3 research/tools/check.py --stats  # yield so far, by source and stage
```

Agents working in Claude Code have a `/research` skill
([../.claude/skills/research/SKILL.md](../.claude/skills/research/SKILL.md)):
`/research` on its own picks up the most valuable open work in the module,
`/research <request>` routes a request to the right stage. It is a door into
the documents above, not a substitute for them.

Site-side commands a publisher may need (`seed_pages.py seed-list`,
`build_sitemap.py`, `build_map_index.py`, `validate.py`) are documented in the
root [README.md](../README.md) and [AGENTS.md](../AGENTS.md).
