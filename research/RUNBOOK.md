# The runbook — how a research run works

One document. Everything a session needs to do the work, in the order it gets
done. The rules behind it are in [AGENTS.md](AGENTS.md); this is the procedure.

**A run is one source taken as far as it goes in one session** — material on
disk, facts extracted, addresses resolved, pages published, work checked, books
closed. Not one stage. Not one handoff. The whole chain, for as much material
as a session can hold.

## Sizing a run

**Take more, not less.** A session should end with a source measurably further
along, not with a stage completed and five open questions handed to the next
agent. The old habit here was one stage per session, and it cost more in
handoff bookkeeping than it saved in focus.

So: pick a batch, and if taking it end to end would leave most of the session
unused, **take the next batch too.** Two context statements read, resolved and
published beats one read and handed off. A collection split by decade means
three decades in a run, not one.

The only reasons to stop short of publishing:

- The material genuinely ran out (a five-page report is a five-page report).
- You hit something that needs a person — a paywall, a licence, a presentation
  decision. File it (see [Filing work](AGENTS.md#filing-work)) and finish
  everything that doesn't depend on it.
- The batch turned out far bigger than it looked. Then finish the part you
  read, close its books completely, and say exactly where you stopped.

**Never stop at "resolved."** A findings file full of resolved entries that
nobody published is the single most expensive state this module can be left in
— see [What we've learned the hard way](AGENTS.md#what-weve-learned-the-hard-way).

## Picking the run

1. **An open loop.** `python3 research/tools/check.py --stats` prints an
   `open` column: resolved findings with nowhere marked. That is finished work
   sitting unpublished. Clear it first — it is the cheapest value on disk.
2. **An open issue** naming a specific document, batch or report. Prefer a
   source already `open` in the register: its dossier records the traps you'd
   otherwise pay to learn.
3. **The next batch the dossier names.** Every dossier's coverage note says
   what is left. That is the queue when no issue exists.
4. **An unaudited first batch** from a source that has published once. Step 6
   below says why that one matters more than the others.
5. **A prospecting run** — when the register is thin on `high`
   search-invisibility sources, or leads have piled up untriaged.
6. **Fix the module.** If the structure is fighting the work, change it. See
   [AGENTS.md → This module improves itself](AGENTS.md#this-module-improves-itself).

Say which you picked and why in a line or two, then do it.

---

# A mining run

## 1. Get the material readable

**Skip this step** if the source is already on disk or read live off the web —
say so in the dossier and move on.

Read the dossier first, and **assume its access notes are a hypothesis.** Fetch
one item and confirm it is what you think it is before planning batches — by
year, by issue, by volume, by block, by decade.

Fetch politely: rate-limit, back off on failure in tens of seconds rather than
five, resume from `state.json` rather than restarting, and stop if you are being
throttled. Honour `robots.txt` and terms of use. A source that forbids automated
access is a `needs-human` issue, not a workaround.

Normalize just enough for the next step: PDFs to text, one file per logical
unit, filenames that map back to a citation. A file you can't cite is a file you
can't use.

Material goes in `research/corpora/<source-id>/`, which is **gitignored**, with
a `state.json` recording what has been fetched.

### Access traps this project has already paid for

- **`WebFetch` returns nothing usable for many PDFs.** Fetch the bytes and
  extract text (`pdftotext`, `pypdf`).
- **SF Planning serves some documents from an M-Files vault**, where the
  `SharedLinks.aspx` URL returns an HTML shell, not the PDF. The real file is at
  the REST path the page's own script names. Worked examples for the Dogpatch
  survey and the Glen Park evaluation are in
  [sources/sf-context-statements.md](sources/sf-context-statements.md).
- **Cite the form a reader can use, fetch the form that works.** Where they
  differ, record both in the dossier and say which is which.
- **Drafts and finals coexist**, and the final sometimes still says DRAFT in its
  page headers. Take the file the adopting body listed; name it in the dossier.
- **A per-read timeout never fires on a slow trickle.** Read against a
  wall-clock deadline. (Same lesson as the DataSF notes in
  [../DATA-SOURCES.md](../DATA-SOURCES.md).)
- **Downloading for analysis is not publishing.** What may be published is
  facts, re-expressed — never the source's sentences, never a scanned page in
  `assets/`, never imagery whose licence doesn't permit redistribution.

## 2. Read it — findings out

Write `research/findings/<source-id>/<batch>.json`, valid against
[schema/finding.schema.json](schema/finding.schema.json). Rules and worked
example: [findings/README.md](findings/README.md).

- **Read the whole batch.** Not a sample, not until you have "enough." Report
  the yield as counts in `coverage`.
- **One entry per fact, not per passage.** A classified ad giving a number, a
  date and a room count is one finding with those fields, not three.
- **Address as written, always.** `address_as_written` keeps the source's own
  words ("1311 Alabama street", "Howard st. bet. 20th and 21st"). Parse into
  `street_number` / `street_name` / `street_type` only where the source is
  unambiguous, and **never "fix" a number you think is an OCR error** — record
  it as written and judge it in step 3.
- **Keep the check material.** Cross streets, lot dimensions, block faces,
  neighbouring numbers. These are what confirms a match later; drop them and the
  finding usually dies.
- **Every entry carries its citation locator** — the corpus file path *and* the
  public citation URL or label a page would print. "The archive" is not a
  citation.
- **Quote sparingly.** `raw.text` is the shortest span that justifies the
  extraction. It exists for steps 3 and 6; it never reaches a page.
- **People:** buildings, contractors, architects and named firms. Not residents,
  occupants or owners — **at extraction time, not later.** See "Privacy — hard
  limits" in the root [AGENTS.md](../AGENTS.md).
- **Zero findings is a valid outcome.** Write the file with an empty `findings`
  array and a truthful `coverage` block. That result stops the next run
  re-reading the same haystack, which is worth almost as much as a hit.

Name the batch after the citable unit that was read: `sn85066387-1895.json`,
`japantown-hcs.json`, `vol-31-no-2.json`.

## 3. Place it — an address becomes a parcel

**Most of the mistakes this project can make live in this step**, so the bias is
toward `unresolved`. Each entry ends `resolved` (with `apn`, `path`,
`eas_address`, `method`, `checked_on`), `unresolved` (with a note saying what is
missing) or `rejected` (with a note saying why it never can resolve).

### Do the mechanical half with the tool

[`tools/resolve_eas.py`](tools/resolve_eas.py) does the joins over a whole
findings file — EAS lookup, parcel confirmation against `sf-parcels` and the
roll, the lowest-number rule, the comparison between a record's two addresses —
and writes a `resolution` for every entry with the reason in `method`:

```bash
python3 research/tools/resolve_eas.py fetch    research/findings/<id>/<batch>.json
python3 research/tools/resolve_eas.py report   research/findings/<id>/<batch>.json
python3 research/tools/resolve_eas.py apply    research/findings/<id>/<batch>.json
python3 research/tools/resolve_eas.py manifest research/findings/<id>/<batch>.json
```

`manifest` writes `research/manifests/<batch>.json` — the resolved parcels that
have no page yet, in the shape `seed_pages.py seed-list` reads. Run it after
`apply`; step 4 seeds from it.

Add **`--area-from-nhood`** to `report`, `apply` and `manifest` together when
the site has few or no pages on the streets in the batch. Without it the
resolver files each new page under the area of the *nearest published page*,
which is right where the site has settled a street and scatters a whole
corridor where it hasn't — North Beach came back split across six directories
on the strength of three pre-existing pages. With it, the analysis neighborhood
the assessor and EAS give the parcel decides, every method says which rule
chose the directory, and a directory the site does not use yet is flagged in
the method for the publisher to confirm.

`report` also prints, under the per-finding lines, **the record's own parcel
against the one it resolved to** — the only check in the tool that tests a
finished resolution instead of producing one. It needs
`assessor_block_as_recorded` and `assessor_lot_as_recorded` on the findings, and
it separates a *re-lotting* since the record was written (same block, ordinary)
from *another block* (usually a digit a scan lost, sometimes the record's own
error). **On any source read from a scan, put the printed block and lot on every
finding and read every "another block" line** — that is what stops an OCR digit
becoming a page.

**A range goes in `extra.address_range_as_recorded`, never in `street_number`.**
The resolver reads the range from that field and looks `street_number` up
literally, so `"street_number": "809-811"` comes back "EAS has no address near
it on this street" for an address EAS holds on one parcel. Put the range in the
extra field and the low number in `street_number`; `check.py` fails an
unresolved finding that gets this wrong.

It declines rather than guesses: no EAS record, a range now split across
parcels the record does not choose between, a condominium's worth of parcels on one point, or two recorded
addresses that are both real all come back `unresolved`. **A resolution you
then make by hand must carry `"by_hand": true`** — `apply` recomputes
everything else, so an unmarked hand judgement reverts to `unresolved` the next
time anyone runs it. The pre-1910 refusals are the common case: the guard now
prints the assessor's `year_property_built` for the parcel the join chose
against the record's own date, which is usually enough to decide. **`report` before
`apply`, and read every conflict it prints** — the tool does the lookups, you do
the judgement. A street the source spells its own way is mapped onto EAS's
spelling where squashing punctuation finds it, and otherwise needs an explicit
`--alias RECORDED=EAS`, which it states in the method.

### The judgement half

1. **Check EAS first.** `sf-eas-addresses` in
   [../DATA-SOURCES.md](../DATA-SOURCES.md) is the canonical list of addresses
   that may have a page. No EAS record → not `resolved`, full stop. Note where
   the fact could still live: a surviving building nearby, or the street hub.
2. **Use the source's own check material.** "1311 Alabama, 40x100" against the
   assessor's `lot_area` of 4,000 sq ft is an identification; a bare number is
   an assumption. Put what you checked in `resolution.method` — that sentence is
   the audit trail.
3. **Get the parcel, not just the address.** Join EAS → `parcel_number`, then
   confirm against `sf-parcels` / the assessor roll. Watch for a parcel spanning
   several street numbers (one page, at the lowest number, titled with the
   range) and for condominium APNs (units, not buildings). Rules: root
   [AGENTS.md](../AGENTS.md) → "Directory contract".
4. **Set `path`** to where the fact belongs — an existing page, or the page that
   would exist. Step 4 needs to know which.

### The renumbering traps

- **1909 renumbering.** Numbers changed across much of the city and some streets
  were renamed. A pre-1909 number is not today's number until EAS and a
  cross-street check say so. Worked examples:
  [../san-francisco/corbett-heights/AGENTS.md](../san-francisco/corbett-heights/AGENTS.md).
- **Mission and Eureka Valley did *not* move in 1909.** Every cross-street check
  run in this corpus resolves to today's number. Check anyway; don't extend the
  finding to other neighborhoods.
- **South Van Ness is the dangerous one.** Howard Street until 1932, and
  **renumbered** when renamed. The offset varies by block face — roughly −1,600
  over 17th–24th but about −1,500 near 13th–16th — so **subtracting a constant
  misplaces buildings by a whole block.** Convert per block face using cross
  streets, or leave it unresolved. The table is in
  [sources/loc-newspapers.md](sources/loc-newspapers.md).
- **Pure renames carry their numbers over:** Lexington Avenue → Lexington
  Street, Army Street → Cesar Chavez, Clara → Ord, Dupont → Grant. **The number
  carrying over is not the building surviving.** Four 1903 Dupont Street
  addresses came back with no EAS record at all on Grant Avenue — the block
  faces kept their numbering and lost those particular lots, to the 1903 plague
  clearances and the 1906 fire. Alias the street, then read what EAS says; a
  rename that resolves to nothing is a `rejected` finding, not a bad alias.
- **Streets that no longer exist** (Falcon Street, expunged by the Market Street
  extension) resolve to nothing. `rejected`, with the note saying where the
  story belongs instead.

### Conflicts

A finding that contradicts the assessor's `year_property_built`, or another
source, is **not** a resolution problem. Resolve the address, keep both claims,
and set `conflict` on the finding so step 4 records the disagreement in the
page's `.unknowns`. Never adjudicate, never average, never quietly prefer the
newer source.

## 4. Publish it

Here you are a **site agent**: the root [AGENTS.md](../AGENTS.md) and
[shared/AGENTS.md](../shared/AGENTS.md) govern exactly. This section only says
how research feeds them.

**Before either route, ask what the pages already say.**

```bash
python3 research/tools/check.py --overlap research/findings/<id>/<batch>.json
```

It runs two scans. **By wording** — every resolved finding whose text
substantially repeats the historical record, hook or narrative already on its
target page. **By name and date** — every finding crediting a practitioner the
page already credits within two years, from another source. The second exists
because the first compares phrasing and two sources rarely phrase a credit the
same way: volume D–F of the professionals biographies had 20 duplicates caught
by wording and **35 more caught only by name and date**, nearly all of them a
prolific builder's houses already documented one by one by the neighbourhood
survey devoted to that builder. A source organised by architect or builder will
overlap a neighbourhood survey of the same person almost completely, and the
neighbourhood survey usually says more. Two statements
cover the same buildings often enough that a citywide batch will land on parcels
a neighbouring survey has already documented. Read each line and decide *before*
writing: decline the duplicate, or trim it to the part that is new. Doing this
after publication costs a re-render and an entry that may contradict a better
one already on the page.

**Route A — the page exists, or should and it's a handful.** Add each fact to
`data.json` by hand, normally as a `historical_record` entry (`date`, `kind`,
`description`, `source`), and add the source to the page's `sources` array with
the citation label from the dossier. Then regenerate the HTML **in the same
commit**:

```bash
python3 scripts/seed_pages.py render <path to the page, street or area>
```

**`render` takes a repo-relative path, and a finding's `resolution.path` is
not one.** Findings store the site path — `/san-francisco/nob-hill/...` — and
`render` treats a leading `/` as an absolute filesystem path, so it exits with
`render: no such path` on the *first* bad argument and renders nothing after
it. Strip the slash. To render exactly the pages a batch published:

```bash
python3 - <<'EOF' > /tmp/pages.txt
import json, pathlib
d = json.load(open("research/findings/<id>/<batch>.json"))
seen = []
for f in d["findings"]:
    r = f["resolution"]
    if r.get("status") == "resolved" and r["path"].strip("/") not in seen:
        seen.append(r["path"].strip("/"))
print("\n".join(seen))
EOF
cat /tmp/pages.txt | xargs -n 60 python3 scripts/seed_pages.py render
```

`data.json` is the only file you write; `validate.py` fails if `index.html` is
not exactly what the renderer produces from it. A conflict from step 3 goes in
`.unknowns`, stated plainly and left unadjudicated.

**Route B — the source names many buildings with no pages.** Generate
`manifests/<batch>.json` with `resolve_eas.py manifest` (above), then:

```bash
python3 scripts/seed_pages.py seed-list --manifest research/manifests/<file>.json
python3 scripts/seed_pages.py districts
python3 scripts/build_sitemap.py
python3 scripts/build_map_index.py
python3 scripts/build_link_index.py
python3 scripts/validate.py
```

The seeder only creates pages that don't exist, and it knows nothing about the
source — the facts still have to be added to those pages afterwards. Seeding is
the scaffold, not the research.

Two things bite when adding those facts in bulk:

- **The parcel decides the page, not the path.** A corner building the source
  addresses on both its streets resolves to two paths and has one page; the
  resolver says so in its note. Key the write on the APN and fix the finding's
  `path` to the page the parcel actually has.
- **Render every page you write, and read what `render` reports.** A page it
  counts as *opted out* (`"rendered": false`) took your `data.json` edit and
  will not show it — that page's HTML is hand-maintained, so the fact has to be
  put there by whoever maintains it. A page it counts as *failed* did not get
  the fact either. Neither is silent: `render` prints both, and `validate.py`
  prints the opt-out count on every run.
- **Intersect your page list with `scripts/render-backlog.txt` first.** That
  file grandfathers pages whose HTML the renderer cannot yet reproduce, and
  `render` does not consult it: a bulk render sweeps any backlogged page in the
  list and can drop hand-written content the renderer has no `data.json` key
  for. Render those pages last, read `git diff` on each, and where the diff
  loses something, restore the file, add your fact to its HTML by hand and leave
  its backlog line in place.

**Check the neighborhood directory the resolver chose before you seed.** It
files a new page under the area of the nearest published page, which is right
where the site has settled a street and wrong where it hasn't: Van Ness Avenue
had three pages in the whole city, and one corridor came back split across five
directories. On a street that thin, file on the analysis neighborhood the
assessor and EAS give the parcel and say so in `resolution.method`.

### Rules that catch publishers out

- **A page is a designed data page, not an article.** Before writing a sentence,
  name the component that could carry the fact instead. Usually one can.
- **Never name the source in the page body.** "The newsletter says…", "a survey
  records…", "according to the archive" — all wrong. The Sources footer is the
  attribution. The trap is not a deliberate citation but a **hedge carried over
  in your own voice** — *the volume gives no year*, *the survey records it as
  demolished* — which reads on the page as the source talking about itself.
  State the fact ("Since demolished"), or drop the hedge and let
  `date_precision` carry it. `check.py` fails on the phrasing it can recognise;
  grep your own descriptions for the source's noun before you commit. The one documented exception is
  [sources/celebrity-residence-guides.md](sources/celebrity-residence-guides.md),
  whose claims are attributed in the body precisely because they're weak.
- **Facts, not wording.** Re-express; never reproduce the source's sentences or
  their structure.
- **An undated credit is not automatically a decline.** `building.architect`,
  `building.builder` and `building.developer` hold a credit with no year, and a
  page can say who built it without claiming when. Decline only where no spec
  row fits either.
- **Privacy binds at publication too.** Buildings, contractors, architects,
  firms, and historical figures already published with dates. Not residents,
  occupants or owners.
- **Don't restate what a component already shows**, and never open the timeline
  with prose. A dated fact joins the page's one timeline in date order; it never
  opens a second rail.

**Then check that the writes actually landed.**

```bash
python3 research/tools/check.py --landed research/findings/<id>/<batch>.json
```

A page that already names the same practitioner under another spelling makes an
`if not already set` write a no-op, and the finding is marked published anyway.
`--landed` reports every published finding whose page carries neither its
description nor a spec row naming anyone it records. Each one is a decline, or a
description trimmed to the part the page lacked with `publish.note` saying so.

### Mark the findings file in the same commit that edits the pages

Every entry you touched gets `publish.status` set to `"published"` with its PR
number, or `"declined"` with a reason. **An entry left unmarked will be
re-published by the next run**, and telling "not done yet" from "done but
unrecorded" costs a full verification pass. This has happened; see
[AGENTS.md → What we've learned the hard way](AGENTS.md#what-weve-learned-the-hard-way).
`check.py` now fails the run if a file has published entries and resolved ones
with no decision recorded. It also fails when two findings headed for a page
resolve to the same parcel under different paths — the corner-lot case, where
the city addresses one building on both its streets and only one of the two
pages will ever exist.

## 5. Check it

Cheap to run, and the only thing standing between a long pipeline and a
confidently wrong encyclopedia. **Audit every entry of a source's first
published batch** — that is when systematic errors are cheapest to catch. After
that, a handful per batch is enough, weighted toward addresses resolved by
inference and anything on a street the dossier flags as renumbered.

1. **The fact on the page matches the finding**, and the finding matches
   `raw.text`. Drift shows up as a date that gained precision it never had, or a
   hedge that got dropped.
2. **The citation resolves.** Open the URL, or confirm the issue/section
   reference is exact enough for a reader to find it. Broken or vague citations
   are the most common real defect.
3. **The address is still right.** Spot-check `resolution.method`, especially on
   renumbered streets.
4. **No people leaked** — residents, occupants or owners in prose, a `hook`, a
   `narrative`, or a permit description.
5. **No source prose leaked** — sentences lifted or lightly paraphrased, or a
   page body naming the archive it came from.
6. **The page still obeys the design contract** — facts in components, prose
   only where it earns its place, `python3 scripts/validate.py` clean.

Corrections are an ordinary site edit in the same PR.

## 6. Close the books

A run's real output is a module that tells the truth about where things stand.
Leave all of this true:

- **The findings file** — every entry carries the decision it is owed:
  `resolution` for every entry, `publish` for every resolved one, `coverage`
  filled in even when nothing was found.
- **The dossier** (`sources/<id>.md`) — the coverage note and the `Verified:`
  line, naming what was read and what wasn't, **and what the run learned.** A
  run that doesn't update its dossier has thrown away most of its value.
- **The register** ([SOURCES.md](SOURCES.md)) — status and coverage phrase, in
  counts, not adjectives.
- **An issue** for what you didn't finish, using
  [templates/issues.md](templates/issues.md). Search open issues for the source
  id first.
- **Clean checks**, then a commit on a branch — never `main` — whose message and
  PR body carry the run's counts:

```bash
python3 research/tools/check.py
python3 scripts/validate.py        # if a page was touched
```

Report the run the same way: **read N, found M, resolved K, published J.** Zero
findings, reported honestly with its coverage recorded, is a completed run.

### The PR body

The one-line counts say how much a run found. They do not say **where it
landed**, which is the first thing a reader of the diff wants and the thing a
150-file diff hides. So a PR body opens with the headline counts and then a
table, one row per neighborhood directory:

```bash
python3 research/tools/check.py --report research/findings/<id>/<batch>.json
```

That prints the table ready to paste. Its columns:

| column | what it counts |
|---|---|
| **Pages created** | pages this batch's own commits added |
| **Pages edited** | pages that already existed and gained a fact |
| **Facts published** | findings that reached a page; more than one can land on the same page |
| **Conflicts stated** | sentences written to a page's `.unknowns` — the source disagreeing with itself or the assessor, left unadjudicated |
| **Dates disputed** | pages where the source's construction year disagrees with the assessor's, in `building.completed_conflict` |
| **Declined** | resolved to a parcel and then not published — a duplicate of what the page already carries, an undated claim with no component to hold it, a fact a better source states first |

**Only findings that reached a parcel can be in it**, because the neighborhood
is a property of the parcel and nothing else. Unresolved and rejected findings
have no row and no column; the tool counts them in one line underneath, which is
the honest shape. Do not invent a neighborhood for them from the street name —
a street runs through several, which is the same mistake `--area-from-nhood`
exists to prevent.

Below the table, say what did *not* resolve and why, grouped by reason. A reader
who sees "26 no EAS record, 9 ranges now split across parcels, 5 condominiums"
learns what the source is like; a reader who sees "41 unresolved" learns
nothing.

---

# A prospecting run

Finding material that carries San Francisco street numbers and that a reader
could not have found by searching that address.

## Judge a source on four things, in this order

1. **Search-invisibility.** Would a reader searching "1311 Alabama Street" ever
   see this? If yes, it is a low-value target no matter how big it is.
2. **Address density.** Does it name street numbers, or only streets,
   neighborhoods and metes-and-bounds? "Between 19th and 20th on the east side
   of Folsom" is not an address. A source that never gives numbers is a context
   source, not a page source.
3. **Datedness.** Can a fact from it be pinned to a year? Undated claims are
   nearly unusable under the evidence bar.
4. **Access and licensing.** Can we get it lawfully and cite it stably?
   Paywalls, login walls and terms forbidding automated access make it a
   `needs-human` lead, not an obstacle to route around.

**Size is not on that list.** Ten thousand pages that yield four addresses is a
good source. A fifth thing decides the ordering in practice: **whether the
source breaks into finishable batches.** One statement is one issue is one run;
a source with no natural batch boundary can be excellent and still unstartable.

## Two gears — picking the wrong one wastes the run

**Triage** — several unverified leads, and you don't yet know which deserve the
effort. Per lead: the four judgements above, one sampled example proving it
carries numbered addresses with dates, and a dated verdict in the **Leads**
table's `triaged` column with its evidence under
[SOURCES.md → Triage notes](SOURCES.md#triage-notes). No dossier, no issue.
Rejected leads are struck through in place with the reason, so nobody spends a
run rediscovering them. *Thirteen dossiers written before knowing which three
are worth mining is thirteen sessions spent to learn what three would have told
you.*

**Promotion** — one lead has survived triage, or arrives obviously strong:

1. A dossier at `sources/<id>.md`, from
   [templates/source-dossier.md](templates/source-dossier.md), with a real
   sampled example in it.
2. A row in [SOURCES.md](SOURCES.md) with status `open`, and the lead's row and
   triage note deleted.
3. An issue naming the first batch — or, better, **keep going and mine it in
   the same run.** Promotion and the first batch is a well-sized run.

Pick the `id` lowercase, hyphenated, stable, and descriptive of the source
rather than the project (`cdnc-sf-papers`, not `newspapers-2`). **Ids are
permanent** — changing one breaks every citation that uses it.

## Before you start

Check [SOURCES.md](SOURCES.md) — registered and leads both — and search open
issues for the source id. Don't re-prospect what's already known. Then establish
what the source actually is (publisher, dates, format, where it lives, whether a
stable citation URL exists) and **sample it** before writing anything down. A
lead promoted on a guess wastes the next run.
