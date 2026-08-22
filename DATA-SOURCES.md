# Data sources

The **live city APIs and datasets** the site is built and maintained from, in
priority order. **Prefer these over unguided web browsing** — they're accurate,
fast, and auditable. Every fact taken from a source gets an entry in the page's
`data.json` `sources` array (query URL + retrieval date) and a citation in the
page footer.

> **Archives, books, newspapers and newsletters are not here.** Those corpora —
> and the whole business of finding, mining and citing them — live in the
> **research module**: [research/AGENTS.md](research/AGENTS.md) for the rules,
> [research/SOURCES.md](research/SOURCES.md) for the register, and
> `research/sources/<id>.md` for each source's dossier. This file stays the
> catalog of endpoints a page is *built* from; that one is the catalog of
> everything a page is *researched* from. See "Research sources" below for the
> ids already in use on pages.

Most DataSF datasets are Socrata: `https://data.sfgov.org/resource/<id>.json`
with SoQL query params (`$where`, `$select`, `$limit`). No auth required;
an app token (header `X-App-Token`) lifts throttling if we ever need it.

> **Query shape matters more than you'd expect.** These datasets are large and
> their text columns are unindexed, so a bulk export — "every 2025 roll row
> where `analysis_neighborhood = 'Castro/Upper Market'"` — reliably fails: the
> server accepts the request, then dribbles the body out over many minutes or
> resets it. A `count(1)` on the same filter returns instantly, so a fast count
> is no evidence the full query will work.
>
> What does work is **many small queries keyed on an indexed column** —
> `parcel_number`, `apn`, `block` — each returning well under a megabyte:
> `$where=parcel_number in ('2752016', …)` with a couple of hundred keys, plus
> a `$select` naming only the fields you need. `scripts/seed_pages.py` does
> exactly this, caches every chunk under `.cache/`, and resumes where it left
> off. Two practical notes if you write your own fetch. **Permits go one block
> per request, paged within the block** (`$order=:id` + `$limit`/`$offset`):
> volume per block spans an order of magnitude — a quiet residential block has
> a few hundred, a Market Street block has thousands — so batching blocks makes
> the worst request unpredictably large and it times out. And **`urllib`'s
> `timeout` is per-read**, so it never fires on a slow trickle and the process
> hangs indefinitely; read in chunks against a wall-clock deadline instead, and
> back off properly (tens of seconds, not five) when failures repeat, because
> repeated failures mean you are being throttled.

> **Verified dates:** each entry carries a `Verified:` line — the last date an
> agent confirmed the endpoint and field names with a live query. If it's
> stale or empty, verify before relying on field names, and update it.

> **Reading a corpus for the few passages that carry a street number** is
> research work, and it has its own doctrine — a low hit rate is the shape of
> the work, not a bad source or a mistaken request. It lives in
> [research/AGENTS.md](research/AGENTS.md) → "Mining a corpus for
> address-level facts."

---

## sf-eas-addresses — Addresses (Enterprise Addressing System)

- **What:** The city's canonical address registry: every address, its APN,
  coordinates, and unit records. This is the master list of which pages may
  exist, the source for `coordinates`, and the address→parcel join key.
- **Endpoint:** `https://data.sfgov.org/resource/3mea-di5p.json` (one row
  per address). Unit-level records: `ramy-di5m` ("Addresses with Units").
- **Use for:** seeding street lists, validating an address exists, APN lookup.
- **Key fields:** `address_number`, `street_name` (**UPPERCASE**, e.g.
  `CASTRO`), `street_type` (`ST`), `parcel_number` (block+lot concatenated,
  e.g. `2752016`), `latitude`/`longitude`, `zip_code`, `supervisor`,
  `nhood` (analysis neighborhood; the Castro is `Castro/Upper Market`).
- **Citation label:** "SF Enterprise Addressing System via DataSF"
- **Verified:** 2026-07-27 (`nhood='Castro/Upper Market'` → 8,290 addresses on
  4,948 parcels)

