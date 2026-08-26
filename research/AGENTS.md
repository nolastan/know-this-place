# The research module — the rulebook

This directory is where **finding** address-level information happens. The rest
of the repo is where the website gets **built and maintained**.

Two documents run this module:

- **This file** — why it exists, what a run is, the evidence bar, the statuses,
  and the lessons that have already cost something.
- **[RUNBOOK.md](RUNBOOK.md)** — the procedure. Read it when you are about to do
  a run.

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
was triaged, with the evidence in [Triage notes](SOURCES.md#triage-notes); a
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

Cross-cutting lessons that cost a session or a correction. Source-specific ones
live in the dossiers. **Add to this list** whenever a run discovers something a
future run would otherwise repeat — that is what makes this module improve
rather than just accumulate.

- **A run that stops at "resolved" leaves the worst possible state.** PR #114
  put 425 `sf-context-statements` findings onto pages and never marked the
  findings file. The next agent could not tell finished work from unstarted
  work, and closing the loop cost a full verification pass over 425 entries
  against 260 pages. *Mark the findings file in the same commit that edits the
  pages.* `check.py` now fails when a file has published entries and resolved
  ones with no decision recorded.
- **A duplicated status will eventually disagree with itself.** The findings
  schema used to carry a file-level `stage` alongside the per-entry statuses;
  PR #114's file said `stage: resolved` while its facts were on pages. Derived
  state belongs in the tool that derives it, not in the file.
- **Don't sample a corpus sequentially to estimate its density.** OAI-PMH and
  most archive APIs return records in accession order, so any prefix is one or
  two accessions rather than a cross-section. A `digitalsf` prospecting pass
  measured 1.2% on that basis and was wrong by more than threefold.
- **Read the field the archivist wrote in, not the one that is easy to parse.**
  `digitalsf`'s `269$a` collapses "between 1946 and 1951" to `1946`, and its
  `907$a` fuzzy-date flag catches only 115 of 298 imprecise dates. Trusting
  either promoted 183 estimates to firm years.
- **Check where a collection actually keeps its people before trusting a flag
  about them.** In `digitalsf` SFP 23 the `600`/`700` personal-name fields hold
  one corporate body and the actual people are in the titles.
- **A stale identifier loses records silently.** EAS carries retired APNs; a
  manifest built by looking EAS up on the active `blklot` drops those parcels
  with no error. Go via the number EAS actually carries.
- **Query coordinates at full precision.** EAS address points sit centimetres
  from their parcel boundary; rounding to six decimals moves enough of them
  across it to lose the parcel.
- **A frequency count over any commercial corpus surfaces the advertisers.** The
  top numbered address in a trade journal is a firm's own office; in Planning
  Commission minutes it is the Commission's own address. The usable material is
  in the long tail.
- **A recorded range is the whole range.** `resolve_eas.py` used to look up only
  a finding's `street_number` whenever it had one, ignoring the
  `address_range_as_recorded` beside it. Every building whose low number has
  since been retired came back "no EAS record" — 550–590 and 731–799 Van Ness
  Avenue among them, both extant and both surveyed. The tool now expands the
  range whenever one is recorded. *If a record states a range, look up every
  number in it.*
- **A record that names its own parcel has already done the placing.** Where a
  range spans several parcels today, the tool declined — correctly, because
  choosing would be adjudicating. But a survey that prints `647/13, 14` has
  identified the parcel itself, and following that is reading the record, not
  deciding for it. `resolve_eas.py` now takes the parcel a finding's
  `extra.assessor_block_as_recorded` **and** `assessor_lot_as_recorded` name
  when it is one of the candidates, and says so in the method.
- **The nearest published page cannot pick the neighbourhood directory on a
  street that has no pages.** The resolver files a new page under the area of
  the nearest existing page; on Van Ness Avenue, which had three pages in the
  whole city, that scattered one corridor across five directories and put 1765
  California Street in `financial-district`. Where a street is that thin, file
  on the **analysis neighbourhood** the assessor and EAS give the parcel, and
  put the reason in `resolution.method`.
- **A lesson nobody can act on gets paid for twice.** The Van Ness run wrote
  down that the nearest published page cannot pick the neighbourhood directory
  on a street the site hasn't settled — and then left `resolve_eas.py` doing
  exactly that, so North Beach came back scattered across six directories and
  the paths would have been hand-patched a second time. *When a run discovers a
  rule, give the tool the switch that applies it.* `--area-from-nhood` and the
  `manifest` subcommand both exist because the knowledge was already in the
  module and only the tooling was missing.
- **A `conflict` is not always a conflict about the address.** `resolve_eas.py`
  read every `conflict` as a disagreement between two recorded addresses and
  printed `"290 Lombard Street" against "None"` into eighteen resolution
  methods. Most conflicts are a source disagreeing with itself about a *date*
  or a *name*; those resolve normally and the disagreement is the page's
  `.unknowns` to carry. The branch now runs only when a second address is
  actually recorded.
- **A page the generator will not render is a hand-authored page.** Publishing
  in bulk means calling `seed_pages.render_html` over pages the run did not
  create, and some of them predate it — a source with no `query`, a field the
  renderer expects as a string. Writing `data.json` and letting the render blow
  up leaves the two files disagreeing, which the root AGENTS.md forbids
  outright. *Render first, write both files or neither, and list what has to be
  edited by hand.*
- **An abbreviated range is not a range.** Surveys print "1843-47" and
  "1761-65" for 1843–1847 and 1761–1765, dropping the digits that don't change.
  `resolve_eas.py` read the pair literally, expanded 47→1843, and reported the
  Japantown statement's Art Deco building at 1843-47 Fillmore Street as spanning
  eighty parcels. The tool now fills a short high end in from the low end.
  *A recorded range needs its high end spelled out before it is expanded.*
- **A parcel found by point can outvote three that were stated.** EAS leaves
  some address rows without a `parcel_number`, and the resolver places those by
  the point their coordinates fall in — which DATA-SOURCES.md already warns sits
  centimetres from a boundary. Inside a recorded range that turned one lot into
  two: 1944 Fillmore Street landed on the neighbour and declined 1940–1946
  Fillmore Street, an extant National Register building whose other three
  numbers all state the same parcel. The tool now takes the stated parcel and
  says so. *Weigh what the record states above what a coordinate implies.*
- **A permit name with no role label near it walks straight onto a page.**
  `seed_pages.py names` flags role words, firm suffixes and titles, so it never
  saw DBI's intake prefix: "one-stop:peter burns:revision to pa …" carries none
  of them. Two names were seeded onto a Japantown page, and a third had been
  sitting on a Mission page since whenever it was seeded. `NAME_HINT` now catches
  the prefix and all three names are on the redaction list. *A privacy filter
  built from role words misses every name that isn't introduced by one — test it
  against the raw text of the pages you just wrote, not only against its own
  flags.*
- **When a source prints both the historical and the current address, looking
  up the historical one resolves silently onto a neighbour.** The Russian Hill
  statement heads each demolished building with its pre-renumbering number and
  adds "site of today's #N". Every one of those old numbers — 2507, 2509, 2513,
  2517, 2519 Larkin, 2612 and 2614 Polk — is still a live EAS address on the
  same block, so `resolve_eas.py` placed six 1870s cottages on the parcels of
  buildings that are standing today, with a confident method sentence each. It
  showed up only because 2509 Larkin landed on the parcel of the extant 1888
  house next door. *A renumbering trap does not always look like a miss; the
  dangerous ones look like clean matches. When a record gives today's address
  for a site, place on that and say so.*
- **EAS holds the numbered streets as zero-padded ordinals**, so a source that
  spells one out — "285 Second Street" — failed at the *street*, not the number,
  and came back "not a street in the city's address registry" for one of the
  busiest streets downtown. `resolve_eas.py` now maps spelled-out ordinals to
  EAS's form (`SECOND` → `02ND`) and states the mapping in the method. *A
  lookup that fails on the street name rather than the number is a spelling
  problem, not a finding.* **The digits fail the same way and were not
  covered**: a survey that writes "20 2nd Street", which is how nearly every
  report writes it, lost 1st, 2nd and 3rd Streets whole — 130 findings in the
  middle of downtown — until the same mapping was taught to accept `2ND` as
  well as `SECOND`.
- **A survey of a redevelopment area is a record of buildings that were about to
  come down, and some did.** The Transit Center survey lists thirteen active
  projects that would demolish buildings it had just inventoried; three of its
  parcels now carry buildings the assessor dates after the survey was written.
  A construction date published on those pages would describe a building that is
  gone. *Compare the assessor's year built with the source's on every finding,
  and where the roll year postdates the source, state both years and let the
  page's `.unknowns` carry the disagreement — never assert a demolition the
  source does not record.*
- **Two surveys of the same buildings do not fit in one page.** The Transit
  Center survey area sits inside the Central SoMa survey area, which this repo
  had already published; 57 of the 123 pages the run reached already carried the
  other survey's `historic_survey` panel, and the renderer holds one. Their
  ratings could not be shown at all, and only the fact the other survey lacks —
  district-contributor status — reached those pages, as a timeline entry.
  *Before planning where a district statement's facts will go, check which of
  its parcels the repo has already documented from a neighbouring survey.*
- **A page-level fact still needs its finding marked published.** Writing a
  surveyed year into `building.completed_conflict` while declining the finding
  that supplied it left a page stating a disagreement with no entry in its
  `sources` — an unsourced sentence, which the root AGENTS.md forbids outright.
  *A finding that reached the page in any component is published, whatever
  component it reached, and the source entry goes with it.*
- **The resolver's path and its manifest disagreed about a parcel's lowest
  number**, because the path reaches EAS rows filed under a since-retired parcel
  and the manifest did not. The seeder put the page at 657 Mission Street while
  every resolution pointed at 655: one parcel, two places, and the facts landing
  on neither. `build_manifest` now carries the path's own number into the list
  it hands the seeder.
- **A parcel with no row on the assessor's secured roll cannot become a page,
  and on an architectural corpus that selects for exactly the best buildings.**
  Eight resolved Russian Hill parcels have `in_asr_secured_roll: false` and no
  roll row in any year, so `seed_pages.py` skipped them: 945 and 947 Green, 2555
  Larkin, 2500 Steiner, 2000 and 2006 Washington, 1925 Gough. They are the
  1910s–1920s apartment houses, several of them the "cooperative" buildings the
  report itself describes — the parcel is not assessed as one property. This is
  the condominium rule's cousin and it bites the same way: *the rule that keeps
  the site honest about parcels also holds back the most-documented buildings,
  so say which ones in the dossier rather than letting them vanish into a
  count.*
- **A note that only exists in `data.json` is not on the page.** Findings runs
  have been writing conflicts into an `unknowns` key since Market & Octavia, and
  `seed_pages.py`'s renderer never read it — the disagreements reached the repo
  and stopped there. The renderer now states them above the "Not yet
  documented" line. *When you invent a key, check that something renders it.*
- **The natural way to write up an inventory finding is the one thing the design
  contract forbids.** A source that says nothing about a building except that it
  is on a list invites the sentence "Picked out by a 2007 walking survey as a
  house predating…" — which is exactly the `a survey records…` pattern the root
  AGENTS.md rules out of a page body. It went onto 129 pages across two batches
  before an audit caught it, because it reads like content rather than like
  attribution. The line: a listing or designation **event** may be stated as an
  event, the way the North Beach pages state a 1982 survey listing; an ordinary
  fact about a building must be stated as a fact, with the attribution left to
  the Sources footer. *Grep the descriptions you are about to publish for
  "survey", "statement", "report" and "according to" before rendering.*
- **A generic entry published beside a specific one is a duplicate, not a second
  finding.** Sources that carry both an inventory and a narrative name the same
  building twice, and the narrative always says more — a firm year, a builder, a
  style. Publish both and the page's one timeline shows two items at the same
  date, the second saying less. Four Parkside findings were declined for this.
  *Before publishing a source with both parts, group the resolved findings by
  parcel and read every page that gets more than one.*
- **`seed_pages.py names` goes quiet once the pages exist.** It only inspects
  parcels still marked seedable, so running it after `seed-list` — which is when
  the root AGENTS.md's instruction reads most naturally — reports zero
  descriptions and zero flags, which looks like a clean privacy pass and is not
  one. It also wants the EAS neighborhood name (`"Sunset/Parkside"`), not the
  directory slug. *Do the privacy pass by reading the `data.json` files the run
  just wrote, and test against the raw permit text rather than the tool's own
  flags.*

- **A row of buildings is not a range, and the resolver cannot tell them
  apart.** `resolve_eas.py` expands a recorded range on the assumption it is
  one building with a two-number address, which is right for "1940–1946
  Fillmore Street" and wrong for "3253 through 3259 Baker Street" — a row of
  four houses on four parcels, which it then declines. The fix is at extraction
  time, not in the tool: record only the two numbers the source actually
  prints, one finding each. The buildings between them are real, but their
  numbers are an inference, and a source will tell you so if you let it — the
  PPIE statement calls 215-287 Avila Street *twelve* bungalows and 2122-2146
  Bay Street *five*, spacings that enumerating by parity would have got wrong
  both times.
- **A privacy filter built from role words also misses the bare preposition.**
  The `one-stop:` lesson above widened `NAME_HINT` to catch DBI's intake
  prefix; it still let "walk in cooler per jesus zapien" onto a Marina page,
  because "per" introduces a name with no label at all. The pattern now flags
  two lowercase words after `per` or `by`, which is noisy — "per field
  findings" flags too — and that is the right trade for a list a person
  reviews. *Every widening of this filter so far has come from a name that
  reached a page. Check the pages you just wrote, not the filter's own output.*
- **A roll build year of 1900 is a floor value, not a construction date.**
  Civic and institutional parcels come off the assessor's secured roll as built
  1900, and the PPIE statement says outright that 1900 on the roll may stand
  for something earlier. Publishing it as a source-versus-assessor
  disagreement invents a conflict that isn't there. Where the parcel holds
  several buildings of several dates, say that instead.

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
   [What we've learned the hard way](#what-weve-learned-the-hard-way) above.
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

- **An Excel-printed PDF table has no rows in its text layer.** The Showplace
  Square survey data is an `.xlsx` printed to PDF: cells wrap, and a row's
  parcel number, address and note sit on three different baselines, sometimes
  above one another's rows. `pdftotext -layout` and every y-clustering parse
  built on it mixed adjacent buildings' architects, styles and dates. The row
  boundaries are in the **content stream**, where each row starts with a `Td`
  that returns the pen to the first column's x; splitting there and taking each
  drawn string's column from its x rebuilt all 633 rows, and disagreed with the
  layout parse on 167 fields — correctly, every time. *Where a table's rows
  matter, read the content stream, not the rendered text; and parse it twice by
  different means and diff the two before trusting either.*
- **Two readers of the same field will eventually disagree, and the failure is
  silent.** `resolve_eas.py` parsed `address_range_as_recorded` in two places —
  once to decide which parcels to fetch, once to decide a finding — with two
  copies of the regex. A batch that wrote its ranges in a shape only one copy
  accepted had every ranged building's parcel left unfetched, and then declined
  those findings for "not an active parcel in sf-parcels", which is a sentence
  about the city rather than about the tool. 57 findings. *One reader per
  field; and when a lookup fails, check that what it looked up was ever
  fetched.*
- **A filter built from suffixes takes the sentences too.** The survey's note
  column names the firm for most buildings and describes the architecture for
  the rest, and a name-detector keyed on "Co.", "&" and capitalisation read
  "Intact small-scale industrial building with finely executed brick cornice"
  as an occupant and put it on a page. The leading word is the tell: an
  adjective at the head of a note means the surveyor is describing, not naming.
