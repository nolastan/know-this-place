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
  The land-use / property-class code is how we determine **residential vs.
  business** during seeding.
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
    1906. Treat his claim as *site* history — record it under `site_history`
    with the source, and let the assessor's `year_property_built` show that the
    structure he saw is not the one standing.
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