## sf-assessor-roll — Assessor Historical Secured Property Tax Rolls

- **What:** Per-parcel, per-year: year built, property class / land use,
  number of units, rooms, lot and building area, assessed values.
  The land-use / property-class code is how a page says what kind of building
  it describes — house, flats, storefront, mixed use.
- **Endpoint:** `https://data.sfgov.org/resource/wv5m-vpq2.json`
- **Query by:** `parcel_number` (block+lot, from EAS) with
  `$order=closed_roll_year DESC&$limit=1` for the latest roll (2025 as of
  last check).
- **Key fields:** `year_property_built`, `use_definition`,
  `property_class_code_definition`, `number_of_units` / `_rooms` /
  `_stories` / `_bathrooms`, `construction_type`, `lot_area`,
  `property_area`, `zoning_code`, `assessed_land_value`,
  `assessed_improvement_value`, `current_sales_date` (a real, if partial,
  sale-history signal), `assessor_neighborhood`, `analysis_neighborhood`.
- **Caution:** this dataset carries no owner names, but if you join any
  dataset that does, **never copy them** (see AGENTS.md privacy rules).
  Condo-unit parcels can report `0` lot area and stories — prefer the
  building's parcel.
- **Citation label:** "SF Office of the Assessor-Recorder via DataSF"
- **Verified:** 2026-07-27 (2025 roll, 4,428 of those Castro parcels; latest
  `closed_roll_year` is 2025)

## sf-building-permits — Building Permits

- **What:** Permits filed and issued: dates, status, description, estimated
  cost. Often the richest ready-made narrative for an ordinary building —
  additions, remodels, repairs after events.
- **Endpoint:** `https://data.sfgov.org/resource/i98e-djp9.json`
- **Query by:** `street_number` + `street_name` — note `street_name` here is
  **Mixed Case** (`Castro`), unlike EAS's uppercase. Also queryable by
  `block` + `lot`.
- **Key fields:** `permit_number`, `permit_type_definition`, `status`,
  `filed_date`, `issued_date`, `completed_date`, `estimated_cost`,
  `revised_cost`, `description`.
- **Per-permit public link (use it):** each permit number has a human-viewable
  record in the DBI permit tracking system —
  `https://dbiweb02.sfgov.org/dbipts/default.aspx?page=Permit&PermitNumber=<permit_number>`.
  Confirmed to resolve for permits back to at least the mid-1980s. Link every
  permit shown on a page to its record here (in HTML, encode `&` as `&amp;`).
- **Caution:** applicant/owner names appear in some fields — don't copy them.
- **Citation label:** "SF Dept. of Building Inspection via DataSF"
- **Verified:** 2026-07-21 (744 Castro St, 6 permits 1985–2016)

## sf-planning — Parcels, zoning, historic resources

- **What:** Zoning, historic-resource status (Article 10 landmarks, survey
  ratings), historic district boundaries. The Property Information Map (PIM)
  aggregates much of this per parcel.
- **Endpoints:** DataSF Socrata datasets, incl. **Historic Resource Status by
  Parcel** (`3tsw-4idn`) — one row per parcel, keyed by `apn` (block+lot, no
  dash); fields `ceqacode` (A / B / C) and `ceqacodea10a11` (A / A* / B / C)
  with `ceqacodereason`. Category **A** = is a historical resource; **A*** =
  listed in / within an Article 10 or 11 district; **B** = unknown / unevaluated;
  **C** = not a historical resource. Also "Historic Districts" (`63x5-g3m4`).
  The PIM at `sfplanninggis.org` aggregates the same per parcel (check for a
  queryable API before scraping).
- **`3tsw-4idn` also carries three fields worth querying every time:** `name`
  (the survey's own name for the building, populated only for named
  resources — e.g. apn 0803022 → `POSTCARD ROW (PART)`, apn 0601005 →
  `SPRECKELS RESIDENCE`), `yearbuilt` (an **independent** build date — compare
  it against the assessor's `year_property_built` and record the conflict
  rather than reconciling it), and `lowstnum`/`highstnum`, which give the
  parcel's street-number range as Planning holds it — a useful second opinion
  on the assessor's `property_location` when deciding whether a parcel spans
  several numbers.
