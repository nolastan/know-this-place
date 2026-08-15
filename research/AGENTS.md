# The research module — agent constitution

This directory is where **finding** address-level information happens. The rest
of the repo is where the website gets **built and maintained**. Keeping them
apart is the point of this module: a research agent reads archives, mines
corpora and hands over verified, resolved, citable facts; a site agent turns
those into pages under `san-francisco/` per the root
[AGENTS.md](../AGENTS.md).

Read this file before doing any research work. Read the root `AGENTS.md` too —
its privacy limits and its evidence rules bind here without exception.

## The goal, and what follows from it

**Know This Place intends to be the first search result for any San Francisco
street address.** A source that is already indexed and ranking does little for
that — a fact anyone can find in three seconds is a fact a reader had no need
of this site for. So the module has a bias, and it is not subtle:

> **Prefer sources that search engines cannot see.** Newspaper archives behind
> OCR, out-of-print books, neighborhood newsletters, association bulletins,
> PDF survey reports, microfilm finding aids, printed journals, oral-history
> transcripts, permit ledgers, city directories. The harder a source is to
> search from outside, the more a page built on it is worth.

Two corollaries agents get wrong often enough to be worth stating:

- **Low yield is fine and expected.** A scanned book that produces four
  citable facts about four addresses is a **win**. See "Mining a corpus for
  address-level facts" below — it is the most important section in this file.
- **A big, easy, already-indexed dataset is not automatically the better
  target.** It usually loses to a small obscure one on the only axis that
  matters here.

## The boundary with the website

| Research module | Website |
|---|---|
| Finds, acquires, mines, resolves, cites | Composes pages, keeps the design contract |
| Writes findings JSON, dossiers, manifests, issues | Writes `data.json` + `index.html` |
| Owns `research/**` and its source ids | Owns `san-francisco/**`, `shared/**`, `scripts/**` |
| Cares whether a fact is true and traceable | Cares how a true fact is presented |

A research agent **may** write to `san-francisco/**` — publishing is the last
stage of the pipeline and someone has to do it. When it does, it is wearing the
site agent's hat and follows the root `AGENTS.md` and
[shared/AGENTS.md](../shared/AGENTS.md) exactly: facts through components, prose
as a last resort, `data.json` regenerated into `index.html`, `validate.py` clean.
What it must never do is let research conventions leak onto a page — no findings
JSON in the content tree, no source dossier prose copied into a `narrative`, no
"the archive shows…" sentences.

## The pipeline

Six stages. Each is a role with a playbook in [roles/](roles/), and each hands
the next one a **file, not a conversation** — so different agents, in different
sessions, days apart, can pick up where the last one stopped.

```
prospect ──▶ acquire ──▶ extract ──▶ resolve ──▶ publish ──▶ audit
 register     get it     messy →     which       onto        check
 the source   on disk    JSON        parcel?     pages       the chain
```

| Stage | Role | Reads | Writes |
|---|---|---|---|
| 1 | [prospector](roles/prospector.md) | the world | a row in [SOURCES.md](SOURCES.md), a stub dossier, a `research:acquire` issue |
| 2 | [acquirer](roles/acquirer.md) | the source | `research/corpora/<id>/` (uncommitted), the dossier's access + coverage notes |
| 3 | [extractor](roles/extractor.md) | raw OCR / PDFs / rows | `research/findings/<id>/<batch>.json` |
| 4 | [resolver](roles/resolver.md) | findings + EAS/parcel APIs | the same file, `resolution` filled in |
| 5 | [publisher](roles/publisher.md) | resolved findings | `san-francisco/**` pages, `research/manifests/*.json`, a PR |
| 6 | [auditor](roles/auditor.md) | published pages + findings | corrections, dossier `Verified:` line |

**A stage may be split across many agents and many sessions.** That is what the
files are for. It is normal and correct to run stage 3 over one batch, file an
issue for the next batch, and stop.

