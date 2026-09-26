# Reference — the things you look up

[AGENTS.md](AGENTS.md) is the rules core: what binds every task. This file is
what a task reaches for once it knows which job it is doing — the `data.json`
schema, the page types and their traps, the seeding procedure, the homepage
grid, and the reasoning behind rules that look arbitrary without it.

Read a section. Don't read the file.

| If you are… | read |
|---|---|
| writing or editing `data.json` | [data.json shape](#datajson-shape) |
| creating pages that don't exist yet | [Seeding a new area](#seeding-a-new-area) |
| touching a historic-district page | [Historic districts](#historic-districts) |
| touching a park, plaza or place in a park | [Place pages](#place-pages) |
| deciding whether a parcel may be a page | [One page per building](#one-page-per-building) |
| touching the homepage | [The homepage](#the-homepage) |
| wondering why the HTML is generated | [Why `index.html` is a build artifact](#why-indexhtml-is-a-build-artifact) |
| writing prose and want the worked examples | [Writing pages — the examples](#writing-pages--the-examples) |

---

## data.json shape

Keys are flexible — capture what exists, omit what doesn't — but follow this
pattern, and always include `address` and non-empty `sources`:

```json
{
  "address": "123 Example Street, San Francisco, CA 94114",
  "path": "/san-francisco/castro/example-street/123/",
  "hook": "One concrete sentence, under 22 words, for the street hub's list. No superlatives.",
  "sub_area": "Optional. The smaller or better-known place the neighborhood goes by here — appended to the line under the heading, after the address or building type. The designation alone, never the parent neighborhood: \"Telegraph Hill\", not \"Telegraph Hill, North Beach\".",
  "apn": "0000-000",
  "coordinates": { "lat": 37.0, "lng": -122.0 },
  "parcel": { "year_built": 1904, "land_use": "...", "units": 2 },
  "public_open_space": [
    { "name": "555 Mission St", "type": "Plaza", "established": "2008",
      "hours": "Open at all times", "location": "...", "seating": "...",
      "source": "sf-popos" }
  ],
  "occupants": [
    { "name": "Burma Superstar", "cuisines": ["Burmese", "Asian"],
      "opening_hours": ["Su 11:30-15:00,17:00-22:00", "Fr,Sa 11:30-15:00,17:30-22:00"],
      "listed_address": "309 Clement Street", "source": "bites" }
  ],
  "public_art": [
    { "title": "Moonrise Sculptures", "artist": "Ugo Rondinone",
      "type": "Sculpture", "medium": "aluminum", "location": "plaza",
      "access": "...", "art_requirement_case": "2001.798X",
      "artist_link": "https://...", "source": "sf-public-art" }
  ],
  "permits": [
    { "number": "...", "filed": "1998-04-02", "status": "complete",
      "description": "DBI's own words, verbatim.",
      "description_edited": "Optional. The sentence the page shows instead.",
      "source": "sf-building-permits" }
  ],
  "permit_summary": {
    "count_on_file": 3102, "range": "1981–2026", "shown_on_page": 25,
    "note": "Why the timeline shows a subset — rendered below the timeline."
  },
  "historical_record": [
    { "date": "1901-04-06", "kind": "building contract",
      "summary": "Optional short label, only when the entry needs one.",
      "description": "One dated, sourced fact from a historical source.",
      "source": "loc-sf-call-1901-04-06" }
  ],
  "narrative": {
    "lead": "One or two sentences carrying only what no component carries.\nOmit the field entirely when the components already say everything.",
    "sections": [
      { "heading": "Notable residents",
        "body": "Genuine story prose only. Omit this array when the page has\nno story beyond the lead. Do not restate facts the components show,\nand never open the permit timeline with one." }
    ],
    "community_note": "Optional. Unverified community contribution, rendered in a labeled .community-note block."
  },
  "sources": [
    { "id": "sf-building-permits",
      "name": "SF Building Permits (DataSF)",
      "supports": "Optional. Which claim on the page rests on this source.",
      "cites": "Optional. Which passage within the source the page rests on.",
      "query": "https://data.sfgov.org/resource/....json?...",
      "retrieved": "2026-07-21" }
  ]
}
```

### `permits` vs `permit_summary`

**`permits` is what the page shows; `permit_summary` says what exists.** For an
ordinary building they are the same thing and there is no summary. A downtown
office tower is not ordinary: DBI holds 3,102 permits for 1 Market Street, one
per tenant per floor, and a 3,102-item timeline is not a page. So the seeder
keeps the largest filings by stated cost plus the earliest on file, and
`permit_summary` states the full count and the rule it used — rendered as one
line *below* the timeline, never above it. The DBI query in `sources` still
returns all of them, which is what makes the subset honest rather than a
silent edit. Never write a figure into that note that isn't computed from the
data you kept.

### `description` vs `description_edited`

**`description` is DBI's words; `description_edited` is ours.** The renderer
shows the edit where there is one and falls back to running `description`
through the mechanical cleaner where there is not. Keep them both: the raw
text is what the `sf-building-permits` citation vouches for, and the redaction
pass and the unit-generalizer read it, so overwriting it would make the page's
own record unverifiable.

Write an edit only where reading the filing against the rest of the record
says something the filing alone does not — that this was the only part of a
project ever carried through, that the matching filing for the next flat was
cancelled, that a proper noun the cleaner lowercased is a street name. Do not
write one to restyle a sentence the cleaner already renders correctly.

### `supports` vs `cites`

Both narrow a citation, from opposite ends. **`cites` says where in the source
the fact is** — which photograph in a newsletter, which entry in a directory.
**`supports` says which of the page's claims rests on the source**, and leads
the footer line. A tourist guide listing where musicians once lived backs one
sentence of a page otherwise built from city records; `"supports":
"Notable-resident claim"` is the difference between citing it for that claim
and appearing to cite it for the parcel.

A survey's own table or appendix is the same thing: `cites` on the source entry
("Appendix A, Table 1"), not a key inside `historic_survey`, which is for what
the survey *found* rather than where it printed it.

### Four traps inside `assessment` and `historic_status`

Both blocks are the assessor's and Planning's columns under this site's names,
and a fact filed one level too low renders as nothing while the block around it
renders fine.

- **A tax exemption is `assessment.exemption`**, the roll's own word for the use
  it was granted for ("Welfare", "Church"), with `exemption_value` where the
  roll gives the exempted amount — the two ride in one "Tax exemption" spec row.
  The amount is not the chart's total: at 57 Post Street it is under half of it.
- **`historic_status.note` closes the timeline**, the way `parcel.note` and
  `assessment.note` do: how far to trust a status the page prints — a parcel
  inside a district boundary whose contributing status nobody has established, a
  Category A finding that came from a project's evaluation rather than a survey.
- **A city landmark's name and number are the top-level `city_landmark`**
  (`{name, number, source}`), which the "City landmark" spec row reads; the
  designation itself is dated, so it is a `historical_record` entry like
  anything else dated, and the ordinance number belongs in that entry. Nothing
  about a landmark goes under `historic_status`, whose job is Planning's CEQA
  columns.
- **Planning's build year is `yearbuilt`** — its spelling, not
  `planning_year_built` or `year_built_reported` — and the page prints it only
  where it contradicts the assessor's, on the line closing the timeline.
  Planning's name for the building is `survey_name`: `historic_status.survey_name`
  is the raw upper-case string the dataset gives, and the top-level key is the
  one the hero tag reads.

### `hook`

The one-line description a hub shows beside the link. It lives here, not in the
hub's HTML, so a hub can be rebuilt without losing it. It is optional: when a
page has no `hook`, the hub derives a plain one from the building's data. Write
one whenever you can say something better than "a 1901 two-flat" — it then
survives every rebuild.

### `historical_record`

The one key for **dated facts that come from a historical source rather than a
city dataset** — a pre-DBI building contract, a fire, a period advertisement,
what stood on the site before. One entry per fact: `date` (ISO where known, a
bare year or a phrase where not), `kind` (`building contract`, `fire`,
`advertisement`, `sale`, `site history`, …), `description`, and `source`
matching an id in `sources`. `summary` is an optional short label; entries may
carry extra keys for what the record itself stated (`cost`, `lot_as_recorded`,
`cross_streets`). Its entries render as items on the page's one `.vtl`, in date
order among the permits — never as prose, and never as a second rail of their
own.

- **An entry from the [news module](news/AGENTS.md) is the exception to
  `description`.** It carries `headline`, `outlet` and `url` instead, and
  renders as the headline in italics followed by the outlet as a link. We do
  not summarize a live outlet's reporting in our own words; the headline is the
  entry and the link is where the story is.
- **One entry per dated event, not per record.** Where a single event left
  several records — the assessor photographing a corner parcel once per street
  number on the same day — `source` is a **list** of their ids and the entry is
  one item on the rail. Two items with the same date make a reader think the
  clock stuttered. Give each of those sources a `title` (the address it was
  filed under) so the links on the merged item can be told apart.
- It replaced `site_history`, which said the same thing under a second name,
  and `building_history.events` (the Corbett Heights pages), migrated here by
  issue #148. Don't reintroduce a third: a dated historical fact goes here.
- **Scalars that aren't a dated fact go on `building`, not here.** An
  architect, a builder, a first owner, what stood on the site before, what the
  build cost, a moved building's former address, the number it answered to
  before the street around it was renumbered, an unresolved conflict in the
  record — `building.architect`/`architect_note`, `building.builder`/
  `builder_note`, `building.first_owner`, `building.site_before`,
  `building.cost_usd`, `building.relocated_from`, `building.former_address`,
  `building.conflict`. A dated event belongs on the timeline; a standing fact
  about the building belongs on `building`, whichever page it first shows up
  on.
  - `relocated_from` and `former_address` are not the same fact:
    `relocated_from` is a building that moved, `former_address` an address
    that did. Neither is `also_addressed`, which is a number the parcel
    still answers to.
- **`building.style` and `building.subdivision`** are the same shape for two
  facts a survey usually carries and sometimes doesn't: the architectural style
  where the source stating it is a newsletter or a context statement's prose
  rather than an inventory (`historic_survey.style` is the commoner case and
  has its own row in the survey panel), and the tract the lot was sold out of.
  Neither is `parcel` data — nothing in the assessor's roll says either.

### `occupants`

**The businesses trading from the building today**, one entry per merchant,
rendered as one "Current occupant" panel heading the aside. `name`, `kinds`
(what the business is — "Yoga", "Fitness" — or `cuisines` where a food
directory wrote them; both render as the muted line under the name),
`opening_hours` (schema.org strings, as the directory publishes them — the
renderer formats them and marks the days not listed as closed),
`listed_address` (the merchant's own door, shown only when it isn't the
page's lead number), `unit` (on a condominium building's page, the unit the
merchant trades from — only where a city record ties the two together),
`source`, matching an id in `sources`, and `also_listed_by`, the other source
ids that list the same business, each also in `sources`.

- **The panel's "Last updated" date is that source's `retrieved`.** Hours
  drift within days, so the date is on the panel as well as in the footer,
  and a refresh that re-reads the directory updates both by changing one
  field. It dates the hours, so an entry with none omits it — and on a panel
  of several it sits with the entry whose hours it dates, unless every entry
  shares one date, in which case the single line closes the panel. Likewise an
  offer only one entry has earned renders under that entry. See
  [shared/BLOCKS.md → Current occupant](shared/BLOCKS.md#current-occupant--panel-occupant).
- **A referral offer belongs to the source, not the entry.** The renderer's
  `REFERRALS` table, keyed by source id, is the only place an offer lives; an
  entry never carries a link of its own, so a merchant from a directory with no
  referral programme never shows one.
- **An offer is a link, or a link and a code.** Where the programme hands out
  a code that no link carries — Insomnia Cookies' — the row adds `code`, and
  the block inverts: the code takes the accent and the box the button would
  have had, states the offer inside it, and the merchant's address drops to an
  ordinary link beneath, with the disclosure line saying where the code goes.
  The code is never hidden inside the link, and never rendered only by script.
- **One business is one entry, whatever number of directories list it.** The
  second directory goes in `also_listed_by` and its button joins the panel;
  the entry's facts and its "Last updated" date are `source`'s, the most
  recently read of them. Two entries for one business would read as two
  businesses.
- **A business is not a person** — see "Privacy" in [AGENTS.md](AGENTS.md).
  The merchant's name, never its owner's.
- Where the entries come from, and how a directory is refreshed, is
  [merchants/AGENTS.md](merchants/AGENTS.md).

### `narrative`

Where all of a page's prose lives — it replaces the old `index.md`. `lead` is
one or two sentences, and is omitted when the components already carry
everything; `sections` is an optional array of `{ heading, body }` for genuine
story, omitted entirely when there's none; `community_note` holds a labeled,
unverified community contribution. Prose here must obey "Writing pages" in
[AGENTS.md](AGENTS.md) — above all, it never restates a structured fact (year
built, room count, permit costs, assessed value) that a component already
renders, never introduces the permit timeline, and never narrates where a fact
came from. `index.html` renders `narrative` verbatim into `.lead` /
`.section-head`+`.prose` / `.community-note` blocks.

---

## Page types and their traps

### One page per building

**One page per building — which means one page per parcel, not per street
number.** Units are documented within their building's page, never as separate
pages.

- **A parcel spanning several street numbers gets ONE page**, in the directory
  of its *lowest* number, titled with the range (e.g. `711/` → "711–715 Castro
  Street"). The assessor's `property_location` reveals these: `0715 0711
  CASTRO` means the parcel runs 711–715. Confirm by checking permits — DBI
  files the same permit numbers under every number on the parcel. Record the
  range in `data.json` under `address_range`, and say so on the page; never
  create a separate page per number, and never treat the shared permits as
  separate events.
- **Condominium parcels are the reverse trap**: each unit has its own APN, and
  the assessor reports `0` lot area and `0` stories for it. Those are *units*,
  not buildings — do not give each one a page. Documenting a condo building
  means establishing which parcels belong to it, which the datasets here don't
  state directly; until that's resolved, skip them and flag it for a human.

Directory names: lowercase, hyphens, no punctuation. Street numbers are the
bare number (`4127`, `4127a` for lettered addresses). The canonical address
list is the EAS dataset in [DATA-SOURCES.md](DATA-SOURCES.md), and a page's
address comes from it wherever it can. **An address EAS lacks, or holds with no
parcel, may still have a page** when a source puts something real there — a
merchant directory's listing, say — and the page's `unknowns` says how the
address and the city's records differ. Place it by the parcel the source's own
coordinates fall on, file it under that parcel's page when one exists, and
where no parcel carries it the page is the address with no parcel facts at all.
A place outside the city never gets one.

### Historic districts

**Historic districts are the fourth page type, and the only one that isn't part
of the containment tree.** A district page lists the documented buildings
standing inside it and the streets it runs through, and carries the district's
own record — period of significance, register standing, local designation —
from the city's survey. It sits at **city** level, not under a neighborhood,
because a great many of them are not contained by one: the Chinatown Historic
District runs through five neighborhood directories and
Kearny-Market-Mason-Sutter through six.

- **They are generated, never hand-listed**: `python3 scripts/seed_pages.py
  districts` reads every address page's `historic_district` and
  `also_in_districts` and rewrites the hubs, keeping each one's hand-written
  lead the way `hubs` keeps a street's. Re-run it whenever pages are added or
  removed; `validate.py` fails until it is current, in both directions — a
  district page missing from its hub, and a hub whose district no longer has
  buildings here.
- **A district needs five documented buildings to get a page.** Below that the
  list says nothing the one or two pages carrying it don't already say, and a
  page that thin is a doorway rather than an entry. Those buildings keep their
  district panel; it just has nowhere to link. **Facets with no record of their
  own behind them — decade, zoning, property class — are not pages and are not
  to be added.**

### Place pages

**A place page is a public space: a park, a plaza, a community garden, or a
named place inside a park** — Mission Dolores Park, Union Square, the Rose
Garden. None of them is a building, and most have no street number, so they
don't fit `/<area>/<street>/<number>/`. They sit one level up, at
`/<city>/<area>/<place-slug>/`, beside the street directories of the
neighborhood they lie in, and the neighborhood hub lists them under "Parks and
public spaces" — generated, like its street list, in both `index.md` and
`index.html`.

- **The source is `place.json`, not `data.json`.** Same rules — every fact
  cited in `sources`, prose only in `narrative`, a dated fact in
  `historical_record`, `index.html` generated and never committed — but a
  different file, so that every tool that walks the tree for address pages
  goes on finding address pages only. The vocabulary is
  `seed_pages.PLACE_KEYS`; `render` re-renders both kinds, and `validate.py`
  holds a place page to render parity like any other.
- **They are seeded from a manifest**, `research/manifests/rpd-places.json`,
  by `python3 scripts/seed_pages.py places --manifest <file>`, create-only
  like `seed-list`. Each entry is either a Rec & Park **property** (`kind:
  "park"`, by `property_id`) or a group of rows from its **facility inventory**
  (`kind: "facility"`, by `rpd_object_ids`) with the name its heading uses.
  The manifest records what took judgement: the parcels a property covers
  (a spatial join against `sf-parcels`), the directory it is filed under (the
  parcel page's, else the neighborhood of the address pages nearest it), and
  the city addresses that fall inside a facility's outline. See
  [DATA-SOURCES.md → sf-rpd-properties](DATA-SOURCES.md#sf-rpd-properties--recreation-and-parks-properties).
- **A place and a parcel are two pages, linked both ways.** The parcel page
  keeps the assessor's and the permit office's record of the land; the place
  page is the park, and lists the parcels it covers. An address page whose
  parcel carries a place shows it in a "Public space on this parcel" panel, so
  a reader who lands on 333 Post Street looking for Union Square finds it. A
  place that shares a parcel with another says so; the page never claims one
  park is part of another on the strength of a shared parcel alone.
- **Golden Gate Park is a neighborhood directory, and its hub is the park.**
  Its places come from the facility inventory, curated to what a visitor goes
  to — gardens, lakes, museums, windmills — and each names the park as its
  `part_of`. Its one parcel, 1700001, is the address page on Fulton Street.
- **A place is where its events land.** A park or plaza whose venue string
  `events/venues.json` knows carries an "Upcoming events" panel for the next
  30 days, and the homepage map's event dots open the place page — see
  [events/AGENTS.md](events/AGENTS.md). Prefer the place page over the parcel
  it sits on when pointing a venue at a page.
- **A slug that collides with a street directory** in the same neighborhood
  takes `-open-space`: South Park is both a street and the park inside it.
- The Presidio is federal land and not in either Rec & Park dataset; it is
  not yet covered.

### Hub pages and their two hand-maintained sections

Hub pages (`index.md`/`index.html` at city, neighborhood, street and
historic-district level) list and link what's beneath them. Keep them current
when adding pages.

**A street hub, a historic-district hub, and the historic-districts index
carry their list in `index.html` only.** `write_street_hub` / `write_district_hub`
/ `write_districts_index` regenerate that list wholesale from their children on
every run — each entry is a projection of a child `data.json` (or, for a
district, of the pages that name it) — so it holds no information `index.md`
would preserve by keeping a second copy (issue #151: 766 `index.md` files once
duplicated exactly this). `index.md` at these three levels keeps only what a
rebuild can't reconstruct: the lead paragraph (`hub_lead`) and any hand-added
section beyond the template (`hub_extra_sections`). `validate.py`'s
`check_hub_covers_children` and `check_hub_sync` read the list back out of
`index.html` for these levels, and still enforce that a child's explicit
`data.json["hook"]` wins — see `street_hub_hook_overrides`.

**A neighborhood hub is different: its street list lives in both files, because
one entry can carry a hand-written override.** `write_neighborhood_hub` reads a
street's existing line back out of `index.md` before rewriting the list
(`existing_street_hooks`) — a person's replacement for the generated summary —
so removing the copy in `index.md` would delete that override on the next
rebuild. `check_hub_sync` for a neighborhood hub therefore still compares the
two files line for line, exactly as it always has.

**A neighborhood hub also links sideways, and those two sections are
hand-maintained.** "Historic districts here" lists every district with a hub
that holds a documented building in this neighborhood; "Adjacent neighborhoods"
is a sentence or two naming the ones it borders, per the city's Analysis
Neighborhoods boundary file. `write_neighborhood_hub` rewrites only the street
list and does not know about either, so nothing regenerates them: when a
neighborhood's first page in a new district lands, add the district to that hub
by hand, in `index.md` and `index.html` both. Neither section uses the
`<a>…</a><br><span class="hook">` pairing, which is what keeps `validate.py`'s
`check_hub_sync` out of them — so the two files agreeing is on you.

A street hub that has grown its own sections beyond the lead+list template (a
"Sources" section, a "The street itself" write-up) is left untouched entirely
by `seed_pages.py hubs` — the command reports it as skipped rather than
clobbering it. From that point its list is hand-maintained in both files, the
same as any other page a person has taken over — the split above only applies
to a hub the generator still rebuilds.

---

## Seeding a new area

Every fact on a fresh page comes from a DataSF API. Don't hand-author those one
at a time:

```
python3 scripts/seed_pages.py plan --neighborhood "Castro/Upper Market"
python3 scripts/seed_pages.py seed --neighborhood "Castro/Upper Market" \
                                   --city san-francisco --area castro
python3 scripts/build_site.py
python3 scripts/validate.py
```

`seed` joins the five datasets in [DATA-SOURCES.md](DATA-SOURCES.md), decides
which parcels may become pages (skipping condominium units and parcels with no
assessor record), writes `data.json` + `index.html` for each **new** one, and
rebuilds the street hub pages beneath the neighborhood. It varies each page's
composition from the data it actually has — a parcel with a timeline, public
art or prose gets the two-column split, its panels in the aside; a parcel with
nothing but panels runs them full width — so the pages are not identical
documents with the numbers swapped.

- **The output is a first draft, not a finished page.** It carries no
  `narrative`, because the script won't invent prose, and per "Writing pages" a
  page whose components carry everything is finished with no prose at all.
  Everything after the draft is hand work.
- **A bug found after seeding is fixed in `data.json`, on the affected pages,
  then re-rendered.** `seed` will not repair anything already on disk — by
  design; that is `render`'s job. If the bug is in the rendering rather than in
  the data, patch `seed_pages.py` and re-render the pages it affects.
- **A thematic set of parcels uses `seed-list`, not `seed`.** `seed` walks one
  analysis neighborhood and takes the residential parcels in it. When the set
  is defined by something else — the buildings in a city inventory, say — name
  the parcels in a manifest under `research/manifests/` and run `seed-list
  --manifest <file>`. It joins the same datasets onto the parcels you give it
  and honours the same create-only rule. Use it downtown even for a whole
  neighborhood: those blocks have been re-parcelized so often that EAS's
  `parcel_number` is frequently a retired APN, and `seed`'s address→parcel join
  silently drops those parcels (see DATA-SOURCES.md → sf-parcels).
- **Review a sample before committing.** Read a handful across the range — a
  parcel with no permits, one with dozens, one spanning several street numbers,
  one in a historic district — and check the numbers against the cited queries.
- **Privacy: run the name check.** `python3 scripts/seed_pages.py names
  --neighborhood "<nhood>"` flags personal names in permit text before they
  reach `data.json`. Review what it flags, add the real names to
  `scripts/permit_redactions.json`, and re-seed. Product and material brands
  (window and roofing manufacturers) are specifications, not names — leave
  those alone.
- **Privacy: read what the room rule could not.** `generalize_rooms` rewrites a
  numbered room to a count only where `is_hotel` holds — the assessor calls the
  parcel a hotel, or the page's own `building.name`/`former_name` does and the
  roll still calls it residential. Everywhere else a numbered room may be a
  dwelling or may be a room named by its function, and only the sentence says
  which. Each one that a new area turns up gets an entry in
  `scripts/permit_room_decisions.json`: `rewrite` with the exact `old`/`new`
  text, or `keep` with the designator left alone, and in both cases a `why`
  that states the evidence. `validate.py` checks every entry against the page
  it names, so a decision whose text DBI later revises fails the build instead
  of rotting quietly.

---

## Why `index.html` is a build artifact

`index.html` is not source. It is a build artifact stored as source: 91% of
address pages regenerate byte-identically from `data.json` through the renderer
the repo already owns, and only 0.7% of `data.json` files carry a `narrative`
at all. Hand-syncing the two was the repo's largest recurring cost and it
failed silently — 358 pages once carried markup a 10,286-file commit was meant
to strip.

So `scripts/seed_pages.py` enforces the split on its own, with one command each
way. `seed` writes into a directory only when the directory is empty of a page,
so a second run creates nothing. `render` does the opposite and only the
opposite: it rewrites `index.html` from the `data.json` already on disk and
never invents a page. Pages carry no marker saying who wrote them, because
there is nothing to decide — the facts are yours to edit either way, and the
HTML is never yours to edit at all.

### The render backlog, and why there isn't one

`scripts/render-backlog.txt` used to grandfather 968 pages whose committed HTML
the renderer could not reproduce. The sweep emptied it and the file is gone, so
`render` now holds nothing back and `validate.py` checks parity on every page.
`--include-backlogged` remains a no-op flag for the same reason.

What the sweep taught is worth keeping: **on the pages that had drifted, most of
what the renderer "could not reproduce" was content sitting in `data.json` under
a key nothing read.** Before concluding a page needs hand-maintained HTML, grep
its `data.json` for the fact you think is stranded — it was there 25 times out of
the 119 the sweep first looked like it would delete, and the fix each time was a
row in the renderer, not an exemption.

### `"rendered": false`

A page whose HTML genuinely has to be maintained by hand sets `"rendered":
false` in its `data.json`; `render` then skips it and `validate.py` skips its
parity check. **Treat that as close to never.** An opted-out page stops picking
up site-wide design changes and goes stale silently — `validate.py` prints the
opt-out count on every run for that reason. Before reaching for it, ask whether
the renderer should learn the block instead; it usually should, and that is a
change to `seed_pages.py`, which is a human's call under ground rule 6.

---

## The site is built, not committed

The repository holds the sources. It does not hold the site. Running
`python3 scripts/build_site.py` turns one into the other in about a minute,
GitHub Actions runs it on every push to `main`
(`.github/workflows/deploy.yml`), and `actions/deploy-pages` publishes the
result. Merging to `main` is still the deploy; what changed is that the deploy
now has a build in it.

**Source — committed, and the only thing you edit:**

| | |
|---|---|
| `san-francisco/**/<number>/data.json` | every fact and every sentence of an address page |
| `san-francisco/**/index.md` | a hub's lead paragraph and any hand-written section |
| `index.html` at the repo root | the homepage, hand-authored |
| `san-francisco/index.html` | the city index, hand-authored — no generator has ever touched it |
| `san-francisco/<neighborhood>/index.html` | 42 of them. A human's prose; `hubs` patches the street list into the page rather than writing it |
| `shared/`, `scripts/`, `research/`, `news/`, `merchants/`, `design/`, `events/` | the stylesheet, the script, the tools, the modules |
| `corpus.jsonl` | derived, but committed on purpose — see below |

**Derived — gitignored, rebuilt every deploy:**

| | |
|---|---|
| `san-francisco/*/*/*/index.html` | 16,287 address pages, 235 MB |
| `san-francisco/*/*/index.html` | 1,298 street hubs and 255 historic-district hubs |
| `san-francisco/historic-districts/index.html` | the district index, written whole by `districts` |
| `sitemap.xml`, `sitemaps/` | the sitemap index and its 44 children |
| `shared/addresses.geojson` | the homepage map's dots |
| `shared/events.geojson` | the homepage map's event dots — built from `events/events.json`, which is source |
| `shared/nearby.json` | the lateral links between pages |
| `events/index.html` | the `/events` listing, written whole by `build_events.py` |
| `stats/index.html` | the dashboard at `/stats/` |

The line between the two is not depth, it is whether a generator can write the
file from nothing. A street hub and an address page it can. A neighborhood hub
it cannot: `write_neighborhood_hub` finds the `<h2>Streets</h2>` list and
replaces it, leaving the lead, the naming explanation and the closing note
alone — so the page has to exist for the generator to run at all, and it is
source.

Untracking the rest took the repository from 35,688 tracked files to 18,056,
and from 397 MB of tracked bytes to 152 MB. That is where the `grep` and
`glob` costs were: a search across the corpus no longer walks a second, larger
copy of every page it has already read in `data.json`.

`corpus.jsonl` is the deliberate exception. It is derived like the rest, but
its entire purpose is to answer a corpus-wide question *without* a build or a
walk — so it stays committed, and the check that it is current is
`git diff --exit-code` in `.github/workflows/validate.yml`.

### What it costs

"The committed bytes are the served bytes" was a real property and it is gone.
A clone is no longer the site; a bad deploy is no longer diffable. What
replaces it is that the build is one stdlib script anyone can run, and that
CI runs the same script on every pull request — so the deployed site is a
function of the repository, checked on the way in rather than inspected after
the fact.

### A street hub with a section of its own

Some streets have a record no building page can hold: when the lots were
divided, the 1922 order that graded the street, the corner an extension took.
`seed_pages.py hubs` carries that through. A `## Heading` in the street's
`index.md` that isn't one of the generator's own is read, written back
verbatim, and rendered into `index.html` — a `## Sources` section into the
footer, where an address page puts its own citations, and everything else into
the main column above the building list. The markdown it understands is what
those sections contain: bullet lists, paragraphs, links, bold and italics.

So `index.md` stays the only copy of the prose and `index.html` stays a build
artifact, which is what keeps every street hub out of the repository. Two of
them — `corbett-heights/mars-street` and `corbett-heights/danvers-street` —
were committed HTML until the generator could read them, and had gone stale in
the way a frozen page does: no stat band, no structured data, a hand-kept
building list and a hand-kept nearby-streets list that nothing updated.

A hub the build skipped would otherwise vanish from the site silently — nothing
committed, no diff to show it. `validate.py` has a build-completeness check for
exactly that: every address directory with a `data.json`, and every hub
directory with an `index.md`, must have an `index.html` after a build.

### Looking at it

```bash
python3 scripts/build_site.py --serve     # build, then serve on :8517
python3 scripts/build_site.py --no-build --serve   # serve what's already built
```

Port 8517 and no other: the Mapbox token and the Google Maps embed key are
URL-restricted to `knowthis.place` and `http://localhost:8517`, so the maps
render there and nowhere else (shared/AGENTS.md). If the port is busy it is
usually a stale `http.server` rooted in another worktree.

---

## The homepage

The root `index.html` is hand-authored, and it is a map and then **In the
news**: `.place-cards.news-cards`, the twelve newest news entries on the site,
maintained by the news module and nothing else — see
[news/PIPELINE.md → The homepage grid](news/PIPELINE.md#the-homepage-grid). The
cards are also the map's data: each one is a pulsing dot on the map above.

There is no featured-addresses grid to put a page you just wrote into. There was
one, and the homepage now spends that room on the news instead, on the grounds
that a story from this week is what brings a stranger back. A page earns its way
onto the homepage by being the address a story is about, which is the news
module's business, not the seeder's.

The one hand-kept list left on the page is the street hubs under **Browse by
street** — the best-covered streets on the site, and what makes the map's
no-JavaScript fallback ("every address is reachable through the links below")
true. Add to it only when a street has genuinely become one of those, and keep
the count where it is.

---

## The corpus index

`corpus.jsonl`, at the repo root, is one line per address page — a `path`,
and whichever of `year` (`parcel.year_built`), `use` (`parcel.use`),
`district` (the page's own historic district, not its overlaps), `earliest`
(the smallest year found across `historical_record` dates and `permits`
`filed` dates), `sources` (deduplicated `sources[].id` values, in the order
they appear) and `hook` the page has. It exists so a question about the whole
corpus — which Mission pages cite a non-`sf-*` source, which pages have a
timeline reaching before 1900 — is a `grep`/`jq` pass over one file instead of
a walk through every directory, without opening 11,000-odd `data.json` files
by hand:

```bash
# Pages with a source that isn't a standard SF dataset or context statement.
jq -c 'select(.sources | any(test("^sf-|-context-statement$|^central-soma-survey$") | not))' corpus.jsonl

# Every page whose timeline reaches back before 1900.
jq -c 'select(.earliest and (.earliest | tonumber) < 1900)' corpus.jsonl
```

Regenerated by `scripts/build_corpus_index.py`, the seventh step of
`scripts/build_site.py`. It is a derived index like the sitemap and the map —
nothing lives here that isn't in a `data.json` already, and `validate.py`
fails if a page is missing from it or an entry outlives its page — but it is
the one derived file that stays **committed**, because a corpus-wide question
should not cost a build. Commit it whenever a build moves it; CI checks that
you did.

---

## Writing pages — the examples

The rules are in [AGENTS.md → Writing pages](AGENTS.md#writing-pages). These
are the worked cases behind them, kept because each one cost a correction.

**Never state a fact twice — this catches adjectives as readily as sentences.**
A timeline opening "1908 · Built" forbids "a house **of 1908**" in the lead; a "7 ·
Rooms" tile forbids "a **seven-room** house." Read the finished lead against
the tags, the tiles and the spec list word by word and cut every phrase one of
them already carries. What survives is usually one clause — that clause is the
lead.

**The Sources footer is the attribution; prose never narrates sourcing.** Don't
write "a published guide to notable residences records…," "the source
states…," "according to…," or "as attributed rather than established." A fact
that made it onto the page is stated as fact — "Jerry Garcia lived here with
his grandparents, 1947–1952" — and the reader follows the footer to see where
it came from. The **only** exception is a genuine contradiction: two sources
disagreeing with each other, a source disagreeing with the city data, or a
source undercutting its own claim. Then describe the disagreement plainly and
don't adjudicate it. Sourcing doubt that is merely *general* is not a
contradiction and earns no words.

**No permit-history introduction.** The timeline *is* the record of what
happened here: never precede it with a paragraph that counts the permits, sums
their costs, groups them into episodes, or characterizes the record ("Six
permits on file, four of them substantive and all complete"). Every one of
those figures is already in the timeline items, and the rest is commentary. If
a filing is deliberately left out of the timeline (street-space permits at a
nominal $1, duplicates that DBI files under several street numbers), disclose
it in one small line *below* the timeline — never in a lead-in paragraph.

**No editorial voice, and no interpretation.** Cut flourishes like "its public
record is the quiet kind," "the record is silent on…," "hints at a longer
story." Cut inference dressed as fact — "a base this low is the signature of a
parcel held since before Proposition 13," "unusually for this block," "a
measure of the building." A page does not list what it has failed to document.
A data *anomaly* may be stated where it changes how the page
reads (the roll reports land and improvements at the same figure, so no split
is charted) — that is a note on the data, not a reading of it.

**No cross-page superlatives.** "The smallest building documented on this
site," "the newest on the 700 block," "the only building documented in Corbett
Heights so far designed by an architect," "the highest assessed value of any
address documented here." Every one of them is a claim about *coverage*, not
about the building — it is false the day a bigger, older or dearer parcel gets
a page, nothing in the repo re-checks it, and a reader can't verify it from the
page. This applies to leads, prose, `.hook` lines on hub pages, `<meta
name="description">`, JSON-LD `description`, and the free `note` fields in
`data.json`. Say what the building *is* — "a 1,000 sq ft house of 1906" — and
let the stat tiles do the comparing.

**Do not force uniformity.** Compose the shared blocks *differently* per
building so the layout fits its story — a history-rich place opens with prose
and photos; a plain one leans on the stat band and timeline. Bespoke layout,
shared components. A **seeded first draft** varies with the data, not with a
story: it drops panels a parcel has no data for and runs a thin permit record
full width instead of splitting the page. That is the right amount of variation
for a draft whose facts are all from one API, and a run of similar buildings
honestly producing similar drafts is not a defect. When a building deserves a
layout the seeder wouldn't have produced, just write it — the page is yours to
edit and nothing will overwrite it.

**Be honest about thin pages.** If all we know is the assessor basics, a clean
stat band + short timeline is a complete page — never pad with generic
neighborhood filler copied across pages. (Neighborhood context lives on the
neighborhood hub page.)

---

## Don't burn effort on these

- **The Street View embed.** `maps_embed_key` is locked to the production
  domain, so the embed fails everywhere else *by design*. Never load, preview,
  screenshot, or "verify" it — a blank embed locally proves nothing is wrong.
  Just check `location="LAT,LNG"` matches `coordinates` in `data.json`.
- **Re-querying an API the seeder already cached.** `.cache/` holds the raw
  dataset rows; the `sources` array records the exact query and retrieval date.
- **Serving the site to look at a generated page.** `validate.py` covers the
  contract; read the HTML.