- **`ceqacodereason` mixes two subjects, and only one of them is the
  building.** It is a comma-separated list of findings; most tokens describe
  the *district* the parcel sits in (`Article 10 Historic District`,
  `California Register Historic District`) or a survey that looked at it
  (`Historic Survey Result`), but four are designations on the building
  itself: `Article 10 Individual Landmark`, `Article 11 Individual`,
  `National Register Individual`, and `Article 10 Individual Landmark Work
  Program`. Match them token by token, never as a substring — the work program
  contains the landmark string and means the opposite of it. It is the Historic
  Preservation Commission's list of *candidates*, and the data says so: a
  parcel whose only local finding is the work program stays `ceqacodea10a11`
  = A, while all 58 parcels here carrying `Article 10 Individual Landmark`
  and all 118 carrying `Article 11 Individual` are A*.
- **Citation label:** "SF Planning Department"
- **Verified:** 2026-07-27 (4,475 Castro parcels fetched by `apn` in chunks of
  400; apn 2752016 = 744 Castro St → ceqacode B). `ceqacodereason` tokens
  tallied across the 9,380 pages holding a `historic_status` on 2026-08-14.

## sf-parcels — Parcels, active and retired

- **What:** Every parcel the city has mapped, with geometry, its address range,
  and — the point of it — an `active` flag. **Downtown, this is the only
  reliable address→parcel join.** EAS's `parcel_number` is the APN as of
  whenever the address record was written, and downtown blocks have been
  re-parcelized repeatedly: of 96 parcels EAS gave for the POPOS and public-art
  addresses, 22 had no row on the current secured roll because the APN had been
  retired. `acdm-wktn` resolves the same address to the parcel that exists now.
- **Endpoint:** `https://data.sfgov.org/resource/acdm-wktn.json`
- **Key fields:** `blklot` / `mapblklot` (the APN), `block_num`, `lot_num`,
  `from_address_num` / `to_address_num` (**text columns** — cast them,
  `from_address_num::number <= 600`, or the query 400s), `street_name`,
  `street_type`, `active`, `in_asr_secured_roll`, `zoning_code`,
  `analysis_neighborhood`, `centroid_latitude` / `_longitude`, and `shape` for
  `intersects()`.
- **Two ways to ask, and you want both:**
  - by address range, as above; and
  - spatially, `$where=active=true AND intersects(shape, 'POINT(<lng> <lat>)')`
    against the address's own EAS coordinates.

  Where they agree, the answer is solid. Where they don't, the assessor's
  `property_location` settles it.
- **Cautions:**
  - **The frontage street is arbitrary on a corner parcel.** 0312031 is "1
    Kearny" to the POPOS inventory and "1–31 Geary" here; 0266009 is "444
    Market" and "1 Front". Neither is wrong — title the page on the street the
    source dataset names, and record the rest as aliases.
  - **An address range sweeps in the other side of the street.** The range on
    0236017 is 100–116 California, and EAS returns 100, **101** and 116 — 101
    California is the tower across the street. Filter to the lead number's
    parity.
  - **A point on a condominium block returns dozens of parcels**, one per unit.
    That is the signal to stop and look for the building's own parcel on the
    roll (333 Bush → 0288033, an office; 0288032 is only its garage condo), or
    to defer the address per AGENTS.md when there isn't one.
