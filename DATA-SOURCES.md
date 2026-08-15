# Data sources

The APIs and datasets agents draw from, in priority order. **Prefer these over
unguided web browsing** — they're accurate, fast, and auditable. Every fact
taken from a source gets an entry in the page's `data.json` `sources` array
(query URL + retrieval date) and a citation in the page footer.

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

> **Most of a source is expected to be irrelevant.** The secondary corpora
> below are read for the few passages that carry a street number, and the ratio
> is brutal by design — 58,620 OCR pages of Chronicling America yielded usable
> mentions for 2,025 addresses; Hittell's 1878 history is a whole book with a
> modest number of numbered addresses in it. **A low hit rate is the shape of
> the work, not a bad source or a mistaken request.** Run the scan, report the
> yield as a count, and never stop to ask whether so little signal is worth
> extracting — see "Mining a corpus for address-level facts" in
> [AGENTS.md](AGENTS.md).

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

## corbett-heights-neighbors — Local history research (secondary)

- **What:** The Corbett Heights Neighbors newsletter carries researched
  per-building history — first owners, contractors, permit dates and stated
  build costs, drawn from building permits, federal censuses and period
  newspapers. The association also publishes Michael Corbett's *Corbett
  Heights: San Francisco, An Historic Context Statement* (2017).
- **Archive:** <https://corbettneighbors.optin.com/newsletter/awlist6655060>
  (association site: <https://corbettneighbors.com>)
- **How to cite:** name the specific issue — title, volume and number, and
  publication date — and link that issue, not the archive index. Where the
  newsletter names its own underlying source (a permit date, a census year, a
  dated newspaper item), **repeat that in the citation** so the chain is
  auditable.
- **Facts, not prose — and cite in the footer only.** Extract discrete facts
  and present them as timeline items, spec rows, tiles and tags; never
  paraphrase the source's sentences (facts aren't copyrightable, wording is).
  **Never name the newsletter in the page body** — it means nothing to a
  reader with no context for it; the citation lives in the Sources footer.
  See `corbett-heights/AGENTS.md`.
- **Cautions:**
  - **Historical addresses.** Street numbers changed in 1909, streets were
    expunged by the Market Street extension, and buildings have been
    demolished, so an address in the newsletter may not exist today. Check
    EAS before creating a page (see `corbett-heights/AGENTS.md` for worked
    examples).
  - **Photograph dates contradict the assessor.** The newsletter dates
    buildings from photographs; the assessor's `year_property_built` often
    disagrees, in both directions. Record both and name the conflict in the
    page's `.unknowns` — never reconcile them silently.
  - **Buildings were moved.** At least one (11 Mars, from Falcon Street) was
    relocated, so a construction date may belong to a different site.
  - **Living people.** Some issues are personal memoirs naming family
    members and the houses they lived in. Take the building facts; leave the
    people out, per the privacy rules in the root AGENTS.md. Deceased
    figures already published with dates (first owners, builders) may be
    named with citations.
- **Coverage so far:** the archive holds 48 issues across 5 pages. All ten
  issues on **page 1** (Dec 2025 – Jul 2026) have been combed; pages 2–5
  (38 issues) are untouched. Page 1 still holds unwritten material on Hattie
  Street, Ord Street and upper Clayton — see issue #3.
- **Verified:** 2026-07-22 (page 1 of the archive, Dec 2025 – Jul 2026)

## loc-newspapers — Historic newspapers, Chronicling America (secondary)

- **What:** Full-text OCR of digitized San Francisco dailies from the Library
  of Congress. A local mirror lives in `sources/loc-newspapers/` (not committed
  — see `.gitignore`); `state.json` records which batches have been pulled.
  Two titles are held so far, and their runs abut exactly, because the first
  was renamed into the second:
  - `sn94052989` — *The Morning Call* (San Francisco). Local coverage: 1890–1894.
  - `sn85066387` — *The San Francisco Call*. Local coverage: 1895–1896,
    1900–1902, 1905–1910.
- **Citation URL:** `https://chroniclingamerica.loc.gov/lccn/<lccn>/<YYYY-MM-DD>/ed-<n>/seq-<n>/`
  — one page image; it redirects to the current `loc.gov` viewer. The OCR file
  path maps to it directly: `sn85066387/1895/04/08-ed-1-seq-004.txt` →
  `.../sn85066387/1895-04-08/ed-1/seq-4/` (drop the leading zeros on `seq`).
- **Citation label:** name the paper, the issue date and the page —
  "*The San Francisco Call*, 8 April 1895, p. 4".

### What is actually usable

Four recurring columns carry address-level facts. Only two of them resolve to
a street number, which is the whole constraint:

- **"Building Contracts" / "Builders' Contracts"** — owner, contractor,
  architect, scope of work and cost. This is a **pre-DBI permit record**, and
  the richest thing in the corpus. But it identifies *new* buildings by
  metes and bounds ("east line of Folsom street, 85 feet south of Twentieth"),
  and only gives a street number for **alterations to an existing building**.
  Those numbered entries are few but excellent.
- **"Real Estate Transactions"** — near-useless as it stands. Entries are
  metes-and-bounds, and the recorded consideration is almost always a nominal
  `$10` or `gift`, not a price. The occasional entry that names a street
  number *and* a real price ("known as 1311 Alabama street, 40x100 feet, sold
  … for $2400") is worth having.
- **"Fire Alarms"** — date, time, alarm box, address, building form
  ("two-story frame") and the damage. Numbered, dated, and directly usable.
- **Classified ads** (to let, for sale, business notices) — the bulk of the
  hits. An ad is dated proof a building **stood at that number**, and often
  states its room count, form (cottage / flat / house) and cross-streets.

### Cautions

- **Verify the number against the cross-streets — the ads hand you the check.**
  Most entries say "bet. 19th and 20th" or "near Guerrero." Confirm that
  against the parcel's own coordinates before trusting the match. Where an
  entry gives lot dimensions, check them against the assessor's `lot_area`:
  25x125 against 3,125 sq ft is a parcel identification, not a coincidence.
- **Mission and Eureka Valley street numbers did *not* move in 1909.** The
  general warning in `corbett-heights/AGENTS.md` still holds for renamed
  streets, but every cross-street check run here resolves to today's number
  (824 Valencia "bet. 19th and 20th"; 3460 16th "between Church and Sanchez";
  2995 Folsom "corner 26th"). Check, don't assume, and don't extend this to
  other neighborhoods.
- **Streets were renamed — and one was renumbered with it.** Lexington Street
  was Lexington *Avenue*, and Cesar Chavez was **Army Street**; both are pure
  renames, so the numbers carry over.
  **South Van Ness is not.** It was Howard Street until 1932, numbered as a
  continuation of Howard through SoMa, and it was **renumbered** when it was
  renamed. Measured against the modern block faces in `3psu-pn9h` (94 ads in
  this corpus that give a Howard number *and* a cross street):

  | at cross street | historical Howard | modern South Van Ness |
  |---|---|---|
  | 13th | ~1616–1759 | 193–249 |
  | 16th | ~1919–2004 | 467–499 |
  | 20th | ~2400–2424 | 801–899 |
  | 21st | ~2505–2544 | 901–999 |
  | 22nd | ~2600s | 1001–1099 |
  | 24th | ~2752–2867 | 1201–1299 |

  The offset is roughly −1,600 over 17th–24th but only about −1,500 nearer
  13th–16th, so **subtracting a constant misplaces buildings by up to a whole
  block.** Convert per block face using the cross streets, or skip the street.
  A Mission-numbered "Howard street" address is never today's Howard Street
  (which ends at 13th) — but it is not that number on South Van Ness either.
- **The OCR is dirty, and it gets worse after 1906.** Expect mangled digits and
  interleaved column text. Read the surrounding lines before trusting a
  reading, and never take a number from OCR alone if the page turns on it.
- **A mention that predates the assessor's `year_property_built` is not proof
  the assessor is wrong** — the building may have been replaced. Record the
  dated fact, name the disagreement in `.unknowns`, and don't adjudicate it
  (the same rule as the Corbett Heights photographs).
- **People.** These columns are full of names — householders in want-ads,
  the dead in funeral notices, tenants in fire reports. Per the root
  `AGENTS.md`, take **contractors, architects and named firms**; leave
  residents, occupants and owners out, however long dead.
- **Coverage is partial.** `state.json` lists 10 batches / 43,769 pages of a
  much larger archive; `batch-index.json` enumerates what has not been pulled.
- **Verified:** 2026-08-04 (58,620 OCR pages scanned; 8,437 numbered-address
  mentions on streets that have pages, across 2,025 distinct addresses)

## hittell-1878 — Hittell's *History of San Francisco* (secondary, period)

- **What:** John S. Hittell, *A History of the City of San Francisco and
  Incidentally of the State of California* (San Francisco: A. L. Bancroft &
  Company, 1878). A Centennial-year history by the Society of California
  Pioneers' own historian, written from the city archives, the mission records
  and the recollections of surviving pioneers. Numbered sections (§1–§245) make
  citation precise — cite the section, not the page.
- **Item record:** <https://www.loc.gov/item/rc01000675/> (Library of Congress,
  call number F869.S3 H7; also available in digital form). Public domain.
- **Use for:** what stood on a site before the present building — Hittell names
  a modest number of addresses by street number (§231 lists the buildings and
  the fortunes that paid for them) and describes the missions, the presidio and
  the Yerba Buena village lots at length.
