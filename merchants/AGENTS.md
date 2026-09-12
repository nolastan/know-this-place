# Merchants

Putting the business that trades from a building today on that building's
page — from ordering apps and merchant directories — as the page's
`occupants`, rendered as the "Current occupant" panel at the top of the aside.

Read the root [AGENTS.md](../AGENTS.md) first; its privacy limits bind here
unchanged. The key and its block are specified in
[REFERENCE.md → occupants](../REFERENCE.md#occupants) and
[shared/BLOCKS.md → Current occupant](../shared/BLOCKS.md#current-occupant--panel-occupant).

## Sources

One row per source — a directory, or a chain that lists its own doors. `id`
is the id a page's `sources` entry and each `occupants` entry cite.
**Referral** says whether the renderer's `REFERRALS` table carries an offer
for it — that table, in `scripts/seed_pages.py`, is the only place an offer
lives.

| id | Source | Read from | Referral | Files |
|---|---|---|---|---|
| `away` | Away, luggage (its own site) | `https://www.awaytravel.com/stores` names sixteen stores and one is in the city; its page, `https://www.awaytravel.com/pages/store/san-francisco-hayes-valley`, prints the address and hours as plain text, with no schema.org markup | $40 off, on Away's own referral page | `away/<date>.json` |
| `bites` | Bites, merchant directory | `https://withbites.com/merchants` — the page's schema.org `ItemList`, every Bites merchant in the country, one `Restaurant` each | $5 off a first order; the link opens the app, not the merchant (no per-merchant deep link exists) | `bites/<date>.json` |
| `bonobos` | Bonobos, men's clothing (its own site) | `https://bonobos.com/locations` links 47 store pages, two of them in the city; each store page carries no schema.org block, so the address and hours come from the Contentful blocks in its `__NEXT_DATA__`, which is what the page prints | 25% off, on Bonobos' own refer-a-friend page; the amount is the issue's, stated on no public page | `bonobos/<date>.json` |
| `brooklinen` | Brooklinen, bedding (its own site) | `https://www.brooklinen.com/pages/our-stores` prints all nine stores' addresses and hours as plain text, with no schema.org markup and no category for the shop | $25 off, on Brooklinen's own rewards page | `brooklinen/<date>.json` |
| `casper` | Casper, mattresses and bedding (its own store finder) | `https://stores.casper.com/ca/sanfrancisco/` lists four stores in the city, but three are Mancini's Sleepworld — a stockist, not a Casper door — and only the Union Street shop is Casper's own; its page carries a schema.org `FurnitureStore` block | 30% off, on Casper's own sign-up | `casper/<date>.json` |
| `fitnesssf` | FITNESS SF, gyms (its own site) | `https://www.fitnesssf.com/locations` names the nine gyms but carries no addresses or hours; each location page, `https://www.fitnesssf.com/location/<slug>`, prints both as plain text, with no schema.org markup and no coordinates | One link for the whole chain: a free month for the person joining, on FITNESS SF's own sign-up | `fitnesssf/<date>.json` |
| `momence` | Momence, class-booking hosts | Momence's host record (`https://momence.com/_api/primary/plugin/hosts/<id>`) confirms each host's name but lists no locations, so the addresses come from each studio's own location pages | Per host: one `REFERRALS` row per studio, keyed `momence-<studio>`, which is also the page's source id; the link opens that studio's sign-up | `momence/<date>.json` |
| `ritual` | Ritual, ordering app | `https://ritual.co/order?lat=&lon=` server-renders its nearby-merchant list into the page's `__NEXT_DATA__` — 36 listings at most, within 5 km, ranked by distance from the point — so a grid of points and a de-duplication by merchant id is what covers the city. Each listing's own page, `https://ritual.co/order<menuPath>`, carries the postal code, the weekly hours and the categories the list leaves out | $10 across the first orders; the link opens Ritual's sign-up page, not the merchant | `ritual/<date>.json` |
| `vuori` | Vuori, clothing (its own site) | `https://vuoriclothing.com/pages/stores` links 132 store pages, one of them in the city (the other San Francisco-named store is the Livermore outlet); the store page carries a schema.org `ClothingStore` block and prints the hours beside it | 20% off, on Vuori's own site | `vuori/<date>.json` |
| `wework` | WeWork, coworking (its own site) | `https://www.wework.com/l/coworking-space/san-francisco--sf-bay-area--CA` names seven locations and links a building page for each, which carries the address in a schema.org `PostalAddress`. Cloudflare turns a plain fetch away, so the pages are read in a browser. **No opening hours**: what a page gives is staffed hours, which is not when a member can get in | A month free on a 12-month membership, on WeWork's own referral page | `wework/<date>.json` |

Directories still to add are the GitHub issues labelled `monetization`.
The "Add merchants" issue form asks for both halves below, so a ticket
filed through it arrives workable.

## Before you start

A ticket is workable when it carries both halves: **a referral link with a real
code** — not a `CODE` or `[REFERRAL CODE]` placeholder — and **a way to list the
directory's San Francisco locations**, whether an API, a GraphQL query, a
schema.org block on the merchant's own pages, or the addresses typed into the
issue. Missing either half, label the issue `needs-human`, say which half is
missing, and stop. Only a human can sign up for the programme, and a guessed
code publishes a dead link.

Settle the **shape of the offer** before writing anything, because it decides
the source ids:

- **One offer for the whole directory** — Bites. One `REFERRALS` row, one
  source id, the same button on every merchant.
- **One offer per merchant or host** — Momence. A `REFERRALS` row and a source
  id per merchant, keyed `<directory>-<merchant>`. The findings file stays one
  file under one `source_id`; `extra.page_source_id` records which row each
  entry publishes under.
- **A row carries a `note` only where its link does not reach the merchant.**
  Bites' link opens the app, so its note says so; a Momence link opens that
  studio's own sign-up, so it carries none.

A directory that is not a list of shops at all — HotelTonight's rotating hotel
inventory, say — is not an `occupants` source, and needs a human's design
decision before any page changes.

## Rules

- **The business, never the people.** A merchant's trading name is a fact
  about the building; its owner, chef, staff and customers are not. A sole
  proprietor whose business is their own name does not go on a page.
- **Publish only what the directory states consistently.** Fetch the page more
  than once before trusting a field. Bites' `priceRange` changed on 111 of 786
  merchants between two fetches seconds apart — it is not a fact and never
  reaches a page. Ratings and menus describe the merchant rather than the
  building and are left out too.
- **The panel says when the listing's hours were read.** Hours drift within
  days (9 of 118 Bites merchants changed theirs in five days of September
  2026), so the panel prints "Last updated" from the source's `retrieved`,
  and a refresh changes that one field. The date belongs to the hours: an
  entry that publishes none — a yoga studio listing only a class schedule —
  omits the line rather than appearing to date the tenancy.
- **Hours the source does not call opening hours are not hours.** WeWork
  publishes "Staffed hours" — when the front desk is manned, Mon–Fri, at every
  San Francisco building — and a member's access is neither of those. Putting
  them in `opening_hours` would have the panel print every WeWork closed at
  the weekend, so they stay in `extra` and the entry publishes none, which
  also takes its "Last updated" line off. Read the label, not the table.
- **A brand's store finder lists other people's shops too.** Casper's names
  four in San Francisco and three are Mancini's Sleepworld, a stockist; an
  entry filed under `casper` would put Casper's referral button on another
  business's page. Only the brand's own doors become entries, and the
  stockists stay in the file marked `publish.status: "declined"`.
- **A referral offer is the source's, not the merchant's.** Never put a link
  in an `occupants` entry. A directory gets an offer by a row in `REFERRALS`,
  added only when a human has supplied the link, and a merchant from any other
  directory never shows one.
- **Occupants describe today.** A refresh replaces a page's entries from that
  source wholesale: a merchant the directory no longer lists comes off the
  page. It is not a timeline fact. An entry two directories share survives a
  refresh that drops one of them — take the dropped directory out of
  `also_listed_by`, or, where it was the entry's `source`, rewrite the entry
  from the directory that still lists it and move that one out of
  `also_listed_by` into `source`. The entry only comes off when no directory
  lists it any more.
- **List what the directory lists.** A shared kitchen trading as three brands
  at one door is three entries; don't adjudicate which is "real". The
  exception is the same listing twice — one point, identical hours, one name a
  prefix of the other — which becomes one entry, the fuller name, with the
  other marked `publish.status: "declined"` and the reason.
- **One business is one entry on a page, across directories too — but it
  keeps every offer.** A merchant trading from two directories —
  Mediterranean Aroma is on both Bites and Ritual — would otherwise appear
  twice in one panel and read as two businesses. It stays one entry, and the
  second directory joins it in `also_listed_by`, which puts that directory's
  button on the panel beside the first's. The page gets a `sources` row for
  both. The entry's own facts — `cuisines`, `opening_hours`,
  `listed_address`, and the "Last updated" date under them — are `source`'s,
  and `source` is **whichever directory was read most recently**; where two
  reads share a date, the entry already on the page stands and the newcomer
  only adds itself to `also_listed_by`. Check for this before writing: the
  run's own new pages are not the only ones a directory lands on.
- **A merchant in a condominium goes on the building's page, never a
  unit's.** The resolver refuses a condominium parcel, rightly; establish the
  building's parcel set instead — every active parcel sharing one sf-parcels
  `mapblklot` — and file one page under the map's key parcel, built with the
  seeder's own `build_record` and then stripped of the roll's unit-scoped
  figures (floor area, rooms, stories, the unit's assessment), with `units`
  counted across the set and a `sf-assessor-roll-building` source citing it.
  Record the resolution with `by_hand: true`. Give the entry a `unit` only
  where a city record ties the merchant to one — 1489 Folsom's restaurant
  permits are all on unit 1 — never by picking one of several commercial
  units.
- **Every San Francisco listing gets a page; nothing outside the city does.**
  Where the resolver gives up — an address EAS lacks, one it holds with no
  parcel, a parcel it files under that the city has retired — look up the
  active parcel the listing's own coordinates (or EAS's point) fall on in
  sf-parcels, and within a few metres when the point sits in the street. Put
  the merchant on that parcel's page if one exists, seed one from it if not,
  and add one `unknowns` line saying how the listing's address and the city's
  records differ. A retired parcel's permits say where its numbers went: DBI
  files 151 Warriors Way and 1655 3rd Street under the same lot, so the
  merchant is on 1655 3rd Street's page. Where no parcel carries an address
  at all, the page is the address with no parcel facts. Check the coordinates
  before trusting them: Bites puts both its Ferry Building and Warriors Way
  listings in Concord, and the Ferry Building is found by name in SF
  Planning's historic resource record instead. Record each such resolution with `by_hand: true`.
- **A listing outside the city stays off** — Bites files three South San
  Francisco (94080) restaurants under the city. The entry stays in the file
  with the reason, as in the news module.

## The file

`<source>/<date>.json` is a findings-shaped record of one read of the
directory, so `research/tools/resolve_eas.py` reads it unchanged: one entry per
San Francisco listing, `address_as_written` verbatim, `street_number` /
`street_name` / `street_type` parsed with the resolver's own
`parse_address` (a "1/2" or a trailing suite letter dropped first), and
`extra` holding what the page takes — `name`, `name_as_listed`, `kinds` or
`cuisines`, `opening_hours`, `geo`, and the listing's own locality and postal
code.
`name` repairs the directory's title-casing (Bites writes "18Th St", "Kfc",
"Ihop"); `name_as_listed` keeps its spelling. `publish` records which page
each entry went on, or why it didn't.

## A run

1. Fetch the directory twice and compare, per the rule above. Keep the
   listings whose locality is San Francisco; check the postal code too —
   Bites files three South San Francisco (94080) restaurants under the city.
2. Write `<source>/<date>.json`, then resolve and seed:

   ```bash
   python3 research/tools/resolve_eas.py report   merchants/<source>/<date>.json
   python3 research/tools/resolve_eas.py apply    merchants/<source>/<date>.json
   python3 research/tools/resolve_eas.py manifest merchants/<source>/<date>.json \
       --out research/manifests/<source>-<date>.json
   python3 scripts/seed_pages.py seed-list --manifest research/manifests/<source>-<date>.json
   ```

3. For each resolved entry, set that page's `occupants` (every entry from the
   source, replacing the last read's) and its `sources` entry for the
   directory, with `supports: "Current occupant"` and `retrieved` set to the
   day of the read. `listed_address` is the listing's own number on the
   page's own spelling of the street, or the other street for a corner
   building. Preserve each `data.json`'s indent (1 or 2 spaces).
4. Rebuild the derived indexes **before** rendering — `render` writes each
   page's Nearby list out of `shared/nearby.json`, so rendering first only
   bakes in the stale one:

   ```bash
   python3 scripts/seed_pages.py districts
   python3 scripts/build_sitemap.py
   python3 scripts/build_map_index.py
   python3 scripts/build_link_index.py
   python3 research/tools/check.py --index
   python3 scripts/seed_pages.py render <each page>
   python3 scripts/validate.py
   ```

5. **Re-render the pages the new ones displaced.** Seeding shifts
   `shared/nearby.json`, so neighbours' Nearby lists change and their HTML goes
   stale — four new pages staled twenty of them, on streets the run never
   touched. Render everything `validate.py` names, then validate again:

   ```bash
   python3 scripts/validate.py | sed -n 's/.*seed_pages.py render //p' | sort -u |
       while read -r page; do python3 scripts/seed_pages.py render "$page"; done
   python3 scripts/validate.py
   ```

   Check the output of each render rather than discarding it: a silent loop
   here reports success while leaving every page stale.