- **Citation label:** "SF Parcels (active and retired) via DataSF"
- **Verified:** 2026-08-06 (83 downtown parcels resolved; `acdm-wktn` agrees
  with the 2025 roll on all 83, where EAS's `parcel_number` did not on 22)

## sf-popos — Privately Owned Public Open Spaces

- **What:** The city's inventory of the plazas, atriums, sun terraces,
  "snippets" and indoor parks that downtown developments must provide and keep
  open to the public — the Downtown Plan's central bargain, in force since 1985
  and applied retroactively to spaces going back to 1959. One row per *space*,
  so a building can have several (345 California has three, 55 Second has
  three), and each has its own hours.
- **Endpoint:** `https://data.sfgov.org/resource/65ik-7wqd.json`
- **Key fields:** `name`, `popos_address`, `type` (Plaza / Atrium / Urban
  Garden / Sun Terrace / Indoor Park / Snippet / Pedestrian Walkway), `hours`,
  `hours_type`, `year` (the entitlement that required it, **not** an opening
  date), `location`, `description`, `landscaping`, `seating_no`, `food_service`,
  `restrooms`, `accessibility`, `signage`, `subject_to_downtown_pln`,
  `block_num` / `lot_num` / `parcel_num`, `latitude` / `longitude`.
- **Cautions:**
  - **`parcel_num` is often stale or wrong** — 1 Post St carries 555
    California's parcel. Re-resolve through `sf-parcels`.
  - The free-text columns are a surveyor's field notes, in mixed voice and
    mixed case ("Security would not disclose hours", "Thayer referenced
    something that is not part of the open space requirement"). Carry them as
    the inventory's own description; don't launder them into site prose.
  - `year` is the year of the requirement. Never present it as the year the
    space opened.
- **Citation label:** "SF Planning Department — Privately Owned Public Open
  Spaces via DataSF"
- **Verified:** 2026-08-06 (81 spaces; 78 of them on 83 documented parcels)

## sf-public-art — Public Art (1% Art Program)

- **What:** Artworks provided under the 1% art requirement the Downtown Plan
  places on large downtown developments — sculpture, murals, fountains, facade
  work — with the medium, where in or on the building it sits, and when the
  public may see it. One row per *work*: 600 California has four.
- **Endpoint:** `https://data.sfgov.org/resource/cf6e-9e4j.json`
- **Key fields:** `name` (the street address, or occasionally a venue name),
  `title` (title **and** artist, run together), `type`, `medium`, `location`,
  `accessibil`, `requiredar` (the Planning case that imposed the requirement,
  wrapped in an HTML anchor), `descriptio` (the *entitlement project*, not the
  artwork — and **truncated mid-sentence**, so don't quote it), `artistlink`,
  `the_geom`.
- **Cautions:**
  - **`name` is not always an address**: three rows name a venue ("Orchard
    Garden Hotel", "SF Dtwn Courtyard by Marriott", "San Francisco Conservatory
    of Music"), and one — "157 Mason" — is a street number the city's own
    address registry doesn't have. Resolve those on `the_geom` and confirm
    against the roll: 157 Mason is parcel 0331017, which the assessor calls 149
    Mason and records as 57 units built 2009, matching the row's own
    description of the entitlement.
  - **`title` needs parsing and is quoted inconsistently** — `'""Guardian""' by
    Bruce Beasley`, `""Riallaro,"" by Frank Stella`, `Bronze Fountain by David
    Tolerton`. Split on " by ", strip the quotes.
  - **The artist is sometimes missing** where the work is well known
    ("Wall Drawing #1012" is Sol LeWitt's), and `type`/`medium` are free text
    in mixed case.
  - `the_geom` points are approximate and occasionally plain wrong — the "125
    Mason" row's point lands near Van Ness. Trust the address, and only fall
    back to geometry when there is no usable address.
- **Citation label:** "SF Planning Department — Public Art (from the 1% Art
  Program) via DataSF"
- **Verified:** 2026-08-06 (65 works; 58 of them on 83 documented parcels)

## sf-historic-districts — Historic district boundaries

- **What:** Polygon boundaries and status for each historic district, used to
  answer "is this parcel in a district, and which one?"
- **Endpoint:** `https://data.sfgov.org/resource/63x5-g3m4.json`
- **Key fields:** `name_1` (district name), `cr` (California Register status),
  `nr` (National Register), `a10` / `a11` (local Article 10 / 11 district),
  `pos_1` (period of significance), `description`.
- **Name the district with a spatial query — never guess.** The per-parcel
  historic dataset's reason field may say "California Register Historic
  District" without naming it, and several districts mention Castro in their
  name or description. Resolve it against the parcel's own coordinates:

  ```
  https://data.sfgov.org/resource/63x5-g3m4.json
    ?$select=name_1,cr,nr,a10,a11,pos_1
    &$where=intersects(the_geom, 'POINT(<lng> <lat>)')
  ```
  Note the argument order: `POINT(longitude latitude)`. An empty result means
  the parcel is in no district.
- **For a whole neighborhood, do the test locally instead.** One `intersects`
  request per parcel is thousands of requests. There are only ~200 districts,
  so page the polygons in (`$select=…,the_geom&$order=:id&$limit=25` — with
  geometry the payload is big enough that larger pages time out) and run
  point-in-polygon in the client. `scripts/seed_pages.py` does this and its
  results were checked against the live `intersects()` query.
- **A district can have several rows, and they disagree.** Duboce Park Historic
  District has one row carrying its Article 10 designation (`cr: No`,
  `a10: Listed`) and another carrying its California Register eligibility
  (`cr: Eligible`, `a10: No`), over the same ground. Reading whichever comes
  back first reports "no local landmark protection" for a parcel that is in an
  Article 10 district. Merge rows by `name_1` and take the strongest status of
  each kind. A parcel can also sit in two genuinely different districts (129 in
  the Castro are in both Chula-Abbey and Chula-Dolores-17th) — lead with the
  one that confers protection and name the other.
- **State the status precisely.** "Eligible" for the California Register is
  **not** "listed", and neither implies local landmark protection — that
  requires an Article 10 district (`a10`). A parcel in a CR-eligible,
  non-Article-10 district carries no local landmark protection; don't imply
  otherwise. Note also that district-derived Category A applies to the whole
  parcel regardless of the building's age, so a modern building inside a
  district still reads as A (see 707 Castro Street, built 1980).
- **Citation label:** "SF Planning Department"
- **Verified:** 2026-07-27 (202 districts paged in with geometry; local
  point-in-polygon reproduces the live query — 711 and 737 Castro St resolve to
  the Castro & Liberty Streets Historic District, CR-eligible, period
  1897–1906, not Article 10; 720 Castro St, on the even side of the same block,
  is inside no district; 19 Hartford St → Hartford Street Historic District)

## historical-imagery — OpenSFHistory & Wikimedia Commons

- **What:** Historical photographs. Wikimedia Commons has a proper API and
  clear licenses — images may be downloaded into `assets/` **only** when the
  license permits redistribution (PD, CC BY, CC BY-SA) and must carry
  credit + license in the figure caption. OpenSFHistory (Western Neighborhoods
  Project) images are generally **link/cite only** — check terms per image.
- **Endpoint:** `https://commons.wikimedia.org/w/api.php`
- **Verified:** —

## streetview — Google Maps Embed API (live embed only)

- **What:** Present-day imagery for every page via a live Street View embed.
- **How:** iframe snippet in [shared/AGENTS.md](shared/AGENTS.md), using
  `maps_embed_key` from `shared/site-config.json` and coordinates from
  `data.json`. Free at any volume in embed form.
- **Do not test, validate, or preview the embed. Ever.** `maps_embed_key` is
  restricted to the production domain, so it returns an error for *every*
  request from a local server, a preview host, `curl`, or a headless browser.
  A failed embed in local preview is the key working as configured — it is not
  a bug, there is nothing to diagnose, and confirming it costs tokens to
  re-learn a fact this file already states. Author the `<ktp-streetview>`
  placeholder from `shared/AGENTS.md`, and move on. The only thing to check is
  that `location="LAT,LNG"` matches `coordinates` in `data.json`.
- **Hard rule:** **Never download, screenshot, or commit Street View imagery
  into `assets/`** — that violates Google's terms. Live embed only.

## sf-dpr-forms — Historic resource survey forms (primary)

- **What:** The State of California DPR 523 forms behind a parcel's
  historic-resource status — the survey's own building record, with the
  architect, the original owner, the construction dates, the style, and the
  evaluation. Where one exists it beats every secondary source on the page.
- **Endpoint:** `https://sfplanninggis.org/docs/DPRForms/<apn>.pdf` — the bare
  APN, no dash (e.g. `3708097.pdf` for 25 Jessie Street). Not every parcel has
  one; a 404 just means no form was prepared.
- **Cautions:** the form's own narrative sometimes contradicts the year built
  it quotes from the assessor (25 Jessie's form lists 1982 and then says the
  building was "completed in 1983"). Record both.
- **Citation label:** "State of California DPR 523 form for <address>, via SF
  Planning"
- **Verified:** 2026-08-06 (apn 3708097 → 25 Jessie Street / One Ecker Square,
  Jorge de Quesada, 1982–83)

## Research sources — cataloged in `research/`

Newspapers, books, journals, newsletters, context statements and survey reports
are **not** listed here. Each has a dossier under `research/sources/<id>.md`,
registered in [research/SOURCES.md](research/SOURCES.md), and is cited on a
page by the same `id` it always was. The ids already on pages:

| id | what | dossier |
|---|---|---|
| `argonaut-sfhs` | *The Argonaut*, journal of the SF Historical Society | [research/sources/argonaut-sfhs.md](research/sources/argonaut-sfhs.md) |
| `celebrity-residence-guides` | Notable-resident guides (tertiary) | [research/sources/celebrity-residence-guides.md](research/sources/celebrity-residence-guides.md) |
| `corbett-heights-neighbors` | Corbett Heights Neighbors newsletter | [research/sources/corbett-heights-neighbors.md](research/sources/corbett-heights-neighbors.md) |
| `digitalsf` | DigitalSF, San Francisco Public Library's catalogued digital archive | [research/sources/digitalsf.md](research/sources/digitalsf.md) |
| `hittell-1878` | Hittell, *History of San Francisco* (1878) | [research/sources/hittell-1878.md](research/sources/hittell-1878.md) |
| `loc-newspapers` | Chronicling America OCR (Morning Call / SF Call) | [research/sources/loc-newspapers.md](research/sources/loc-newspapers.md) |
| `local-news` | Neighborhood news outlets | [research/sources/local-news.md](research/sources/local-news.md) |
| `sf-context-statements` | SF Planning historic context statements & surveys | [research/sources/sf-context-statements.md](research/sources/sf-context-statements.md) |
| `spur-popos-guide` | SPUR, *Secrets of San Francisco* | [research/sources/spur-popos-guide.md](research/sources/spur-popos-guide.md) |

Editing a page still means citing these normally — the dossier is where the
access notes, cautions and coverage log live, and it is the file a research
agent updates after a pass.

## Known gaps

- **Sale/transfer history:** San Francisco recorder data has no free public
  API. The assessor roll's assessed values and recorded-document hints are
  what we have. Paid options (ATTOM, Estated, CoreLogic) are a future
  decision — don't scrape listing sites (Zillow/Redfin terms prohibit it).
- **Census/ACS demographics:** neighborhood-level context only, for hub
  pages. Never present block-level demographics on an individual address
  page.

## Adding a source

**An API or bulk dataset the site queries** gets a section here, in the same
shape (id, What, Endpoint, Use for, Cautions, Citation label, Verified), in
priority order, referenced by `id` from `data.json`. Sources must be either
open data, properly licensed, or plainly citable public web pages.

**Anything read rather than queried** — an archive, a book, a run of a
newspaper, a newsletter, a PDF report — is a research source. Don't add it
here: register it in [research/SOURCES.md](research/SOURCES.md) and write its
dossier, per [research/RUNBOOK.md](research/RUNBOOK.md) → "A prospecting run."
