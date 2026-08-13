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
- **Citation label:** "SF Planning Department"
- **Verified:** 2026-07-27 (4,475 Castro parcels fetched by `apn` in chunks of
  400; apn 2752016 = 744 Castro St → ceqacode B)

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
  they name streets and numbers constantly — except when they don't. Some are
  guides written *for* a survey rather than reports of one, and those name no
  street numbers at all; the Mission District statement below is the worked
  example, and checking which kind you have is the first thing to do with a new
  one. The landing page listing the
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
  - San Francisco Planning Department (Matt Weintraub, Citywide Survey Project
    Manager, author), *City within a City: Historic Context Statement for San
    Francisco's Mission District*, November 2007, adopted 2007 (95 pp. in 98
    PDF pages), source id `mission-district-context-statement`. Listed on the
    SF Planning page as "Mission District (Adopted 2007)". **No page on this
    site cites it**, because it names no street numbers — see "The Mission
    District statement" below before spending a pass on it.
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
**The Mission District statement names no street numbers at all — not one, in
95 pages.** It is the one document in this set that yielded nothing, and the
reason is structural rather than accidental, so don't re-read it hoping for a
different answer:
- **It is a survey *guide*, not a survey.** Its stated job is to give the
  historic contexts, property types and registration requirements that the
  Department's own 2007–2008 surveys would then apply to individual buildings.
  It says so on its second page and again in "Existing Information and
  Programs": roughly 1,000 southern Mission properties were to be documented
  during 2008, in a separate product. The per-property records this document
  points at are therefore somewhere else, and going after them is the useful
  next move — see "Where the Mission's address-level data actually is" below.
- **There is no inventory table and no appendix.** Unlike the Central
  Waterfront statement, which promises eight appendices and delivers three,
  this one promises none. Its table of contents runs Introduction →
  Documenting Historic Resources → nine period chapters → Bibliography, ending
  at printed page 95, and the PDF's 98 pages are exactly that plus three
  sheets of front matter. Nothing is truncated or missing.
- **Everything it discusses is located by intersection, block bounds, street
  segment or district.** Around fifty individually named properties appear in
  the narrative — Mission Dolores chapel, the Tanforan Cottages, St. Peter's
  and St. John's, the Victoria, New Mission and El Capitan theaters, the
  National Guard Armory, the Notre Dame School, the B'nai David Temple, the
  Girls' Club, Mission High School, Valencia Gardens, the Bernal Dwellings,
  Dolores Terrace, the Mission Bank, the John Center Water Works, the Valencia
  Hotel, Recreation Park, Seals Stadium and others — and every one of them is
  pinned only to something like "Valencia and Fifteenth Streets", "the block
  bounded by Shotwell, Folsom, Fifteenth and Sixteenth", "on Sixteenth Street"
  or "just west of the project study area". The only two numerals adjacent to
  a street name in the whole document are the intersections "Larkin and 9th
  Streets" and "Valencia and 28th". Resolving any of these would mean picking
  a corner of an intersection or joining a proper name against a second
  dataset, which is the "stays unresolved" case in AGENTS.md → "Mining a
  corpus"; the Central Waterfront pass declined the identical class of hit and
  this one does too.
- **A useful non-address fact it does carry** is that the assessor's 1900
  year-built is a placeholder: San Francisco's building records burned in
  1906, so "almost all pre-disaster properties were arbitrarily assigned a
  'place-holder' construction date of 1900 in the Assessor's records"
  (footnote 9). That is the same 1900 the Central Waterfront statement's dates
  disagree with, and it is worth knowing before writing a page that leans on
  the roll's year built for a pre-1906 Mission building.
- **Where the Mission's address-level data actually is.** The document names
  its own predecessors and successors, and those are the documents to go after
  when the Mission is worked again: N. Moses Corrette's *Inner Mission North
  1853–1943 Context Statement* (2005); the Inner Mission North Survey itself,
  running since 2001 and about three-quarters complete in 2007, which produced
  the eight historic districts the Planning data already carries; Roland-Nawi
  Associates' *Mission Dolores Historic Context Statement* (2007); Page &
  Turnbull's *Context Statement: Market and Octavia Neighborhood Plan Area*
  (2007); and the 2007–2008 southern Mission survey this statement was written
  to guide. None of those is read into the repo.
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
- **Verified:** 2026-08-13 (Mission District: read all 98 pages of the archived
  PDF — 95 printed pages of narrative plus three of front matter, which is the
  whole document; its table of contents promises no appendix and none is
  missing. **0 numbered San Francisco street addresses appear in it**, so 0
  resolved in EAS, 0 pages were created and 0 were edited, and no page cites
  this document. The count is not an estimate: every numeric token in the
  extracted text was audited, and all of them are years, page numbers,
  populations, unit counts, dimensions or footnote and bulletin numbers. Around
  fifty individually named properties are discussed, each located only by
  intersection, block bounds, street segment or district — the class of hit the
  Central Waterfront pass also left undocumented. The three full-page graphics
  with no extractable text, PDF pages 45, 47 and 70, were rendered and read:
  they are the 1889, 1899 and 1914 Sanborn thematic maps, labelled with land
  uses and institution names and carrying no street numbers either. Coverage
  note: this document is read in full and nothing in it is outstanding, and it
  needs no second pass. What it points at has not been read — Corrette's *Inner
  Mission North 1853–1943 Context Statement* (2005), the Inner Mission North
  Survey, Roland-Nawi's *Mission Dolores Historic Context Statement* (2007),
  Page & Turnbull's Market & Octavia statement (2007), and the 2007–2008
  southern Mission survey of about 1,000 properties this statement was written
  to guide. Those, not this, are where the Mission's per-property records live.
  The Japantown and other adopted statements on the same SF Planning page
  remain untouched.)

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