**A stage may also be skipped when it has nothing to do** — a source with ten
addresses in it does not need a manifest, and a source read live off the web
needs no `corpora/` directory. Skipping is a judgement call recorded in the
dossier, not a silent omission.

## Handoff artifacts

- **[SOURCES.md](SOURCES.md)** — the register. One row per source: id, kind,
  search-invisibility, status, yield so far. This is the module's index; if a
  source isn't in it, it doesn't exist.
- **`sources/<id>.md`** — the dossier. How to get at the source, what it
  contains, every caution learned the hard way, what has been covered and what
  hasn't, and the `Verified:` line. **The dossier is the memory of the module.**
  A pass that doesn't update its dossier has thrown away most of its value.
- **`findings/<id>/<batch>.json`** — the machine-readable handoff between
  stages 3, 4 and 5. Schema and rules: [findings/README.md](findings/README.md)
  and [schema/finding.schema.json](schema/finding.schema.json).
- **`manifests/*.json`** — parcel lists for `scripts/seed_pages.py seed-list`,
  when a source names enough buildings with no pages to be worth seeding in
  bulk. This is research output the site tooling consumes.
- **GitHub issues** — the queue between agents and humans. See "Filing work"
  below.

Validate the JSON side of that with:

```bash
python3 research/tools/check.py
```

It checks the register against the dossiers on disk, and every findings file
against the schema. Stdlib only; run it before you commit.

## Mining a corpus for address-level facts

Much of the research here is **a deliberately low-yield scan of a large
source** — an OCR newspaper run, a period history, a bulk dataset export — for
the handful of passages that pin a fact to a street number. Needles in a
haystack is the design, not an accident, and the measured numbers say so: the
Chronicling America pass in [sources/loc-newspapers.md](sources/loc-newspapers.md)
read **58,620 OCR pages to find 8,437 numbered-address mentions across 2,025
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
  whether the task should be narrowed — and don't open the results with a
  caveat about how thin the material was. Read the whole thing and report what
  you found.
- **A small harvest is a successful pass, and zero is a valid result.** Report
  the outcome as counts — "read N pages/rows, found M numbered-address
  mentions, K of them on streets that have pages here" — in the PR body, in the
  findings file's `coverage` block, and in the dossier's `Verified:` line. A
  pass that surfaces three usable facts out of ten thousand rows has done its
  job; a pass that surfaces none has also done its job, and says so in the same
  form. Neither is a failure to explain away.
- **Scarcity never lowers the evidence bar.** This is the one thing low yield
  genuinely changes, and it changes it in the opposite direction from the
  temptation: do not stretch a weak match to make the harvest look bigger. A
  metes-and-bounds entry with no street number stays unresolved; a mangled OCR
  digit stays unresolved; an 1878 number with no EAS record does not become a
  page; a South Van Ness conversion done by subtracting a constant is wrong.
  Discarding the large majority of candidate hits is the expected arithmetic.
- **Record the scan, not just the hits.** Update the dossier with what was
  covered and what wasn't (the `Verified:` line, plus a coverage note naming the
  batches, issues or sections still untouched), so the next pass resumes instead
  of re-reading the same haystack. File an issue for what's left.
- **Volume doesn't relax privacy.** These corpora are dense with people —
  householders in want-ads, tenants in fire reports, owners in transfer
  notices. Take buildings, contractors, architects and named firms; leave
  residents, occupants and owners, per "Privacy — hard limits" in the root
  [AGENTS.md](../AGENTS.md). The size of the input is not a reason to loosen
  that, and the low yield of a pass is never a reason to make up the difference
  with people.

## The evidence bar

Every fact that leaves this module carries three things: **a date, a street
number, and a citation precise enough for a reader to check.** A finding
missing any of them is `unresolved`, and unresolved findings stay in the
findings file — they never reach a page.