- **Cautions:**
  - **Street numbers are the binding problem.** Hittell writes in 1878; street
    numbers changed, streets were renamed (his Dupont Street is today's Grant
    Avenue), and nothing here establishes that an 1878 number is the same
    parcel as today's. Check EAS first — several of his addresses (811 Dupont,
    419 and 317 California, 228 Montgomery) have no modern EAS record at all,
    which is the end of the matter under the directory contract. Where a number
    does resolve, say on the page that the correspondence is unverified.
  - **The buildings are usually gone.** He is describing a city that burned in
    1906. Treat his claim as *site* history — record it under
    `historical_record` with `"kind": "site history"` and the source, and let
    the assessor's `year_property_built` show that the structure he saw is not
    the one standing.
  - **He editorializes, and he speculates.** He flags his own guesses ("presump-
    tively the same structure"), and elsewhere he does not. Take dates, names
    and events; leave the judgements, and never carry his characterizations of
    Indigenous people into a page.
  - **He is a source for the site, not for the present parcel.** Every
    structured fact on the page still comes from the city datasets.
- **Citation label:** "John S. Hittell, *A History of the City of San Francisco
  and Incidentally of the State of California* (1878), §N"
- **Verified:** 2026-08-04 (§231 gives 400 and 420 Montgomery Street to Samuel
  Brannan, 1853; §12–14, 24 and 27 cover the founding and secularization of
  Mission San Francisco de Asís)

## spur-popos-guide — SPUR, *Secrets of San Francisco* (secondary)

- **What:** SPUR's field guide to the downtown POPOS, written from site visits.
  It carries what the city's own inventory doesn't: what a space is actually
  made of, how you get into it, whether the seating has quietly been annexed by
  a restaurant, and a plain quality rating (Excellent / Good / Fair / Poor).
  The best available second opinion on the `sf-popos` rows.
- **Guide:** <https://www.spur.org/sites/default/files/2013-10/popos-guide.pdf>
  (SF Planning publishes its own map and guide at
  <https://sfplanninggis.org/popos/POPOS_and_PublicArt.pdf>, which is the
  better source for entrances and hours.)
- **Cautions:**
  - **Fetch it as a PDF and extract the text** — `WebFetch` returns nothing
    usable for either file. Agents that have got at it used `pdftotext` or
    `pypdf`.
  - **It is dated.** The guide is a 2010s snapshot; hours, furniture and food
    service have changed, and several spaces have been renovated since.
    Prefer `sf-popos` for the facts a page states, and use SPUR for design
    description and for a documented discrepancy.
  - **Its ratings are judgements, not facts.** Never carry "rated Excellent"
    onto a page as if it were a property of the space.
  - It sometimes assigns a space to the wrong address — it places a kinetic
    ring sculpture at 560 Mission that another source gives to 201 Mission.
    Check the address against `sf-popos` before using an entry.
- **Citation label:** "SPUR, *Secrets of San Francisco: A Guide to San
  Francisco's Privately-Owned Public Open Spaces*"
- **Verified:** 2026-08-06

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
## argonaut-sfhs — *The Argonaut*, journal of the SF Historical Society (secondary)

- **What:** *The Argonaut: Journal of the San Francisco Historical Society*, a
  twice-yearly peer-reviewed local-history journal. Articles are researched from
  the city directories, period newspapers, corporate records and family papers,
  and they name streets and buildings constantly. Volumes read into the repo so
  far:
  - **29 no. 2 (Winter 2018)** — Robert Bardell, "The Presidio & Ferries
    Railroad" (pp. 6–33); Robert Cherny, "A New Eyewitness Account of the 1906
    Earthquake" (pp. 34–43); Ken Sproul, ed., "Letter by William Hindshaw"
    (pp. 44–55).
  - **30 no. 1 (Summer 2019)**, the Midwinter Fair issue — Taryn Edwards,
    "Before the Midwinter Fair: The Mechanics' Institute's 'Pacific Rim'
    Industrial Exhibitions of 1869 and 1871" (pp. 8–23); Lee Bruno, "The Winter
    of Our Dreams" (pp. 24–33); Lorri Ungaretti, "A Look at the Midwinter Fair"
    (pp. 34–65); Rodger C. Birt, "A Rare Midwinter Exposition Artifact"
    (pp. 66–71); Sofia Herron Geller, "Art Activism" (pp. 74–79).
  - **30 no. 2 (Winter 2020)** — Vincent Ring, "A Second Tunnel for The Sunset"
    (pp. 6–21); Hudson Bell, "The Last Bastion of San Francisco's Californios:
    The Mission Dolores Settlement, 1834–1848" (pp. 22–41); Peter M. Field,
    "A Tenderloin District History: The Pioneers of St. Ann's Valley: 1847–1860"
    (pp. 42–83).
  - **31 no. 1 (Summer 2020)** — Stefanie E. Williams, "The Rise and Decline of
    the German-Speaking Community in San Francisco, 1850–1924" (pp. 6–51);
    William R. Huber, "Sutro's San Francisco—What's Left?" (pp. 52–71); Alan
    Ziajka, "World War I and the University of San Francisco" (pp. 72–80).
  - **31 no. 2 (Winter 2021)**, the Black San Francisco issue — James L.
    Taylor, "Introduction: A Paradigm for Civil Rights in California"
    (pp. 6–11); Paul Gutierrez, "Mary Ellen Pleasant's Quest for Equality for
    All" (pp. 12–27); Lee Bruno, "We Are Brethren: San Francisco's
    19th-century African American Newspapers' Relentless Pursuit of Liberty and
    Justice" (pp. 28–41); Hudson Bell, "Exodus: San Francisco's Black Community
    in the 1850s" (pp. 42–53); Philip M. Montesano, "San Francisco Black
    Churches in the Early 1860s: Political Pressure Group" (pp. 54–61); Rodger
    C. Birt and Charles Wong, "The Western Addition District: Documentary
    Project" (pp. 88–103); Winnie Quock, "Botany and Horticulture: Symbols of
    Flourishing Against the Odds" (pp. 106–110).
  - **32 no. 1 (Summer 2021)** — Angus Macfarlane, "Putting San Francisco on
    the Map, Part 1: A Riddle Wrapped in a Mystery, Inside an Enigma"
    (pp. 8–29); Gary F. Kurutz, "Woodward's Gardens: Robert B. Woodward's
    'Central Park of the Pacific'" (pp. 30–63); Lisa Dunseth, "The Junior
    Recreation Museum in Balboa Park: The Brainchild of Josephine Randall and
    Bert Walker" (pp. 64–80).
- **Format:** print journal; no API and no per-article URL. Cite author,
  article title, volume, issue, season, year and page range. Publisher: San
  Francisco Historical Society, P.O. Box 420470, San Francisco, CA 94142-0470.
- **Use for:** what a site was before its present building — a car barn, a
  factory, a pleasure resort — and for dated events (a house reported nearly
  completed, a service that ended). Record each as one `historical_record`
  entry, usually `"kind": "site history"`.
- **Cautions:**
  - **Most of what it names has no street number.** These articles locate
    things by corner ("Union and Laguna," "Fillmore and Bay") or by landmark
    ("the site of today's Marina Safeway"). Nothing here resolves a corner to a
    parcel without guessing, so those get no page — the same rule as
    `hittell-1878`.
  - **Numbered addresses still have to clear EAS.** 847 Valencia Street and 616
    Filbert Street, both named in the Winter 2018 volume, have no modern EAS
    record; under the directory contract that is the end of the matter.
  - **A demolished building can take its number with it.** The Summer 2021
    volume gives 600 Ocean Avenue as the address of the Junior Recreation
    Museum's original home in Balboa Park, which it says was demolished for
    freeway construction. EAS has no record of 600 Ocean Avenue today — the
    number itself didn't survive the building — so it gets no page, the same
    outcome as a corner that never had a number at all. 1661 Octavia Street,
    Mary Ellen Pleasant's "House of Mystery" in the Winter 2021 volume, goes
    the same way: no EAS record, and no active parcel range on Octavia covers
    the number (1650 and 1700 are the nearest).
  - **A nineteenth-century street number is not a modern one.** The Winter 2021
    volume gives 273 Washington Street for the Atheneum Institute and locates
    it on Washington between Stockton and Powell. Today's 273 Washington would
    be eight blocks east, between Battery and Front, and EAS has no such
    address in any case. 184 Clay Street "at Kearny" and 119 Merchant Street
    "between Montgomery and Kearny" fail the same way — EAS's Merchant Street
    now begins at 408. A number that contradicts its own cross-streets is a
    pre-renumbering address, not a second building and not a resolvable one.
  - **A city survey name can resolve a segment the volume leaves open.** The
    same volume puts Third Baptist's first church on "Dupont (now Grant Avenue)
    between Greenwich and Filbert," with no number. Planning's `3tsw-4idn`
    names parcel 0087009 — 1640–1644 Grant Avenue — `SITE OF FIRST COLORED
    BAPTIST CHURCH; TH`, and SF Planning's landmark designation report for the
    congregation cites the State DPR registration application for "1642-44
    Grant Avenue." No guessing is involved, so it gets a page. Query the `name`
    field on candidate parcels before writing a segment off.
  - **A congregation's present address resolves what its history doesn't.** The
    Winter 2021 volume locates the three churches formed in 1852 by corner and
    segment throughout — Scott Street, Powell between Jackson and Pacific,
    Stockton between Clay and Sacramento — and then gives each congregation's
    present-day numbered address. Those three clear EAS and become pages
    (1399 McAllister, 970 Laguna, 2155–2159 Golden Gate); the nineteenth-century
    corners behind them do not. The page is about the building at the modern
    number; the earlier sites are `historical_record` entries on it.
  - **Golden Gate Park is one parcel.** Parcel 1700001 carries more than sixty
    EAS addresses, among them the de Young Museum at 50 Hagiwara Tea Garden
    Drive, the Japanese Tea Garden at 75, and the California Academy of Sciences
    at 55 Music Concourse Drive. A page on that parcel would describe the park,
    not any of them, so the Winter 2021 volume's whole Golden Gate Park walking
    tour lands on no page — the same outcome as the SFSU campus below.
  - **The journal isn't only about San Francisco.** The Summer 2021 volume
    follows General Vallejo to Casa Grande in Sonoma and Robert Woodward to
    Oak Knoll in Napa County. Both are real, dated, numbered-enough facts, and
    neither gets a page here — this site covers San Francisco only.
  - **Its dates will disagree with the assessor.** Bardell dates the Casebolt
    house to a March 1868 newspaper report; the roll and Planning both say 1865.
    Record both and name the disagreement in `.unknowns` — never adjudicate.
  - **A relocated building is a claim about a structure, not a parcel.** Where
    the journal says a house was moved to an address, say so and leave the
    roll's year built standing beside it.
  - **A whole block named by the building on it today is resolvable; a corner
    is not.** The Summer 2019 volume puts the Mechanics' Institute's exhibition
    building on "the block that now contains the Bill Graham Civic Auditorium."
    That block is one parcel (0812001) carrying one EAS address, 99 Grove
    Street, which SF Planning names `EXPOSITION AUDITORIUM` — no guessing is
    involved, so it gets a page. "Larkin and Grove," a corner of the same block,
    still doesn't.
  - **A volume can contradict itself about a site.** The Summer 2019 volume
    describes the pavilion of the 1868–71 exhibitions as being at Union Square
    *and* at Larkin and Grove, which is where the 1882 building went. Record
    only what a page can support and leave the conflation alone.
  - **A named present-day building resolves a street segment; two named
    buildings resolve nothing.** The Winter 2020 volume puts Jonathan
    Kittredge's 1855 house on "the north side of Ellis Street between Powell and
    Mason" and adds that the property is now the Hotel Fusion. The hotel gives
    its own address as 140 Ellis Street — parcel 0326023, on the even-numbered
    (north) side of that block, which the EAS coordinates confirm — so the
    segment resolves without guessing and gets a page. The same volume puts an
    1847 pond at "Powell, Eddy, Market and Fifth" and names **two** present-day
    buildings for it, the Flood Building and San Francisco Centre. One
    intersection, two buildings, four corners: that resolves to no parcel, the
    same as "Larkin and Grove."
  - **A tunnel, a proposed route and a settlement are not parcels.** Most of the
    Winter 2020 volume is about things no parcel can hold — the Sunset Tunnel's
    bore under Buena Vista Park, two portals at Merrit/Danvers and Cole/Alma
    that were never built, a dedication crowd at an intersection, and the
    Mission Dolores and Yerba Buena settlements. A whole article can name places
    constantly and still yield nothing; record the pass and move on.
  - **A street number in the journal can point at the wrong building.** The
    Summer 2020 volume gives the German House as 624 Polk Street. 624 Polk is
    parcel 0741006B, which SF Planning names `MAYFAIR HOTEL` and dates to 1928.
    Every other detail in the same entry — the cornerstone ceremony at Polk and
    Turk, five storeys, completion in 1912, the landmark designation — matches
    0742002 across the street, which Planning names `CALIFORNIA HALL` and dates
    to 1912. Check a number against the parcel before taking it: a number that
    contradicts its own entry is a transcription error, not a second building.
  - **A campus is one parcel, and a floor of one building on it is not a page.**
    The volume puts the Sutro Library on the fifth and sixth floors of the
    J. Paul Leonard Library at 1600 Holloway Avenue. EAS gives 7299005 for that
    address, a retired APN; the parcel that exists now is 7299006, the whole
    3.9-million-sq-ft SFSU campus carrying three EAS addresses. A page there
    would describe the campus, not the library, so it gets none. The library's
    earlier home at 480 Winston Drive is its own parcel and does.
  - **An exempt public parcel reads as vacant on the roll.** 7298008 (470–480
    Winston Drive) is `Vacant Lot Public Use` with no building area, no year
    built and no assessed value in every roll year from 2007 through 2025 —
    including the years the Sutro Library was open on it. On land exempt from
    the secured roll the classification records the exemption, not what stands
    on the ground. Say that; never report the parcel as empty.
  - **People.** These articles are full of private individuals — earthquake
    survivors, families, children in an orphanage. Take the businessmen,
    builders and public figures the historical record already covers; leave
    everyone else out, per the root `AGENTS.md`.
- **Citation label:** "Author, 'Article title,' *The Argonaut: Journal of the
  San Francisco Historical Society*, vol. N, no. N (Season Year), pp. N–N"
- **Verified:** 2026-08-06 (vol. 29 no. 2, Winter 2018: 17 places named, 3 of
  which resolve to an EAS address — 440–444 Jackson, 2727 Pierce, 2460 Union.
  vol. 30 no. 1, Summer 2019: 12 places named, 3 of which resolve — 57–65 Post,
  1 Montgomery, 99 Grove. The other nine are located by corner, by street
  segment or by park feature: Montgomery between Post, Sutter and Kearny; Bush
  Street; 8th Street between Mission and Market; Larkin and Grove; Pier 70 /
  First and Mission; the Music Concourse; the Administration Building site at
  its western end; the Fine Arts Building site; and Strawberry Hill)
- **Verified:** 2026-08-11 (vol. 31 no. 1, Summer 2020: 36 places named, 7 of
  them with a street number, 2 of which become pages — 601–625 Polk, which the
  volume gives as 624 Polk, and 470–480 Winston Drive. Of the other five
  numbered addresses, 526 California, 117 Capp and 304 Turk have no EAS record;
  141 Albion is now five condominium parcels and is held back under the
  condominium rule in AGENTS.md; and 1600 Holloway is the whole SFSU campus
  parcel. The remaining 29 are located by corner, by street segment, by park
  feature or by venue name — Temple Emanu-El on Sutter, Belden Place, Woodward's
  Gardens, 18th near Valencia, 15th and Mission, 20th and Folsom, Army Street,
  Golden Gate Avenue, O'Farrell and Gough, Eddy and Gough, Sutter near
  Divisadero, Third and Market, the Golden Gate Park bandstand, Eighth and
  Brannan, Sutro Heights, the Cliff House, Sutro Baths, 48th and Point Lobos,
  the Sutro Depot, the Battery Street warehouse, the Montgomery Street offices,
  22nd near Howard, Turk Street, 12th and Folsom, Sutter Street, 2nd between
  Howard and Folsom, Hayes and Shrader, Fulton and Parker — and one, the
  Deutsches Altenheim, is in Oakland)
- **Verified:** 2026-08-11 (vol. 30 no. 2, Winter 2020: 16 places named, **none
  of them with a street number**, and 1 of which resolves — 140 Ellis Street,
  reached through the present-day hotel the volume names on the site. The other
  15 are corners, street segments, an intersection, a tunnel alignment, two
  portals that were never built and two settlements: Mason between Eddy and
  Ellis; Powell/Eddy/Market/Fifth; Ellis between Stockton and Powell; Powell and
  Ellis; Turk and Polk; Eddy between Market and Mason; Geary and Mason; Market
  between Fourth and Fifth; O'Farrell between Mason and Taylor; O'Farrell
  between Taylor and Jones; Taylor and Eddy; the Merrit/Danvers and Cole/Alma
  portals; the Duboce Avenue tunnel route; 48th and Judah; the Mission Dolores
  settlement; and Yerba Buena. The Ring and Bell articles land on no page)
- **Verified:** 2026-08-12 (vol. 32 no. 1, Summer 2021: 10 places named, 2 of
  which become pages — 678 Mission Street, reached through the California
  Historical Society building the volume names on the O'Farrell grant site
  (occupied 1993–2024, since sold), and 199 Museum Way, reached through the
  Randall Museum the volume names on the Corona Heights site. Of the other
  eight: Casa Grande (Sonoma) and Oak Knoll (Napa County) are outside San
  Francisco; 600 Ocean Avenue's building was demolished and the address no
  longer clears EAS; and the west side of Grant Avenue between Clay and
  Washington, the site southeast of the Richardson home, the corner of
  Sacramento and Leidesdorff, Mission Street between 13th and 15th, and Laurel
  Hill Cemetery are all located by segment, corner or landmark rather than a
  resolvable number)
- **Verified:** 2026-08-12 (vol. 31 no. 2, Winter 2021: 17 places named, plus
  the present-day address the volume gives for each of the three congregations
  it follows — 20 in all — 4 of which become pages. Three are those present-day
  addresses: 1399 McAllister Street (Third Baptist Church, Landmark No. 275),
  970 Laguna Street (Bethel A.M.E. Church) and 2155–2159 Golden Gate Avenue
  (First A.M.E. Zion Church, landmark designation initiated March 2026). The
  fourth is 1640–1644 Grant Avenue, reached through Planning's survey name for
  the parcel. Of the other 16: 1661 Octavia, 273 Washington, 184 Clay and 119
  Merchant are numbered but have no EAS record, and the last three are
  pre-renumbering addresses whose own cross-streets place them elsewhere;
  Jessie and Ecker, Battery and Washington, Post and Kearny, and Jane and
  Natoma are corners; Sansome between California and Pine, Powell between
  Jackson and Pacific, Stockton between Clay and Sacramento, and Scott Street
  are segments; and Golden Gate Park, the de Young Museum, the Japanese Tea
  Garden and the California Academy of Sciences all sit on parcel 1700001, the
  park itself. Only Montesano's article yields a page; the Taylor, Gutierrez,
  Bruno, Bell, Birt/Wong and Quock articles land on none)
- **Coverage:** volumes 29 no. 2, 30 nos. 1–2, 31 nos. 1–2 and 32 no. 1 read in
  full.

## local-news — Neighborhood news (secondary)

- **What:** Context and stories: Hoodline Castro archives, Bay Area Reporter
  archive (ebar.com), SF Chronicle. No structured APIs — this is cite-the-URL
  browsing territory. Quote sparingly; summarize and link.
- **Use for:** notable events tied to a specific address. Skip for routine
  seeding.

## celebrity-residence-guides — Notable-resident claims (tertiary)

- **What:** Tourism and pop-history guides that list addresses where public
  figures lived. Used so far: SF Tourism Tips, "Where Famous People Lived in
  San Francisco" — <https://www.sftourismtips.com/where-famous-people-lived-in-san-francisco.html>.
- **Treat as the weakest tier of source.** These pages rarely cite where
  their own claims come from, and they contradict each other on dates and
  even on which building. That doesn't make them unusable — it makes them
  *attributed* rather than asserted.
- **How to use:**
  - **Attribute in the page body, not just the footer** ("a published guide
    to notable residences records…"), so a reader can see the claim is
    second-hand. This is the opposite of the corbett-heights rule, where the
    underlying research is primary and the newsletter name means nothing to
    a reader.
  - **Carry the source's own hedges and conflicts through.** Where the guide
    flags a claim as disputed, or two addresses compete for the same story,
    say so on both pages and cross-link them — never silently pick a winner.
  - One claim is **one `.tag` or one `.speclist` row**, per the writing
    rules. A notable resident does not earn a prose section.
  - Never state a residency as fact in `data.json`; nest it under a
    `notable_residents` array whose entries each carry `"source"` and, where
    the guide hedges, `"disputed": true`.
- **Privacy — the binding constraint.** The root AGENTS.md bars naming or
  alluding to **current** residents, publicly available or not. These guides
  routinely name people who still live at the address, often in the present
  tense ("when he's in town"). **Omit any claim phrased as present or
  ongoing occupancy**, and record the omission in the page's `.unknowns`
  without naming anyone. Only past residency — dated, or stated in the past
  tense about someone who has plainly moved on or died — may be named.
- **Citation label:** name the guide and its title, and link the page.
- **Verified:** 2026-07-23 (26 San Francisco addresses listed; all but one
  resolve in EAS)

## sf-context-statements — SF Planning historic context statements (secondary)

- **What:** The historic context statements SF Planning has adopted for
  individual neighborhoods and survey areas — consultant reports that set out
  an area's development history and then inventory its buildings. They are the
  richest address-level history available for the districts that have one, and
  they name streets and numbers constantly. The landing page listing the
  adopted statements is
  `https://sfplanning.org/project/sf-histories-historic-context-statements#completed`.
- **Read into the repo so far:**
  - Kelley & VerPlanck Historical Resources Consulting, *Bayview-Hunters Point
    Area B Survey: Town Center Activity Node — Historic Context Statement*,
    prepared for the San Francisco Redevelopment Agency, adopted February 11,
    2010 (197 pp.), source id `bvhp-area-b-context-statement`.
  - San Francisco Planning Department (Jonathan Lammers, project manager),
    *Central SoMa Historic Context Statement & Historic Resource Survey*,
    adopted by the Historic Preservation Commission March 16, 2016, Motion No.
    0277, Case No. 2011.1356E (115 pp.), source id
    `central-soma-context-statement`. The survey adopted with it — the
    property information catalog and the survey results table, which are in
    the hearing packet rather than the statement — is cited separately as
    `central-soma-survey`
    (`https://sfplanning.s3.amazonaws.com/commissions/hpcpackets/Central%20SoMa.pdf`,
    548 pp.). See "The Central SoMa statement" below.
  - San Francisco Planning Department, *Central Waterfront Cultural Resources
    Survey: Summary Report and Draft Context Statement*, prepared with the
    Central Waterfront Survey Advisory Committee, San Francisco Architectural
    Heritage, the Dogpatch Neighborhood Association and Page & Turnbull,
    Architects, October 2000 – October 2001, adopted 2001 (43 pp.), source id
    `central-waterfront-context-statement`. Listed on the SF Planning page as
    "Central Waterfront Survey and Context Statement (Adopted 2001)". See
    "The Central Waterfront statement" below.
  - Michael R. Corbett, *Corbett Heights, San Francisco (Western Part of
    Eureka Valley) Historic Context Statement*, prepared for Corbett Heights
    Neighbors and funded by the Historic Preservation Fund Committee, adopted
    by the Historic Preservation Commission 16 August 2017, Motion No. 0314,
    Case No. 2015-006003SRV (261 pp.), source id
    `corbett-heights-context-statement`. The PDF is served from
    `default.sfplanning.org`, not the S3 archive:
    `http://default.sfplanning.org/Preservation/CorbettHeightsHCS/hp_corbett_hcs_HCS_FINAL-081617.pdf`
    (there is a May 2017 draft alongside it — take the FINAL). See "The
    Corbett Heights statement" below.
  - Christopher VerPlanck, *Dogpatch Historic District Survey* (description of
    the neighborhood, context statement, illustrations and survey forms),
    September 2001, adopted 2001 (35 pp.), source id
    `dogpatch-context-statement`. Listed on the SF Planning page as "Dogpatch
    Historic Context Statement (Adopted 2001)". It is **not** on the S3
    archive; SF Planning serves it from an M-Files vault, and the
    `SharedLinks.aspx` URL returns an HTML shell, not the PDF. The file itself
    is at the REST path that page's script names —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/3e8b29b9c2a36962ffa191a884c1aabb534f7de60b3808d9f8d7bfd966aa6d57/content`
    — while the `SharedLinks.aspx` form is what a page cites. See "The Dogpatch
    survey" below.
  - Christopher VerPlanck (VerPlanck Historic Preservation Consulting), *Duboce
    Triangle Historic Context Statement*, prepared for the Duboce Triangle
    Neighborhood Association, dated August 26, 2022, adopted 2022 (181 pp.),
    source id `duboce-triangle-context-statement`. The PDF is on the S3 archive
    at
    `https://sfplanning.s3.amazonaws.com/default/files/Preservation/DuboceTriangleHCS/preserv_duboce_triangleHCS-draft.pdf`.
    The cover and every page header read **DRAFT**, and the SF Planning listing
    page carries it under "Duboce Triangle Historic Context Statement (Adopted
    2022)"; there is no non-draft file. Cite it as adopted 2022 and say the file
    is the draft. See "The Duboce Triangle statement" below.
  - Elaine B. Stiles, *Eureka Valley Historic Context Statement*, prepared for
    the Eureka Valley Neighborhood Association with the San Francisco Historic
    Preservation Fund Committee and the Planning Department, adopted by the
    Historic Preservation Commission December 20, 2017 (260 pp.), source id
    `eureka-valley-context-statement`. The PDF is served from
    `default.sfplanning.org`, not the S3 archive:
    `http://default.sfplanning.org/Preservation/EurekaValleyHCS/hp_eureka_valley_hcs_HCS_FINAL-122017.pdf`
    (there is an April 2017 review draft alongside it — take the FINAL). **The
    cover of the FINAL carries the adoption line, but every page header still
    reads "DRAFT ‐ Eureka Valley Historic Context Statement / May 2017."** Cite
    it as adopted 2017. See "The Eureka Valley statement" below.
  - Carey & Co., Inc., *Historic Resources Evaluation: Glen Park Community
    Plan*, prepared for PBS&J, dated December 21, 2010, adopted 2011 (118 pp.),
    source id `glen-park-context-statement`. **It is not titled a context
    statement** — it is the CEQA historic resources evaluation for the Glen
    Park Community Plan EIR, containing a context statement as one of its four
    tasks — and SF Planning lists it as "Glen Park Historic Context Statement
    (Adopted 2011)". SF Planning serves it from the same M-Files vault as the
    Dogpatch survey, so the `SharedLinks.aspx` URL returns an HTML shell; the
    file itself is at the REST path
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/e21915779d1b8ac21bb5023f7b6d453afaec3018897014eb32cd699ef9af3fc3/content`
    while the `SharedLinks.aspx` form is what a page cites. See "The Glen Park
    evaluation" below.
  - Kelley & VerPlanck Historical Resources Consulting (Tim Kelley and
    Christopher VerPlanck), *India Basin Survey, San Francisco, California —
    Final Report*, prepared for the Bayview Historical Society, dated May 1,
    2008, adopted 2008 (120 pp.), source id `india-basin-context-statement`.
    Listed on the SF Planning page as "India Basin Survey and Context Statement
    (Adopted 2008)". It is on the S3 archive at
    `https://sfplanning.s3.amazonaws.com/archives/documents/4049-Final_India%20Basin_05.01.08.pdf`.
    Same consultants as the Bayview-Hunters Point Area B statement two years
    later, and the two overlap on the three India Basin buildings that already
    had pages here. See "The India Basin survey" below.
- **Shape of the yield.** Two very different parts, and both are worth the
  pass:
  - **Appendix A, Table 1** is a per-property inventory — 159 rows carrying an
    APN, an address, a one-line description of the building, ratings from the
    earlier surveys (Here Today 1968, the 1976 citywide architectural survey,
    Article 10, the UMB survey, Carey & Company's South Bayshore survey) and a
    provisional California Register status code. This is structured data; parse
    it from the PDF's word positions rather than from `pdftotext` lines, or the
    superscript in "3<sup>rd</sup> Street" lands in the next row's address
    column.
  - **The narrative chapters** name maybe forty addresses with a real story
    attached, scattered through 190 pages of district history that names none.
    That is the normal ratio; see AGENTS.md → "Mining a corpus."
- **Cautions:**
  - **The addresses in the table are the survey's, not the city's.** Follow the
    APN, not the printed address, and check both against EAS: this one gives
    1420 Phelps Street for a parcel EAS calls 1450, 1773–75 Newcomb Avenue for
    a parcel on McKinnon, 5051 Third Street for the parcel EAS numbers 5075,
    and 1015 Third Street in its recommendations for the 5015 Third Street of
    its own table. Several APNs have since been retired.
  - **The status codes are provisional.** The report says so itself: they were
    assigned on architectural criteria alone. Its own recommendations define
    what the two "3" codes mean here — the 84 rows coded `3CS` are the
    properties it found may be eligible for the California Register under
    Criterion 3, and the rows coded `3S` are the properties it put forward as
    potential National Register or City Landmark listings. It never defines the
    Carey & Company or UMB rating scales, so record those without a gloss.
  - **The report contradicts itself in places** — 4408–42 Third Street is an
    Italianate commercial block in the table and a 1946 Streamline Moderne
    building in the text; 1552 Palou Avenue is an Eastlake farmhouse in one and
    a Queen Anne dwelling in the other. State the disagreement; don't
    adjudicate it.
  - Condition notes ("abandoned", "demolished") are as of 2009, and the
    assessor sometimes disagrees now.
- **The Central SoMa statement is shaped differently, and its inventory is not
  in it.** The adopted statement is 115 pages of narrative with no property
  table at all; the survey's per-property records live in the Historic
  Preservation Commission's adoption packet, which reprints the statement and
  then adds them. Read the packet, not just the statement.
  - **Packet pages 126–253 are the property information catalog**: one page per
    surveyed building, with the APN, the address, the year built, the proposed
    status code and Article 11 rating, the eligible district, and then the
    architect, historic name, style, frame, cladding, roofline, windows,
    ornament, integrity and the 1913 and 1950 Sanborn uses. 75 buildings.
  - **Packet pages 254–481 are the survey results table**, one row per parcel
    in the whole plan area — 1,004 of them. It is printed as six column-groups
    of 38 pages each (254, 292, 330, 368, 406, 444 are the group starts), so
    the columns for one parcel are spread across six pages. Parse it from word
    positions: rows are bottom-aligned, a row's band runs from just past the
    previous MAPBLKLOT anchor's y to its own, the first row of every page puts
    its wrapped opening line at y≈83.8 (above every anchor, below the y=74
    header), and the same band on the matching page of each group is the same
    parcel. Verified against the catalog: architect, historic name, style and
    frame agree on every property the two share.
  - **Take the short columns, not the long ones.** The join is exact but the
    wide free-text columns (ornament, windows, planning notes) overflow their
    column bounds and come back clipped. The catalog has the same fields laid
    out cleanly for the 75 buildings it covers; use it there and take only
    codes, ratings, names, styles and framing from the table.
  - **It contradicts itself between the two.** 633 Folsom Street is 6Z in the
    catalog and 3CS in the results table; 12 Mint Plaza is 6L and 6Z; 66 Mint
    Street is 3CD and 3CB. The catalog also splits a code the table combines
    (`1S, 3CD` against `3CB`). Record both and say which is which.
  - **The narrative contradicts itself too**: the Waldorf lodging house that
    survived 1906 is at 24–26 5th Street in one passage and 44–48 5th Street
    everywhere else; the California Casket Company building is 943 Mission in
    one and 959–965 Mission in the rest; the Central Hotel is 566–586 3rd
    Street twice and 576–586 once; the Southern Police Station is 360 4th
    Street throughout and 350 in a caption; the A. Carlisle building is 1948 in
    the text and 1947 in the recommendations.
  - **Most of the plan area was surveyed before.** For 386 of the parcels the
    only thing this document adds is which earlier survey covered them, and for
    33 it records nothing at all — those get no citation, because a page does
    not cite a source that told it nothing.
  - **A results-table row can describe a building that is gone.** 942 Mission
    Street is coded 6Z for a two-storey warehouse demolished in 2012; the
    assessor dates the hotel there now to 2015. Where the survey's year built
    and the roll's disagree the page states both.
**The Central Waterfront statement has no inventory in it at all, and that is
not a truncated download.** The archived PDF is the 43-page summary report and
context statement. Its table of contents promises eight appendices; six of them
are present only as one-line cover sheets. What is actually in the file:
- **Appendix C** — four maps (survey boundary, street names and the Dogpatch,
  P.G.&E. and Pier 70 sub-areas, the 1899 Sanborn, and the Bethlehem Steel
  general plan of 1957 with the Pier 70 building numbers).
- **Appendix E** — a one-page table of general periods of development.
- **Appendix F** — the definitions of the National Register status codes the
  survey used (1S, 2, 3B, 3D, 3S, 4D2, 4D5, 4R, 4S1, 4S2, 4X, 5S3, 5D1, 5N,
  5B1, 6Z1). Definitions only; no property is assigned one here.
- **Appendices A, B, D, G and H** — cover sheets. The DPR 523 forms, the NR
  Status Code Matrix, the Station A forms and Christopher VerPlanck's Dogpatch
  Historic Resource Survey and its own status-code matrix are all elsewhere.
  So **no per-property status code can be taken from this document.** The body
  gives them only by district and only as a majority ("the majority of
  resources in the Dogpatch neighborhood have been identified as 5D1"), which
  is not a finding about any one building — don't assign it to one. VerPlanck's
  Dogpatch survey is listed separately on the same SF Planning page as
  *Dogpatch Historic Context Statement*; the forms are the thing to go after
  when that one is read.
- **The addresses are in the narrative, and there are nine of them.** Two
  paragraphs on small oil companies and small Art Deco industrial buildings
  name four Third Street and 18th Street addresses as type examples; two more
  paragraphs on early dwellings name five. Everything else the report discusses
  is identified by Pier 70 building number (101, 102, 104, 105, 108, 109, 113,
  114, 116, 117, 118, 21, 38 — from a 1957 Bethlehem Steel plan, not a street
  grid) or by intersection: the California Canneries building at Minnesota and
  18th, the American Barrel Company at Sierra (22nd) and Illinois, the Western
  Sugar Refinery remnant at the foot of 23rd Street, the du Pont powder
  magazine at Maryland and Humboldt, the Union Iron Works administration
  building and Weeks & Day powerhouse at Illinois and 20th. None of those
  carries a street number and none of them became a page.
- **Cautions specific to it:**
  - **A named address can be a site, not a building.** 550 18th Street and
    2075 Third Street are one parcel (3994044), and the small oil-company
    buildings the survey pointed at are gone — the roll dates what stands there
    now to 2008 and Planning codes the parcel C. That address is documented as
    site history, not as a surveyed building.
  - **It contradicts itself on 718 22nd Street.** The text describes the
    dwelling at 718; footnote 32 and the bibliography both cite the DPR 523B
    form for it as "118 22nd Street". There is no 118 22nd Street in EAS. Both
    readings are on the page.
  - **Its dates run 20 to 30 years earlier than the assessor's.** The roll
    gives 1900 for four of these dwellings; the survey gives 1872, 1876, circa
    1875 and circa 1884. 1900 is the roll's default for a building it can't
    date, so the disagreement is worth recording rather than resolving.
  - **"Outside Dogpatch" means outside the 2001 survey's Dogpatch boundary.**
    Three of the buildings it files that way — 670–674 Tennessee, 2476–2478
    and 2636–2638 Third — are inside the Article 10 Dogpatch Historic District
    today. Don't read the survey's placement as a statement about the district.
  - Street renamings are given in passing and are worth keeping: Kentucky
    Street became Third Street, Sierra Street became 22nd Street, and the
    east-west streets were numbered in the first years of the 20th century.
**The Corbett Heights statement has three inventories and none of them is an
appendix table of the usual kind.** The document is a narrative history with
its address-level findings scattered across five places, and they disagree with
each other often enough that the disagreements are half the yield:
- **Section VI.B, "Potentially Significant Resources"** (pp. 188–189) — 48
  addresses with an estimated date and a one-line style. The report says in the
  same breath that it is *not a survey*, that the list is conservative rather
  than exhaustive, and that omission from it means nothing. Every page that
  carries a row from it says so.
- **Appendix F reprints two earlier surveys.** The 1968 Junior League *Here
  Today* listing (21 addresses with a one-line identifier) was adopted by the
  Board of Supervisors under Resolution No. 268-70, so Planning counts those
  buildings as individual historic resources — that is the one place in this
  document with real regulatory weight. The 1976 Department of City Planning
  architectural survey (74 rows) gives a block and lot, an address, and a
  rating of 0–5 where a second number is a reviewer's revision; it was never
  adopted. Appendix F also carries the two City Landmarks in the area,
  No. 79 (Miller-Joost House, 3224 Market) and No. 80 (Nobby Clarke Mansion,
  250 Douglass), both designated 7 December 1975.
- **Two "Partial List of Buildings" tables** (pp. 78 and 142) are the best
  thing in it — 23 buildings of 1860–1906 and 15 of 1906–1945 with a date and
  a named architect, contractor or builder drawn from *California Architect and
  Building News*, the historian Gary Goss's files and the 1900 census. **Their
  owner column is dropped on the way in**, per the privacy rules; the
  architects and contractors are kept.
- **The rest is in figure captions.** Roughly forty more dates and styles
  appear only under photographs, and several of them contradict the tables.
- **Cautions:**
  - **The 1976 block and lot are 1976's.** Nineteen of its 96 parcels no longer
    exist in EAS, and several that do have been re-lotted so the old lot now
    points at a different building: 2655/22 is printed "1262 Clayton" and
    resolves to 1272; 2656/27 is printed "3090 Market" and resolves to 3088;
    2654/8 is printed "48 Mars" and resolves to 52; 2625/18 is printed "2
    Douglass" and resolves to 7 Ord. Match on the printed address, record the
    printed block and lot beside it as `apn_as_surveyed`, and let a reader see
    both.
  - **It contradicts itself on dates.** 99 Ord Street is 1931 in the text and
    1932 in the potentially-significant list; 312 Caselli is 1894 in a caption
    and 1893 in the list; 64–68 Douglass is 1908 in a caption and 1909 in the
    architects' table; 4789 Nineteenth is 1908 in the table and 1909 in the
    text. Moody's candy factory is at 4655 Eighteenth in one passage and 4653
    in another, and the Coffin row on Caselli is seven houses in the text and
    eight in the builder's own advertisement. All of these are on the pages as
    stated disagreements.
  - **Its dates run ahead of the assessor's, and the roll's 1900 is a
    placeholder.** Where the two disagree the page shows the roll in the
    `Built …` tag and the report's date as `building.completed`, with the
    conflict named in `.unknowns`.
  - **Condominium conversion has eaten a lot of this area.** Fifteen of the
    parcels the report names are now condominium APNs the roll gives 0 lot
    area, so AGENTS.md holds them back — including three of the buildings the
    1968 survey listed.
  - **It names San Francisco addresses well outside the neighborhood**, as the
    other work of the architects who built in it (the Chancellor Hotel, the
    Native Sons Building, the James Lick Baths, the Chateau Tivoli) and as the
    house of the man who subdivided it. Those are documented as building
    credits on their own pages, not as anything the statement surveyed.
**The Dogpatch survey is the report the Central Waterfront statement points at,
and it stops one section short of its own inventory.** Its table of contents
promises four sections and the PDF carries three: the description of the
neighborhood, the context statement, and the illustrations. **Section 4,
"Dogpatch Historic District Survey Forms," is not in the file** — pages 30–35
are figures and the document ends there. So this one, like the Central
Waterfront statement, assigns no status code to any single building, and the
DPR 523B forms it cites in its own footnotes are still elsewhere.
- **What is in it is narrative, and dense with numbers.** The two prose
  sections name 90 distinct numbered San Francisco addresses in 28 pages, a far
  higher rate than the other statements here — the description section alone
  lists the neighborhood's builders address by address, and its non-contributor
  and heavily-altered paragraphs are effectively an inventory written as prose.
- **Cautions specific to it:**
  - **The survey's dates run 5 to 30 years ahead of the assessor's, and the
    roll's 1900 is a placeholder.** Of the 60 parcels documented here, 23 carry
    a dated conflict. Where the two disagree the page shows the roll in the
    `Built …` tag and the survey's date as `building.completed`, with the
    conflict named in `.unknowns`.
  - **Its printed ranges do not always match a parcel.** "800-04 22nd Street"
    spans two parcels (800–802 and 804–806) and both pages say so; "760-790
    Tennessee" spans three; "1103-05 Tennessee" and "1105-07 Tennessee" are the
    same building under two numbers in the same document, and only 1105–1107 is
    an address the city carries. Match on the printed address, record it as
    `address_as_surveyed`, and let a reader see both.
  - **It repeats the Central Waterfront statement's 118 22nd Street error** —
    the same author's footnote again gives the DPR 523B form for the dwelling
    at 718 22nd Street as "118 22nd Street", an address EAS has never had.
  - **It contradicts itself on the vacant lots**, listing "six vacant lots" and
    then naming seven, and on 740 Tennessee Street, which it says was
    constructed in 1881 and, four pages later, was moved to the site that year.
    Both readings are on the page.
  - **Two of the buildings it calls non-contributors predate the period of
    significance it gives.** 991 Tennessee (roll: 1933) and 1025 Tennessee
    (roll: 1937) are grouped with the 14 buildings it says were "constructed
    after the period of significance," which it defines as 1867–1945.
  - **Condominium conversion has taken out much of the best of it.** Fourteen
    of the addresses it names are now condominium APNs the roll gives 0 lot
    area, so AGENTS.md holds them back — including 920–922 Minnesota, half of
    the pair it names as a type example, and 1016–18 Tennessee.
  - **Business proprietors are named throughout** — the grocers, saloon-keepers
    and butchers of the 1890s to the 1940s, by name and address. Those are
    owners and occupants, so the pages carry the **firms** (Howley's Liquors,
    Dugan's Liquors, J. J. Twomey & Son's Market, Graham Fuel & Feed) and not
    the people. The architects, carpenters and contractors are kept.
  - Street renamings are given in passing, matching the Central Waterfront
    statement: Kentucky Street became Third Street, Sierra Street became 22nd
    Street, Butte Street became 19th, Solano Street became 18th, and Napa
    Street became 20th.
**The Duboce Triangle statement has no inventory table at all.** Like Central
SoMa, it is narrative from end to end: 130 pages of neighborhood history, a
chapter on property types and architectural styles, and a recommendations
chapter. The accompanying survey inventoried 552 properties and its
spreadsheet is not in the file, so the statement assigns no status code, rating
or per-property record to anything. What it does carry, and what the pages here
take, is a list of potential city landmark candidates, five proposed local
landmark districts with their member addresses printed out, and several dozen
buildings named in the narrative with a style, an estimated date and a reason
for the mention.
- **Cautions specific to it:**
  - **The candidate list is 38 entries and the text calls it 37.** "Presented
    below is a list of 37 potential city landmark candidates," the
    recommendations chapter says, and "Photographs of all 37 properties follow";
    the introduction says 38 twice. The bullets number 38. Every page that
    carries the candidacy says so.
  - **It contradicts itself on addresses more than most.** The Charles Strothoff
    House is 2274 15th Street in the narrative, 2272–2276 15th Street in the
    candidate list and 2272–2276 **16th** Street in the styles chapter; the
    apartment building at 221 Noe Street is 211 Noe in its figure caption; the
    1937 mixed-use building at 286–288 Noe Street is 266–268 Noe in its figure
    caption; 282 Castro Street is 282 **Church** Street in its figure caption;
    2168 15th Street is 2168 **18th** Street in its figure caption; the
    Norwegian-Danish Methodist church is 750 14th Street in the Scandinavian
    institution list and 754 14th Street in the narrative, and EAS has only 750.
    Follow EAS, record the printed form as `address_as_surveyed`, and name the
    disagreement.
  - **It contradicts itself on dates and on the Born tract's builder.** 963 14th
    Street is Ca. 1885 and Ca. 1880; 245 Castro Street is Ca. 1870 and Ca. 1875;
    101–111 Noe Street is Ca. 1890 and Ca. 1895; 106–112 Noe Street is 1924
    and 1922; 178–180 Church Street is a 1937 building and a 1911 building
    remodelled Ca. 1935; 3633–3635 16th Street is a 1940s building and a
    Victorian remodelled Ca. 1935; the St. Ansgar/Gethsemane merger is 1964 and
    1965; the Castro Street tract is Stephen A. Born's and William S. Born's.
    Both readings go on the page.
  - **Its "Ca." dates are estimates and the roll's 1900 is a placeholder**, so
    most of the disagreement between them is not a finding. The estimated date
    goes in `historic_survey.year_built_as_surveyed`, never in
    `building.completed`, which is reserved here for the dates the statement
    documents outright.
  - **Condominium conversion has taken out a quarter of what it names.**
    Twenty-eight of the parcels are now condominium APNs, which AGENTS.md holds
    back — including nine of the 38 landmark candidates. Ten of those
    twenty-eight are conversions since the last roll year their old APN appears
    in, so the APN EAS still carries has no 2025 roll row and the successor is a
    condominium.
  - **The Market Street frontage is deliberately outside its survey** — it was
    covered by the 2006–09 Market & Octavia survey — but the statement
    discusses those buildings anyway, so the Swedish American Hall, the José
    Theater and Safeway are all named without being inventoried.
  - **Business proprietors and building owners are named in passing**, as in the
    Dogpatch survey. Architects, builders and contractors are kept; residents
    and owners are not.
**The Eureka Valley statement has no appendix inventory either, and its
address-level findings are spread across four places.** Like Central SoMa and
Duboce Triangle it is narrative from end to end — 240 pages of neighbourhood
history, property types and styles, evaluation frameworks and recommendations —
with no property table and no status code assigned to any building. What it
carries at address level is:
- **The builder tables in the Streetcar Suburb chapter** (pp. 51–55), the best
  thing in it. Fernando Nelson's is a real inventory: ~50 rows of address, date,
  house form and style. Shorter runs follow for Charles L. Hinkel (5 houses),
  Louis Landler (11), John Anderson (2 rows covering 19 houses) and John A.
  Swenson (2).
- **The figure captions in the property-type and architectural-style chapters**
  (pp. 135–201), which are effectively a second inventory written as captions:
  roughly ninety buildings with a date, a form and a style.
- **The narrative chapters**, which name the churches, halls, banks, garages,
  schools, the library, the post office, the recreation centre, the breweries
  and bottling works, and — through long quotations from the 2015 citywide
  LGBTQ context statement — several dozen bars, shops and organisations.
- **The evaluation frameworks** (pp. 204–240), which name about twenty-five
  buildings as worked examples of what might be eligible under each criterion,
  and the **recommendations** (pp. 241–243), which put forward three potential
  San Francisco Landmarks — the Fernando Nelson House, the Kirby House and
  Phoenix Brewery, and the Charles Hinkel House — plus four concentrations of
  developer housing to study as potential historic districts.
- **Cautions:**
  - **Check a printed disagreement against the parcel before recording it as
    one.** This statement names buildings by whichever of a parcel's street
    numbers is to hand, and several apparent contradictions are nothing of the
    kind: Cliff's Variety is 471 Castro Street in the property-type chapter and
    479 in a footnote, and EAS puts 471, 479 and 483 on one parcel; the bank at
    Castro and Market is 410 in most passages, 400 and 400–410 in two captions,
    and 400 and 410 are one parcel. Collingwood Hall's 4144 and 4150 18th
    Street, and the Elephant Walk's 500 and 506 Castro Street, are the same
    again. Resolve both numbers before writing the disagreement down.
  - **The disagreements that survive that test cluster on its own landmarks.**
    The Castro Theater is 429 Castro Street in the landmark list and the style
    chapter and 429–431 in a caption, but the recommendations and an LGBTQ HCS
    quotation attach **Landmark #100 to 479 Castro Street** — a different parcel,
    and the one the statement itself identifies as the site of the Nasser
    Brothers' theatre of 1910, this theatre's predecessor, so the slip is
    between the two theatre sites rather than random. The Twin Peaks Tavern is
    401 Castro Street in the landmark list and **410** in an LGBTQ HCS
    quotation, 410 being the bank across the intersection. The Kirby/Phoenix
    Brewery building is 552 Noe Street in a caption and **560** in the
    industrial-production framework — two parcels — while the Kirby residence is
    560 in the narrative and **550** in a caption, a number EAS has never
    carried. Collingwood Hall is on 18th Street throughout and on **Collingwood
    Street** once. The Swedish-American Hall is 2168–2173 Market Street in the
    landmark list and **1274 Market Street** twice; the Women's Building is 3543
    18th Street once and **3548** twice, a different block. Nelson's Hartford
    Street row is 20–64 in the builder table and **2–64** in the
    recommendations. Record both readings and follow EAS.
  - **It contradicts itself on dates too.** Most Holy Redeemer is 1901 in the
    narrative and 1900 in the style chapter; the recreation centre is 1954 in a
    caption and 1956 in the text; 3951–3959 17th Street is 1910 with 28 units in
    one caption, 1910 with 20 units in the evaluation framework and ca. 1915 in
    another caption; 546 Liberty Street is 1897 in Nelson's table and ca. 1900 in
    a caption; 187 Douglass Street is ca. 1900 in one caption and ca. 1870 in
    another; 2500 Market Street is 1933 in the text and 1920 in a caption; the
    Hinkel house is 1892 in the builder table and 1891 in the recommendations,
    and Hinkel dies in 1908 in one passage and "sometime between 1900 and 1910"
    in another. The Castro group is 740–748 Castro, ca. 1892 in one caption and
    742–750 Castro, 1895/1898 in another.
  - **Its dates are reconnaissance-level and the statement says so twice** — it
    is "an evaluative tool, not a decision-making document," and inclusion or
    exclusion "does not represent a value judgement." Every page carrying a row
    from it says so.
  - **The roll's 1900 is a placeholder here as elsewhere**, so most of the gap
    between the statement's dates and the assessor's is not a finding. The
    statement's date goes in `historic_survey.year_built_as_surveyed` and is
    dropped where it simply matches the roll.
  - **Condominium conversion and stale APNs take out a tenth of what it names.**
    Twelve of the parcels are condominium APNs AGENTS.md holds back — including
    both halves of Nelson's 4141–4143 20th Street and his best house, the
    towered 4138 20th Street — and twenty more have no 2025 roll row, among them
    the Most Holy Redeemer neighbours at 150 Eureka Street, the earthquake
    cottages at 300 Cumberland Street and the Swedish-American Hall.
  - **Business proprietors, club presidents and bar owners are named
    throughout.** The firms are kept (Cora Lou Confectioners, Eggers & Company,
    the Phoenix Brewery, Ruby's Clay, Littleman's, McNaughton & Turner) and the
    proprietors are not. Architects, builders and contractors are kept, as are
    the public figures the historical record already covers — Harvey Milk, Bob
    Ross, Cleve Jones, Bobbi Campbell, Mayor P. H. McCarthy — and the civic-club
    leaders whose houses the statement names as their significance.
  - **It names addresses well outside the study area** as landmarks "related to
    Eureka Valley," as the earlier homes and first houses of its builders, and
    as citywide style examples. Those are documented as what they are, not as
    anything this statement surveyed.
**The Glen Park evaluation is a CEQA document, not a survey report, and that
changes the shape of everything in it.** Carey & Co. wrote it for the Glen Park
Community Plan EIR: a context statement of the neighborhood, a reconnaissance
survey of 110 parcels, an intensive survey of eight, a district analysis, an
impacts analysis and mitigation measures. It is 118 pages, of which roughly 30
are the context statement and 25 the property evaluations; the rest is
regulatory framework, prehistory, CEQA impact findings and the project
description. Where it carries address-level facts:
- **The "Description and Evaluation of Surveyed Properties" chapter**
  (pp. 44–60), the best thing in it — a full description, a documented
  construction date, an architect or builder from the building permits, an
  eligibility finding and an integrity assessment for each of seven properties
  on eight parcels: 584 Bosworth Street, 21 Brompton Avenue, 23–25 Brompton
  Avenue, 2830–2842 and 2852–2862 Diamond Street, the Glen Park BART station
  and its power station, and the Glen Park Elementary School. Five are found
  not eligible, the station eligible for the California Register only, and the
  school eligible for the National Register, the California Register and City
  Landmark designation.
- **A five-entry list in the impacts chapter** (p. 67) of the buildings the
  **San Francisco Planning Department** — not Carey & Co. — found eligible for
  the California Register in its own survey of the area west of Lippard Avenue
  and the NC district: 601 Bosworth Street, 657, 683 and 701–703 Chenery
  Street, and 2784–2786 Diamond Street. That survey, "Glen Park Area Plan HRE:
  West of Lippard and NCT" (SFPD 2010), holds the DPR forms and is a separate
  document.
- **The cultural-context and property-type chapters**, which name about
  thirty addresses as dated examples of a builder's cottages, a style or a
  building type, mostly in photograph captions.
- **Cautions:**
  - **Appendix C is a cover sheet.** The introduction says every one of the 110
    surveyed parcels was recorded on a DPR 523A form and the eight evaluated
    ones on 523B forms, "which are located in Appendix C." The appendix in the
    archived PDF is one title page and nothing else, so **no per-property DPR
    record, rating or status code can be taken from this document** — the
    reconnaissance survey of the other 102 parcels is effectively not in it.
    Appendices A-1 and A-2 are maps and Appendix B is the project description.
  - **It assigns no California Historical Resource Status Codes at all.** It
    lists the seven code headings in its regulatory chapter and then evaluates
    in prose. Pages carry the finding in `historic_survey.finding`, which is
    why that key exists; never translate a finding into a code.
  - **It contradicts itself on addresses, and the archived scan is annotated.**
    The Planning Department's eligible list prints "2784-2786 Chenery Street"
    for a Diamond Street parcel, and someone has written DIAMOND above it in
    ink on the archived copy. A photograph caption gives 701 Chenery Street as
    "107 Chenery Street"; the Spanish Eclectic commercial building at Chenery
    and Diamond is 664–670 in the text and 664–676 in both its captions, which
    is three parcels rather than two; 645 Bosworth Street is "645 Bosworth
    Avenue" four times and never "Street"; and 23–25 Brompton Avenue is
    "Brompton Street" twice.
  - **Its own counts do not always match.** The Craftsman row it prints as
    "763-791 Chenery Street" is "a row of five Craftsman homes" in the text and
    six parcels on the roll, all of them built 1921–1922.
  - **The city has since disagreed with its district finding.** The evaluation
    examined four concentrations, including the commercial core at Diamond and
    Chenery, and concluded that no eligible historic district exists in the
    plan area; Planning now carries seven of these parcels in the California
    Register-eligible **Glen Park Center Historic District** (period of
    significance 1897–1929). Planning also gives the BART station as
    individually listed on the National Register, which this evaluation found
    it not yet eligible for. Both disagreements are stated on the pages.
  - **Its dates are from building permits, not estimates**, so where they
    disagree with the roll the disagreement is real: 657 Chenery Street is 1872
    against the roll's 1900, 701–703 Chenery is "the early 1890s" against 1904,
    and 2852–2862 Diamond is 1925 against 1924. It also describes 21 Brompton
    Avenue as a three-story apartment building where the roll has a two-story
    single-family dwelling.
  - **It is dense with residents, and they are the bulk of its property
    histories.** Each of the five evaluated non-eligible properties gets a
    paragraph tracing owners and tenants through the census, city directories,
    voter registrations and the assessor's sales ledgers, by name and
    occupation, some of them still the owners. All of that is left out under
    the privacy rules. The **firms** are kept (the Mission Building Company,
    Van's Barber & Beauty Shop, Kerr's Toggery, the Glen Park Cleaners, Lucas'
    Hair Designing, the Glen Park Barber Shop, Derian Jewelers, the Enterprise
    Steam Beer Saloon, the G. H. Umbsden Realty Company), and so are the
    architects and builders (V. Teslo, Christopher J. Kernan, H. Barker, Lewis
    P. Hobart, Bliss & Fairweather, J. L. McLaughlin, Leo Epp, DeLuca and Sons,
    Ernest Born, Corlett & Spackman, Douglas Baylis, William G. Merchant, and
    the dairyman William Tietz who built his own house).
**The India Basin survey is the one document in this set whose own DPR 523
forms are in it**, and they are most of its value. It is 120 pages: 51 of
narrative, bibliography and recommendations, and the rest an appendix holding
38 Primary Records (523A), 13 Building, Structure and Object Records (523B) and
one District Record (523D) for a proposed boat-yard district. Where its
address-level facts are:
- **The 38 Primary Records** cover every building in the survey area built in
  or before 1962 — an APN, a street address, a construction date from the
  Department of Building Inspection, a resource-attribute code and a paragraph
  of physical description apiece. A Primary Record carries no status code and
  no eligibility finding, so most of these become a survey panel with a note
  and nothing else.
- **The 13 Building, Structure and Object Records** are the evaluated ones:
  a National Register status code (3S, 3CS, 6L, 6Y, 6Z), an architectural
  style, a builder, a construction history and a written eligibility finding.
  Four properties are found eligible — the Albion Brewery (881 Innes, National
  Register), and 900 Innes, 911 Innes, 967 Innes and 702 Earl Street for the
  California Register — and the rest are found ineligible, two of them with a
  note that they nevertheless warrant special consideration in local planning.
- **The District Record** proposes an India Basin Boat Yards district of eight
  parcels centred on Hudson Avenue and Griffith Street, eligible for the
  California Register under Criteria 1 and 3, period of significance 1893–1935.
  It describes each parcel's docks, ways, shops and sheds by APN, and it is the
  only place the report dates the boat-yard buildings.
- **The narrative chapters** name about a dozen more addresses — the school,
  the co-operative store, Anderson's own house and shop, the war-worker
  "junior fives" — of which most are numbers the city no longer carries.
- **Cautions:**
  - **The locational-data field (P2e) on a Primary Record is often the
    previous form's APN, copied down a run of adjacent properties.** 714, 718
    and 724 Innes all print Lot 003B; 939, 943 and 947 all print Lot 016B;
    1064 and 1068 both print Lot 007A. The form's own identifier field (P1) is
    the correct one in every case checked, and it is what the assessor's
    `property_location` agrees with. Take P1, not P2e.
  - **Two forms print the wrong block.** 951 and 955 Innes are given as Block
    3653; both are Block 4653.
  - **Its own counts do not match the appendix.** The methodology chapter says
    it prepared 523B forms "for twelve individual properties built before
    1939"; the appendix holds thirteen, all of them pre-1939. The report also
    gives the Hunters Point Restaurant a 1976 summary rating of 1 at 850 Innes
    while filing the restaurant's Primary Record under 840 Innes.
  - **EAS is the stale side here, not the survey.** 863 and 869 Innes Avenue
    resolve in EAS to Lots 014B and 014A, parcels the assessor has retired and
    the parcel dataset marks inactive; the survey's Lots 022 and 021 are the
    live ones and carry those addresses on the current roll. 714 Innes has an
    EAS row with no parcel number at all, and the survey's Lot 003 is what the
    roll puts the address on.
  - **It contradicts itself on the Hunters Point Restaurant, and on two
    dates.** The restaurant is 840 Innes Avenue in the property-type chapter
    and on its own form, and 850 Innes Avenue — Pop Anderson's house — in the
    1976-survey list and the condition chapter. 869 Innes is 2003 on its form
    and a 1938 "junior five" in the narrative; 967 Innes is 1917 on its form
    and in its building record and 1920 in the narrative; 963 Innes is the
    Wilmer and Hilda Wilson Residence on its form and "the Jorgensen cottage"
    in the narrative. Two of the building records date a house a year before
    its own Primary Record does (935 Innes: June 1934 against 1935; 993 Innes:
    November 1937 against 1938).
  - **Its addresses for the church do not agree either.** Our Lady of Lourdes
    at 410 Hawes Street is also identified as 955 Innes Avenue, which is a 1956
    dwelling on a different parcel across the avenue.
  - **The eight-parcel district it proposed is not the district the city now
    carries.** Planning maps the India Basin Scow Schooner Boatyard Vernacular
    Cultural Landscape over these parcels, California Register-eligible with a
    period of significance of 1875–1936, against the survey's 1893–1935. Both
    are on the pages.
  - **A large block of the waterfront has left the secured roll.** 702 Earl
    Street and 840 Innes Avenue, and four of the eight boat-yard parcels
    (4630/006, 4645/010, 010A and 011), are active parcels with EAS addresses
    whose APNs last appear on the 2023 roll, so the seeder makes no page for
    them — including the Heerdt boat yard at 702 Earl, one of the four
    properties the survey found individually eligible.
  - **The Building, Structure and Object Records are chains of title.** Each
    one traces owners and tenants by name through deeds, city directories and
    the census, often to the present owner, and the Primary Records print the
    current owner's name and address outright. All of that is left out under
    the privacy rules. The **builders** are kept (William J. Heerdt, Leo R.
    Miller, Konrad W. Richter, Arthur Simpson, Wilmer W. and Hilda A. Wilson,
    Ingeborg Jorgenson, Paul Runge, George M. Moore, James F. Gibbs and
    Katherine Stauffer), as are the shipwrights the repo already names —
    Johnson J. Dircks, William I. Stone, Henry P. "Pop" Anderson, Charles J.
    Jorgenson, Fred Siemer — the architects of the brewery's 1938
    reconstruction (Bakewell & Weihe), and the **firms** (Anderson &
    Cristofani, Allemand Brothers, Siemer & Bruer & Co., Wm. J. Heerdt Boat
    Building, Surfside Liquors, Nueva Castilla Iron Works, the Mountain Springs
    Water Company, R. F. J. Meiswinkel Co., Skyscraper Crane and Rigging Co.,
    Market Fellowship, the Hunters Point Co-operative Society).
  - Street renamings are given throughout and are worth keeping: Innes Avenue
    was 9th Avenue South and, for a decade from about 1880, Corea Avenue;
    Hudson was 8th Avenue South and Banama; Galvez was Trinidad; Griffith was
    'G' Street, Hawes 'H' Street, Lane 'L' Street; Evans was 5th Avenue South;
    Ingalls Street became Middle Point Road. The present names date from 1910.
- **Citation label:** name the consultant, the report and its adoption date,
  and link the SF Planning listing page.
- **Verified:** 2026-08-11 (read all 197 pages; 159 inventory rows plus ~60
  numbered-address mentions in the narrative, resolving to 190 parcels with
  EAS records and a current assessor roll row. Not resolvable, and so not
  documented: 4417–23 Third Street, rowhouses the survey records as demolished
  and whose parcels are retired; 894 Innes Avenue; 420 Pacific Street; and the
  two dozen addresses the report itself marks "no longer extant". Coverage
  note: the Central Waterfront, Market & Octavia, Japantown and other adopted
  statements on the same page are untouched.)
- **Verified:** 2026-08-12 (Central SoMa: read all 115 pages of the statement
  and all 548 of the adoption packet. 108 numbered addresses in the narrative
  chapters, 75 property records in the catalog and 1,004 rows in the survey
  results table, naming 995 distinct APNs between them. 755 of those resolve to
  a parcel with a 2025 assessor roll row and an EAS address and become a page:
  717 new pages citing this document, 3 pre-existing pages edited by hand, and
  35 new pages that cite nothing from it because its results table records
  nothing for them. A fourth pre-existing page, 845 Market Street, was edited
  by hand although its APN carries no EAS address of its own — the survey names
  it, and the page was already here. 240 APNs do not resolve: 91 are
  condominium parcels the roll gives 0 lot area and which AGENTS.md holds back,
  88 have no 2025 roll row, and 61 have no EAS address record. Of the addresses
  named only in the narrative, these clear none of that and stay undocumented:
  95 Jack London Alley, 222–226 Jessie Street, 465 Stevenson Street, 666 Folsom
  Street, 40 Hawthorne Street, 34 Mint Street, 935 Market Street, 935 Folsom
  Street, 336 Ritch Street, 83 6th Street and 790 Folsom Street have no EAS
  record at all; 128 King Street, 271 Clara Street, 365 5th Street, 434 Brannan
  Street, 633 Folsom Street and 801 Market Street resolve in EAS to a parcel
  with no current roll row; and 357 Tehama Street and 601 4th Street are
  condominium parcels. The report's own demolished addresses — 171 Howard
  Street, 693 Mission Street, 49 4th Street, 239 Minna Street, 820 Howard
  Street, 740 Harrison Street, 365 3rd Street, 727 Folsom Street and 390 4th
  Street — are named as gone and were never candidates. Coverage note: the
  statement and the packet are read in full; nothing in this document set is
  outstanding.)
- **Verified:** 2026-08-13 (Central Waterfront: read all 43 pages, which is the
  whole archived PDF — the report, its bibliography and image list, and the
  three appendices that carry content. 11 numbered San Francisco addresses
  appear in the text. Nine of them name buildings the survey recorded, and all
  nine resolve in EAS to 8 parcels, every one of them active in `acdm-wktn`
  with a 2025 roll row: 550 18th Street and 2075 Third Street are the same
  parcel, 3994044. All 8 became new pages under `san-francisco/dogpatch/`, a
  new neighborhood directory; no page here already covered any of them, so
  none were edited. The other two numbered addresses are not documented: 118
  22nd Street, which the bibliography and footnote 32 give as the DPR form's
  address for the dwelling the text calls 718 22nd Street, has no EAS record on
  22nd Street at all; and 536 Clay Street is the Hinton Printing Company's own
  address in an 1895 bibliographic citation, not a property in the survey area.
  The parcels: 3994044 (550–560 18th), 4043001 (707 18th), 4108006 (718 22nd),
  3996004 (670–674 Tennessee), 4044052 (2130 Third), 4108003R (2360–2364
  Third), 4108003D (2476–2478 Third), 4172020 (2636–2638 Third). Coverage note:
  this document is read in full and nothing in it is outstanding, but its own
  appendices are not in it — the DPR 523 forms, the NR Status Code Matrix and
  VerPlanck's Dogpatch Historic Resource Survey are separate documents and are
  untouched, as are the Market & Octavia, Japantown and other adopted
  statements on the same SF Planning page.)
- **Verified:** 2026-08-13 (Corbett Heights: read all 261 pages of the adopted
  final. 226 distinct numbered San Francisco addresses are named — 216 in the
  study area, across the five inventories and the figure captions, and 10
  elsewhere in the city as architects' other work or Pioche's own house. 200 of
  the 216 resolve in EAS, to 193 parcels. 174 pages now cite the document: 80
  new and 94 edited, across `castro` (101), `corbett-heights` (63),
  `nob-hill` (4, a new neighborhood directory with a hand-written hub),
  `mission` (2) and one each in `chinatown`, `south-of-market`, `tenderloin`
  and `western-addition`. Five of the edited pages are hand-authored HTML and
  were edited by hand, as was the Danvers Street hub, which carries
  hand-written sections the hub generator refuses to overwrite.
  Not documented, and why: **29 are condominium parcels** the roll gives 0 lot
  area, which AGENTS.md holds back — 4343 and 4378–4380 Seventeenth; 4515,
  4547, 4569, 4627, 4655, 4658, 4666 and 4683 Eighteenth; 4594 Nineteenth; 18,
  58, 246 and 248 Caselli; 4 Corwin; 64, 180 and 272 Douglass; 54 Lower
  Terrace; 2805 and 3393 Market; 68 Saturn; 38 Yukon; 1366 Clayton; 218 and 238
  Corbett; 25 Hattie; and 32 Eagle. Three of those (58 Caselli, 238 Corbett, 25
  Hattie) are buildings the adopted 1968 survey listed, so the condominium rule
  is holding back real historic resources here, not marginal ones. **Thirteen
  are named at a number EAS has never had**: 100 Ord, 228 Douglass, 360
  Caselli, 4513 Eighteenth, 201 Corbett, 111–123 Douglass (the California
  Brewing Company site), 50 Yukon, 98 Levant, 98 Carson, 24 Mars, 4695
  Eighteenth, 4228 Nineteenth and 1 Eagle. **Five more have an EAS row with no
  parcel number**: 4502 Eighteenth, 29 Ord, 4547 and 4569 Eighteenth, and 67
  Hattie. The first two are documented on the parcel their printed range or
  1976 lot lands on (4500 Eighteenth and 31 Ord); the last three are not.
  Three addresses printed as the report's own are documented under the number
  EAS gives the parcel: 4365–4369 Seventeenth on the 166 Corbett Avenue page,
  3064 Market on 3066 Market, and 4676–4680 Eighteenth on 4678. The addresses
  the report itself
  gives as historical — 2 and 103 and 427 Falcon Street, 3084 Merritt Street,
  1018 Seventeenth Street (where 126–128 Ord stood before 1894) and 110 Ord —
  are on streets the Market Street extension erased or numbers that no longer
  exist, and were never candidates; 126 Museum Way, demolished about 2008, is
  documented as site history on the parcel that carries the address today.
  Seven rows of the 1860–1906 research table give a cross-street rather than a
  number ("Hattie between Seventeenth and Eighteenth", "Ord and Seventeenth")
  and stay unresolved. Coverage note: this document is read in full and nothing
  in it is outstanding. The Corbett Heights Neighbors newsletter archive it
  draws on is a separate source (`corbett-heights-neighbors`, pages 2–5 still
  untouched), and the Eureka Valley, Duboce Triangle, Market & Octavia,
  Japantown and other adopted statements on the same SF Planning page are
  untouched.)
- **Verified:** 2026-08-13 (Dogpatch: read all 35 pages, which is the whole
  file — 28 of them carry text and the last six are figures. 90 distinct
  numbered San Francisco addresses appear in them. 58 resolve in EAS to 60
  parcels with a 2025 assessor roll row, and all 60 are now pages: 60 new ones
  under `san-francisco/dogpatch/` (37 Tennessee Street, 12 22nd Street, 9
  Minnesota Street, 1 Third Street) and `san-francisco/potrero-hill/`, a new
  neighborhood directory with a hand-written hub holding 1202–1204 19th Street.
  Three pages that already existed were edited by hand instead: 707 18th Street
  and 718 22nd Street, both from the Central Waterfront pass, and 132–142
  Second Street in `east-cut`, which the survey names as 140–42 2nd Street for
  a second Pelton skyscraper. 63 pages cite the document. 23 of them record a
  date the survey and the roll disagree on. Not documented, and why:
  **fourteen are condominium parcels** the roll gives 0 lot area, which
  AGENTS.md holds back — 900 and 920–22 Minnesota; 724–26, 900, 901, 950, 993,
  1011, 1016–18, 1108–10, 1159–63 and 1167–69 Tennessee; and 812–14 22nd. Two
  of those are buildings the survey treats as type examples (920–22 Minnesota,
  half of a named pair, and 1108–10 Tennessee, one of the four Welch flats), so
  the condominium rule is holding back contributors here, not intrusions.
  **Fifteen are named at a number EAS has never had**: 627, 699, 750, 800–50,
  850, 1005, 1007, 1009, 1185 and 1191 Tennessee; 118, 700 and 807 22nd; 2310
  Third; and 1532 Kentucky Street, whose street was renamed and renumbered as
  Third Street. Three of those are on parcels documented under another number —
  700 22nd on the 702 22nd Street page, 2310 Third on the 2300 Third Street
  page, and 807 22nd behind 1100 Tennessee — and are recorded there as the
  survey printed them. **One has an EAS row but no active parcel**: 1095–99
  Tennessee. **One is a strong match at a number the city does not carry**: the
  Kentucky Hotel of 1902, printed "2500-03 3rd Street", which is a range across
  both sides of the street; EAS has 2501 (the Muni yard) and 2502–2504 (an
  18-unit multi-family building of 1900 on the corner of 22nd). Neither number
  is the one printed, so it stays undocumented. Coverage note: this document is
  read in full and nothing in it is outstanding, but Section 4, its own survey
  forms, is not in the file — the DPR 523 forms are a separate document and are
  untouched, as are the Eureka Valley, Duboce Triangle, Market & Octavia,
  Japantown and other adopted statements on the same SF Planning page.)
- **Verified:** 2026-08-13 (Duboce Triangle: read all 181 pages of the adopted
  draft — the ten chronological chapters, the property-type and
  architectural-style chapters, the recommendations and the bibliography. **186
  distinct numbered San Francisco addresses are named**, counting a printed
  range by its low number: most of them in Duboce Triangle itself, the rest as
  the Scandinavian and Finnish institutions of the wider Upper Market area, as
  citywide examples of a style, or as the site of the Ham and Eggs Fire. **172
  have an EAS row and 171 of those carry a parcel number.** 138 pages now cite
  the document: **24 new and 114 edited**, across `castro` (130), `mission` (5),
  and one each in `hayes-valley`, `financial-district` and `inner-sunset` (a new
  neighborhood directory with a hand-written hub, for the Henry Doelger Building
  at 320 Judah Street). Of the 38 entries in the statement's landmark-candidate
  list, **29 are documented and 9 are held back as condominium parcels**.
  Not documented, and why: **28 are condominium parcels** the roll classes
  `Condominium`, which AGENTS.md holds back — 951–955 Fourteenth; 2150,
  2179–2183, 2229–2231, 2253–2255 and 2263–2265 Fifteenth; 45–49 and
  56–58 Beaver; 45–49 Belcher; 74–76, 84–86, 164–166, 210–212,
  214–216, 222–224 and 301–303 Castro; 200 Dolores; 19–23 Henry; 47,
  201–203, 207–209, 229–231, 233, 247–251 and 255–259 Noe; and 43–45,
  71 and 151–153 Sanchez. Nine of those are candidates on the statement's own
  landmark list, so the condominium rule is holding back the buildings it most
  wanted protected. Ten of the 28 converted after the roll year their old APN
  last appears in, so EAS still carries an APN with no 2025 roll row while the
  live successor is a condominium; 229–231 Noe has an EAS row with no parcel
  number at all. **Fourteen are named at a number EAS has never had**: 754
  Fourteenth, 2272 Sixteenth, 3276 Sixteenth, 3555 Sixteenth, 3744 Seventeenth,
  4032 Seventeenth, 2168 Eighteenth, 32 Beaver, 431 Duboce, 211 Noe, 250 Noe,
  479 Market, 725 O'Farrell and 320 Sansome. Four of those are the statement's
  own misprints and are documented under the number the city carries — 754
  Fourteenth on the 80 Belcher Street page, 2272 Sixteenth and 2168 Eighteenth
  on 2272–2276 and 2168 Fifteenth, and 211 Noe on 221 Noe — with the printed
  form recorded as `address_as_surveyed`. Six are buildings the statement itself
  records as demolished (the Swedish Athletic Club, the Swedish Home for Girls,
  Finnila's Finnish Baths, the Norwegian Singing Society hall, the villa at 32
  Beaver Street, and the apartment building at 250–258 Noe Street that burned
  in 1963 and is now the Noe-Beaver Mini Park). 3555 Sixteenth is the old
  Eureka Valley branch library, which the statement itself renumbers to 1 José
  Sarria Court; 479 Market is Cliff's Variety, which is on Castro Street, not
  Market; and 725 O'Farrell and 320 Sansome are a 1905 florist's shop and an
  1859 society's rooms, both long gone. Two addresses stand on parcels the roll
  has renumbered since EAS was last refreshed and are documented on the live
  APN: 300 Castro Street (2622002, not the 2622088 EAS gives) and 2168–2174
  Market Street (3542062, not 3542017). Coverage note: this document is read in
  full and nothing in it is outstanding, but the reconnaissance survey adopted
  alongside it — the GIS field application and the spreadsheet of all 552
  properties, with their estimated dates, methods of construction, uses, styles
  and alterations — is not in the file and is untouched, as are the Eureka
  Valley, Market & Octavia, Japantown and other adopted statements on the same
  SF Planning page.)
- **Verified:** 2026-08-14 (Eureka Valley: read all 260 pages of the adopted
  final — the seven chronological themes, the property-type and
  architectural-style chapters, the evaluation frameworks, the recommendations
  and the bibliography. **325 distinct numbered San Francisco addresses are
  named**, counting a printed range by each of its numbers: most of them in the
  study area between 16th and 21st streets, the rest as landmarks "related to
  Eureka Valley" outside it, as the earlier homes and first houses of its
  builders, or as citywide style examples. **305 of them resolve in EAS to a
  parcel; the 302 that also carry a usable fact collapse onto 297 parcels, 262
  of which may be documented.** 263 pages now cite the
  document: **36 new and 227 edited**, across `castro` (258) and one each in
  `mission`, `haight-ashbury`, `tenderloin`, `glen-park` and `noe-valley` — the
  last two new neighbourhood directories with hand-written hubs. Sixteen of the
  edited pages carry hand-authored HTML and had the survey panel and source
  line inserted by hand rather than regenerated.
  Not documented, and why: **15 are condominium parcels** the roll classes
  Condominium, which AGENTS.md holds back — and the conversions have taken most
  of one Fernando Nelson row: 4138, 4140, 4141 and 4143 20th Street, including
  the towered Queen Anne at 4138 that is the most elaborate house he built on
  that block. The rest are 39 Hartford Street; 571 and 573 Liberty Street, two
  of John Anderson's five; 129 Hancock Street; 294 Collingwood Street; 19 Eureka
  Street; 3918 and 3920 20th Street; 189 Collingwood Street; 356 Collingwood
  Street; and 336 Cumberland Street.
  **Twenty more have an EAS parcel with no 2025 roll row**, so the seeder will
  not make a page for them: 4000, 4036 and 4052 18th Street (three of Nelson's);
  40 Hartford Street; 750 and 757 Castro Street (one of them Hinkel's); 158 and
  150 and 201 Eureka Street — 150 being the Bethel/Central Baptist church that
  became the Metropolitan Community Church; 3936 and 3942 19th Street; 3525 16th
  Street; 482 Liberty Street; 3943 17th Street; 179 Douglass Street; 617 and 627
  Castro Street; 72 Collingwood Street, Mayor P. H. McCarthy's house; and 300
  Cumberland Street, the pair of 1906 earthquake cottages the statement calls the
  study area's one resource directly associated with the earthquake and fire.
  One of those twenty is documented anyway: EAS gives the Swedish-American Hall
  the retired APN 3542017, but the building already has a page under its current
  parcel 3542062, and that page carries the citation — which is why 263 pages
  cite the document against 262 documentable parcels.
  **Fourteen are named at a number EAS has never carried**: 406 and 709 Castro
  Street, 4062 and 4103–4105 18th Street, 4032 17th Street, 17 and 76
  Collingwood Street, 4448–4450 Douglass Street, 450 Sanchez Street, 1074
  Guerrero Street, and two of the report's own misprints — 2 Hartford Street,
  where the recommendations mean 20, and 4144–4150 Collingwood Street, where
  they mean 18th. **Six more have an EAS row with no parcel number**: 511 Castro
  Street, 3897 and 3988 18th Street, 4400 19th Street, and 65 and 234
  Collingwood Street. 1274 Market
  Street resolves, but the only thing the statement says about it — that it is
  the Swedish-American Hall — is a misprint for 2168–2174 Market Street, so it
  gets no page and the disagreement is recorded on the hall's own. The buildings
  the statement itself calls no longer extant — 406, 470–476 and 511 Castro
  Street, 17 and 76 Collingwood Street, the Douglass and Everett and McCreery
  buildings, the Trinity Methodist Episcopal church and the Twin Peaks Lodge Hall
  — were never candidates. Coverage note: this document is read in full and
  nothing in it is outstanding. The 2015 Citywide Historic Context Statement for
  LGBTQ History in San Francisco, which it quotes at length and defers to, is a
  separate document and is untouched, as are the Market & Octavia, Japantown and
  other adopted statements on the same SF Planning page.)
- **Verified:** 2026-08-14 (Glen Park: read all 118 pages, which is the whole
  archived PDF — the introduction and findings, the methodology, the regulatory
  framework, the cultural context, the property-type overview, the seven
  property evaluations, the district analysis, the impacts and mitigation
  chapters, the bibliography, and the four appendices, of which A-1 and A-2 are
  maps, B is the project description and C is a cover sheet with no DPR forms
  behind it. **58 distinct numbered San Francisco addresses are named**,
  counting a printed range by each of its numbers: 17 on Chenery Street, 14 on
  Diamond, 10 on Brompton, 5 on Bosworth, 4 on Wilder, 2 each on Joost and
  Lippard, and one each on Arlington, Congo, Monterey and Mission. **52 have an
  EAS row and 50 of those carry a parcel number** — the two that do not are 2856
  and 2901 Diamond Street. 44 pages now cite the document:
  **44 new and 0 edited**, all under `san-francisco/glen-park/`, across ten new
  street directories — chenery-street (16), brompton-avenue (10), diamond-street
  (5), bosworth-street (4), wilder-street (3), joost-avenue (2), and one each on
  arlington-street, congo-street, lippard-avenue and monterey-boulevard. Seven
  of the eight parcels the evaluation surveyed intensively are documented; the
  eighth, 23–25 Brompton Avenue, is documented as two pages because its Lot 030
  has since been split into Lots 033 and 034. Not documented, and why: **45
  Wilder Street** is now four condominium APNs on mapblklot 6745101, which
  AGENTS.md holds back. **The Glen Park BART power station** (Block 6745, Lot
  066) is an active parcel with a 2025 roll row, but the report gives it no
  street number and EAS carries no address for the parcel at all, so one of the
  eight evaluated properties has no page. **Six are named at a number EAS has
  never had**: 107 and 702 Chenery Street, 612 Bosworth Street, 2440 and 2909
  Diamond Street, and 2862 Diamond Street. 107 Chenery is the report's own
  caption misprint for 701 and is recorded on that page; 2440 Diamond is a
  firehouse the report calls no longer extant; 2909 Diamond is where the Glen
  Park Branch Library stood before BART, recorded on the station's page; 702
  Chenery is the Enterprise Steam Beer Saloon of 1898–1920 and 612 Bosworth the
  Mission Building Company's own address, neither of which the city carries;
  2862 Diamond is the assessor's high number for a parcel EAS tops out at 2860.
  **Two more resolve but are not documented**: 180 Lippard Avenue, where the
  only thing the report says is which named individual lived there, which the
  privacy rules withhold; and 1650 Mission Street, the Planning Department's own
  office in five footnotes, not a property in the survey. The Glen Park BART
  station is documented on the APN the report itself gives (6755026) — EAS
  carries 2901 Diamond Street with no parcel number, and the address point falls
  inside that parcel. Coverage note: this document is read in full and nothing
  in it is outstanding, but the DPR 523A and 523B forms its Appendix C promises
  are not in it, and the Planning Department's companion survey, "Glen Park Area
  Plan HRE: West of Lippard and NCT" (SFPD 2010) — which holds the DPR forms for
  the five buildings it found California Register-eligible and for 24 more — is
  a separate document and is untouched, as are the Market & Octavia, Japantown
  and other adopted statements on the same SF Planning page.)
- **Verified:** 2026-08-14 (India Basin: read all 120 pages, which is the whole
  archived PDF — the seven chronological context chapters, the property-type
  and recommendations chapters, the bibliography, Appendix A (three scanned
  Sanborn sheets of 1899–1900, 1913–15 and 1948–50, pp. 56–58, images with no
  text) and Appendix B, which holds 38 DPR 523A Primary Records, 13 523B
  Building, Structure and Object Records and one nine-page 523D District
  Record. **50 distinct numbered San Francisco addresses are named**, counting a
  printed range by the number the survey files it under: 39 on Innes Avenue, 3
  on Middle Point Road, 2 each on Earl and Hawes streets, and one each on
  Hunters Point Boulevard, Galvez Avenue, Jerrold Avenue and Revere Avenue. The
  ten owner and consultant addresses the Primary Records print — including 4000
  Third Street and 671 Illinois Street — are withheld under the privacy rules
  and are not counted. **41 of the 50 resolve to a parcel with an EAS address
  and a 2025 assessor roll row.** 43 pages now cite the document: **40 new and 3
  edited**, all under `san-francisco/bayview-hunters-point/` — innes-avenue
  (32), hudson-avenue (3), middle-point-road (3), hawes-street (2), and one each
  on earl-street, griffith-street and hunters-point-boulevard, six of those
  seven being new street directories. The three edited pages — 881, 900 and 911
  Innes Avenue, from the Area B pass — carry hand-authored HTML and had the
  survey panel, the new spec rows and the source line inserted by hand rather
  than regenerated. Of the eight parcels in the boat-yard district the survey
  proposed, four are documented (4629A/010 as 900 Hudson Avenue, 4630/002 as
  890 Hudson, 4646/001 as 901 Hudson, and 4646/002 as 404 Griffith Street, the
  parcel the district record addresses as 900A Innes Avenue). Not documented,
  and why: **six parcels are active, addressed and off the current roll** —
  their APNs last appear on the 2023 roll, so the seeder makes no page — namely
  702 Earl Street (the Heerdt boat yard of 1935, one of the four properties the
  survey found individually eligible), 840 Innes Avenue (the Hunters Point
  Restaurant), and the four remaining district parcels 4630/006, 4645/010,
  4645/010A and 4645/011, which hold the Allemand Brothers yard and its office
  of about 1930. **Five are named at a number EAS has never had**: 850 Innes
  Avenue (Pop Anderson's own house, and the address the 1976-survey list and
  the condition chapter give the Hunters Point Restaurant), 892 Innes (his
  boat-building shop and planing mill on the 1913–15 Sanborn, gone), 901 Innes
  (the Hunters Point School of 1911–1930, removed), 615 Galvez Avenue and 690
  Jerrold Avenue (the Hunters Point Co-operative Society's store of 1939 and
  the house it started in). Three more of the report's own numbers are
  documented under the number the city carries: 5 Earl Street and 700 Innes
  Avenue on the 740 Earl Street page, and 904½ Innes Avenue on 904 Innes, each
  with the printed form recorded as `address_as_surveyed`; 700A Innes Avenue is
  the report's own earlier number for 702 Earl Street, which has no page. 1109
  Revere Avenue is a grocer's shop named only as an owner's business and is
  withheld under the privacy rules. Two vacant lots the survey folds into the
  930 Innes Avenue record, 934 and 936 Innes, are documented within that page
  rather than as pages of their own, and so is 4646/005A, which carries no
  street address. Coverage note: this document is read in full and nothing in it
  is outstanding. The Market & Octavia, Japantown and other adopted statements
  on the same SF Planning page are untouched.)

## Known gaps

- **Sale/transfer history:** San Francisco recorder data has no free public
  API. The assessor roll's assessed values and recorded-document hints are
  what we have. Paid options (ATTOM, Estated, CoreLogic) are a future
  decision — don't scrape listing sites (Zillow/Redfin terms prohibit it).
- **Census/ACS demographics:** neighborhood-level context only, for hub
  pages. Never present block-level demographics on an individual address
  page.

## Adding a source

Add a section in the same shape (id, What, Endpoint, Use for, Cautions,
Citation label, Verified) in priority order, and reference its `id` from
`data.json`. Sources must be either open data, properly licensed, or
plainly citable public web pages.
