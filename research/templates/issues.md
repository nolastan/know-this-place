# Issue templates

Agents in this module are **expected** to file issues — for the batch they
didn't get to, the next stage, or the one thing that needs a person. An issue
is how work survives the end of a session.

Conventions (full rules in [../AGENTS.md](../AGENTS.md) → "Filing work"):

- **Title:** `research(<source-id>): <specific thing>`
- **Labels:** `research` + the stage label + `needs-human` when blocked.
- **Body:** always states the source id, the stage, the input, and the
  definition of done. Search open issues for the source id before filing.
- End any comment or issue body you post on GitHub with the attribution footer
  your harness requires.

---

## `research:lead` — evaluate a candidate source

```markdown
**Source:** <name, publisher, dates covered>
**Where:** <URL or where it physically lives>
**Why it could be worth mining:** <expected address-level payload, in concrete terms>
**Search-invisibility:** <high|medium|low, and why>

**Definition of done:** a dossier at `research/sources/<id>.md`, a row in
`research/SOURCES.md`, and either a `research:acquire` issue or the lead
retired in place with the reason.

Playbook: `research/roles/prospector.md`
```

## `research:acquire` — get the material readable

```markdown
**Source id:** `<id>`
**Dossier:** research/sources/<id>.md
**Target:** <what to fetch: which years, volumes, reports>
**Known access notes:** <what the prospector found; treat as a hypothesis>

**Definition of done:** material under `research/corpora/<id>/` with a
`state.json`, the dossier's access section rewritten from what actually worked,
status moved to `mining` in the register, and a `research:extract` issue for the
first batch.

Playbook: `research/roles/acquirer.md`
```

## `research:extract` — mine a batch

```markdown
**Source id:** `<id>`
**Batch:** <the citable unit: a year, a volume, one report>
**Input:** research/corpora/<id>/<path>
**Expect:** a low hit rate. Read the whole batch; report the yield as counts.

**Definition of done:** `research/findings/<id>/<batch>.json` validating under
`python3 research/tools/check.py`, a `coverage` block that is true even if it
reads "found none", the dossier's coverage note updated, and a
`research:resolve` issue pointing at the file.

Playbook: `research/roles/extractor.md`
```

## `research:resolve` — addresses to parcels

```markdown
**Source id:** `<id>`
**Findings file:** research/findings/<id>/<batch>.json
**Unresolved entries:** <n>
**Known traps for this source:** <renumbering, OCR digits, metes and bounds>

**Definition of done:** every entry `resolved` (with apn, path and the method
that proved it), `unresolved`, or `rejected` — each with its reason — and a
`research:publish` issue for the resolved set. Resolving few of many is the
expected outcome.

Playbook: `research/roles/resolver.md`
```

## `research:publish` — onto the site

```markdown
**Source id:** `<id>`
**Findings file:** research/findings/<id>/<batch>.json
**Resolved entries:** <n>  (**pages that exist:** <n> · **pages that don't:** <n>)

**Definition of done:** a PR adding the facts to `data.json` + regenerated
`index.html` (or a manifest run for pages that don't exist yet), every entry
marked `published` with its PR number or `declined` with a reason,
`python3 scripts/validate.py` and `python3 research/tools/check.py` clean.

Playbook: `research/roles/publisher.md` — and the root `AGENTS.md` governs
everything that lands on a page.
```

## `research:audit` — check the chain

```markdown
**Source id:** `<id>`
**Batch:** <batch>
**Pages touched:** <paths or the PR link>

**Definition of done:** each sampled fact traced page → finding → `raw.text` →
citation, corrections filed as an ordinary site PR, and the dossier's
`Verified:` line updated with the date and what was checked.

Playbook: `research/roles/auditor.md`
```

## `needs-human` — blocked on a person

```markdown
**Source id:** `<id>`
**Blocked on:** <paywall | login | licensing terms | a library visit | a schema
or presentation decision>
**What was tried:** <specifics>
**What would unblock it:** <the smallest thing a person could do>

Nothing here is a workaround to route around — a source that forbids automated
access stays blocked until a person decides.
```
