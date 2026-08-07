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
- **Coverage:** volumes 29 no. 2 and 30 no. 1 read in full. Volumes 30 no. 2,
  31 nos. 1–2 and 32 no. 1 are untouched.

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
