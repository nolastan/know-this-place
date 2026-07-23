# Data sources

The APIs and datasets agents draw from, in priority order. **Prefer these over
unguided web browsing** — they're accurate, fast, and auditable. Every fact
taken from a source gets an entry in the page's `data.json` `sources` array
(query URL + retrieval date) and a citation in the page footer.

Most DataSF datasets are Socrata: `https://data.sfgov.org/resource/<id>.json`
with SoQL query params (`$where`, `$select`, `$limit`). No auth required;
an app token (header `X-App-Token`) lifts throttling if we ever need it.

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
- **Verified:** 2026-07-21 (queried 700 block of Castro St, 56 rows)

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
- **Verified:** 2026-07-21 (parcel 2752016 = 744 Castro St)

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
- **Citation label:** "SF Planning Department"
- **Verified:** 2026-07-22 (dataset `3tsw-4idn`, apn 2752016 = 744 Castro St → ceqacode B)

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
- **State the status precisely.** "Eligible" for the California Register is
  **not** "listed", and neither implies local landmark protection — that
  requires an Article 10 district (`a10`). A parcel in a CR-eligible,
  non-Article-10 district carries no local landmark protection; don't imply
  otherwise. Note also that district-derived Category A applies to the whole
  parcel regardless of the building's age, so a modern building inside a
  district still reads as A (see 707 Castro Street, built 1980).
- **Citation label:** "SF Planning Department"
- **Verified:** 2026-07-21 (711 and 737 Castro St resolve to the Castro &
  Liberty Streets Historic District, CR-eligible, period 1897–1906, not
  Article 10; 720 Castro St, on the even side of the same block, is inside no
  district)

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
  - **Historical addresses.** Street numbers changed in 1909 and buildings
    have been demolished, so an address in the newsletter may not exist
    today. Check EAS before creating a page (see
    `corbett-heights/AGENTS.md` for worked examples).
  - **Living people.** Some issues are personal memoirs naming family
    members and the houses they lived in. Take the building facts; leave the
    people out, per the privacy rules in the root AGENTS.md. Deceased
    figures already published with dates (first owners, builders) may be
    named with citations.
- **Verified:** 2026-07-22 (page 1 of the archive, Dec 2025 – Jul 2026)

## local-news — Neighborhood news (secondary)

- **What:** Context and stories: Hoodline Castro archives, Bay Area Reporter
  archive (ebar.com), SF Chronicle. No structured APIs — this is cite-the-URL
  browsing territory. Quote sparingly; summarize and link.
- **Use for:** notable events tied to a specific address. Skip for routine
  seeding.

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