- **The address is the hard part, and it is where the mistakes are.** Street
  numbers were changed (1909 renumbering), streets were renamed, and one street
  was renumbered *when* it was renamed (Howard → South Van Ness — see
  [sources/loc-newspapers.md](sources/loc-newspapers.md), which has the block-face
  table and the warning against subtracting a constant). Resolve against
  `sf-eas-addresses`; where the source gives cross streets or lot dimensions,
  use them as the check. No EAS record means no page — record the fact against
  the surviving building or the street hub, or leave it unresolved.
- **Never reconcile a conflict silently.** A source that contradicts the
  assessor, or another source, is recorded as a conflict and named in the
  page's `.unknowns`. Adjudicating is not research; it is invention.
- **Cite what you actually read.** The issue, page and date of a newspaper; the
  section of a book; the volume, number and article of a journal; the page of a
  PDF report. "The archive" is not a citation.
- **Facts, not wording.** Extract discrete facts and re-express them through
  page components. Never reproduce a source's sentences or their structure —
  facts aren't copyrightable, expression is. This applies to every secondary
  source in `sources/`.

## Filing work

Agents here are **expected** to create GitHub issues rather than doing
everything in one session. An issue is how a pass hands off what it couldn't
finish, and how it asks a human for the one thing it can't do itself.

- **Labels:** `research` on every issue, plus the stage —
  `research:lead`, `research:acquire`, `research:extract`, `research:resolve`,
  `research:publish`, `research:audit`. `needs-human` when it is blocked on a
  person (a paywall, a library visit, a licensing call, a schema decision).
  GitHub silently drops labels that don't exist in the repo — if one is
  missing, say so in the issue body and add `needs-human`.
- **Title:** `research(<source-id>): <the specific thing>` — e.g.
  `research(loc-newspapers): extract batch sn85066387/1906`.
- **Body:** use the templates in [templates/issues.md](templates/issues.md).
  Every issue states the **source id**, the **stage**, the **input** (file
  paths, URLs, batch names), and the **definition of done** in one line. An
  issue another agent can't start without asking a question is a bad issue.
- **One issue per unit of work someone can actually finish**, not one per
  source. "Read the 38 remaining context statements" is a bad issue; "Add the
  Japantown Historic Context Statement (Revised 2011)" is a good one — and the
  38 issues already open against this repo are exactly that shape.
- **Don't file duplicates.** Search open issues for the source id first.

## Corpora on disk

Raw source material — PDFs, OCR dumps, scraped HTML, dataset exports — goes in
`research/corpora/<source-id>/`, which is **gitignored**. It is large,
re-downloadable, and often not ours to redistribute.

- Keep a `state.json` (or equivalent) in each corpus directory recording what
  has been fetched, so a later pass resumes rather than re-downloads.
- **What gets committed is the findings, not the corpus.** If a fact only
  exists in an uncommitted file, it isn't a fact yet — get it into a findings
  file with its citation.
- Never commit copyrighted source text into the repo. Quotations in a findings
  file are the minimum needed to justify the extraction (a clause, not a
  column), and never reach a page.
- Be a good citizen when fetching: rate-limit, back off on failure, identify
  the client, and honour `robots.txt` and terms of use. If a source forbids
  automated access, that is a `needs-human` issue, not a workaround.

## Amending this module

**This module is meant to change.** The pipeline above is the current best
guess at how the work divides, not a constitution handed down. An agent that
finds the structure fighting the work should fix the structure:

- Add a role, a stage, a tool, a schema field, or a whole new kind of artifact
  when the work needs it. Update this file, [README.md](README.md) and the
  affected role playbooks **in the same commit** — a change to the pipeline
  that leaves the docs describing the old one is worse than no change.
- Record *why* in the commit message. The next agent inherits the structure
  without the conversation.
- **Two things need a human's say-so:** changing the meaning of an existing
  `sources` id already cited on published pages (it breaks citations), and
  anything that changes what appears on a page under `san-francisco/**`
  (that is the root `AGENTS.md`'s territory, not this file's).
- Everything else — reorganizing the roles, splitting a dossier, adding a
  script under `tools/`, rewriting this section — is yours to change. Leave the
  module easier to use than you found it.
